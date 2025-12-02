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
























































# main_async_cook_optimized.py
from machine import Pin, I2C, PWM, ADC, time_pulse_us
import time, network, uasyncio as asyncio
from lcd import I2cLcd
import dht, ujson

# ------------------ Pins / hardware ------------------
chop = Pin(25, Pin.OUT)
heat = Pin(26, Pin.OUT)
blend = Pin(27, Pin.OUT)
sink = Pin(13, Pin.OUT)

trig = Pin(4, Pin.OUT)
sink_echo = Pin(5, Pin.IN)
trash_echo = Pin(16, Pin.IN)

solar_servo_pin = 17
trash_servo_pin = 18

chop_led = Pin(14, Pin.OUT)
heat_led = Pin(12, Pin.OUT)
blend_led = Pin(2, Pin.OUT)

ldr_left = ADC(Pin(33))
ldr_right = ADC(Pin(32))
ldr_left.atten(ADC.ATTN_11DB)
ldr_right.atten(ADC.ATTN_11DB)

# DHT11 sensor (pin 19)
dht_sensor = dht.DHT11(Pin(19))
current_temp = None

# ------------------ State ------------------
chop_state = False
heat_state = False
blend_state = False

# ------------------ Wi-Fi AP ------------------
def start_ap(ssid="COOK", password="qweqweqwe"):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    try:
        ap.config(essid=ssid, password=password, authmode=3)
    except:
        ap.config(essid=ssid, password=password)
    print("AP started, ifconfig:", ap.ifconfig())
    return ap

# ------------------ LCD (optional) ------------------
try:
    i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)
    addr = i2c.scan()[0]
    lcd = I2cLcd(i2c, addr, 16, 2)
except Exception as e:
    lcd = None

async def show_async(msg):
    # update LCD but avoid blocking; do nothing if LCD missing
    if not lcd: return
    try:
        lcd.clear()
        lcd.putstr(str(msg))
    except:
        pass

# small helper for one-time synchronous show (used in startup)
def show(msg):
    if not lcd: return
    try:
        lcd.clear()
        lcd.putstr(str(msg))
    except:
        pass

show("COOK Ready")

# ------------------ Servo helper (async, non-blocking) ------------------
async def move_servo_async(pin_num, angle, duration_ms=300):
    try:
        pwm = PWM(Pin(pin_num), freq=50)
        pulse_us = 500 + int((angle / 180.0) * 2000)
        duty_ratio = pulse_us / 20000.0
        # try both duty interfaces depending on firmware
        try:
            pwm.duty(int(duty_ratio * 1023))
        except:
            pwm.duty_u16(int(duty_ratio * 65535))
        await asyncio.sleep_ms(duration_ms)
        pwm.deinit()
    except Exception:
        # don't crash event loop on servo errors
        try:
            pwm.deinit()
        except:
            pass

# ------------------ Ultrasonic single read ------------------
def ultra_once(trig_pin: Pin, echo_pin: Pin, timeout_us=300000):
    trig_pin.value(0)
    time.sleep_us(2)
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)
    duration = time_pulse_us(echo_pin, 1, timeout_us)
    if duration < 0:
        return None
    return (duration * 0.0343) / 2

# ------------------ Async tasks ------------------

# DHT reader (every 2s)
async def dht_task():
    global current_temp
    while True:
        try:
            dht_sensor.measure()
            current_temp = dht_sensor.temperature()
            # update LCD less often, in background
            await show_async("T:{}C".format(current_temp))
        except Exception:
            # ignore read errors
            pass
        await asyncio.sleep(2)

# Heater safety cutoff (turn off heater if temp >= MAX_TEMP)
MAX_TEMP = 80
async def heater_safety():
    global heat_state
    while True:
        try:
            if heat_state and current_temp is not None and current_temp >= MAX_TEMP:
                heat_state = False
                heat.value(0)
                heat_led.value(0)
                await show_async("HEATER OFF HOT")
        except Exception:
            pass
        await asyncio.sleep(1)

# Sink monitoring (ultrasonic)
async def periodic_sensors():
    while True:
        try:
            val = ultra_once(trig, sink_echo)
            if val is not None and val <= 15:
                sink.value(1)
                await asyncio.sleep(1)
                sink.value(0)
            await asyncio.sleep_ms(300)
        except Exception:
            await asyncio.sleep_ms(500)

# Trash servo automation
async def trash_task_loop():
    cooldown_ms = 3000
    last = 0
    while True:
        try:
            now = time.ticks_ms()
            if time.ticks_diff(now, last) > cooldown_ms:
                val = ultra_once(trig, trash_echo)
                if val is not None and val <= 40:
                    await move_servo_async(trash_servo_pin, 0, duration_ms=600)
                    await asyncio.sleep_ms(600)
                    await move_servo_async(trash_servo_pin, 90, duration_ms=600)
                    last = time.ticks_ms()
            await asyncio.sleep_ms(500)
        except Exception:
            await asyncio.sleep_ms(500)

# Solar tracking (LDR)
async def solar_track_loop():
    angle = 90
    tolerance = 10
    await move_servo_async(solar_servo_pin, angle, duration_ms=200)
    while True:
        try:
            diff = ldr_left.read() - ldr_right.read()
            if abs(diff) >= tolerance:
                if diff < -tolerance:
                    angle = min(180, angle + 5)
                elif diff > tolerance:
                    angle = max(0, angle - 5)
                await move_servo_async(solar_servo_pin, angle, duration_ms=200)
            await asyncio.sleep(2)
        except Exception:
            await asyncio.sleep(2000)

# ------------------ HTML Web Interface ------------------
ROOT_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>COOK Async</title>
<style>
body{font-family:Arial;background:#121212;color:#eee;text-align:center}
.container{max-width:420px;margin:20px auto;padding:18px;background:#1e1e1e;border-radius:10px}
button{width:100px;margin:6px;padding:10px;border:none;border-radius:8px;cursor:pointer}
.on{background:#4caf50;color:#fff} .off{background:#a33;color:#fff}
</style></head>
<body><div class="container">
<h2>COOK Controls</h2>
<p id="temp">Temperature: --°C</p>
<button id="chop_btn">Chop OFF</button>
<button id="blend_btn">Blend OFF</button>
<button id="heat_btn">Heat OFF</button>
<p id="status">Status: ready</p>
</div>
<script>
async function toggle(name){
  try{
    const r = await fetch('/'+name);
    const s = (await r.text()).trim()==='1';
    const b = document.getElementById(name+'_btn');
    b.innerText = name.toUpperCase() + (s?' ON':' OFF');
    b.className = s?'on':'off';
  }catch(e){document.getElementById('status').innerText='Network error'}
}
async function refresh(){
  try{
    const r = await fetch('/state');
    const j = await r.json();
    ['chop','blend','heat'].forEach(n=>{
      const b = document.getElementById(n+'_btn');
      b.innerText = n.toUpperCase() + (j[n]?' ON':' OFF');
      b.className = j[n]?'on':'off';
    });
    document.getElementById('temp').innerText = 'Temperature: ' + j.temp + '°C';
  }catch(e){}
}
['chop','blend','heat'].forEach(n=>{
  document.getElementById(n+'_btn').onclick = ()=>toggle(n);
});
setInterval(refresh,2000);
refresh();
</script></body></html>
"""

# ------------------ HTTP SERVER (robust writer handling) ------------------
async def handle_client(reader, writer):
    global chop_state, blend_state, heat_state
    try:
        line = await reader.readline()
        if not line:
            try: await writer.aclose()
            except: pass
            return
        try:
            line = line.decode().strip()
        except:
            line = str(line)
        parts = line.split()
        if len(parts) < 2:
            try: await writer.aclose()
            except: pass
            return
        method, path = parts[0], parts[1]

        # consume headers
        while True:
            h = await reader.readline()
            if not h or h == b'\r\n':
                break

        if method == 'GET' and path == '/':
            body = ROOT_HTML
            try:
                writer.write('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
                writer.write(body)
                await writer.drain()
            except Exception:
                pass
            finally:
                try: await writer.aclose()
                except: pass
            return

        # toggles
        for name in ('chop','blend','heat'):
            if method == 'GET' and path == f'/{name}':
                state = not globals()[f"{name}_state"]
                globals()[f"{name}_state"] = state
                globals()[name].value(1 if state else 0)
                globals()[f"{name}_led"].value(1 if state else 0)
                try:
                    writer.write('HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n')
                    writer.write('1' if state else '0')
                    await writer.drain()
                except Exception:
                    pass
                finally:
                    try: await writer.aclose()
                    except: pass
                return

        if method == 'GET' and path == '/state':
            data = {
                'chop': chop_state,
                'blend': blend_state,
                'heat': heat_state,
                'temp': current_temp if current_temp is not None else -1
            }
            try:
                body = ujson.dumps(data)
                writer.write('HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
                writer.write(body)
                await writer.drain()
            except Exception:
                pass
            finally:
                try: await writer.aclose()
                except: pass
            return

        # not found
        try:
            writer.write('HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot found')
            await writer.drain()
        except Exception:
            pass
        finally:
            try: await writer.aclose()
            except: pass

    except Exception:
        try: await writer.aclose()
        except: pass

# ------------------ MAIN ------------------
async def main():
    # ensure outputs off
    for p in (chop, blend, heat, chop_led, blend_led, heat_led, sink):
        try: p.value(0)
        except: pass

    show("COOK Ready")
    start_ap()

    # start server
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Server listening on 0.0.0.0:80")

    # create tasks
    asyncio.create_task(dht_task())
    asyncio.create_task(heater_safety())
    asyncio.create_task(periodic_sensors())
    asyncio.create_task(trash_task_loop())
    asyncio.create_task(solar_track_loop())

    # keep running
    try:
        async with server:
            await server.serve_forever()
    finally:
        # cleanup if needed
        try: server.close()
        except: pass

# run
try:
    asyncio.run(main())
finally:
    try:
        asyncio.new_event_loop()
    except:
        pass
