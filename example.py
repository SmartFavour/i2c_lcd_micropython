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

































from machine import Pin as pin,PWM,ADC,time_pulse_us,I2C
import network,uasyncio as asyncio,socket
from lcd import I2cLcd

chop = pin(25,pin.OUT)
heat = pin(26,pin.OUT)
blend = pin(27,pin.OUT)
sink = pin(13,pin.OUT)

chop_state = heat_state = blend_state = False

trash_echo = pin(, pin.IN)
sink_echo = pin(, pin.IN)
trig = pin(4,pin.OUT)

trash_servo = 17
solar_servo - 18

ldr1 = ADC(pin(32))
ldr2 = ADC(pin(33))

left = ldr1.atten(ADC.ATTN_11DB)
right = ldr2.atten(ADC.ATTN_11DB)


try:
    i2c= I2C(0,scl = pin(22),sda= pin(21),freq = 400000)
    addr = i2c.scan()[0]
    display = I2cLcd(i2c,addr,16,2)
except Exception as e:
    print("Lcd exception:")
    display = None
ref = display.clear()
def show(a,b,string):
    if display:
        try:
            display.goto(a,b)
            display.write(string)
        except:
            print("check lcd")
            pass
show("Cook ready")

def connect_ap(ssid="COOK",password = "cook12345"):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid = ssid,password = password,authmode = 3)
    print("ap mode:",ap.ifconfig())
    ref
    show(0,0ssid)
    show(1,0,password)
    return ap

def ultra(echo_pin:pin,timeout_us = 30000):
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    duration = time_pulse_us(echo_pin,1,timeout_us)
    distance = duration*0.0343/2
    if duration < 0:
        return None
    return distance

def servo(pin_num,angle,duration_ms=400):
    try:
        p = PWM(pin(pin_num),freq=50)
        pulse_us = 500 +(angle/180.0)*2000
        duty_ratio = pulse_us/2000.0
        try:
            p.duty_u16(duty_ratio *1023)
        except:
            p.duty(int(duty_ratio*65535))
        time.sleep_ms(duration_time)
        p.deinit()
    except:
        pass

async def periodic_sensor():
    while True:
        try:
            val = ultra(sink_ehco)
            if val is not None and val <= 15:
                sink.value(1)
                await asyncio.sleep(1)
                sink.value(0)
            await asyncio.sleep_ms(300)
        except:
            await asyncio.sleep_ms(500)
async def trahopp():
    cooldown_ms = 3000
    last = 0
    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now,last) > cooldown_ms:
            val = ultra(trash_echo)
            if val is not None and val<= 30:
                servo(trash_servo,0,duration_ms=600)
                await asyncio.sleep_ms(600)
                servo(trash_servo,90,duration_ms = 600)
                last= time.ticks_ms()
        await asyncio.sleep_ms(500)
html = f""""""
async def handle_client(reader,writer):
    global chop_state,heat_state,blend_state
    try:
        request = (await reader.readline()).decode().strip()
        if not request:
            await writer.aclose()
            return
        parts = request.split()
        if len(parts)<2:
          await writer.aclose()
            return

        method,path = parts[0],parts[1]

        while True:
            h= await reader.readline()
            if not h or h==b'\r\n': break

            if method== 'GET':
                it = 
                if path == '/':
                    writer.write('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n'.encode())
                    writer.write(html)
                    await writer.drain()
                    await wrietr.aclose()
                    return
              
                if path =='/heat':
                    heat_state=not heat_state
                    heat.value(0 if heat_state else 1)
                    body = "HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n".encode()
                    writer.write(body)
                    writer.write('1' if heat_state else '0')
                    await writer.drain()
                    await writer.aclose()
                    return
                        
                if path =='/chop':
                    chop_state=not chop_state
                    chop.value(0 if chop_state else 1)
                    body = "HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n".encode()
                    writer.write(body)
                    writer.write('1' if chop_state else '0')
                    await writer.drain()
                    await writer.aclose()
                    return
                    
                
                if path =='/blend':
                    blend_state=not blend_state
                    blend.value(0 if blend_state else 1)
                    body = "HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n".encode()
                    writer.write(body)
                    writer.write('1' if blend_state else '0')
                    await writer.drain()
                    await writer.aclose()
                    return


                if path == '/state':
                    import ujson
                    body = ujson.dumps{'chop':chop_state,'heat':heat_state,'blend':blend_state}
                    writer.write('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n'.encode())
                    writer.write(body)
                    await writer.drain()
                    await writer.aclose()
                    return

            writer.write('HTTP/1.0 404 Not found\r\nContent-Type: text/plain\r\n\r\nNot found')
            await writer.drain()
            await writer.aclose()

        except:
            try: await write.aclose()
            except: pass

async def main_code():
    for p in (chop, blend,chop_led,sink,heat_led,blend_led)
    try:
        p.value(1)
    except: pass

    connect_ap()
    server = await asyncio.start_server(handle_client,"0.0.0.0",80)
    asyncio.create_task(periodic_sensors())
    asyncio.create_taske(trashopp())

    while True:
        await asyncio.sleep(1)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
            
                
                    
    
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
