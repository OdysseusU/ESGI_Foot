
from microbit import *
from microbit_class import radio_transmitter

r = radio_transmitter()

while True:
    sleep(10)
    r.update()