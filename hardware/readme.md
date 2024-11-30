# PS1 Project Voting System

A MicroPython-based voting system for PS1's project showcases, using RFID key fobs for voter identification, dual OLED displays, and rotary encoder input.

## Hardware Components
- Raspberry Pi Pico (RP2040)
- RDM6300 125KHz RFID Reader
- 1.3" OLED Display (SPI)
- SH1107 1.12" OLED Display (I2C)
- Rotary Encoder with Button
- 2x Push Buttons

## Code Evolution

### vote2.py - Manual ID Entry Version
- Basic voting functionality with manual ID entry
- Simple display functions for both screens
- Basic select/vote/results states
- Simple JSON saving/loading
- Basic encoder handling
- Single votes.json and voters.json files

### vote5.py - Initial RFID Version
- Added RFID reader integration but basic implementation
- Added display class refinements
- Added welcome screens
- Improved state management
- Added team information displays
- Basic in-progress vote handling
- First attempt at display orientation fixes

### vote5-final.py - Current Version
- Complete RFID implementation with proper debouncing and validation
- In-progress vote saving/resuming functionality
- Missing categories tracking and display
- Proper completed judges tracking
- Multiple data files (votes.json, completed_judges.json, in_progress_votes.json)
- Improved display orientation fixes
- Added error handling for all file operations
- Better state management with clear transitions
- Comprehensive help text on both displays
- Thank you screens and better UX flow
- Better button debouncing implementation
- More robust encoder handling
- Debug messages for troubleshooting

## Pin Configuration

```python
# SPI OLED Pins (1.3")
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

# I2C Pins (SH1107)
SCL = 1
SDA = 0

# RFID UART Pin
RFID_RX = 5

# Input Device Pins
ENC_A = 21  # Rotary Encoder A
ENC_B = 20  # Rotary Encoder B
KEY_A = 15  # OLED Button A
KEY_B = 17  # OLED Button B
```

## Usage
1. Power up the device
2. Present RFID key fob to reader
3. Use rotary encoder to select categories
4. Use buttons to confirm selections
5. View results using the results mode

## Data Storage
The system maintains three JSON files:
- votes.json: Tracks all votes by category
- completed_judges.json: List of RFID tags that have completed voting
- in_progress_votes.json: Saves incomplete voting sessions for resume capability
