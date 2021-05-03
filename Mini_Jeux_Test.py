from pyb import SPI, Pin, UART, LED, delay

CS = Pin("PE3", Pin.OUT_PP)
SPI_1 = SPI(
    1,  # PA5, PA6, PA7
    SPI.MASTER,
    baudrate=50000,
    polarity=0,
    phase=0,
    # firstbit=SPI.MSB,
    # crc=None,
)

push_button = pyb.Pin("PA0", pyb.Pin.IN, pyb.Pin.PULL_DOWN)
uart = UART(2, 115200)
led_1 = pyb.LED(1)
led_2 = pyb.LED(2)
led_3 = pyb.LED(3)
led_4 = pyb.LED(4)

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

def clear_screen():
    uart.write("\x1b[2J \x1b[ ? 25 l")

def move(x, y):
    uart.write("\x1b[{};{}H".format(x, y))

def read_reg(addr):
    CS.low()
    SPI_1.send(addr | 0x80)  # 0x80 pour mettre le R/W à 1
    tab_values = SPI_1.recv(1)  # je lis une liste de 1 octet
    CS.high()
    return tab_values[0]

def write_reg(addr, value):
    CS.low()
    SPI_1.send(addr | 0x00)  # write
    SPI_1.send(value)
    CS.high()

def convert_value(high, low):
    value = (high << 8) | low
    if value & (1 << 15):
        # negative number
        value = value - (1 << 16)
    return value

def read_acceleration(base_addr):
    low = read_reg(base_addr)
    high = read_reg(base_addr + 1)
    return convert_value(high, low)


class Racket:
    def __init__(self, x, y, skin):
        self.x = x
        self.y = y
        self.skin = skin

    def erase(self):
        move(self.x, self.y)
        uart.write('  ' * len(self.skin))

    def move_right(self):
        self.erase()
        if self.y < (Right_Value - len(self.skin) - 5):
            self.y += velocity
        move(self.x, self.y)
        uart.write(self.skin)
        delay(100)

    def move_left(self):
        self.erase()
        if self.y > (Left_Value + 2):
            self.y -= velocity
        move(self.x, self.y)
        uart.write(self.skin)
        delay(100)

    def move_backward(self):
        self.erase()
        if self.x < (Bottom_Value - 2):
            self.x += velocity
        move(self.x, self.y)
        uart.write(self.skin)
        delay(100)

    def move_fordward(self):
        self.erase()
        if self.x > (Max_Value_move - 2):
            self.x -= velocity
        move(self.x, self.y)
        uart.write(self.skin)
        delay(100)


class Projectil:

    def __init__(self, x, y, skin):
        self.x = x
        self.y = y
        self.skin = skin

    def erase(self):
        move(self.x, self.y)
        uart.write('  ' * len(self.skin))

    def move(self):
        self.erase()
        if self.x > (Top_Value + 3):
            self.x -= (velocity * 2)
            move(self.x, self.y)
            uart.write(self.skin)
        elif self.x == (Top_Value + 3):
            proj_group.remove(self)
        delay(1)


def init_jeu():
    for Value_x in range(int(Top_Value), int(Bottom_Value)):
        move(Value_x, Left_Value)
        uart.write("|")
        move(Value_x, Right_Value)
        uart.write("|")

    for Value_y in range(int(Left_Value), int(Right_Value)):
        move(Top_Value, Value_y)
        uart.write("~")
        move(Bottom_Value, Value_y)
        uart.write("~")


Left_Value = 0
Right_Value = 205
Top_Value = 0
Max_Value_move = 42
Bottom_Value = 62

velocity = 1

value_spawn_x = 60
value_spawn_y = 100

r = Racket(x=value_spawn_x, y=value_spawn_y, skin="|-0-|")
proj_group = []

addr_who_am_i = 0x0F
#uart.write(read_reg(addr_who_am_i))
addr_ctrl_reg1 = 0x20
write_reg(addr_ctrl_reg1, 0x77)

clear_screen()
init_jeu()

while True:

    x_accel = read_acceleration(0x29)
    y_accel = read_acceleration(0x2B)
    z_accel = read_acceleration(0x2D)
    #value = str("Value X : {}, Value Y : {}, Value Z : {} \n".format(x_accel, y_accel, z_accel))
    #uart.write(value)
    #print("{:20}, {:20}, {:20}".format(x_accel, y_accel, z_accel))

    if push_button.value() == 1:
        proj_group.append(Projectil(x=(r.x+1), y=(r.y+2), skin="@"))

    for projectil in proj_group:
        projectil.move()

    if x_accel < 247:
        led_3.on()
        led_4.off()
        delay(50)
        r.move_fordward()

    elif x_accel == 247:
        led_4.on()
        led_3.on()
        delay(50)
        led_4.off()
        led_3.off()

    elif x_accel > 247:
        led_4.on()
        led_3.off()
        delay(50)
        r.move_backward()

    if y_accel < 7:
        led_2.on()
        led_1.off()
        r.move_left()

    elif y_accel == 7:
        led_2.on()
        led_1.on()
        delay(50)
        led_2.off()
        led_1.off()

    elif y_accel > 7:
        led_1.on()
        led_2.off()
        r.move_right()



