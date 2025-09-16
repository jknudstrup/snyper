# hardware_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# Supports:
# ST7789 display with Raspberry Pi Pico W

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

from gui.core.ugui import Display
from machine import Pin, SPI
import gc

# The driver import path might need to be adjusted depending on your file structure.
# Assuming you have the st7789 driver library installed.
from display.drivers.st7789 import *

# This is a generic class name, but your driver class might be named differently
# (e.g., in your earlier code it was LCD_1inch3).
# We'll assume the library provides a class that wraps the ST7789 functionality.
SSD = ST7789 # Assuming the library class is named ST7789

# --- Pin assignments from your hardware setup ---
# Your previous code used:
# BL = 13
# DC = 8
# RST = 12
# MOSI = 11
# SCK = 10
# CS = 9

# Assigning your pins to the variable names used in the library's example.
pcs = Pin(9, Pin.OUT, value=1)   # Chip Select (CS) is on pin 9
prst = Pin(12, Pin.OUT, value=1)  # Reset (RST) is on pin 12
pbl = Pin(13, Pin.OUT, value=1)   # Backlight (BL) is on pin 13

gc.collect()  # Precaution before instantiating framebuf

# Configure the SPI bus with your pins.
spi = SPI(1, 10_000_000, sck=Pin(10), mosi=Pin(11), miso=None)
pdc = Pin(8, Pin.OUT, value=0)   # Data/Command (DC) is on pin 8

# Create the display driver instance using your pins.
ssd = SSD(spi, dc=pdc, cs=pcs, rst=prst, disp_mode=PORTRAIT)

# You'll also need to update the button pins to match your hardware if they are different.
# Your previous code used:
keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
keyX = Pin(19 ,Pin.IN,Pin.PULL_UP)
keyY= Pin(21 ,Pin.IN,Pin.PULL_UP)
up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
# ctrl = Pin(3,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)


# You must match the button pins here to what you've connected on your board.
# The `micropython-micro-gui` library uses a specific button layout.
# Based on the example, we'll map your existing button pins to the library's expected inputs.
# nxt = Pin(20, Pin.IN, Pin.PULL_UP) # Using your 'right' button for next
# # sel = ctrl
# sel = Pin(21, Pin.IN, Pin.PULL_UP) # Using your 'keyY' button for select
# prev = Pin(16, Pin.IN, Pin.PULL_UP) # Using your 'left' button for previous
# increase = Pin(2, Pin.IN, Pin.PULL_UP) # Using your 'up' button for increase
# decrease = Pin(18, Pin.IN, Pin.PULL_UP) # Using your 'down' button for decrease

# sel = keyY
# nxt = right
# prev = left
# increase = up
# decrease = down

sel = keyY
nxt = down
prev = up
increase = right
decrease = left


display = Display(ssd, nxt, sel, prev, increase, decrease)