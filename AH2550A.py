# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 14:35:01 2023

@author: Albert
"""

import pyvisa
import numpy as np

class AH2550A:
    def __init__(self, resource):
        self.instrument = pyvisa.ResourceManager().open_resource(resource)

    def read_identity(self):
        identity = self.instrument.query("*IDN?")
        return(identity)
    
    def reset(self):
        self.instrument.query("*RST")
        return
        
    def single_measurement(self):
        """
        Output: 1x3 numpy array with column positions signifying capacitance [pF], loss [nS], and measurement voltage [V]
        """
        measurement = self.instrument.query('SINGLE')

        # making the string result into a numpy array
        measurement = measurement.replace("C= ", "")
        measurement = measurement.replace("   PF L=", ",")
        measurement = measurement.replace("   NS V= ", ",")
        measurement = measurement.replace("     V", "")
        measurement = measurement.replace(" OVEN", "") #occurs during warmup of AH2550A
        measurement = measurement.replace("\n", "")
        measurement_data = np.array(measurement.split(",")).T
        measurement_data = measurement_data.astype(float)
        
        return measurement_data
    
    def __del__(self):
        self.instrument.close()
        return

if __name__ == "__main__":

    capacitance_bridge_resource = 'GPIB0::28::INSTR'
    
    CB = AH2550A(capacitance_bridge_resource) # CB is Capacitance Bridge
    print(CB.read_identity())
    meas = CB.single_measurement()
    print(meas)
    
    