number_led = [1, 3, 2, 4]
delay = 1000

while push_button.value() == 1:
    delay -= 50
    for i in number_led:
        #pyb.delay(100)
        if i == 1:
            led = pyb.LED(i)
            led_2 = pyb.LED(3)
            led.on(), led_2.on()
            pyb.delay(delay)
            led.off(), led_2.off()
        elif i == 2:
            led = pyb.LED(i)
            led_2 = pyb.LED(4)
            led.on(), led_2.on()
            pyb.delay(delay)
            led.off(), led_2.off()
        elif i == 3:
            led = pyb.LED(i)
            led_2 = pyb.LED(2)
            led.on(), led_2.on()
            pyb.delay(delay)
            led.off(), led_2.off()
        elif i == 4:
            led = pyb.LED(i)
            led_2 = pyb.LED(1)
            led.on(), led_2.on()
            pyb.delay(delay)
            led.off(), led_2.off()
    #pyb.delay(100)
    boucle -= 0.5
