from machine import Pin, SPI, UART
import framebuf
import time
import json

# OLED Display Pins (1.3")
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

# RFID
RFID_RX = 5

# Rotary Encoder Pins
ENC_A = Pin(21, Pin.IN, Pin.PULL_UP)
ENC_B = Pin(20, Pin.IN, Pin.PULL_UP)

# OLED Buttons
KEY_A = Pin(15, Pin.IN, Pin.PULL_UP)    # Left button
KEY_B = Pin(17, Pin.IN, Pin.PULL_UP)    # Right button

# System Modes
MODE_WAITING = "WAITING_FOR_RFID"
MODE_SELECT = "SELECT_VOTER"
MODE_VOTING = "VOTING"
MODE_RESULTS = "RESULTS"
MODE_THANK_YOU = "THANK_YOU"

# Voting System Constants
TEAMS = ["TabDuel", "VibeBox", "Harmony Hub", "Duncan Box"]
CATEGORIES = [
    "Best Trophy",
    "Best Immersive",
    "Most Improved",
    "Best Engineering",
    "Most Artistic"
]

class RDM6300:
    def __init__(self, rx_pin=5):
        # Initialize UART
        self.uart = UART(1, 
            baudrate=9600,
            rx=Pin(rx_pin),
            bits=8,
            parity=None,
            stop=1,
            timeout=100
        )
        
        # State tracking
        self.last_tag = None
        self.last_read_time = 0
        self.read_delay = 2000  # 2 second delay between same card reads
        
    def read_tag(self):
        """Read a tag and return it only if it's a new read or sufficient time has passed"""
        if not self.uart.any():
            return None
            
        # Read all available data
        data = self.uart.read()
        if not data or len(data) < 14:  # Minimum complete frame size
            return None
            
        # Process all complete frames in the data
        tag = None
        for i in range(len(data)):
            # Look for start byte
            if data[i] == 0x02 and i + 13 < len(data):
                # Check if we have a complete frame
                if data[i + 13] == 0x03:
                    try:
                        # Extract middle 10 bytes as tag ID
                        tag = data[i+1:i+11].decode()
                        break  # Use first valid frame found
                    except:
                        continue
        
        if not tag:
            return None
            
        # Handle debouncing/repeat reads
        current_time = time.ticks_ms()
        if tag == self.last_tag and time.ticks_diff(current_time, self.last_read_time) < self.read_delay:
            return None
            
        # Update state
        self.last_tag = tag
        self.last_read_time = current_time
        return tag
    
    def clear_tag(self):
        """Clear the last read tag - useful when changing states"""
        self.last_tag = None
        
    def flush(self):
        """Clear any pending data in the UART buffer"""
        if self.uart.any():
            self.uart.read()

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
        
        self.write_cmd(0xAE)  # turn off display
        self.write_cmd(0x00)  # set lower column start address
        self.write_cmd(0x10)  # set higher column start address
        self.write_cmd(0xB0)  # set page start address
        self.write_cmd(0xdc)  # set display start line
        self.write_cmd(0x00)
        self.write_cmd(0x81)  # contract control
        self.write_cmd(0x6f)  # 128
        self.write_cmd(0x21)  # Column addressing mode
        self.write_cmd(0xa1)  # set segment remap
        self.write_cmd(0xc0)  # Com scan direction
        self.write_cmd(0xa4)  # Disable Entire Display On
        self.write_cmd(0xa6)  # normal / reverse
        self.write_cmd(0xa8)  # multiplex ratio
        self.write_cmd(0x3f)  # duty = 1/64
        self.write_cmd(0xd3)  # set display offset
        self.write_cmd(0x60)
        self.write_cmd(0xd5)  # set osc division
        self.write_cmd(0x41)
        self.write_cmd(0xd9)  # set pre-charge period
        self.write_cmd(0x22)
        self.write_cmd(0xdb)  # set vcomh
        self.write_cmd(0x35)
        self.write_cmd(0xad)  # set charge pump enable
        self.write_cmd(0x8a)  # Set DC-DC enable
        self.write_cmd(0XAF)  # turn on display

    def show(self):
        self.write_cmd(0xb0)
        for page in range(0, 64):
            self.column = page
            self.write_cmd(0x00 + (self.column & 0x0f))
            self.write_cmd(0x10 + (self.column >> 4))
            for num in range(0, 16):
                self.write_data(self.buffer[page * 16 + num])

class VotingSystem:
    def __init__(self):
        self.oled = OLED_1inch3()
        self.rfid = RDM6300()  # New RFID reader
        self.mode = MODE_WAITING  # Start in RFID waiting mode
        self.current_category = 0
        self.selected_team = 0
        self.voter_id = 1
        self.max_voters = 50
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

    def save_data(self):
        """Save voting data to files"""
        with open('votes.json', 'w') as f:
            json.dump(self.votes, f)
        with open('voters.json', 'w') as f:
            json.dump(self.voters, f)

    def display_waiting_rfid(self):
        """Display RFID waiting screen"""
        self.oled.fill(0)
        self.oled.text("Tap your fob", 20, 20, 1)
        self.oled.text("to start voting", 10, 35, 1)
        self.oled.show()

    def display_voter_selection(self):
        """Display voter ID selection screen"""
        self.oled.fill(0)
        self.oled.text("PS1 Member ID:", 0, 0, 1)
        self.oled.text(f"ID: {self.voter_id}", 0, 20, 1)
        
        if self.voter_id in self.voters:
            self.oled.text("Already voted!", 0, 40, 1)
            self.oled.text("B: View Results", 0, 50, 1)
        else:
            self.oled.text("A: Start Vote", 0, 40, 1)
            if any(self.voters):  # Only show results option if votes exist
                self.oled.text("B: Results", 0, 50, 1)
        
        self.oled.show()

    def display_voting_screen(self):
        """Display category voting interface"""
        self.oled.fill(0)
        category = CATEGORIES[self.current_category]
        
        # Display category name (split if needed)
        if len(category) > 16:
            words = category.split()
            line1 = words[0]
            line2 = " ".join(words[1:])
            self.oled.text(line1, 0, 0, 1)
            self.oled.text(line2, 0, 10, 1)
        else:
            self.oled.text(category, 0, 5, 1)
        
        # Display selected team
        self.oled.text("Select Winner:", 0, 25, 1)
        self.oled.text(TEAMS[self.selected_team], 0, 35, 1)
        
        # Display controls
        self.oled.text("A:Select  B:Back", 0, 55, 1)
        self.oled.show()

    def display_results(self):
        """Display voting results"""
        self.oled.fill(0)
        category = CATEGORIES[self.current_category]
        
        # Show category name
        if len(category) > 16:
            self.oled.text(category[:16], 0, 0, 1)
            self.oled.text(category[16:], 0, 10, 1)
        else:
            self.oled.text(category, 0, 0, 1)
            
        # Show votes for each team
        y = 20
        if category in self.votes:
            for team in TEAMS:
                votes = self.votes[category].get(team, 0)
                self.oled.text(f"{team}: {votes}", 0, y, 1)
                y += 10
                
        self.oled.text("Rot:Next B:Back", 0, 55, 1)
        self.oled.show()

    def display_thank_you(self):
        """Display thank you message"""
        self.oled.fill(0)
        self.oled.text("Thank you for", 20, 20, 1)
        self.oled.text("voting!", 35, 30, 1)
        self.oled.show()
        time.sleep(2)
        self.mode = MODE_WAITING  # Return to waiting for RFID
        self.needs_refresh = True

    def register_vote(self):
        """Register vote for current category"""
        category = CATEGORIES[self.current_category]
        team = TEAMS[self.selected_team]
        
        if category not in self.votes:
            self.votes[category] = {}
            
        self.votes[category][team] = self.votes[category].get(team, 0) + 1
        
        # Move to next category or finish
        self.current_category += 1
        self.selected_team = 0  # Reset team selection
        
        if self.current_category >= len(CATEGORIES):
            self.current_category = 0
            self.voters.append(self.voter_id)
            self.save_data()
            self.mode = MODE_THANK_YOU
            return True
        return False

def encoder_handler(pin):
    """Handle rotary encoder rotation"""
    global voting_system
    if ENC_A.value():  # Clockwise
        if voting_system.mode == MODE_SELECT:
            voting_system.voter_id = min(voting_system.max_voters, voting_system.voter_id + 1)
        elif voting_system.mode == MODE_VOTING:
            voting_system.selected_team = (voting_system.selected_team + 1) % len(TEAMS)
        elif voting_system.mode == MODE_RESULTS:
            voting_system.current_category = (voting_system.current_category + 1) % len(CATEGORIES)
    else:  # Counter-clockwise
        if voting_system.mode == MODE_SELECT:
            voting_system.voter_id = max(1, voting_system.voter_id - 1)
        elif voting_system.mode == MODE_VOTING:
            voting_system.selected_team = (voting_system.selected_team - 1) % len(TEAMS)
        elif voting_system.mode == MODE_RESULTS:
            voting_system.current_category = (voting_system.current_category - 1) % len(CATEGORIES)
    voting_system.needs_refresh = True

# Initialize the voting system
voting_system = VotingSystem()

# Set up encoder interrupt
ENC_B.irq(trigger=Pin.IRQ_FALLING, handler=encoder_handler)

# Main loop
last_refresh = time.ticks_ms()
REFRESH_DELAY = 100  # Minimum ms between refreshes

while True:
    current_time = time.ticks_ms()
    
    # Check for RFID tags in waiting mode
    if voting_system.mode == MODE_WAITING:
        tag = voting_system.rfid.read_tag()
        if tag:
            print(f"Tag read: {tag}")  # For debugging
            voting_system.mode = MODE_SELECT
            voting_system.needs_refresh = True
    
    # Main loop continued...

    # Handle button inputs based on current mode
    if time.ticks_diff(current_time, last_refresh) > 50:  # Basic debounce
        if voting_system.mode == MODE_SELECT:
            if not KEY_A.value() and voting_system.voter_id not in voting_system.voters:
                voting_system.mode = MODE_VOTING
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
            if not KEY_B.value() and any(voting_system.voters):
                voting_system.mode = MODE_RESULTS
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
        elif voting_system.mode == MODE_VOTING:
            if not KEY_A.value():  # A button pressed
                if voting_system.register_vote():
                    voting_system.mode = MODE_THANK_YOU
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
            if not KEY_B.value():  # B button pressed
                voting_system.mode = MODE_WAITING
                voting_system.current_category = 0
                voting_system.selected_team = 0
                voting_system.needs_refresh = True
                voting_system.rfid.clear_tag()  # Clear the last tag so it can be read again
                time.sleep(0.2)
                
        elif voting_system.mode == MODE_RESULTS:
            if not KEY_B.value():  # B button pressed
                voting_system.mode = MODE_WAITING
                voting_system.needs_refresh = True
                voting_system.rfid.clear_tag()  # Clear the last tag so it can be read again
                time.sleep(0.2)
    
    # Update display only when needed and after minimum delay
    if voting_system.needs_refresh and time.ticks_diff(current_time, last_refresh) > REFRESH_DELAY:
        if voting_system.mode == MODE_WAITING:
            voting_system.display_waiting_rfid()
        elif voting_system.mode == MODE_SELECT:
            voting_system.display_voter_selection()
        elif voting_system.mode == MODE_VOTING:
            voting_system.display_voting_screen()
        elif voting_system.mode == MODE_RESULTS:
            voting_system.display_results()
        elif voting_system.mode == MODE_THANK_YOU:
            voting_system.display_thank_you()
        
        voting_system.needs_refresh = False
        last_refresh = current_time
    
    time.sleep(0.01)  # Small delay to prevent busy-waiting
