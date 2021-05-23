# main.py -- put your code here!
from pyb import SPI, Pin, LED, delay, UART


push_button = pyb.Pin("PA0", pyb.Pin.IN, pyb.Pin.PULL_DOWN)
uart = UART(2, 115200)
CS = Pin("PE3", Pin.OUT_PP)
SPI_1 = SPI(
    1,
    SPI.MASTER,
    baudrate=50000,
    polarity=0,
    phase=0,
)

CS.low()
SPI_1.send(0x0F | 0x80)
tab_values = SPI_1.recv(1)
CS.high()
value = tab_values[0]

while True:
    uart.write(value)


