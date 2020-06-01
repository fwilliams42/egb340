# RPi
import json
import time
from datetime import datetime
from gpiozero import LED, Button

import board
import busio
import digitalio
import adafruit_pcd8544
from PIL import Image, ImageDraw, ImageFont

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

# Create blank image for drawing. 1 bit colour
image = Image.new("1", (display.width, display.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Load a TTF font.
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

# New classes

class Menu():
    def __init__(self):

        with open('public/json/menu.json') as f:
            self.data = json.load(f)
            self.path = list()
            self.options = list(self.data.keys())
            self.current = self.options[0]
        
    def csr_up(self):
        ind = self.options.index(self.current) # Get the current index

        if ind != 0:
            self.current = self.options[ind - 1]
        else:
            self.current = self.options[-1]

        if self.current == 'disp_method':
            self.csr_up()

        self.disp()

    def csr_down(self):
        ind = self.options.index(self.current) # Get the current index
        
        if ind != len(self.options) - 1:
            self.current = self.options[ind + 1] # Set the currently selected option to the next
        else:
            self.current = self.options[0]

        if self.current == 'disp_method':
            self.csr_down()

        self.disp()
            
    def enter(self):

        cdir = self.get_dir()
        if cdir['disp_method'] == 'menu':
            self.path.append(self.current)
            self.options = list(cdir[self.current].keys())
            self.current = self.options[0]

        self.disp()

    def exit(self):

        try:
            self.path.pop()
            cdir = self.get_dir()
            self.options = list(cdir.keys())
            self.current = self.options[0]
        except IndexError:
            pass

        self.disp()

    def disp(self, cdir=None):
        if cdir is None:
            cdir = self.get_dir()

        if cdir['disp_method'] == 'menu':
            self.update()
        elif cdir['disp_method'] == 'data':
            self.disp_key_val()

    def get_dir(self):
        cdir = dict(self.data)

        for p in self.path:
            cdir = cdir[p]

        return cdir

    def update(self):

        draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0) # Clear drawing
        for i, text in enumerate(self.options):
            
            if text == 'disp_method':
                continue

            if text == self.current:
                text += " *"

            draw.text(
                (BORDER, BORDER + i * FONTSIZE),
                text,
                font=font,
                fill=255,
            )

        display.image(image)
        display.show()
    
    def disp_key_val(self):
        
        draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0) # Clear drawing

        i = 0
        cdir = self.get_dir()
        for key, val in cdir.items():

            if key == 'disp_method':
                continue
            
            text = f"{key}: {val}"

            draw.text(
                (BORDER, BORDER + i * FONTSIZE),
                text,
                font=font,
                fill=255,
            )

            i += 1
        
        display.image(image)
        display.show()

    def reload_data(self):
        with open('public/json/menu.json') as f:
            self.data = json.load(f)

    def timing(self, btn):  
        
        while btn.is_pressed: # not
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
menu.disp()

class TimingButton(Button):
    def __init__(self, pin=None, pull_up=False, active_state=None, bounce_time=None, hold_time=1, hold_repeat=False, pin_factory=None, number=None):
        super().__init__(pin=pin, pull_up=pull_up, active_state=active_state, bounce_time=bounce_time, hold_time=hold_time, hold_repeat=hold_repeat, pin_factory=pin_factory)
        self.start_time = datetime.now()
        self.end_time = datetime.now()
        self.is_timing = False
        self.number = number

# Setup i/o
led = LED(17)

enterBtn = Button(12)
exitBtn = Button(26)
downBtn = Button(4)
upBtn = Button(16)
tb1Btn = TimingButton(pin=21, number=1)
tb2Btn = TimingButton(pin=19, number=2)

def enterBtn_handler():
    menu.enter() 

def exitBtn_handler():
    menu.exit()

def downBtn_handler():
    menu.csr_down()

def upBtn_handler():
    menu.csr_up()

def btn_tb_gen_pressed(btn):
    btn.is_timing = True

    print(f"Timing started on toothbrush {btn.number}.")
    btn.start_time = datetime.now()

    menu.timing(btn)

def btn_tb_gen_released(btn):
    btn.is_timing = False

    print(f"Timing cancelled on toothbrush {btn.number}.")
    btn.end_time = datetime.now()

    t = btn.start_time.isoformat(sep=' ', timespec='minutes')
    dt = round((btn.end_time - btn.start_time).total_seconds(), 2)

    if (dt < 1): # 1 second min otherwise won't count
        menu.disp()
        return

    new_data_point = {'t': t, 'y': dt}

    user, secs = updateChart(btn, new_data_point)
    score, rank = updateTable(user)
    updateMenuStats(user, score, rank, secs)
    
    menu.reload_data()
    menu.disp()

def updateChart(btn, new_data_point):
    # Add the new data point
    with open('public/json/chart.json', 'r') as f:
        chart_data = json.load(f)

    # chart_data['data']['datasets'][$user$]['data'][$datapoint$]
    chart_data['data']['datasets'][btn.number-1]['data'].append(new_data_point) 

    with open('public/json/chart.json', 'w') as f:
        json.dump(chart_data, f, ensure_ascii=False, indent=4)

    temp = chart_data['data']['datasets'][btn.number-1]

    user = temp['label']
    total_secs = round(sum(item['y'] for item in temp['data']), 2)

    return user, total_secs

def updateTable(user):
    # Update the score
    with open('public/json/table.json', 'r') as f:
        table_data = json.load(f)

    user_index = find(table_data['data'], 'first', user)

    table_data['data'][user_index]['score'] += 1

    table_data['data'] = sorted(table_data['data'], key = lambda k: k['score'], reverse = True)
    
    for i, item in enumerate(table_data['data'], start=1):
        item['rank'] = i

    with open('public/json/table.json', 'w') as f:
        json.dump(table_data, f, ensure_ascii=False, indent=4)

    temp = table_data['data'][user_index]

    return temp['score'], temp['rank']

def updateMenuStats(user, score, rank, secs):
    with open('public/json/menu.json', 'r') as f:
        menu_data = json.load(f)
    
    menu_data['users'][user]['data'] = {
        'rank': rank,
        'score': score,
        'secs': secs,
        'disp_method': 'data'
    }

    with open('public/json/menu.json', 'w') as f:
        json.dump(menu_data, f, ensure_ascii=False, indent=4)

# Event handlers
enterBtn.when_activated = enterBtn_handler
exitBtn.when_activated = exitBtn_handler
downBtn.when_activated = downBtn_handler
upBtn.when_activated = upBtn_handler

tb1Btn.when_pressed = btn_tb_gen_pressed
tb1Btn.when_released = btn_tb_gen_released

tb2Btn.when_pressed = btn_tb_gen_pressed
tb2Btn.when_released = btn_tb_gen_released

# Swapped
# tb2Btn.when_released = btn_tb_gen_pressed
# tb2Btn.when_pressed = btn_tb_gen_released

print("Hardware controller started...")

# Useful functions elsewhere

def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return None

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