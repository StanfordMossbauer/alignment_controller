# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 10:16:25 2023

@author: Albert
"""

import serial
import numpy as np

class MDT693B:
    def __init__(self, resource):
        self.piezo_serial = serial.Serial(port=resource, 
                                          baudrate = 115200,
                                          bytesize = serial.EIGHTBITS,
                                          parity = serial.PARITY_NONE,
                                          stopbits = serial.STOPBITS_ONE,
                                          timeout = 0.1)

    def undo_thorlabs_format(self, msg):
        msg = msg.replace(">","")
        msg = msg.replace("[","")
        msg = msg.replace("]","")
        msg = msg.replace(" ","")
        msg = float(msg)
        return msg

    def read_identity(self):
        self.piezo_serial.write("id? \r")
        identity = self.piezo_serial.read(200)
        identity = identity.replace("\r", "\n")
        return(identity)

    def read_x_voltage(self):
        self.piezo_serial.write("xvoltage? \r")
        x_voltage_datum = self.piezo_serial.readline()
        x_voltage_datum = self.undo_thorlabs_format(x_voltage_datum)
        return x_voltage_datum

    def read_y_voltage(self):
        self.piezo_serial.write("yvoltage? \r")
        y_voltage_datum = self.piezo_serial.readline()
        y_voltage_datum = self.undo_thorlabs_format(y_voltage_datum)
        return y_voltage_datum
    
    def read_z_voltage(self):
        self.piezo_serial.write("zvoltage? \r")
        z_voltage_datum = self.piezo_serial.readline()
        z_voltage_datum = self.undo_thorlabs_format(z_voltage_datum)
        return z_voltage_datum
    
    def read_xyz_voltage(self):
        xyz_voltage_data = np.zeros(0)
        xyz_voltage_data = np.append(xyz_voltage_data, self.read_x_voltage())
        xyz_voltage_data = np.append(xyz_voltage_data, self.read_y_voltage())
        xyz_voltage_data = np.append(xyz_voltage_data, self.read_z_voltage())
        return xyz_voltage_data.T
    
    def write_x_voltage(self, value):
        self.piezo_serial.write("xvoltage=")
        self.piezo_serial.write(bytes(value))
        self.piezo_serial.write("\r")
        return

    def write_y_voltage(self, value):
        self.piezo_serial.write("yvoltage=")
        self.piezo_serial.write(bytes(value))
        self.piezo_serial.write("\r")
        return

    def write_z_voltage(self, value):
        self.piezo_serial.write("zvoltage=")
        self.piezo_serial.write(bytes(value))
        self.piezo_serial.write("\r")
        return
    
    def write_xyz_voltage(self, values):
        """
        Inputs: takes a 1x3 numpy array of voltage floats
        """
        self.write_x_voltage(values[0])
        self.write_y_voltage(values[1])
        self.write_z_voltage(values[2])
        return
    
    def __del__(self):
        self.piezo_serial.close()

if __name__ == "__main__":
    PVC = MDT693B("COM3") # PVC is Piezo Voltage Controller
    print(PVC.read_identity())

    PVC.write_x_voltage(1.5)
    PVC.write_y_voltage(2)
    PVC.write_z_voltage(3)

    print(PVC.read_x_voltage())
    print(PVC.read_y_voltage())
    print(PVC.read_z_voltage())
    
    xyz_voltage_data = PVC.read_xyz_voltage()
    print(xyz_voltage_data)
    
    PVC.__del__()
