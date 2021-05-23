from pyb import SPI, Pin, UART, LED, delay, Timer

p = 0
t = Timer(4, freq=1000)

channel_groups = (
    t.channel(1, mode=Timer.PWM, pin=Pin("PD12")),
    t.channel(2, mode=Timer.PWM, pin=Pin("PD13")),
    t.channel(3, mode=Timer.PWM, pin=Pin("PD14")),
    t.channel(4, mode=Timer.PWM, pin=Pin("PD15")))

while True:

    if p < 100:
        p += 0.1
        for channel in channel_groups[:]:
            channel.pulse_width_percent(p)
        delay(1)
    else:
        while p > 1:
            p -= 0.1
            for channel in channel_groups[:]:
                channel.pulse_width_percent(p)
            delay(1)


