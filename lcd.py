# i2c_lcd.py
from machine import I2C
import time

class I2cLcd:
    def __init__(self, i2c, addr, rows, cols):
        self.i2c = i2c
        self.addr = addr
        self.rows = rows
        self.cols = cols
        self.backlight = 0x08
        self.lcd_init()

    def lcd_write(self, cmd, mode=0):
        high = mode | (cmd & 0xF0) | self.backlight
        low = mode | ((cmd << 4) & 0xF0) | self.backlight
        self.i2c.writeto(self.addr, bytes([high | 0x04]))
        self.i2c.writeto(self.addr, bytes([high & ~0x04]))
        self.i2c.writeto(self.addr, bytes([low | 0x04]))
        self.i2c.writeto(self.addr, bytes([low & ~0x04]))
        time.sleep_ms(2)

    def lcd_init(self):
        time.sleep_ms(20)
        self.lcd_write(0x33)
        self.lcd_write(0x32)
        self.lcd_write(0x28)
        self.lcd_write(0x0C)
        self.lcd_write(0x06)
        self.lcd_write(0x01)
        time.sleep_ms(5)

    def clear(self):
        self.lcd_write(0x01)
        time.sleep_ms(5)

    def goto(self, line, pos):
        line_offsets = [0x80, 0xC0]
        self.lcd_write(line_offsets[line] + pos)

    def write(self, string):
        for char in string:
            self.lcd_write(ord(char), 1)
