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
KEY_B = Pin(16, Pin.IN, Pin.PULL_UP)    # Right button

# System Modes
MODE_WAITING = "WAITING_FOR_RFID"
MODE_JUDGE_MENU = "JUDGE_MENU"
MODE_CATEGORY_SELECT = "CATEGORY_SELECT"
MODE_VOTING = "VOTING"
MODE_CONFIRM_SUBMIT = "CONFIRM_SUBMIT"
MODE_RESULTS = "RESULTS"
MODE_THANK_YOU = "THANK_YOU"

# Add special category for final submission
SUBMIT_OPTION = "SUBMIT VOTES"

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
        self.rfid = RDM6300()
        self.mode = MODE_WAITING
        self.selected_category = 0  # For category selection menu
        self.selected_team = 0
        self.current_judge_id = None
        self.needs_refresh = True
        self.temp_votes = {}  # Store temporary votes until submission
        
        # Load or initialize voting data
        try:
            with open('votes.json', 'r') as f:
                self.votes = json.load(f)
        except:
            self.votes = {category: {} for category in CATEGORIES}
            
        try:
            with open('completed_judges.json', 'r') as f:
                self.completed_judges = json.load(f)
        except:
            self.completed_judges = []
            
        try:
            with open('in_progress_votes.json', 'r') as f:
                self.in_progress_votes = json.load(f)
        except:
            self.in_progress_votes = {}

    def save_data(self):
        """Save all voting data to files"""
        with open('votes.json', 'w') as f:
            json.dump(self.votes, f)
        with open('completed_judges.json', 'w') as f:
            json.dump(self.completed_judges, f)
        with open('in_progress_votes.json', 'w') as f:
            json.dump(self.in_progress_votes, f)

    def display_waiting_rfid(self):
        """Display initial screen"""
        self.oled.fill(0)
        self.oled.text("Cyberjam Round II", 5, 10, 1)
        self.oled.text("Tap PS1 key fob", 10, 35, 1)
        self.oled.show()

    def display_judge_menu(self):
        """Display judge menu screen"""
        self.oled.fill(0)
        self.oled.text("Judge ID:", 0, 0, 1)
        self.oled.text(str(self.current_judge_id), 0, 15, 1)
        
        if self.current_judge_id in self.completed_judges:
            self.oled.text("Already submitted!", 0, 30, 1)
            self.oled.text("B: View Results", 0, 45, 1)
        else:
            self.oled.text("A: Start/Continue", 0, 30, 1)
            self.oled.text("B: Exit", 0, 45, 1)
        self.oled.show()

    def display_category_select(self):
        """Display category selection menu"""
        self.oled.fill(0)
        self.oled.text("Select Category:", 0, 0, 1)
        
        # Get current selection (category or submit option)
        if self.selected_category < len(CATEGORIES):
            current = CATEGORIES[self.selected_category]
        else:
            current = SUBMIT_OPTION
        
        # Show current selection
        self.oled.text(">", 0, 20, 1)
        if len(current) > 16:
            self.oled.text(current[:16], 10, 20, 1)
            self.oled.text(current[16:], 10, 30, 1)
        else:
            self.oled.text(current, 10, 20, 1)
        
        # Show if category has been voted
        if current != SUBMIT_OPTION:
            voted = self.temp_votes.get(current, None)
            if voted:
                self.oled.text(f"Voted: {voted}", 10, 40, 1)
        
        self.oled.text("A:Select B:Back", 0, 55, 1)
        self.oled.show()

    def display_voting_screen(self):
        """Display team voting interface"""
        self.oled.fill(0)
        category = CATEGORIES[self.selected_category]
        
        # Display category name
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
        
        self.oled.text("A:Select  B:Back", 0, 55, 1)
        self.oled.show()

    def display_confirm_submit(self):
        """Display submission confirmation screen"""
        self.oled.fill(0)
        self.oled.text("Submit Votes?", 15, 10, 1)
        self.oled.text("A: Confirm", 5, 30, 1)
        self.oled.text("B: Go Back", 5, 45, 1)
        self.oled.show()

    def submit_votes(self):
        """Submit all votes and mark judge as completed"""
        # Transfer temporary votes to permanent storage
        for category, team in self.temp_votes.items():
            if category not in self.votes:
                self.votes[category] = {}
            self.votes[category][team] = self.votes[category].get(team, 0) + 1
        
        # Mark judge as completed and clear temporary votes
        self.completed_judges.append(self.current_judge_id)
        if self.current_judge_id in self.in_progress_votes:
            del self.in_progress_votes[self.current_judge_id]
        self.temp_votes = {}
        self.save_data()
        
    def get_missing_categories(self):
        """Return list of categories that haven't been voted on yet"""
        missing = []
        for category in CATEGORIES:
            if category not in self.temp_votes:
                missing.append(category)
        return missing

    def display_missing_categories(self):
        """Show warning about missing category votes"""
        missing = self.get_missing_categories()
        if not missing:
            return False
            
        self.oled.fill(0)
        self.oled.text("Missing votes:", 0, 0, 1)
        
        # Display missing categories
        y = 15
        for category in missing[:4]:  # Show up to 4 categories
            if len(category) > 16:
                self.oled.text(category[:16], 0, y, 1)
                y += 10
                self.oled.text(category[16:], 0, y, 1)
            else:
                self.oled.text(category, 0, y, 1)
            y += 10
            
        if len(missing) > 4:
            self.oled.text("...and more", 0, y, 1)
        
        self.oled.text("B: Back", 0, 55, 1)
        self.oled.show()
        return True

    def load_in_progress_votes(self):
        """Load any in-progress votes for the current judge"""
        if self.current_judge_id in self.in_progress_votes:
            self.temp_votes = self.in_progress_votes[self.current_judge_id]
        else:
            self.temp_votes = {}

    def save_in_progress_votes(self):
        """Save current voting progress"""
        self.in_progress_votes[self.current_judge_id] = self.temp_votes
        self.save_data()

    def display_results(self):
        """Display voting results"""
        self.oled.fill(0)
        category = CATEGORIES[self.selected_category]  # Changed from current_category
        
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
        if voting_system.mode == MODE_CATEGORY_SELECT:
            max_options = len(CATEGORIES) + 1  # Categories plus SUBMIT option
            voting_system.selected_category = (voting_system.selected_category + 1) % max_options
        elif voting_system.mode == MODE_VOTING:
            voting_system.selected_team = (voting_system.selected_team + 1) % len(TEAMS)
        elif voting_system.mode == MODE_RESULTS:
            voting_system.selected_category = (voting_system.selected_category + 1) % len(CATEGORIES)  # Changed from current_category
    else:  # Counter-clockwise
        if voting_system.mode == MODE_CATEGORY_SELECT:
            max_options = len(CATEGORIES) + 1
            voting_system.selected_category = (voting_system.selected_category - 1) % max_options
        elif voting_system.mode == MODE_VOTING:
            voting_system.selected_team = (voting_system.selected_team - 1) % len(TEAMS)
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
    if time.ticks_diff(current_time, last_refresh) > 50:
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
                else:  # SUBMIT option selected
                    missing = voting_system.get_missing_categories()
                    if not missing:
                        voting_system.mode = MODE_CONFIRM_SUBMIT
                    else:
                        voting_system.display_missing_categories()
                        time.sleep(2)  # Show the missing categories for 2 seconds
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
            voting_system.display_waiting_rfid()
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
    
    time.sleep(0.01)
