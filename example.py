#A simple hello world example for the lcd library micropython.
from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time

# Initialize I2C for the LCD
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

# Scan to find your LCD address
print("I2C addresses found:", i2c.scan())

# Create LCD object (use 0x27 or your address)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# Clear screen and display text
lcd.clear()
lcd.write("Hello, world!")

# Keep message displayed
while True:
    time.sleep(1)
