# main.py -- put your code here!
from pyb import Pin, LED, delay, UART


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
uart = UART(2, 115200)


def clear_screen():
    uart.write("\x1b[2J \x1b[ ? 25 l")


def move(x, y):
    uart.write("\x1b[{};{}H".format(x, y))


def hello():
    uart.write("Hello !")


while True:
    wait_pin_change(pin=push_button, etat_souhaite=1)
    move(20, 50)
    hello()
    wait_pin_change(pin=push_button, etat_souhaite=0)
    clear_screen()
