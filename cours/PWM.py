from pyb import Timer, Pin, delay

t = Timer(4, freq=1000)
channels = [
    t.channel(1, mode=Timer.PWM, pin=Pin("PD12")),
    t.channel(2, mode=Timer.PWM, pin=Pin("PD13")),
    t.channel(3, mode=Timer.PWM, pin=Pin("PD14")),
    t.channel(4, mode=Timer.PWM, pin=Pin("PD15")),
]
for _ in range(10):
    for percent in range(100):
        for channel in channels:
            channel.pulse_width_percent(percent)
            delay(1)
    for percent in range(100, 1, -1):
        for channel in channels:
            channel.pulse_width_percent(percent)
            delay(1)

