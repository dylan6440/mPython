
# main.py -- put your code here!
from pyb import Pin, LED, delay

def wait_pin_change(pin, etat_souhaite):
    # wait for pin to change value
    # it needs to be stable for a continuous 50ms
    active = 0
    while active < 50:
        if pin.value() == etat_souhaite:
            active += 1
        else:
            active = 0
        delay(1)


push_button = pyb.Pin("PA0", pyb.Pin.IN, pyb.Pin.PULL_DOWN)
led = pyb.LED(4)


while True:
    wait_pin_change(pin=push_button, etat_souhaite=1)
    led.toggle()
    wait_pin_change(pin=push_button, etat_souhaite=0)
