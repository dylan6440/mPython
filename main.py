# main.py -- put your code here!
from pyb import SPI, Pin, UART, LED, delay, Timer
from random import choice, randint
import pyb

# entrez l'adresse de votre accélérométre
value_addr_X = 0x29
value_addr_Y = 0x2B

# entrez les valeurs de votre X et Y quand l'axcélérométre est à plat
balanced_x = 247
balanced_y = 7

# Ne toucher pas ci-dessous
# |--------------------------------------------------------------------------------------------------------------------|
# |--------------------------------------------------------------------------------------------------------------------|
# |--------------------------------------------------------------------------------------------------------------------|

# definition des ports SPI | UART | Button | LED
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

# definition des variables utilisees et leur valeur par defaut

clock_timer = 0

Left_Value = 0
Right_Value = 205
Top_Value = 0
Max_Value_move = 52
Bottom_Value = 62

default_velocity = 1
velocity = default_velocity
test = 0

default_value_max_proj = 6
value_max_proj = default_value_max_proj

score = 0
default_score = 0

temps_de_jeux = 0
default_temps_de_jeux = 0

value_spawn_x = 60
value_spawn_y = 100

proj_group = []
spaceship_group = []
spaceship_group_2 = []
spaceship_group_3 = []
proj_spaceship_group = []


# definition des fonctions de lecture et d'ecriture | mouvement curseur UART

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


# creation de la classe racket (spaceship user)

class Racket:
    def __init__(self, x, y, skin):
        self.x = x
        self.y = y
        self.skin = skin
        self.etat = 0

    def erase(self):
        move(x=self.x, y=(self.y - 1))
        uart.write(' ' * (len(self.skin) +1))

    def move_right(self):
        led_1.on()
        led_2.off()
        self.erase()
        if self.y < (Right_Value - len(self.skin) - 5):
            self.y += 1 + velocity
        move(self.x, self.y)
        uart.write(self.skin)
        delay(100)

    def move_left(self):
        led_2.on()
        led_1.off()
        self.erase()
        if self.y > (Left_Value + 2 + len(self.skin)):
            self.y -= 1 + velocity
        move(self.x, self.y)
        uart.write(self.skin)
        delay(100)

    def move_backward(self):
        led_4.on()
        led_3.off()
        self.erase()
        if self.x < (Bottom_Value - (2 * velocity)):
            self.x += velocity
        move(self.x, self.y)
        uart.write(self.skin)
        delay(100)

    def move_fordward(self):
        led_3.on()
        led_4.off()
        self.erase()
        if self.x > (Max_Value_move - (2 * velocity)):
            self.x -= velocity
        move(self.x, self.y)
        uart.write(self.skin)
        delay(100)


# creation de la classe projectil (user)

class Projectil:

    def __init__(self, x, y, skin):
        self.x = x
        self.y = y
        self.skin = skin
        self.etat = 0

    def erase(self):
        move(self.x, (self.y - 1))
        uart.write(' ' * (len(self.skin) + 1))

    def move(self):
        self.erase()
        self.collide()
        if self.etat == 0:
            if self.x > (Top_Value + 3):
                self.x -= 2
                move(self.x, self.y)
                uart.write(self.skin)

            else:
                proj_group.remove(self)
        else:
            proj_group.remove(self)

        delay(1)

    def collide(self):
        global score
        for enemies in (spaceship_group + spaceship_group_2 + spaceship_group_3):
            if enemies.x <= self.x < enemies.x + 1 and enemies.y <= self.y < enemies.y + len(enemies.skin):
                enemies.health -= 1
                if enemies.health == 0:
                    enemies.erase()
                    spaceship_group.remove(enemies)
                    score += (600 - (velocity * 100))
                self.etat = 1


# creation d'un projectil (user) qui s'ajoute dans la liste des projectils user

def new_proj():
    proj_group.append(Projectil(x=(r.x + 1), y=(r.y + (len(r.skin) // 2)), skin="@"))


# creation de la classe Projectil ennemie

class Projectil_Spaceship:

    def __init__(self, x, y,):
        self.x = x
        self.y = y
        self.skin = "#"
        self.etat = 0

    def erase(self):
        move(self.x, self.y)
        uart.write(' ' * len(self.skin))

    def move(self):
        global game
        self.erase()
        self.collide()
        if self.etat == 0:
            if self.x < (Bottom_Value - velocity - 1):
                self.x += 1 + (velocity // 2)
                move(self.x, self.y)
                uart.write(self.skin)
            else:
                proj_spaceship_group.remove(self)
        delay(1)

    def collide(self):
        if r.x <= self.x < r.x + 2 and r.y <= self.y < r.y + len(r.skin):
            self.etat = 1
            r.etat = 1


# creation de la classe Spaceship ennemie

class Spaceship:
    def __init__(self, x, y, skin, health):
        self.x = x
        self.y = y
        self.skin = skin
        self.health = health
        self.etat_shoot = 0
        self.tab_skin = self.skin.splitlines()

    def erase(self):
        move(self.x, self.y)
        a = 0
        for i in self.tab_skin:
            move(x=(self.x + a), y=self.y - 1)
            uart.write(' ' * (len(i) + 1))
            a += 1

    def move_left(self):
        self.erase()
        if self.y > (Left_Value + 2):
            self.y -= 1 + (velocity // 2)
        self.write_skin()

    def move_right(self):
        self.erase()
        if self.y < (Right_Value - len(self.tab_skin[0]) - 5):
            self.y += 1 + (velocity // 2)
        self.write_skin()

    def move_forward(self):
        self.erase()
        if self.x < (Max_Value_move - velocity):
            self.x += 1
        self.write_skin()

    def move_backward(self):
        self.erase()
        if self.x > (Top_Value + velocity):
            self.x -= 1
        self.write_skin()

    def write_skin(self):
        move(self.x, self.y)
        a = 0
        for i in self.tab_skin:
            move(x=(self.x + a), y=self.y)
            uart.write(i)
            a += 1

    def shoot(self):
        if self.etat_shoot <= 25:
            proj_spaceship_group.append(
                Projectil_Spaceship(
                    x=self.x + 1 + len(self.tab_skin),
                    y=self.y + (len(self.tab_skin[0]) // 2),
                )
            )
            self.etat_shoot += 1

skin_enemis = r"""||--V--||"""

skin_boss = r"""..............................
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⣀⣠⢤⣶⣄⣀⡀⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⢀⣴⡾⠿⠿⠏⠛⠉⠋⠷⢿⣆⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⣞⢿⠇⠄⠄⠄⠄⠄⠄⠄⠄⠉⢣⣀⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⣿⣽⠆⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠳⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⣿⣿⠇⡀⠤⠄⣀⣀⡄⠄⠄⢀⠠⠒⢱⠆⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⢸⣿⡆⠄⢤⡤⣤⡤⠠⠄⠄⡙⠹⠞⠻⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠜⣿⡷⡀⠄⠄⠈⠄⠄⠄⠄⠱⡄⠄⠄⢰⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠈⣈⡙⣇⠄⠄⠄⠄⠄⠄⠄⠄⠌⢦⠄⠄⡆⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⢍⣣⠄⠄⠄⠄⠄⠄⣤⣀⣀⣂⡹⠄⡏⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⡀⣴⣿⣿⡀⢰⣶⣶⣶⠿⠿⠿⠿⡷⣴⡃⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⣿⢻⣿⣿⣾⡀⠱⢄⢀⣀⣀⡼⠁⢾⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⢳⠈⢿⣹⠿⣢⣄⣀⠄⣠⣤⢽⣾⡿⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⢹⣰⣞⣿⡇⠉⢿⣿⣷⣿⣿⣿⠏⠁⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠨⡟⠃⢽⣅⠄⠈⠏⠛⠿⠿⠉⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠈⠄⠄⠈⠙⠛⠶⠚⠉⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
"""


# definition des fonctions utilisees

def clock(timer):
    global clock_timer
    clock_timer += 1


def velocity_up(timer):
    global value_max_proj, velocity, test
    test += 1
    if (test % 2) == 0:
        if velocity < 5:
            velocity += 1

        if value_max_proj > 3:
            value_max_proj -= 1


def temps_de_jeux_up(timer):
    global temps_de_jeux
    temps_de_jeux += 1


def borders():
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


def logo():
    logo = r"""
 ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄  ▄               ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░░▌▐░░▌      ▐░▌▐░▌             ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀            ▀▀▀▀█░█▀▀▀▀ ▐░▌░▌     ▐░▌ ▐░▌           ▐░▌ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ 
▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌                         ▐░▌     ▐░▌▐░▌    ▐░▌  ▐░▌         ▐░▌  ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌       ▐░▌▐░▌          
▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░▌          ▐░█▄▄▄▄▄▄▄▄▄                ▐░▌     ▐░▌ ▐░▌   ▐░▌   ▐░▌       ▐░▌   ▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌          ▐░░░░░░░░░░░▌               ▐░▌     ▐░▌  ▐░▌  ▐░▌    ▐░▌     ▐░▌    ▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
 ▀▀▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░▌          ▐░█▀▀▀▀▀▀▀▀▀                ▐░▌     ▐░▌   ▐░▌ ▐░▌     ▐░▌   ▐░▌     ▐░█▀▀▀▀▀▀▀█░▌▐░▌       ▐░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀█░█▀▀  ▀▀▀▀▀▀▀▀▀█░▌
          ▐░▌▐░▌          ▐░▌       ▐░▌▐░▌          ▐░▌                         ▐░▌     ▐░▌    ▐░▌▐░▌      ▐░▌ ▐░▌      ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌     ▐░▌            ▐░▌
 ▄▄▄▄▄▄▄▄▄█░▌▐░▌          ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄            ▄▄▄▄█░█▄▄▄▄ ▐░▌     ▐░▐░▌       ▐░▐░▌       ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░▌      ▐░▌  ▄▄▄▄▄▄▄▄▄█░▌
▐░░░░░░░░░░░▌▐░▌          ▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░░▌▐░▌      ▐░░▌        ▐░▌        ▐░▌       ▐░▌▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌
 ▀▀▀▀▀▀▀▀▀▀▀  ▀            ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀            ▀▀▀▀▀▀▀▀▀▀▀  ▀        ▀▀          ▀          ▀         ▀  ▀▀▀▀▀▀▀▀▀▀   ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀ """
    tab_logo = logo.splitlines()
    largeur = len(tab_logo[7])
    a = 1
    b = int((Right_Value - largeur) / 2)
    for i in tab_logo:
        move((2 + a), b)
        uart.write(i)
        a += 1


def logo_game_over():
    logo = r"""
 ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄       ▄▄  ▄▄▄▄▄▄▄▄▄▄▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄               ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░▌     ▐░░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░░▌▐░▌             ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░▌░▌   ▐░▐░▌▐░█▀▀▀▀▀▀▀▀▀           ▐░█▀▀▀▀▀▀▀█░▌ ▐░▌           ▐░▌ ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌
▐░▌          ▐░▌       ▐░▌▐░▌▐░▌ ▐░▌▐░▌▐░▌                    ▐░▌       ▐░▌  ▐░▌         ▐░▌  ▐░▌          ▐░▌       ▐░▌
▐░▌ ▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░▌ ▐░▐░▌ ▐░▌▐░█▄▄▄▄▄▄▄▄▄           ▐░▌       ▐░▌   ▐░▌       ▐░▌   ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌
▐░▌▐░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌  ▐░▌  ▐░▌▐░░░░░░░░░░░▌          ▐░▌       ▐░▌    ▐░▌     ▐░▌    ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░▌ ▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░▌   ▀   ▐░▌▐░█▀▀▀▀▀▀▀▀▀           ▐░▌       ▐░▌     ▐░▌   ▐░▌     ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀█░█▀▀ 
▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌▐░▌                    ▐░▌       ▐░▌      ▐░▌ ▐░▌      ▐░▌          ▐░▌     ▐░▌  
▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄           ▐░█▄▄▄▄▄▄▄█░▌       ▐░▐░▌       ▐░█▄▄▄▄▄▄▄▄▄ ▐░▌      ▐░▌ 
▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░░▌        ▐░▌        ▐░░░░░░░░░░░▌▐░▌       ▐░▌
 ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀            ▀▀▀▀▀▀▀▀▀▀▀          ▀          ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀                                                                                                                      
"""

    tab_logo = logo.splitlines()
    largeur = len(tab_logo[6])
    a = 1
    b = int((Right_Value - largeur) / 2)
    for i in tab_logo:
        move((43 + a), b)
        uart.write(i)
        a += 1


def logo_victory():
    logo = r"""
 ▄               ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄         ▄ 
▐░▌             ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌
 ▐░▌           ▐░▌  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░▌       ▐░▌
  ▐░▌         ▐░▌       ▐░▌     ▐░▌               ▐░▌     ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌
   ▐░▌       ▐░▌        ▐░▌     ▐░▌               ▐░▌     ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌
    ▐░▌     ▐░▌         ▐░▌     ▐░▌               ▐░▌     ▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
     ▐░▌   ▐░▌          ▐░▌     ▐░▌               ▐░▌     ▐░▌       ▐░▌▐░█▀▀▀▀█░█▀▀  ▀▀▀▀█░█▀▀▀▀ 
      ▐░▌ ▐░▌           ▐░▌     ▐░▌               ▐░▌     ▐░▌       ▐░▌▐░▌     ▐░▌       ▐░▌     
       ▐░▐░▌        ▄▄▄▄█░█▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄      ▐░▌     ▐░█▄▄▄▄▄▄▄█░▌▐░▌      ▐░▌      ▐░▌     
        ▐░▌        ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░░░░░░░░░░░▌▐░▌       ▐░▌     ▐░▌     
         ▀          ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀       ▀       ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀       ▀                                                                                                
"""

    tab_logo = logo.splitlines()
    largeur = len(tab_logo[6])
    a = 1
    b = int((Right_Value - largeur) / 2)
    for i in tab_logo:
        move((43 + a), b)
        uart.write(i)
        a += 1


def game_reset():
    global spaceship_group, proj_group, proj_spaceship_group, default_velocity, velocity, default_value_max_proj, value_max_proj
    global spaceship_group_2, spaceship_group_3, clock_timer, test
    for enemies in spaceship_group[:]:
        enemies.erase()
    for enemies in spaceship_group_2[:]:
        enemies.erase()
    for enemies in spaceship_group_3[:]:
        enemies.erase()
    spaceship_group = []
    spaceship_group_2 = []
    spaceship_group_3 = []
    for proj in proj_group[:]:
        proj.erase()
    proj_group = []
    proj_spaceship_group = []

    clock_timer = 0

    test = 0
    velocity = 1
    value_max_proj = default_value_max_proj


def game_info():
    spaceship = len(spaceship_group) + len(spaceship_group_2) + len(spaceship_group_3)
    info_game = "Niveau : {} || Temps de Jeux = {} min {} sec || Score = {} || Velocity = {} || Max Projectil = {} || Projectil Actuel = {} || Vaisseau ennemies = {} ".format(
        game,
        (temps_de_jeux // 60),
        (temps_de_jeux % 60),
        score,
        velocity,
        value_max_proj,
        len(proj_group),
        spaceship,
    )
    move((Bottom_Value + 1), ((Right_Value - len(info_game)) // 2))
    uart.write(info_game)


def game_home():
    global game, temps_de_jeux, default_temps_de_jeux
    temps_de_jeux = default_temps_de_jeux
    clear_screen()
    borders()
    logo()

    # 120 caracteres par ligne

    text = """
________________________________________________________________________________________________________________________ 
|                                                                                                                      |
|                                          Bienvenue sur mon Space Invaders !                                          |
|                                      Créé par Dylan Orto élève à Ynov Bordeaux                                       |
|                 Vous retrouverez dans ce jeux, plusieurs niveaux dans lesquels la difficulté augmente                |
|                              Vous aurez une petite surprise dans le dernier niveau ;-)                               |
|                                                                                                                      |
|                     Lisez les règles du jeux avant de lancer le décompte pour lancer la partie !                     |
|             Pour lancer le décompte il vous suffit d'appuyer 1 seconde sur le boutton bleu de la carte !             |
|                                                                                                                      |
|             Le boutton noir de la carte vous sert seulement si vous voulez recommencer la parti à zéro !             |
|______________________________________________________________________________________________________________________|
|                                                                                                                      |
| Les règles du jeux sont les suivantes :                                                                              |
|                                                                                                                      |
| - Votre vaisseau peut se déplacer de la gauche vers la droite mais aussi d'avant en arrière !                        |
|   Bouger votre carte là où vous voulez amener votre vaiseau !                                                        |
|                                                                                                                      |
| - Votre vaisseau a un nombre limité de missiles tirés en simultané                                                   |
|   Il vous suffit d'appuyer sur le boutton bleu de la carte !                                                         |
|                                                                                                                      |
| - Toutes les 1 minutes :                                                                                             |
|                                                                                                                      |        
|       - Votre vitesse de déplacement augmentera pour augmenter la difficulté                                         |
|       - Votre nombre de missiles simultanés diminuera                                                                |
|       - Votre score obtenu par ennemies éliminés diminue de 100                                                      |
|         Les données sont écrites en bas !                                                                            |
|                                                                                                                      |
|           La vitesse de déplacement, le nombre de missiles simultané et le score obtenue par éliminations            |
|                          seront remits à leur valeur par défaut à chaque début de niveau                             |
|                                                                                                                      |
| - Attention ! Les vaisseaux ennemies ont la capacité de tirer des missiles                                           |
|   Quand le niveau augmente, les vaisseaux gagnent en capacité de déplacement et tirent plus souvent                  | 
|   Dans le niveau 4 tous les vaisseau doivent être touché 2 fois pour être mort                                       |
|   Le boss présent dans ce niveau, doit être touché 20 fois pour mourir !                                             |
|                                                                                                                      |
|                                                                                                                      |
|                                                Bonne chance a vous !!                                                |
|                                             Obtenez le meilleur Score !!                                             |
|                                                                                                                      |
|______________________________________________________________________________________________________________________|
"""

    tab_text = text.splitlines()
    largeur = len(tab_text[1])
    a = 0
    b = int((Right_Value - largeur) // 2)
    for i in tab_text:
        move((19 + a), b)
        uart.write(i)
        a += 1

    text_2 = """
    _____________________
    |                   |
    |  Votre vaisseau!  |
    |                   |
    |       |-0-|       |
    |                   |
    |   Vos missiles!   |
    |                   |
    |         @         |
    |___________________|
    """

    tab_text_2 = text_2.splitlines()
    largeur_2 = len(tab_text_2[1])
    a = 0
    b = int((((Right_Value - largeur) // 2) - largeur_2)//2)
    mid = (Bottom_Value // 2) - 6
    for i in tab_text_2:
        move((mid + a), b)
        uart.write(i)
        a += 1

    text_3 = r"""
_____________________
|                   |
| Vaisseau Ennemie! |
|                   |
|    ||---V---||    |
|                   |
| Missiles Ennemie! |
|                   |
|         #         |
|___________________|
    """

    tab_text_3 = text_3.splitlines()
    largeur_3 = len(tab_text_3[1])
    a = 0
    b = int((((Right_Value // 2) + (largeur // 2)) + (largeur_3 // 2))+1)
    mid = (Bottom_Value // 2) - 7
    for i in tab_text_3:
        move((mid + a), b)
        uart.write(i)
        a += 1

    while True:
        game_info()
        if push_button.value() == 1:
            move(17, 60)
            uart.write("Le jeux se lance dans : ")
            for i in range(10, -1, -1):
                value_compteur = "{} | ".format(i)
                uart.write(value_compteur)
                delay(1000)
            game = "Level 1"
            break


def victory():
    global game
    clear_screen()
    game_reset()
    game_info()
    borders()
    logo()
    logo_victory()

    text = """
________________________________________________________________________________________________________________________ 
|                                                                                                                      |
|                                                                                                                      |
|                                            Bravo vous avez fini le jeux !                                            |
|                                                                                                                      |
|                                                                                                                      |
|                                           Votre Score final est de : {}                                              |
|                               Votre temps total pour finir est de : {} min et {} sec                                 |
|                                                                                                                      |
|                                                                                                                      |
|                            Vous pouvez relancer une partie en repartant au menu principal                            |
|             Pour lancez le décompte il vous suffit d'appuyer 1 seconde sur le boutton bleu de la carte !             |
|                                                                                                                      |
|                                                                                                                      |
|______________________________________________________________________________________________________________________|
""".format(score, (temps_de_jeux // 60), (temps_de_jeux % 60))

    tab_text = text.splitlines()
    largeur = len(tab_text[1])
    a = 0
    b = int((Right_Value - largeur) // 2)
    for i in tab_text:
        move((24 + a), b)
        uart.write(i)
        a += 1

    while True:
        if push_button.value() == 1:
            move(18, 60)
            uart.write("Retours au menu principale dans : ")
            for i in range(10, -1, -1):
                value_compteur = "{} | ".format(i)
                uart.write(value_compteur)
                delay(1000)
            game = "HOME"
            break


def game_over():
    global game
    clear_screen()
    game_reset()
    game_info()
    borders()
    logo()
    logo_game_over()
    text = """
________________________________________________________________________________________________________________________ 
|                                                                                                                      |
|                                                                                                                      |
|                                          Vous êtes mort ! Essayez encore !!                                          |
|                                                                                                                      |
|                                                                                                                      |
|                                           Votre Score final est de : {}                                           |
|                               Votre temps total pour finir est de : {} min et {} sec                                 |
|                                                                                                                      |
|                                                                                                                      |
|                            Vous pouvez relancer une partie en repartant au menu principal                            |
|             Pour lancez le décompte il vous suffit d'appuyer 1 seconde sur le boutton bleu de la carte !             |
|                                                                                                                      |
|                                                                                                                      |
|______________________________________________________________________________________________________________________|
""".format(score, (temps_de_jeux // 60), (temps_de_jeux % 60))

    tab_text = text.splitlines()
    largeur = len(tab_text[1])
    a = 0
    b = int((Right_Value - largeur) // 2)
    for i in tab_text:
        move((24 + a), b)
        uart.write(i)
        a += 1

    while True:
        if push_button.value() == 1:
            move(20, 60)
            uart.write("Retours au menu principale dans : ")
            for i in range(10, -1, -1):
                value_compteur = "{} | ".format(i)
                uart.write(value_compteur)
                delay(1000)
            game = "HOME"
            break


# definition des niveaux

def game_level_1():
    global game, temps_de_jeux, default_temps_de_jeux

    clear_screen()
    borders()
    game_reset()
    temps_de_jeux = default_temps_de_jeux

    for y in range(8):
        for x in range(2):
            spaceship_group.append(Spaceship(x=5 + x * 6, y=33 + 19 * y, skin=skin_enemis, health=1))

    while True:

        for enemies in spaceship_group[:]:
            enemies.write_skin()

        game_info()

        x_accel = read_acceleration(value_addr_X)
        y_accel = read_acceleration(value_addr_Y)

        if r.etat == 1:
            game_reset()
            game = "Game OVER"
            break

        if push_button.value() == 1 and len(proj_group) < value_max_proj:
            new_proj()

        for projectil in proj_group:
            projectil.move()

        for proj_spaceship in proj_spaceship_group:
            proj_spaceship.move()

        if len(spaceship_group) > 0:
            if (clock_timer % 20) == 0:
                choice(spaceship_group).shoot()

        elif len(spaceship_group) == 0:
            game_reset()
            game = "Level 2"
            break

        if x_accel < balanced_x:
            r.move_fordward()

        elif x_accel > balanced_x:
            r.move_backward()

        elif x_accel == balanced_x:
            led_4.on()
            led_3.on()
            delay(100)
            led_4.off()
            led_3.off()

        if y_accel < balanced_y:
            r.move_left()

        elif y_accel > balanced_y:
            r.move_right()

        elif y_accel == balanced_y:
            led_2.on()
            led_1.on()
            delay(100)
            led_2.off()
            led_1.off()


def game_level_2():
    global game

    game_reset()
    clear_screen()
    borders()

    for y in range(8):
        for x in range(2):
            spaceship_group.append(Spaceship(x=5 + x * 6, y=33 + 19 * y, skin=skin_enemis, health=1))
    for y in range(9):
        for x in range(2):
            spaceship_group.append(Spaceship(x=8 + x * 6, y=24 + 19 * y, skin=skin_enemis, health=1))

    for enemies in spaceship_group[:]:
        enemies.write_skin()

    while True:
        game_info()

        x_accel = read_acceleration(value_addr_X)
        y_accel = read_acceleration(value_addr_Y)

        if r.etat == 1:
            game_reset()
            game = "Game OVER"
            break

        if push_button.value() == 1 and len(proj_group) < value_max_proj:
            new_proj()

        for projectil in proj_group:
            projectil.move()

        for proj_spaceship in proj_spaceship_group:
            proj_spaceship.move()

        if len(spaceship_group) > 0:
            if (clock_timer % 10) != 0:
                if (clock_timer % 10) < 5:
                    for enemies in spaceship_group:
                        enemies.move_left()
                elif (clock_timer % 10) > 5:
                    for enemies in spaceship_group:
                        enemies.move_right()

            elif (clock_timer % 10) == 0 or (clock_timer % 15) == 0:
                choice(spaceship_group).shoot()

        elif len(spaceship_group) == 0:
            game_reset()
            game = "Level 3"
            break

        if x_accel < balanced_x:
            r.move_fordward()

        elif x_accel > balanced_x:
            r.move_backward()

        elif x_accel == balanced_x:
            led_4.on()
            led_3.on()
            delay(100)
            led_4.off()
            led_3.off()

        if y_accel < balanced_y:
            r.move_left()

        elif y_accel > balanced_y:
            r.move_right()

        elif y_accel == balanced_y:
            led_2.on()
            led_1.on()
            delay(100)
            led_2.off()
            led_1.off()


def game_level_3():
    global game

    game_reset()
    clear_screen()
    borders()

    for y in range(8):
        for x in range(4):
            spaceship_group.append(Spaceship(x=5 + x * 6, y=33 + 19 * y, skin=skin_enemis, health=1))
    for y in range(9):
        for x in range(3):
            spaceship_group.append(Spaceship(x=8 + x * 6, y=24 + 19 * y, skin=skin_enemis, health=1))

    for enemies in spaceship_group[:]:
        enemies.write_skin()

    while True:
        game_info()

        x_accel = read_acceleration(value_addr_X)
        y_accel = read_acceleration(value_addr_Y)

        if r.etat == 1:
            game_reset()
            game = "Game OVER"
            break

        if push_button.value() == 1 and len(proj_group) < value_max_proj:
            new_proj()

        for projectil in proj_group:
            projectil.move()

        for proj_spaceship in proj_spaceship_group:
            proj_spaceship.move()

        if len(spaceship_group) > 0:
            if (clock_timer % 10) != 0:
                if (clock_timer % 10) < 5:
                    for enemies in spaceship_group:
                        enemies.move_left()
                elif (clock_timer % 10) > 5:
                    for enemies in spaceship_group:
                        enemies.move_right()

            elif (clock_timer % 10) == 0 or (clock_timer % 15) == 0 or (clock_timer % 20) == 0:
                choice(spaceship_group).shoot()

            elif (clock_timer % 20) == 0:
                for enemies in spaceship_group[:]:
                    enemies.move_forward()

        elif len(spaceship_group) == 0:
            game_reset()
            game = "Level 4"
            break

        if x_accel < balanced_x:
            r.move_fordward()

        elif x_accel > balanced_x:
            r.move_backward()

        elif x_accel == balanced_x:
            led_4.on()
            led_3.on()
            delay(100)
            led_4.off()
            led_3.off()

        if y_accel < balanced_y:
            r.move_left()

        elif y_accel > balanced_y:
            r.move_right()

        elif y_accel == balanced_y:
            led_2.on()
            led_1.on()
            delay(100)
            led_2.off()
            led_1.off()


def game_level_4():
    global game

    game_reset()
    clear_screen()
    borders()

    for y in range(3):
        for x in range(3):
            spaceship_group.append(Spaceship(x=5 + x * 9, y=24 + 19 * y, skin=skin_enemis, health=2))
    for y in range(2):
        for x in range(2):
            spaceship_group.append(Spaceship(x=10 + x * 9, y=33 + 19 * y, skin=skin_enemis, health=2))

    for y in range(3):
        for x in range(3):
            spaceship_group_2.append(Spaceship(x=23 + x * 9, y=81 + 19 * y, skin=skin_enemis, health=2))
    for y in range(2):
        for x in range(2):
            spaceship_group_2.append(Spaceship(x=28 + x * 9, y=90 + 19 * y, skin=skin_enemis, health=2))

    for y in range(3):
        for x in range(3):
            spaceship_group_3.append(Spaceship(x=5 + x * 9, y=138 + 19 * y, skin=skin_enemis, health=2))
    for y in range(2):
        for x in range(2):
            spaceship_group_3.append(Spaceship(x=10 + x * 9, y=147 + 19 * y, skin=skin_enemis, health=2))

    spaceship_group_2.append(Spaceship(x=5, y=95, skin=skin_boss, health=20))

    for enemies in (spaceship_group + spaceship_group_2 + spaceship_group_3):
        enemies.write_skin()

    while True:
        game_info()

        x_accel = read_acceleration(value_addr_X)
        y_accel = read_acceleration(value_addr_Y)

        if r.etat == 1:
            game_reset()
            game = "Game OVER"
            break

        if push_button.value() == 1 and len(proj_group) < value_max_proj:
            new_proj()

        for projectil in proj_group:
            projectil.move()

        for proj_spaceship in proj_spaceship_group:
            proj_spaceship.move()

        if len(spaceship_group) > 0 or len(spaceship_group_2) > 0 or len(spaceship_group_3) > 0:
            if (clock_timer % 10) != 0:
                if (clock_timer % 10) < 5:
                    for enemies in (spaceship_group + spaceship_group_2 + spaceship_group_3):
                        enemies.move_left()
                elif (clock_timer % 10) > 5:
                    for enemies in (spaceship_group + spaceship_group_2 + spaceship_group_3):
                        enemies.move_right()

            elif (clock_timer % 3) == 0 or (clock_timer % 5) == 0:
                if len(spaceship_group) > 0:
                    choice(spaceship_group).shoot()
                if len(spaceship_group_2) > 0:
                    choice(spaceship_group_2).shoot()
                if len(spaceship_group_3) > 0:
                    choice(spaceship_group_3).shoot()

            if (clock_timer % 15) == 0:
                a = randint(0, 5)

                if a == 1:
                    for enemies in spaceship_group[:]:
                        enemies.move_forward()
                if a == 2:
                    for enemies in spaceship_group_2[:]:
                        enemies.move_forward()
                if a == 3:
                    for enemies in spaceship_group_3[:]:
                        enemies.move_forward()
                if a == 4:
                    for enemies in (spaceship_group + spaceship_group_2 + spaceship_group_3):
                        enemies.move_backward()

        elif len(spaceship_group) == 0 and len(spaceship_group_2) == 0 and len(spaceship_group_3) == 0:
            game_reset()
            game = "Victory"
            break

        if x_accel < balanced_x:
            r.move_fordward()

        elif x_accel > balanced_x:
            r.move_backward()

        elif x_accel == balanced_x:
            led_4.on()
            led_3.on()
            delay(100)
            led_4.off()
            led_3.off()

        if y_accel < balanced_y:
            r.move_left()

        elif y_accel > balanced_y:
            r.move_right()

        elif y_accel == balanced_y:
            led_2.on()
            led_1.on()
            delay(100)
            led_2.off()
            led_1.off()


# creation de notre vaisseau
r = Racket(x=value_spawn_x, y=value_spawn_y, skin="|-0-|")

addr_ctrl_reg1 = 0x20
write_reg(addr_ctrl_reg1, 0x77)

# boucle infinie pour les differents stades du jeux

game = "HOME"

while True:

    t = Timer(4, freq=0.2/6)
    t.callback(velocity_up)

    t = Timer(5, freq=1)
    t.callback(clock)

    t = Timer(6, freq=1)
    t.callback(temps_de_jeux_up)

    if game == "HOME":
        game_home()

    elif game == "Level 1":
        game_level_1()

    elif game == "Level 2":
        game_level_2()

    elif game == "Level 3":
        game_level_3()

    elif game == "Level 4":
        game_level_4()

    elif game == "Victory":
        victory()

    elif game == "Game OVER":
        game_over()
