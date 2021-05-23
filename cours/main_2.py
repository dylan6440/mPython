# main.py -- put your code here!
import pyb

push_button = pyb.Pin("PA0", pyb.Pin.IN, pyb.Pin.PULL_DOWN)
led = pyb.LED(4)

while True:
    if push_button.value() == 1:
        led.toggle()
