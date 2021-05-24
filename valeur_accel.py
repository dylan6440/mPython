from pyb import SPI, Pin, UART, LED, delay, Timer

# entrez l'adresse de votre accélérométre

#LIS302DL

value_addr_X = 0x29
value_addr_Y = 0x2B


# Ne toucher pas ci-dessous
# |------------------------------------------------------------------------------------------------|
# |------------------------------------------------------------------------------------------------|
# |------------------------------------------------------------------------------------------------|

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

while True:
    clear_screen()
    move(1, 1)
    x_accel = read_acceleration(value_addr_X)
    y_accel = read_acceleration(value_addr_Y)

    value = str("Value X : {}, Value Y : {} \n".format(x_accel, y_accel))
    uart.write(value)
    delay(1000)

