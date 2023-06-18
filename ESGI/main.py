# Imports go at the top
from microbit import *
from robot_class import *
# from microbit_class import radio_receiver
import math

r = Robot()
# receiver = radio_receiver()
id_robot = 5

# def strategy(posx,posy,theta):
#     v = min(math.sqrt(posx*posx+posy*posy),100)

#     a = (math.atan2(posy,posx) - theta)*180/math.pi
#     a = (a + 180) % 360 - 180

#     r.move(0,a*math.pi/180)

r.activatePID(1)
sleep(1000)
def loop():
    g = r.line()
    l = 0
    #if len(g) == 6:
        #l=g[0]*r.w_deg_max*2+g[1]*r.w_deg_max+g[2]*r.w_deg_max-g[3]*r.w_deg_max-g[4]*r.w_deg_max-g[5]*r.w_deg_max*2
    r.move(0.2, l)
    # receiver.update()
    # if bool(receiver.positions) & (id_robot in receiver.positions.keys()):
    #     strategy(receiver.positions[id_robot][0],receiver.positions[id_robot][1],receiver.positions[id_robot][2])
    # else:
    #     r.moteurStop()

while True:
    loop()
    sleep(100)

    