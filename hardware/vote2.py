from machine import Pin, I2C, SPI
import framebuf
import time
import json

# SPI OLED Pins (1.3")
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

# I2C for SH1107
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

# After i2c initialization, add:
print("Scanning I2C addresses...")
devices = i2c.scan()
print(f"Found devices at: {[hex(device) for device in devices]}")

# Rotary Encoder Pins
ENC_A = Pin(21, Pin.IN, Pin.PULL_UP)
ENC_B = Pin(20, Pin.IN, Pin.PULL_UP)

# OLED Buttons
KEY_A = Pin(15, Pin.IN, Pin.PULL_UP)
KEY_B = Pin(16, Pin.IN, Pin.PULL_UP)

# Voting System Constants
TEAMS =  ["VibeBox", "Harmony Hub", "Duncan Box"]
CATEGORIES = [
    "Best Trophy",
    "Best Immersive",
    "Most Improved",
    "Best Engineering",
    "Most Artistic"
]

TEAM_INFO = {
    "VibeBox": "NFC Fashion\nAmbient Space\nMusic Control",
    "Harmony Hub": "AI Music\nReal-time Build\nCommunity Choice",
    "Duncan Box": "Supply Chain\nSmart Container\nQR Tracking"
}

class OLED_1inch3(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 128
        self.height = 64
        self.rotate = 180
        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1, 2000_000)
        self.spi = SPI(1, 20000_000, polarity=0, phase=0, sck=Pin(SCK), mosi=Pin(MOSI), miso=None)
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HMSB)
        self.init_display()
        self.white = 0xffff
        self.black = 0x0000
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""  
        self.rst(1)
        time.sleep(0.001)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)
        
        self.write_cmd(0xAE)
        self.write_cmd(0x00)
        self.write_cmd(0x10)
        self.write_cmd(0xB0)
        self.write_cmd(0xdc)
        self.write_cmd(0x00)
        self.write_cmd(0x81)
        self.write_cmd(0x6f)
        self.write_cmd(0x21)
        self.write_cmd(0xa1) # 180 degree rotation
        self.write_cmd(0xc0)
        self.write_cmd(0xa4)
        self.write_cmd(0xa6)
        self.write_cmd(0xa8)
        self.write_cmd(0x3f)
        self.write_cmd(0xd3)
        self.write_cmd(0x60)
        self.write_cmd(0xd5)
        self.write_cmd(0x41)
        self.write_cmd(0xd9)
        self.write_cmd(0x22)   
        self.write_cmd(0xdb)
        self.write_cmd(0x35)  
        self.write_cmd(0xad)
        self.write_cmd(0x8a)
        self.write_cmd(0XAF)

    def show(self):
        self.write_cmd(0xb0)
        for page in range(0, 64):
            self.column = page
            self.write_cmd(0x00 + (self.column & 0x0f))
            self.write_cmd(0x10 + (self.column >> 4))
            for num in range(0, 16):
                self.write_data(self.buffer[page * 16 + num])

class SH1107:
    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        self.pages = height // 8
        self.buffer = bytearray(self.pages * width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, width, height, framebuf.MONO_VLSB)
        self.addr = 0x3c
        self.init_display()
        self.needs_refresh = True
        
    def write_cmd(self, cmd):
        i2c.writeto(self.addr, bytes([0x00, cmd]))

    def write_data(self, buf):
        i2c.writeto(self.addr, b'\x40' + buf)
        
    def init_display(self):
        for cmd in [
            0xAE, 0xDC, 0x00, 0x81, 0x7F, 
            0x20, 0xA0, 0xC0, 0xA8, 0x7F,
            0xD3, 0x00, 0xD5, 0x51, 0xD9,
            0x22, 0xDB, 0x35, 0xB0, 0xDA,
            0x12, 0xA4, 0xA6, 0xAF
        ]:
            self.write_cmd(cmd)
            
    def show(self):
        if self.needs_refresh:
            for page in range(self.pages):
                self.write_cmd(0xB0 + page)
                self.write_cmd(0x00)
                self.write_cmd(0x10)
                self.write_data(self.buffer[self.width * page:self.width * (page + 1)])
            self.needs_refresh = False

    def clear(self):
        self.framebuf.fill(0)
        self.needs_refresh = True
        self.show()

class VotingSystem:
    def __init__(self):
        # Initialize displays
        self.main_oled = OLED_1inch3()  # Your existing main OLED class
        self.info_oled = SH1107()
        
        self.mode = "SELECT_VOTER"
        self.voter_id = 1
        self.current_team = 0
        self.current_category = 0
        self.needs_refresh = True
        
        # Load or initialize voting data
        try:
            with open('votes.json', 'r') as f:
                self.votes = json.load(f)
        except:
            self.votes = {category: {} for category in CATEGORIES}
            
        try:
            with open('voters.json', 'r') as f:
                self.voters = json.load(f)
        except:
            self.voters = []

    def update_info_display(self):
        """Update team info on the SH1107 display"""
        self.info_oled.clear()
        fb = self.info_oled.framebuf
        
        team = TEAMS[self.current_team]
        info = TEAM_INFO[team]
        
        # Draw title
        fb.text(team, 0, 0, 1)
        fb.text("-" * 16, 0, 10, 1)
        
        # Draw info text
        y = 25
        for line in info.split('\n'):
            fb.text(line, 0, y, 1)
            y += 12
            
        self.info_oled.needs_refresh = True
        self.info_oled.show()

    def update_voting_display(self):
        """Update voting interface on main OLED"""
        self.main_oled.fill(0)
        
        if self.mode == "SELECT_VOTER":
            self.main_oled.text("PS1 Member ID:", 0, 0, 1)
            self.main_oled.text(f"ID: {self.voter_id}", 0, 20, 1)
            self.main_oled.text("A: Start Vote", 0, 40, 1)
            self.main_oled.text("B: Results", 0, 50, 1)
            
        elif self.mode == "VOTING":
            self.main_oled.text(CATEGORIES[self.current_category], 0, 0, 1)
            self.main_oled.text("Select Winner:", 0, 20, 1)
            self.main_oled.text(TEAMS[self.current_team], 0, 35, 1)
            self.main_oled.text("A:Select  B:Back", 0, 55, 1)
            
        elif self.mode == "RESULTS":
            cat = CATEGORIES[self.current_category]
            self.main_oled.text(cat[:16], 0, 0, 1)
            y = 15
            if cat in self.votes:
                for team in TEAMS:
                    votes = self.votes[cat].get(team, 0)
                    self.main_oled.text(f"{team}: {votes}", 0, y, 1)
                    y += 10
                    
        self.main_oled.show()

    def register_vote(self):
        """Register vote for current category"""
        category = CATEGORIES[self.current_category]
        team = TEAMS[self.current_team]
        
        if category not in self.votes:
            self.votes[category] = {}
            
        self.votes[category][team] = self.votes[category].get(team, 0) + 1
        
        # Move to next category
        self.current_category += 1
        if self.current_category >= len(CATEGORIES):
            self.current_category = 0
            self.voters.append(self.voter_id)
            self.save_data()
            return True
        return False

    def save_data(self):
        with open('votes.json', 'w') as f:
            json.dump(self.votes, f)
        with open('voters.json', 'w') as f:
            json.dump(self.voters, f)

def encoder_handler(pin):
    """Handle rotary encoder rotation"""
    global voting_system
    if ENC_A.value():  # Clockwise
        if voting_system.mode == "SELECT_VOTER":
            voting_system.voter_id = min(50, voting_system.voter_id + 1)
        elif voting_system.mode == "VOTING":
            voting_system.current_team = (voting_system.current_team + 1) % len(TEAMS)
            voting_system.update_info_display()
        elif voting_system.mode == "RESULTS":
            voting_system.current_category = (voting_system.current_category + 1) % len(CATEGORIES)
    else:  # Counter-clockwise
        if voting_system.mode == "SELECT_VOTER":
            voting_system.voter_id = max(1, voting_system.voter_id - 1)
        elif voting_system.mode == "VOTING":
            voting_system.current_team = (voting_system.current_team - 1) % len(TEAMS)
            voting_system.update_info_display()
        elif voting_system.mode == "RESULTS":
            voting_system.current_category = (voting_system.current_category - 1) % len(CATEGORIES)
    voting_system.needs_refresh = True

# Initialize and run
voting_system = VotingSystem()
ENC_B.irq(encoder_handler, Pin.IRQ_FALLING)

# Main loop with reduced refresh rate
last_refresh = time.ticks_ms()
REFRESH_DELAY = 100  # Minimum ms between refreshes

while True:
    current_time = time.ticks_ms()
    
    # Handle button inputs
    if voting_system.mode == "SELECT_VOTER":
        if not KEY_A.value():  # A button pressed
            if voting_system.voter_id not in voting_system.voters:
                voting_system.mode = "VOTING"
                voting_system.needs_refresh = True
                voting_system.update_info_display()  # Show first team info
                time.sleep(0.2)
            else:
                voting_system.main_oled.fill(0)
                voting_system.main_oled.text("Already voted!", 0, 20, 1)
                voting_system.main_oled.show()
                time.sleep(1)
                voting_system.needs_refresh = True
                
        if not KEY_B.value():  # B button pressed
            voting_system.mode = "RESULTS"
            voting_system.needs_refresh = True
            time.sleep(0.2)
            
    elif voting_system.mode == "VOTING":
        if not KEY_A.value():  # A button pressed
            if voting_system.register_vote():
                voting_system.mode = "SELECT_VOTER"
                voting_system.main_oled.fill(0)
                voting_system.main_oled.text("Voting complete!", 0, 20, 1)
                voting_system.main_oled.show()
                time.sleep(1)
            voting_system.needs_refresh = True
            time.sleep(0.2)
            
        if not KEY_B.value():  # B button pressed
            voting_system.mode = "SELECT_VOTER"
            voting_system.needs_refresh = True
            time.sleep(0.2)
            
    elif voting_system.mode == "RESULTS":
        if not KEY_B.value():  # B button pressed
            voting_system.mode = "SELECT_VOTER"
            voting_system.needs_refresh = True
            time.sleep(0.2)
    
    # Update display only when needed and after minimum delay
    if voting_system.needs_refresh and time.ticks_diff(current_time, last_refresh) > REFRESH_DELAY:
        voting_system.update_voting_display()
        voting_system.needs_refresh = False
        last_refresh = current_time
    
    time.sleep(0.01)  # Small delay to prevent busy waiting
