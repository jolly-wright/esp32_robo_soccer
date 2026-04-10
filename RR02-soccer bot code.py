import network, espnow, time, machine, json, gc
from machine import Pin, PWM

#pin setup#
#leds
led1 = PWM(Pin(15), freq=1000)
led2 = PWM(Pin(13), freq=1000)
led3 = PWM(Pin(2), freq=1000)
led4 = PWM(Pin(26), freq=1000)
#motor driver pins
#Left 4 pins
LLEN = machine.Pin(18, machine.Pin.OUT)
LREN = machine.Pin(23, machine.Pin.OUT)
LLPWM = PWM(Pin(21), freq=20000)
LRPWM = PWM(Pin(19), freq=20000)
#Right 4 pins
RLEN = machine.Pin(17, machine.Pin.OUT)
RREN = machine.Pin(16, machine.Pin.OUT)
RLPWM = PWM(Pin(4), freq=20000)
RRPWM = PWM(Pin(25), freq=20000)
#wifi for espnow
w0 = network.WLAN(network.STA_IF)
w0.active(True)
#espnow com
espcom = espnow.ESPNow()
espcom.active(True)

#functions#
#shutdown func for no signal
def shutdown():
    led1.duty(0)
    led2.duty(0)
    led3.duty(0)
    led4.duty(0)
    LLEN.value(0)
    LREN.value(0)
    RLEN.value(0)
    RREN.value(0)
    LLPWM.duty(0)
    LRPWM.duty(0)
    RRPWM.duty(0)
    RLPWM.duty(0)
shutdown()
#main event func
def event(data):
    print(data)
    light = data['ljoysw']
    if light == 1:
        led1.duty(20)
        led2.duty(20)
        led3.duty(200)
        led4.duty(200)
    else:
        led1.duty(0)
        led2.duty(0)
        led3.duty(0)
        led4.duty(0)
    x = data["rjoyx"]
    y = data["rjoyy"]
    throttle = data['ljoyy']
    throttle = int((100+throttle)/2) #to convert the -100 to 100 range into 0-100
    if (x<=10 and x>=-10):
        x = 0
    if (y<=10 and y>=-10):
        y = 0
    left = y-x
    right = y+x
    val_list = [left, right]
    for i in range(2):
        if (val_list[i] > 100):
            val_list[i] = 100
        if (val_list[i] < -100):
            val_list[i] = -100
    if val_list[0] < 0:
        lrotate = 'b'
        val_list[0] = val_list[0]*-1
    else:
        lrotate = 'f'
    if val_list[1] < 0:
        rrotate = 'b'
        val_list[1] = val_list[1]*-1
    else:
        rrotate = 'f'
    left_val = int((((val_list[0]*throttle)/100)/100)*1023)
    right_val = int((((val_list[1]*throttle)/100)/100)*1023)
    print(f'(l, r) = {val_list[0]}, {val_list[1]},throttle({throttle})')
    print(f'left, right = {left_val}, {right_val}')
    if lrotate == 'b':
        LLPWM.duty(0)
        LRPWM.duty(left_val)
    else:
        LLPWM.duty(left_val)
        LRPWM.duty(0)
    if rrotate == 'b':
        RLPWM.duty(0)
        RRPWM.duty(right_val)
    else:
        RLPWM.duty(right_val)
        RRPWM.duty(0)
mac = b'\x00K\x12<\xf28' #known mac address of a controller
espcom.add_peer(mac)
confirm = 'ok'
con_msg = json.dumps(confirm) #confirm msg of receiving signal
recv_error = 0
#enabling drivers
LLEN.value(1)
LREN.value(1)
RLEN.value(1)
RREN.value(1)
while True:
    try:
        host, msg = espcom.recv(100)
        if host==mac:
            try:
                data = json.loads(msg)
                print('data')
                event(data)
                espcom.send(con_msg)
                recv_error = 0
            except Exception as e:
                recv_error+=1
                print(e)
        else:
            recv_error+=1
    except Exception as er:
        print(er)
        continue
    if recv_error>=6:
                shutdown()
                recv_error=0
    time.sleep(0.07)