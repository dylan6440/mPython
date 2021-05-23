def game_play():
    global game

    t = Timer(4, freq=1 / 180)
    t.callback(velocity_up)

    t = Timer(5, freq=2)
    t.callback(clock)

    #   for y in range(8):
    #       for x in range(3):
    #           spaceship_group.append(Spaceship(x=5 + x * 6, y=33 + 19 * y, skin="||--V--||"))
    #   for y in range(9):
    #       for x in range(2):
    #            spaceship_group.append(Spaceship(x=8 + x * 6, y=24 + 19 * y, skin="||--V--||"))

    for y in range(4):
        for x in range(1):
            spaceship_group.append(Spaceship(x=5 + x * 6, y=33 + 19 * y, skin="||--V--||"))

    while True:
        game_info()

        x_accel = read_acceleration(value_addr_X)
        y_accel = read_acceleration(value_addr_Y)
        # z_accel = read_acceleration(0x2D)
        # value = str("Value X : {}, Value Y : {}, Value Z : {} \n".format(x_accel, y_accel, z_accel))
        # uart.write(value)
        # print("{:20}, {:20}, {:20}".format(x_accel, y_accel, z_accel))

        if r.etat == 1:
            game = "Game OVER"
            break

        if push_button.value() == 1 and len(proj_group) < value_max_proj:
            new_proj()

        for projectil in proj_group:
            projectil.move()

        for proj_spaceship in proj_spaceship_group:
            proj_spaceship.move()

        if len(spaceship_group) > 0:
            if (clock_timer % 15) != 0:
                if (clock_timer % 15) < 8:
                    for enemies in spaceship_group:
                        enemies.move_left()
                elif (clock_timer % 15) >= 8:
                    for enemies in spaceship_group:
                        enemies.move_right()
            elif (clock_timer % 5) == 0:
                choice(spaceship_group).shoot()

            elif (clock_timer % 30) == 0:
                for enemies in spaceship_group:
                    enemies.move_forward()
        elif len(spaceship_group) == 0:
            game_reset()
            game = "Victory"
            break

        if x_accel < balanced_x:
            r.move_fordward()

        elif x_accel == balanced_x:
            led_4.on()
            led_3.on()
            delay(100)
            led_4.off()
            led_3.off()

        elif x_accel > balanced_x:
            r.move_backward()

        if y_accel < balanced_y:
            r.move_left()

        elif y_accel == balanced_y:
            led_2.on()
            led_1.on()
            delay(100)
            led_2.off()
            led_1.off()

        elif y_accel > balanced_y:
            r.move_right()
