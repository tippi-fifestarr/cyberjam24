# Vote 5, with "improved" UI/UX and voting progress saver, but bugs! 
# Part 1: Imports and Initial Setup
from machine import Pin, I2C, SPI, UART
import framebuf
import time
import json

# Hardware Pin Assignments
# ======================

# SPI OLED Pins (1.3")
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

# Initialize I2C for SH1107
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

# Debug: I2C Scanner
print("Scanning I2C addresses...")
devices = i2c.scan()
print(f"Found devices at: {[hex(device) for device in devices]}")

# RFID UART Pin
RFID_RX = 5

# Input Device Pins
ENC_A = Pin(21, Pin.IN, Pin.PULL_UP)  # Rotary Encoder A
ENC_B = Pin(20, Pin.IN, Pin.PULL_UP)  # Rotary Encoder B
KEY_A = Pin(15, Pin.IN, Pin.PULL_UP)  # OLED Button A
KEY_B = Pin(17, Pin.IN, Pin.PULL_UP)  # OLED Button B

# System States
# ============
MODE_WAITING = "WAITING_FOR_RFID"
MODE_JUDGE_MENU = "JUDGE_MENU"
MODE_CATEGORY_SELECT = "CATEGORY_SELECT"
MODE_VOTING = "VOTING"
MODE_CONFIRM_SUBMIT = "CONFIRM_SUBMIT"
MODE_RESULTS = "RESULTS"
MODE_THANK_YOU = "THANK_YOU"

# Special category for final submission
SUBMIT_OPTION = "SUBMIT VOTES"

# Voting System Data
# ================
TEAMS = ["VibeBox", "Harmony Hub", "Duncan Box"]
CATEGORIES = [
    "Best Trophy",
    "Best Immersive",
    "Most Improved",
    "Best Engineering",
    "Most Artistic"
]

# Team Information Dictionary
TEAM_INFO = {
    "VibeBox": {
        "small": "NFC Fashion\nAmbient Space\nMusic Control",
        "big": [
            "Wearable NFC Tech",
            "Interactive Fashion",
            "Ambient Lighting"
        ]
    },
    "Harmony Hub": {
        "small": "AI Music\nReal-time Build\nCommunity Choice",
        "big": [
            "AI-Powered Music",
            "Real-time Creation",
            "Community Driven"
        ]
    },
    "Duncan Box": {
        "small": "Supply Chain\nSmart Container\nQR Tracking",
        "big": [
            "Smart Logistics",
            "IoT Container",
            "Real-time Tracking"
        ]
    }
}

# Welcome Screen ASCII Art
WELCOME_ART = """
   ____      _               _
  / ___|   _| |__   ___ _ __(_) __ _ _ __ ___
 | |  | | | | '_ \ / _ \ '__| |/ _` | '_ ` _ \\
 | |__| |_| | |_) |  __/ |  | | (_| | | | | | |
  \____\__, |_.__/ \___|_|  |_|\__,_|_| |_| |_|
       |___/
"""

# Part 2: RFID and Display Classes

class RDM6300:
    """RFID Reader Class for RDM6300 module"""
    def __init__(self, rx_pin=5):
        self.uart = UART(1, 
            baudrate=9600,
            rx=Pin(rx_pin),
            bits=8,
            parity=None,
            stop=1,
            timeout=100
        )
        self.last_tag = None
        self.last_read_time = 0
        self.read_delay = 2000  # 2 second delay between same card reads
        
    def read_tag(self):
        """Read RFID tag, includes debouncing and validation"""
        if not self.uart.any():
            return None
            
        data = self.uart.read()
        if not data or len(data) < 14:
            return None
            
        # Look for start and end markers in the data
        tag = None
        for i in range(len(data)):
            if data[i] == 0x02 and i + 13 < len(data):  # Start marker
                if data[i + 13] == 0x03:  # End marker
                    try:
                        tag = data[i+1:i+11].decode()  # Extract tag data
                        break
                    except:
                        continue
        
        if not tag:
            return None
            
        # Implement debouncing for repeated reads
        current_time = time.ticks_ms()
        if tag == self.last_tag and time.ticks_diff(current_time, self.last_read_time) < self.read_delay:
            return None
            
        self.last_tag = tag
        self.last_read_time = current_time
        return tag
    
    def clear_tag(self):
        """Clear the last read tag"""
        self.last_tag = None
        
    def flush(self):
        """Clear any pending data in the UART buffer"""
        if self.uart.any():
            self.uart.read()

class OLED_1inch3(framebuf.FrameBuffer):
    """Driver for the 1.3 inch OLED display (SPI)"""
    def __init__(self):
        self.width = 128
        self.height = 64
        
        # Initialize control pins
        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)
        self.dc = Pin(DC, Pin.OUT)
        
        self.cs(1)
        self.dc(1)
        
        # Initialize SPI
        self.spi = SPI(1,
                      baudrate=10000000,
                      polarity=0,
                      phase=0,
                      sck=Pin(SCK),
                      mosi=Pin(MOSI),
                      miso=None)
        
        # Initialize framebuffer
        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HMSB)
        self.init_display()
        
    def write_cmd(self, cmd):
        """Write a command to the display"""
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        """Write data to the display"""
        self.cs(1)
        self.dc(1)
        self.cs(0)
        if isinstance(buf, bytearray):
            self.spi.write(buf)
        else:
            self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize the display with required commands"""
        # Reset sequence
        self.rst(1)
        time.sleep(0.01)
        self.rst(0)
        time.sleep(0.1)
        self.rst(1)
        time.sleep(0.1)
        
        self.write_cmd(0xAE)  # Display off
        self.write_cmd(0x00)  # Set lower column start address
        self.write_cmd(0x10)  # Set higher column start address
        self.write_cmd(0x40)  # Set display start line
        self.write_cmd(0xB0)  # Set page address
        self.write_cmd(0x81)  # Set contrast control
        self.write_cmd(0xFF)  # Max contrast
        self.write_cmd(0xA1)  # Set segment remap (changed to A0 from A1)
        self.write_cmd(0xA6)  # Normal display
        self.write_cmd(0xA8)  # Select multiplex ratio
        self.write_cmd(0x3F)  # Duty = 1/64
        self.write_cmd(0xC0)  # Set COM output direction (changed to C0 from C8)
        self.write_cmd(0xD3)  # Set display offset
        self.write_cmd(0x00)  # No offset
        self.write_cmd(0xD5)  # Set display clock
        self.write_cmd(0x80)  # Recommended value
        self.write_cmd(0xD9)  # Set precharge period
        self.write_cmd(0xF1)  # Recommended value
        self.write_cmd(0xDA)  # Set COM pins
        self.write_cmd(0x12)
        self.write_cmd(0xDB)  # Set VCOMH
        self.write_cmd(0x40)
        self.write_cmd(0x8D)  # Set charge pump
        self.write_cmd(0x14)
        self.write_cmd(0xAF)  # Display on

    def show(self):
        """Update the display with the current buffer contents"""
        for page in range(8):
            self.write_cmd(0xB0 + page)
            self.write_cmd(0x00)
            self.write_cmd(0x10)
            self.write_data(self.buffer[page*16:(page+1)*16])

class SH1107:
    """Driver for the SH1107 OLED display (I2C)"""
    def __init__(self, width=128, height=128):
        self.width = width
        self.height = height
        self.pages = height // 8
        self.buffer = bytearray(self.pages * width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, width, height, framebuf.MONO_VLSB)
        self.addr = 0x3c  # Fixed I2C address for the display
        self.init_display()
        
    def write_cmd(self, cmd):
        """Write a command to the display"""
        i2c.writeto(self.addr, bytes([0x00, cmd]))

    def write_data(self, buf):
        """Write data to the display"""
        i2c.writeto(self.addr, b'\x40' + buf)
        
    def init_display(self):
        """Initialize the display with required commands"""
        commands = [
            0xAE,  # display off
            0xDC, 0x00,  # set display start line
            0x81, 0x7F,  # set contrast control
            0xA0,  # segment remap (change to 0xA0 to flip horizontally)
            0xA8, 0x7F,  # multiplex ratio
            0xD3, 0x00,  # set display offset
            0xD5, 0x51,  # set display clock
            0xD9, 0x22,  # set pre-charge period
            0xDB, 0x35,  # set vcomh
            0xB0,  # set page address
            0xDA, 0x12,  # com pins configuration
            0xA4,  # display all points normal
            0xA6,  # normal display
            0xC0,  # Set COM scan direction (0xC0 for normal, 0xC8 for flip)
            0xAF   # display on
        ]
        
        for cmd in commands:
            self.write_cmd(cmd)
            time.sleep(0.001)

    def show(self):
        """Update the display with the current buffer contents"""
        for page in range(self.pages):
            self.write_cmd(0xB0 + page)
            self.write_cmd(0x00)
            self.write_cmd(0x10)
            self.write_data(self.buffer[self.width * page:self.width * (page + 1)])
            
    def clear(self):
        """Clear the display"""
        self.framebuf.fill(0)
        self.show()
        
# Part 3: VotingSystem Class - Core and Display Methods

class VotingSystem:
    """Main voting system controller class"""
    def __init__(self):
        # Initialize displays and RFID reader
        self.main_oled = OLED_1inch3()
        self.info_oled = SH1107()
        self.rfid = RDM6300()
        
        # Initialize state variables
        self.mode = MODE_WAITING
        self.current_judge_id = None
        self.selected_category = 0
        self.selected_team = 0
        self.needs_refresh = True
        self.temp_votes = {}
        
        # Load or initialize voting data with error handling
        try:
            with open('votes.json', 'r') as f:
                self.votes = json.load(f)
        except (OSError, ValueError) as e:
            print(f"Initializing new votes file: {e}")
            self.votes = {category: {} for category in CATEGORIES}
            
        try:
            with open('completed_judges.json', 'r') as f:
                self.completed_judges = json.load(f)
        except (OSError, ValueError) as e:
            print(f"Initializing new judges file: {e}")
            self.completed_judges = []
            
        try:
            with open('in_progress_votes.json', 'r') as f:
                self.in_progress_votes = json.load(f)
        except (OSError, ValueError) as e:
            print(f"Initializing new progress file: {e}")
            self.in_progress_votes = {}
            
        # Show initial welcome screen
        self.display_welcome()

    def save_data(self):
        """Save all voting data to files with error handling"""
        try:
            with open('votes.json', 'w') as f:
                json.dump(self.votes, f)
            with open('completed_judges.json', 'w') as f:
                json.dump(self.completed_judges, f)
            with open('in_progress_votes.json', 'w') as f:
                json.dump(self.in_progress_votes, f)
        except OSError as e:
            print(f"Error saving data: {e}")

    def load_in_progress_votes(self):
        """Load in-progress votes for current judge"""
        if self.current_judge_id in self.in_progress_votes:
            self.temp_votes = self.in_progress_votes[self.current_judge_id]
        else:
            self.temp_votes = {}

    def save_in_progress_votes(self):
        """Save current in-progress votes"""
        if self.current_judge_id:
            self.in_progress_votes[self.current_judge_id] = self.temp_votes
            self.save_data()

    def get_missing_categories(self):
        """Return list of categories still needing votes"""
        return [cat for cat in CATEGORIES if cat not in self.temp_votes]

    def submit_votes(self):
        """Submit all votes and update records"""
        if not self.current_judge_id:
            return
            
        # Add votes to main voting record
        for category, team in self.temp_votes.items():
            if category not in self.votes:
                self.votes[category] = {}
            if team not in self.votes[category]:
                self.votes[category][team] = 0
            self.votes[category][team] += 1
        
        # Update completed judges and clean up in-progress
        self.completed_judges.append(self.current_judge_id)
        if self.current_judge_id in self.in_progress_votes:
            del self.in_progress_votes[self.current_judge_id]
        
        # Clear temporary votes
        self.temp_votes = {}
        
        # Save all changes
        self.save_data()

    def display_welcome(self):
        """Display welcome screen on both displays"""
        # Small display shows instructions
        self.info_oled.clear()
        fb = self.info_oled.framebuf
        fb.text("Welcome!", 0, 0, 1)
        fb.text("Tap key fob", 0, 20, 1)
        fb.text("to begin", 0, 32, 1)
        self.info_oled.show()
        
        # Big display shows art and title
        self.main_oled.fill(0)
        lines = WELCOME_ART.strip().split('\n')
        y = 2
        for line in lines:
            self.main_oled.text(line[:21], 0, y, 1)
            y += 8
        self.main_oled.text("PS1 Project Voting", 20, 55, 1)
        self.main_oled.show()

    def display_judge_menu(self):
        """Display judge menu on both displays"""
        # Small display - ID and instructions
        self.info_oled.clear()
        fb = self.info_oled.framebuf
        fb.text("Judge Menu", 0, 0, 1)
        fb.text(f"ID: {self.current_judge_id}", 0, 20, 1)
        
        if self.current_judge_id in self.completed_judges:
            fb.text("Already voted!", 0, 40, 1)
        else:
            fb.text("A: Start/Resume", 0, 40, 1)
        self.info_oled.show()
        
        # Big display - welcome and status
        self.main_oled.fill(0)
        self.main_oled.text("Welcome Judge!", 5, 5, 1)
        self.main_oled.text("-" * 20, 5, 15, 1)
        
        if self.current_judge_id in self.completed_judges:
            self.main_oled.text("You have already", 10, 25, 1)
            self.main_oled.text("submitted votes", 10, 35, 1)
            self.main_oled.text("B: View Results", 10, 45, 1)
        else:
            if self.current_judge_id in self.in_progress_votes:
                self.main_oled.text("You have votes", 10, 25, 1)
                self.main_oled.text("in progress", 10, 35, 1)
            self.main_oled.text("A: Start/Continue", 10, 45, 1)
            self.main_oled.text("B: Exit", 10, 55, 1)
        self.main_oled.show()

    def update_info_display(self):
        """Update team info on both displays"""
        self.info_oled.clear()
        fb = self.info_oled.framebuf
        
        team = TEAMS[self.selected_team]
        info = TEAM_INFO[team]["small"]
        
        # Draw title on small display
        fb.text(team, 0, 0, 1)
        fb.text("-" * 16, 0, 10, 1)
        
        # Draw info text on small display
        y = 25
        for line in info.split('\n'):
            fb.text(line, 0, y, 1)
            y += 12
        
        self.info_oled.show()
        
        # Big display - detailed info
        self.main_oled.fill(0)
        big_info = TEAM_INFO[team]["big"]
        
        self.main_oled.text(team, 5, 5, 1)
        self.main_oled.text("-" * 20, 5, 15, 1)
        
        y = 25
        for line in big_info:
            self.main_oled.text(line, 10, y, 1)
            y += 12
        
        self.main_oled.show()

    def display_missing_categories(self):
        """Display missing categories on both screens"""
        missing = self.get_missing_categories()
        
        # Update small display
        self.info_oled.clear()
        fb = self.info_oled.framebuf
        fb.text("Missing Votes:", 0, 0, 1)
        y = 15
        for cat in missing[:4]:  # Show up to 4 missing categories
            fb.text(cat[:16], 0, y, 1)
            y += 12
        self.info_oled.show()
        
        # Update main display
        self.main_oled.fill(0)
        self.main_oled.text("Missing Categories", 5, 5, 1)
        self.main_oled.text("-" * 20, 5, 15, 1)
        y = 25
        for cat in missing:
            if len(cat) > 21:
                words = cat.split()
                self.main_oled.text(" ".join(words[:2]), 5, y, 1)
                y += 10
                self.main_oled.text(" ".join(words[2:]), 5, y, 1)
            else:
                self.main_oled.text(cat, 5, y, 1)
            y += 10
        self.main_oled.show()
        
    def display_category_select(self):
        """Display category selection screens"""
        # Small display - categories
        self.info_oled.clear()
        fb = self.info_oled.framebuf
        fb.text("Select Category:", 0, 0, 1)
        
        if self.selected_category < len(CATEGORIES):
            current = CATEGORIES[self.selected_category]
        else:
            current = SUBMIT_OPTION
        
        fb.text(">", 0, 20, 1)
        fb.text(current[:16], 10, 20, 1)
        
        if current in self.temp_votes:
            fb.text(f"Team: {self.temp_votes[current]}", 0, 40, 1)
        fb.text("A:Select B:Back", 0, 55, 1)
        self.info_oled.show()
        
        # Big display - progress
        self.main_oled.fill(0)
        self.main_oled.text("Category Selection", 5, 5, 1)
        self.main_oled.text("-" * 20, 5, 15, 1)
        
        voted = len(self.temp_votes)
        total = len(CATEGORIES)
        self.main_oled.text(f"Progress: {voted}/{total}", 10, 25, 1)
        
        # Show category description if applicable
        if self.selected_category < len(CATEGORIES):
            cat = CATEGORIES[self.selected_category]
            if len(cat) > 16:
                words = cat.split()
                self.main_oled.text(" ".join(words[:2]), 10, 40, 1)
                self.main_oled.text(" ".join(words[2:]), 10, 50, 1)
            else:
                self.main_oled.text(cat, 10, 45, 1)
        self.main_oled.show()

    def display_voting_screen(self):
        """Display voting screen for current category"""
        # Small display - team selection
        self.info_oled.clear()
        fb = self.info_oled.framebuf
        
        team = TEAMS[self.selected_team]
        info = TEAM_INFO[team]["small"]
        
        fb.text(team, 0, 0, 1)
        fb.text("-" * 16, 0, 10, 1)
        fb.text(info.split('\n')[0], 0, 25, 1)
        fb.text("A:Select B:Back", 0, 55, 1)
        self.info_oled.show()
        
        # Big display - category and team info
        self.main_oled.fill(0)
        category = CATEGORIES[self.selected_category]
        
        # Display category name
        if len(category) > 16:
            words = category.split()
            self.main_oled.text(words[0], 0, 0, 1)
            self.main_oled.text(" ".join(words[1:]), 0, 10, 1)
        else:
            self.main_oled.text(category, 0, 5, 1)
        
        self.main_oled.text("-" * 20, 0, 20, 1)
        self.main_oled.text("Selected Team:", 0, 30, 1)
        self.main_oled.text(team, 10, 40, 1)
        
        self.main_oled.text("A:Vote  B:Back", 0, 55, 1)
        self.main_oled.show()

    def display_confirm_submit(self):
        """Display vote confirmation screen"""
        # Small display - confirmation
        self.info_oled.clear()
        fb = self.info_oled.framebuf
        fb.text("Submit Votes?", 0, 0, 1)
        fb.text("A: Yes", 0, 20, 1)
        fb.text("B: No, go back", 0, 35, 1)
        self.info_oled.show()
        
        # Big display - summary
        self.main_oled.fill(0)
        self.main_oled.text("Vote Summary", 5, 5, 1)
        self.main_oled.text("-" * 20, 5, 15, 1)
        
        y = 25
        for category in CATEGORIES:
            if category in self.temp_votes:
                team = self.temp_votes[category]
                text = f"{category[:8]}: {team[:8]}"
                self.main_oled.text(text, 0, y, 1)
                y += 10
        self.main_oled.show()

    def display_results(self):
        """Display voting results for current category"""
        category = CATEGORIES[self.selected_category]
        
        # Small display - navigation
        self.info_oled.clear()
        fb = self.info_oled.framebuf
        fb.text("Results", 0, 0, 1)
        fb.text(category[:16], 0, 15, 1)
        if len(category) > 16:
            fb.text(category[16:], 0, 25, 1)
        fb.text("Rotate: Next", 0, 45, 1)
        fb.text("B: Exit", 0, 55, 1)
        self.info_oled.show()
        
        # Big display - results
        self.main_oled.fill(0)
        self.main_oled.text(category[:21], 0, 0, 1)
        if len(category) > 21:
            self.main_oled.text(category[21:], 0, 10, 1)
            y_start = 25
        else:
            y_start = 15
            
        self.main_oled.text("-" * 20, 0, y_start, 1)
        y = y_start + 10
        
        if category in self.votes:
            for team in TEAMS:
                votes = self.votes[category].get(team, 0)
                self.main_oled.text(f"{team}: {votes}", 5, y, 1)
                y += 10
        
        self.main_oled.show()

    def display_thank_you(self):
        """Display thank you message"""
        # Small display
        self.info_oled.clear()
        fb = self.info_oled.framebuf
        fb.text("Thank you!", 25, 30, 1)
        self.info_oled.show()
        
        # Big display
        self.main_oled.fill(0)
        self.main_oled.text("Thank you for", 20, 20, 1)
        self.main_oled.text("your votes!", 25, 35, 1)
        self.main_oled.show()
        time.sleep(2)
        self.mode = MODE_WAITING
        self.needs_refresh = True

def encoder_handler(pin):
    """Handle rotary encoder rotation"""
    global voting_system
    if ENC_A.value():  # Clockwise
        if voting_system.mode == MODE_CATEGORY_SELECT:
            max_options = len(CATEGORIES) + 1  # Categories plus SUBMIT option
            voting_system.selected_category = (voting_system.selected_category + 1) % max_options
        elif voting_system.mode == MODE_VOTING:
            voting_system.selected_team = (voting_system.selected_team + 1) % len(TEAMS)
            voting_system.update_info_display()
        elif voting_system.mode == MODE_RESULTS:
            voting_system.selected_category = (voting_system.selected_category + 1) % len(CATEGORIES)
    else:  # Counter-clockwise
        if voting_system.mode == MODE_CATEGORY_SELECT:
            max_options = len(CATEGORIES) + 1
            voting_system.selected_category = (voting_system.selected_category - 1) % max_options
        elif voting_system.mode == MODE_VOTING:
            voting_system.selected_team = (voting_system.selected_team - 1) % len(TEAMS)
            voting_system.update_info_display()
        elif voting_system.mode == MODE_RESULTS:
            voting_system.selected_category = (voting_system.selected_category - 1) % len(CATEGORIES)
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
            voting_system.current_judge_id = tag
            voting_system.mode = MODE_JUDGE_MENU
            voting_system.load_in_progress_votes()
            voting_system.needs_refresh = True
    
    # Handle button inputs with debounce
    if time.ticks_diff(current_time, last_refresh) > 50:  # Basic debounce
        if voting_system.mode == MODE_JUDGE_MENU:
            if not KEY_A.value() and voting_system.current_judge_id not in voting_system.completed_judges:
                voting_system.mode = MODE_CATEGORY_SELECT
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
            if not KEY_B.value():
                if voting_system.current_judge_id in voting_system.completed_judges:
                    voting_system.mode = MODE_RESULTS
                else:
                    voting_system.mode = MODE_WAITING
                    voting_system.save_in_progress_votes()
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
        elif voting_system.mode == MODE_CATEGORY_SELECT:
            if not KEY_A.value():
                if voting_system.selected_category < len(CATEGORIES):
                    voting_system.mode = MODE_VOTING
                    voting_system.update_info_display()
                else:  # SUBMIT option selected
                    missing = voting_system.get_missing_categories()
                    if not missing:
                        voting_system.mode = MODE_CONFIRM_SUBMIT
                    else:
                        # Show missing categories temporarily
                        voting_system.display_missing_categories()
                        time.sleep(2)
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
            if not KEY_B.value():
                voting_system.mode = MODE_JUDGE_MENU
                voting_system.save_in_progress_votes()
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
        elif voting_system.mode == MODE_VOTING:
            if not KEY_A.value():
                category = CATEGORIES[voting_system.selected_category]
                team = TEAMS[voting_system.selected_team]
                voting_system.temp_votes[category] = team
                voting_system.mode = MODE_CATEGORY_SELECT
                voting_system.save_in_progress_votes()
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
            if not KEY_B.value():
                voting_system.mode = MODE_CATEGORY_SELECT
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
        elif voting_system.mode == MODE_CONFIRM_SUBMIT:
            if not KEY_A.value():
                voting_system.submit_votes()
                voting_system.mode = MODE_THANK_YOU
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
            if not KEY_B.value():
                voting_system.mode = MODE_CATEGORY_SELECT
                voting_system.needs_refresh = True
                time.sleep(0.2)
                
        elif voting_system.mode == MODE_RESULTS:
            if not KEY_B.value():
                voting_system.mode = MODE_WAITING
                voting_system.needs_refresh = True
                time.sleep(0.2)
    
    # Update display when needed
    if voting_system.needs_refresh and time.ticks_diff(current_time, last_refresh) > REFRESH_DELAY:
        if voting_system.mode == MODE_WAITING:
            voting_system.display_welcome()
        elif voting_system.mode == MODE_JUDGE_MENU:
            voting_system.display_judge_menu()
        elif voting_system.mode == MODE_CATEGORY_SELECT:
            voting_system.display_category_select()
        elif voting_system.mode == MODE_VOTING:
            voting_system.display_voting_screen()
        elif voting_system.mode == MODE_CONFIRM_SUBMIT:
            voting_system.display_confirm_submit()
        elif voting_system.mode == MODE_RESULTS:
            voting_system.display_results()
        elif voting_system.mode == MODE_THANK_YOU:
            voting_system.display_thank_you()
        
        voting_system.needs_refresh = False
        last_refresh = current_time
    
    time.sleep(0.01)  # Small delay to prevent busy waiting
