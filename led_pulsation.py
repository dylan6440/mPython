from pyb import SPI, Pin, UART, LED, delay, Timer

p = 0

t = Timer(4, freq=1000)


channel1 = t.channel(1, mode=Timer.PWM, pin=Pin("PD12"))
channel2 = t.channel(2, mode=Timer.PWM, pin=Pin("PD13"))
channel3 = t.channel(3, mode=Timer.PWM, pin=Pin("PD14"))
channel4 = t.channel(4, mode=Timer.PWM, pin=Pin("PD15"))

def pulse(value):
    channel1.pulse_width_percent(value)
    channel2.pulse_width_percent(value)
    channel3.pulse_width_percent(value)
    channel4.pulse_width_percent(value)


while True:

    if p < 100:
        p += 0.1
        pulse(p)
        delay(1)
    else:
        while p > 1:
            p -= 0.1
            pulse(p)
            delay(1)


