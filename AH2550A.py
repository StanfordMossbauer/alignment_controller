# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 14:35:01 2023

@author: Albert

(Copied over by Joey and modified)
"""

import pyvisa
import numpy as np

class AH2550A:
    def __init__(self, resource='GPIB0::28::INSTR', timeout=1000):
        self.instrument = pyvisa.ResourceManager().open_resource(resource)
        self.instrument.timeout = timeout

    def read_identity(self):
        identity = self.instrument.query("*IDN?")
        return(identity)
    
    def reset(self):
        self.instrument.query("*RST")
        return

    def _get_single_measurement(self, verbose=False):
        measurement = self.instrument.query('SINGLE')

        # making the string result into a numpy array
        if verbose:
            print(measurement)
        measurement = measurement.replace("C= ", "")
        measurement = measurement.replace("   PF L=", ",")
        measurement = measurement.replace("   NS V= ", ",")
        measurement = measurement.replace("     V", "")
        measurement = measurement.replace("   V", "")
        measurement = measurement.replace("  V", "")
        measurement = measurement.replace(" OVEN", "") #occurs during warmup of AH2550A
        measurement = measurement.replace("\n", "")
        measurement_data = np.array(measurement.split(",")).T
        return measurement_data
        
    def single_measurement(self, max_attempts=1, verbose=False):
        """
        Output: 1x3 numpy array with column positions signifying capacitance [pF], loss [nS], and measurement voltage [V]
        """
        attempts = 0
        while attempts < max_attempts:
            data = self._get_single_measurement(verbose=verbose)
            try:
                data = data.astype(float)
                return data
            except:
                print(data)
                attempts += 1
        raise IndexError('Max attempts exceeded\n' + ''.join(data))
        return 

    def n_measurements(self, n, max_attempts=1, verbose=False):
        c = np.zeros(n)
        l = np.zeros(n)
        v = np.zeros(n)
        for j in range(n):
            c[j], l[j], v[j] = self.single_measurement(max_attempts=max_attempts, verbose=verbose) 
        return c, l, v
    
    def __del__(self):
        self.instrument.close()
        return

if __name__ == "__main__":

    capacitance_bridge_resource = 'GPIB0::28::INSTR'
    
    CB = AH2550A(capacitance_bridge_resource) # CB is Capacitance Bridge
    print(CB.read_identity())
    meas = CB.single_measurement()
    print(meas)
    
    
