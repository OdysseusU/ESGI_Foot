#(c) 2021 Christophe Gueneau
#Pour robot MaqueenPlus

from microbit import *
from time import sleep_ms
from machine import time_pulse_us

import math

class LED:
    OFF = 0x00
    RED = 0x01
    GREEN = 0x02
    YELLOW = 0x03
    BLUE = 0x04
    PURPLE = 0x05
    CYAN = 0x06
    WHITE = 0x07

class INFRARED:
    L3 = 0
    L2 = 1
    L1 = 2
    R1 = 3
    R2 = 4
    R3 = 5

class DIR:
    OFF = 0
    FORWARD = 1
    BACKWARD = 2

class Robot:
    def __init__(self):
        self.moteur(0, 0, 0, 0)

        # self.x,self.y,self.t,self.v = 0,0,0,0
        # self.cGI,self.cDI = self.codeursInit()
        # self.pcGI,self.pcDI = self.cGI,self.cDI
        # self.cG,self.cD = 0,0
        # self.pcG,self.pcD = 0,0

        self.R = 0.0215
        self.L = 0.1
        self.rpm = 133
        self.motor_reduction = 1/150
        self.radps = self.rpm*2*math.pi/60 #13.92 rad/s - Wheel angular velocity
        #self.degps = self.rpm*360/60 #798 deg/s - Wheel angular velocity
        self.v_max = self.radps*self.R #0.3 m/s - Max linear velocity
        self.w_max = self.R*2/self.L #0.43 rad/s - Max robot angular velocity
        self.w_deg_max = self.w_max*180/math.pi #24.7 deg/s - Max robot angular velocity

        self.prevE,self.iE = 0,0

    def moteur(self, dirG:DIR, vitG, dirD:DIR, vitD):
        """ Direction (0 = Brake, 1 = Forward, 2 = Backward) and Velocity (0-1) to both motors """
        i2c.write(0x10, bytearray([0x00, dirG, int(vitG*128), dirD, int(vitD*128)]))

    # def moteurG(self, dir:DIR, vit):
    #     """ Direction (0 = Brake, 1 = Forward, 2 = Backward) and Velocity (0-1) to motor Left """
    #     i2c.write(0x10, bytearray([0x00, dir, int(vit*128)]))

    # def moteurD(self, dir:DIR, vit):
    #     """ Direction (0 = Brake, 1 = Forward, 2 = Backward) and Velocity (0-1) to motor Right """
    #     i2c.write(0x10, bytearray([0x02, dir, int(vit*128)]))

    def moteurStop(self):
        """ Stops both motors by setting 0 to direction """
        i2c.write(0x10, bytearray([0x00, 0, 0, 0, 0]))

    def activatePID(self, t_o_f):
        """ Activate PID """
        i2c.write(0x10, bytearray([0x0A, int(t_o_f)]))

    def line(self) -> list:
        """ Get whether the Line sensor sees a black line """
        buf = bytearray(1)
        buf[0] = 0x1D
        i2c.write(0x10, [0x1D])
        etatByte = (i2c.read(0x10, 1)[0])
        return [bool(etatByte & 2**i) for i in range(6)]

    # def line_index(self, indexCapteur:INFRARED) -> bool:
    #     """ Get whether one of the Line sensor sees a black line """
    #     i2c.write(0x10, bytearray([0x1D]))
    #     etatByte = (i2c.read(0x10, 1)[0])
    #     etatCapteur = bool(etatByte & 2**indexCapteur)
    #     if etatCapteur != 0:
    #         return True
    #     return False
    
    def line_grey(self):
        """ Get Grayscale value from infrared sensor """
        i2c.write(0x10, bytearray([0x1E]))
        buf = i2c.read(0x10, 1)
        i2c.write(0x10, bytearray([0x20]))
        buf = buf + i2c.read(0x10, 1)
        
        i2c.write(0x10, bytearray([0x21]))
        buf = buf + i2c.read(0x10, 5*2)

        return [int.from_bytes(buf[(i*2):(i*2+1)],'big') for i in range(len(buf)//2)]

    # def servo(self, index, angle):
    #     i2c.write(0x10, bytearray([0x14+index, angle]))

    def ledRgb(self, couleurG:LED, couleurD:LED):
        """ Set color to the front LEDS """
        i2c.write(0x10, bytearray([0x0b, couleurG, couleurD]))

    def distance(self, pinTrig, pinEcho):
        """ Calcul de distance avec ultrason """
        pinTrig.write_digital(1)
        sleep_ms(10)
        pinTrig.write_digital(0)
        t = time_pulse_us(pinEcho, 1)
        d = 340 * t // 20000
        return d

    # def codeursInit(self):
    #     """
    #     Initialisation des codeurs
    #     """
    #     try:
    #         i2c.write(0x10, bytearray([0x04]))
    #         buf = i2c.read(0x10, 4)
            
    #         a=int.from_bytes(buf[:2],'big')
    #         b=int.from_bytes(buf[2:],'big')
    #         return (a,b)
    #     except Exception as e:
    #         print(e)
    #     return (0,0)

    # def codeurs(self):
    #     """
    #     Lecture des codeurs
    #     """
    #     try:
    #         i2c.write(0x10, bytearray([0x00]))
    #         buf = i2c.read(0x10, 3)
            
    #         asign = buf[0]
    #         if asign == 2:
    #             asign = -1
                
    #         bsign = buf[2]
    #         if bsign == 2:
    #             bsign = -1
            
    #         i2c.write(0x10, bytearray([0x04]))
    #         buf = i2c.read(0x10, 4)
            
    #         self.cGI=int.from_bytes(buf[:2],'big')
    #         a = asign*(self.cGI-self.pcGI)
    #         self.cG += a
    #         self.pcGI = self.cGI

    #         self.cDI=int.from_bytes(buf[2:],'big')
    #         b = bsign*(self.cDI-self.pcDI)
    #         self.cD += b
    #         self.pcDI = self.cDI

    #         return a,b
            
    #     except Exception as e:
    #         print(e)
    #     return 0,0

    # def update(self,dt):
    #     """
    #     Mise à jour du codeur et de la position
    #     dt: temps en s
    #     """
    #     G,D = self.codeurs()
    #     dG = G/80*math.pi
    #     dD = D/80*math.pi
    #     self.t += self.R/self.L*(dD-dG)
    #     self.v = self.R/2*(dD+dG)/dt
    #     self.x = self.x + math.cos(self.t)*dt
    #     self.y = self.y + math.sin(self.t)*dt

    def move(self,v,w):
        """
        Permet de transformer un vecteur vitesse en commande moteur
        v: vitesse en m/s
        w: vitesse angulaire en deg/s
        """
        stop_limit = 0

        G = v/self.R - self.L/2*w/180*math.pi/self.R
        D = v/self.R + self.L/2*w/180*math.pi/self.R
        
        #Directions
        dirG = int(DIR.FORWARD) if G > stop_limit else (int(DIR.BACKWARD) if G < -stop_limit else int(DIR.OFF))
        dirD = int(DIR.FORWARD) if D > stop_limit else (int(DIR.BACKWARD) if D < -stop_limit else int(DIR.OFF))

        #Vitesses en pourcentage et limitées à 100%
        g = abs(G)/self.radps
        G = g if g < 1 else 1
        d = abs(D)/self.radps
        D = d if d < 1 else 1
            
        self.moteur(dirG,G,dirD,D)
        return (dirG+dirD)>0

    # def control(self,v,t,dt):
    #     """
    #     Permet de controler la vitesse avec un PID
    #     v: vitesse en m/s
    #     t: angle en rad
    #     dt: temps en s
    #     """
    #     et = t - self.t
    #     self.iE += et*dt

    #     P=10
    #     D=1
    #     I=0.01
    #     pid = P*et + D*(et-self.prevE)/dt#+I*self.iE

    #     return self.move(v,pid)

    