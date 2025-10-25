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

# from machine import Pin, I2C, time_pulse_us
# import time
# from i2c_lcd import I2cLcd
# 
# # --- LCD SETUP ---
# i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)   # Adjust pins for your board
# lcd = I2cLcd(i2c, 0x27, 2, 16)  # Address 0x27 or 0x3F (check with i2c.scan())
# 
# # --- ULTRASONIC SENSORS ---
# # Sensor 1 pins
# TRIG1 = Pin(5, Pin.OUT)
# ECHO1 = Pin(18, Pin.IN)
# 
# # Sensor 2 pins
# TRIG2 = Pin(17, Pin.OUT)
# ECHO2 = Pin(16, Pin.IN)
# 
# # --- RELAY SETUP ---
# relay = Pin(19, Pin.OUT)  # Relay control pin
# relay.off()
# 
# # --- FUNCTIONS ---
# def measure_distance(trig, echo):
#     trig.off()
#     time.sleep_us(2)
#     trig.on()
#     time.sleep_us(10)
#     trig.off()
#     duration = time_pulse_us(echo, 1, 30000)  # 30ms timeout
#     distance = (duration / 2) * 0.0343  # in cm
#     return distance
# 
# # --- MAIN LOOP ---
# lcd.clear()
# lcd.write("Ultrasonic Test")
# 
# time.sleep(2)
# lcd.clear()
# 
# while True:
#     d1 = measure_distance(TRIG1, ECHO1)
#     d2 = measure_distance(TRIG2, ECHO2)
# 
#     lcd.goto(0, 0)
#     lcd.write("D1:{:>5.1f}cm".format(d1))
#     lcd.goto(1, 0)
#     lcd.write("D2:{:>5.1f}cm".format(d2))
# 
#     # Simple relay control
#     if d1 < 10 or d2 < 10:
#         relay.on()
#     else:
#         relay.off()
# 
#     time.sleep(0.5)
