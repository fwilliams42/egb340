# RPi
import json
from datetime import datetime
import time
from gpiozero import LED, Button, HoldMixin, DigitalInputDevice

import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_pcd8544

import requests

# Parameters to Change
BORDER = 5
FONTSIZE = 10

spi = busio.SPI(board.SCK, MOSI=board.MOSI)
dc = digitalio.DigitalInOut(board.D6)  # data/command
cs = digitalio.DigitalInOut(board.CE0)  # Chip select
reset = digitalio.DigitalInOut(board.D5)  # reset

display = adafruit_pcd8544.PCD8544(spi, dc, cs, reset)

# Contrast and Brightness Settings
display.bias = 4
display.contrast = 40

# Turn on the Backlight LED
backlight = digitalio.DigitalInOut(board.D13)  # backlight
backlight.switch_to_output()
backlight.value = True

# Clear display.
display.fill(0)
display.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (display.width, display.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black background
draw.rectangle((0, 0, display.width, display.height), outline=255, fill=255)

# Draw a smaller inner rectangle
draw.rectangle(
    (BORDER, BORDER, display.width - BORDER - 1, display.height - BORDER - 1),
    outline=0,
    fill=0,
)

# Load a TTF font.
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

# Draw Some Text
text = "Welcome!"
(font_width, font_height) = font.getsize(text)
draw.text(
    (display.width // 2 - font_width // 2, display.height // 2 - font_height // 2),
    text,
    font=font,
    fill=255,
)

# Display image
display.image(image)
display.show()

# New classes

class Menu():
    def __init__(self):

        self.parentlist = list()
        with open('public/json/menu.json') as f:
            self.parentlist.append(json.load(f))

        self.options = list(self.parentlist[0].keys())
        self.current = self.options[0]
        
    def csr_up(self):
        ind = self.options.index(self.current) # Get the current index

        if ind != 0:
            self.current = self.options[ind - 1]
        else:
            self.current = self.options[-1]

        print(self.current)

    def csr_down(self):
        ind = self.options.index(self.current) # Get the current index
        
        if ind != len(self.options) - 1:
            self.current = self.options[ind + 1] # Set the currently selected option to the next
        else:
            self.current = self.options[0]
        
    def enter(self):
        
        temp = self.parentlist[-1][self.current] # Menu option going into

        if isinstance(temp, dict):
            self.parentlist.append(temp)
            self.options = list(temp.keys())
            self.current = self.options[0]
            self.update()
        elif isinstance(temp, list):
            # Trigger display of the list
            self.disp_list(temp)
            pass

    def exit(self):

        if len(self.parentlist) > 1:
            self.parentlist.pop()
            self.options = list(self.parentlist[-1].keys())
            self.current = self.options[0]
            
        self.update()


    def update(self):

        draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0) # Clear drawing

        for i, text in enumerate(self.options):

            if text == self.current:
                text += " *"

            draw.text(
                (BORDER, BORDER + i * font_height),
                text,
                font=font,
                fill=255,
            )

        display.image(image)
        display.show()
    
    def disp_list(self, li):
        
        draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0) # Clear drawing

        for i, val in enumerate(li):
            
            text = str(val)
            draw.text(
                (BORDER, BORDER + i * font_height),
                text,
                font=font,
                fill=255,
            )
            print(text)
        
        display.image(image)
        display.show()
        
    def timing(self, btn):  
        
        while btn.is_pressed:
            draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0) # Clear drawing
            sec = round((datetime.now() - btn.start_time).total_seconds(), 2)
            text = str(sec)

            draw.text(
                (BORDER, BORDER),
                text,
                font=font,
                fill=255
            )

            display.image(image)
            display.show()
            
            time.sleep(0.2)
            
menu = Menu()
menu.update()

class TimingButton(Button):
    def __init__(self, pin=None, pull_up=False, active_state=None, bounce_time=None, hold_time=1, hold_repeat=False, pin_factory=None, number=None):
        super().__init__(pin=pin, pull_up=pull_up, active_state=active_state, bounce_time=bounce_time, hold_time=hold_time, hold_repeat=hold_repeat, pin_factory=pin_factory)
        self.start_time = datetime.now()
        self.end_time = datetime.now()
        self.is_timing = False
        self.number = number

# Setup i/o
led = LED(17)
btn1 = Button(26)
btn2 = Button(16)
btn3 = Button(4)
btn4 = Button(12)
btn_tb1 = TimingButton(pin=21, number=1)
# btn_tb2 = TimingButton(pin=21, number=2)

def btn1handler():
    menu.enter()
    # led.toggle() 

def btn2handler():
    menu.exit()

def btn3handler():
    menu.csr_down()
    # led.toggle()

def btn4handler():
    menu.csr_up()
    # led.toggle()

def btn_tb_gen_pressed(btn):
    btn.is_timing = True

    print('Timing started.')
    btn.start_time = datetime.now()

    menu.timing(btn)

def btn_tb_gen_released(btn):
    btn.is_timing = False

    print('Timing cancelled.')
    btn.end_time = datetime.now()

    t = btn.start_time.isoformat(sep=' ', timespec='minutes')
    dt = round((btn.end_time - btn.start_time).total_seconds(), 2)

    if (dt < 1): # 1 second min otherwise won't count
        menu.update()
        return

    new_data_point = {'t': t, 'y': dt}

    user = updateChart(btn, new_data_point)
    updateTable(btn, user)
    
    menu.update()

def updateChart(btn, new_data_point):
    # Add the new data point
    with open('public/json/chart.json', 'r') as f:
        chart_data = json.load(f)

    # chart_data['data']['datasets'][$user$]['data'][$datapoint$]
    chart_data['data']['datasets'][btn.number-1]['data'].append(new_data_point) 

    with open('public/json/chart.json', 'w') as f:
        json.dump(chart_data, f, ensure_ascii=False, indent=4)

    return chart_data['data']['datasets'][btn.number-1]['label']

def updateTable(btn, user):
    # Update the score
    with open('public/json/table.json', 'r') as f:
        table_data = json.load(f)

    for data in table_data['data']:
        if (data['first'] == user):
            data['score'] += 1

    table_data['data'] = sorted(table_data['data'], key = lambda k: k['score'], reverse=True)
    
    for i, item in enumerate(table_data['data'], start=1):
        item['rank'] = i

    with open('public/json/table.json', 'w') as f:
        json.dump(table_data, f, ensure_ascii=False, indent=4)

def btn_tb1handler_pressed():
    btn_tb_gen_pressed(btn_tb1)

def btn_tb1handler_released():
    btn_tb_gen_released(btn_tb1)

# Event handlers
btn1.when_activated = btn1handler
btn2.when_activated = btn2handler
btn3.when_activated = btn3handler
btn4.when_activated = btn4handler
btn_tb1.when_pressed = btn_tb1handler_pressed
btn_tb1.when_released = btn_tb1handler_released

print("Hardware controller started...")

# Website to hardware functionality

def flash_menu():
    print("This will flash the menu")

def toggle_leds():
    print("This will toggle LEDs")

server_allowed_funcs = {'lcd': flash_menu, 'toggle': toggle_leds}

while True:
    func = input()
    try:
        server_allowed_funcs[func]()
    except:
        pass