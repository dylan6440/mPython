# main.py -- put your code here!
from pyb import SPI, Pin, UART, LED, delay, Timer

Left_Value = 0
Right_Value = 205
Top_Value = 0
Max_Value_move = 42
Bottom_Value = 62

velocity = 1
value_max_proj = 20

value_spawn_x = 60
value_spawn_y = 100


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
    uart.write("\x1b[2J\x1b[?25l")


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
        if self.x > (Top_Value + velocity + 3):
            self.x -= (velocity)
            move(self.x, self.y)
            uart.write(self.skin)
        else:
            proj_group.remove(self)
        delay(1)


def new_proj():
    proj_group.append(Projectil(x=(r.x + 1), y=(r.y + 2), skin="@"))

class Ship:
    def __init__(self, x, y, skin, etat):
        self.x = x
        self.y = y
        self.skin = skin
        self.etat = etat


def compteur():
    move(20, 70)
    for i in range(15, -1, -1):
        value_compteur = "{} | ".format(i)
        uart.write(value_compteur)
        if push_button.value() == 1:
            break
        delay(1000)


def compteur_end():
    move(20, 25)
    text = "Try again : "
    uart.write(text)
    for i in range(60, 30, -1):
        value_compteur = "{} | ".format(i)
        uart.write(value_compteur)
        if push_button.value() == 1:
            break
        delay(1000)
    move(21, (25+len(text)))
    for i in range(30, -1, -1):
        value_compteur = "{} | ".format(i)
        uart.write(value_compteur)
        if push_button.value() == 1:
            break
        delay(1000)



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


def velocity_up(timer):
    global value_max_proj, velocity
    if velocity < 5:
        velocity += 1

    if value_max_proj > 3:
        value_max_proj -= 2

def logo():
    logo = r""" 
 ________  ________  ________  ________  _______           ___  ________   ___      ___ ________  ________  _______   ________  ________      
|\   ____\|\   __  \|\   __  \|\   ____\|\  ___ \         |\  \|\   ___  \|\  \    /  /|\   __  \|\   ___ \|\  ___ \ |\   __  \|\   ____\     
\ \  \___|\ \  \|\  \ \  \|\  \ \  \___|\ \   __/|        \ \  \ \  \\ \  \ \  \  /  / | \  \|\  \ \  \_|\ \ \   __/|\ \  \|\  \ \  \___|_    
 \ \_____  \ \   ____\ \   __  \ \  \    \ \  \_|/__       \ \  \ \  \\ \  \ \  \/  / / \ \   __  \ \  \ \\ \ \  \_|/_\ \   _  _\ \_____  \   
  \|____|\  \ \  \___|\ \  \ \  \ \  \____\ \  \_|\ \       \ \  \ \  \\ \  \ \    / /   \ \  \ \  \ \  \_\\ \ \  \_|\ \ \  \\  \\|____|\  \  
    ____\_\  \ \__\    \ \__\ \__\ \_______\ \_______\       \ \__\ \__\\ \__\ \__/ /     \ \__\ \__\ \_______\ \_______\ \__\\ _\ ____\_\  \ 
   |\_________\|__|     \|__|\|__|\|_______|\|_______|        \|__|\|__| \|__|\|__|/       \|__|\|__|\|_______|\|_______|\|__|\|__|\_________\
   \|_________|                                                                                                                   \|_________|                                                                                                                                         
"""
    tab_logo = logo.splitlines()
    largeur = len(tab_logo[7])
    a = 1
    b = int((Right_Value - largeur)/2)
    for i in tab_logo:
        move((25 + a), b)
        uart.write(i)
        a += 1

def logo_game_over():
    logo = r"""
 ________  ________  _____ ______   _______           ________  ___      ___ _______   ________     
|\   ____\|\   __  \|\   _ \  _   \|\  ___ \         |\   __  \|\  \    /  /|\  ___ \ |\   __  \    
\ \  \___|\ \  \|\  \ \  \\\__\ \  \ \   __/|        \ \  \|\  \ \  \  /  / | \   __/|\ \  \|\  \   
 \ \  \  __\ \   __  \ \  \\|__| \  \ \  \_|/__       \ \  \\\  \ \  \/  / / \ \  \_|/_\ \   _  _\  
  \ \  \|\  \ \  \ \  \ \  \    \ \  \ \  \_|\ \       \ \  \\\  \ \    / /   \ \  \_|\ \ \  \\  \| 
   \ \_______\ \__\ \__\ \__\    \ \__\ \_______\       \ \_______\ \__/ /     \ \_______\ \__\\ _\ 
    \|_______|\|__|\|__|\|__|     \|__|\|_______|        \|_______|\|__|/       \|_______|\|__|\|__|                                                                                                  
"""

    tab_logo = logo.splitlines()
    largeur = len(tab_logo[6])
    a = 1
    b = int((Right_Value - largeur) / 2)
    for i in tab_logo:
        move((35 + a), b)
        uart.write(i)
        a += 1


def game_play():
    t = Timer(4, freq=1/60)
    t.callback(velocity_up)

    while True:

        x_accel = read_acceleration(0x29)
        y_accel = read_acceleration(0x2B)
        #z_accel = read_acceleration(0x2D)
        # value = str("Value X : {}, Value Y : {}, Value Z : {} \n".format(x_accel, y_accel, z_accel))
        # uart.write(value)
        # print("{:20}, {:20}, {:20}".format(x_accel, y_accel, z_accel))

        move((Right_Value + 10), (Top_Value + 10))
        uart.write("Velocity = {} | Max Projectil = {} | Projectil Actuel = {} ".format(velocity, value_max_proj, len(proj_group)))


        if push_button.value() == 1 and len(proj_group) < value_max_proj:
            new_proj()

        for projectil in proj_group:
            projectil.move()

        if x_accel < 247:
            led_3.on()
            led_4.off()
            r.move_fordward()

        elif x_accel == 247:
            led_4.on()
            led_3.on()
            delay(100)
            led_4.off()
            led_3.off()

        elif x_accel > 247:
            led_4.on()
            led_3.off()
            r.move_backward()

        if y_accel < 7:
            led_2.on()
            led_1.off()
            r.move_left()

        elif y_accel == 7:
            led_2.on()
            led_1.on()
            delay(100)
            led_2.off()
            led_1.off()

        elif y_accel > 7:
            led_1.on()
            led_2.off()
            r.move_right()


r = Racket(x=value_spawn_x, y=value_spawn_y, skin="|-0-|")
proj_group = []

addr_who_am_i = 0x0F
# uart.write(read_reg(addr_who_am_i))
addr_ctrl_reg1 = 0x20
write_reg(addr_ctrl_reg1, 0x77)

game = "Lancement"

while True:

    if game == "Lancement":
        clear_screen()
        init_jeu()
        logo()
        compteur()
        game = "Play"

    elif game == "Play":
        clear_screen()
        init_jeu()
        game_play()

    elif game == "Game OVER":
        clear_screen()
        init_jeu()
        logo()
        logo_game_over()
        compteur_end()
        game = "Play"
