from pyb import SPI, Pin, UART, LED, delay, Timer


led_1 = pyb.LED(1)
led_2 = pyb.LED(2)
led_3 = pyb.LED(3)
led_4 = pyb.LED(4)

def cligno_1(timer):
    led_1.toggle()

def cligno_2(timer):
    led_2.toggle()

def cligno_3(timer):
    led_3.toggle()

while True:
    t = Timer(4, freq=2)
    t.callback(led_1)

    t = Timer(5, freq=0.2)
    t.callback(led_2)

    t = Timer(6, freq=0.2/6)
    t.callback(led_3)

