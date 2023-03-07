# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 17:29:15 2023

@author: Albert
"""
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from AH2550A_driver import AH2550A
from MDT693B_driver import MDT693B
import time

class ALIGNMENT_ALGORITHM:
    def __init__(self, CB, PVC):
        self._CB = CB
        self._PVC = PVC
        self.state_data_log = np.empty((0,6), float)
        self.DIAMETER_DISKS = 1.250 # inches
        self.permittivity = 8.854E-12 # F/m
        self.normal_orientation_voltage_state = [80.0, 48.0, 80.0]
        
    def minimum_capacitance_to_distance(self, capacitance_pf):
        """
        Input: Capacitance in pF
        Output: Distance in microns
        """
        capacitance = 1E-12*capacitance_pf
        disk_area = np.pi*(self.DIAMETER_DISKS*0.0254*0.5)**2 # Area in m^2
        distance_micron = 1E6*self.permittivity*disk_area/capacitance
        return distance_micron
        
    def sweep_a_axis(self, voltage_sweep_limit, sweep_number):
        sweep=np.linspace(-voltage_sweep_limit, voltage_sweep_limit, sweep_number)
        for j in range(sweep_number):
            x_voltage_command = self.normal_orientation_voltage_state[0] + sweep[j]
            y_voltage_command = self.normal_orientation_voltage_state[1] - 0.5*sweep[j]
            z_voltage_command = self.normal_orientation_voltage_state[2] - 0.5*sweep[j]
            self.state_change([x_voltage_command, y_voltage_command, z_voltage_command])
            _current_state = self.state_measurement()
            self.log_data(_current_state)    
        return sweep
    
    def sweep_b_axis(self, voltage_sweep_limit, sweep_number):
        sweep=np.linspace(-voltage_sweep_limit, voltage_sweep_limit, sweep_number)
        for j in range(sweep_number):
            x_voltage_command = self.normal_orientation_voltage_state[0] - 0.5*sweep[j]
            y_voltage_command = self.normal_orientation_voltage_state[1] + sweep[j]
            z_voltage_command = self.normal_orientation_voltage_state[2] - 0.5*sweep[j]
            self.state_change([x_voltage_command, y_voltage_command, z_voltage_command])
            _current_state = self.state_measurement()
            self.log_data(_current_state)    
        return sweep
    
    def sweep_c_axis(self, voltage_sweep_limit, sweep_number):
        sweep=np.linspace(-voltage_sweep_limit, voltage_sweep_limit, sweep_number)
        for j in range(sweep_number):
            x_voltage_command = self.normal_orientation_voltage_state[0] - 0.5*sweep[j]
            y_voltage_command = self.normal_orientation_voltage_state[1] - 0.5*sweep[j]
            z_voltage_command = self.normal_orientation_voltage_state[2] + sweep[j]
            self.state_change([x_voltage_command, y_voltage_command, z_voltage_command])
            _current_state = self.state_measurement()
            self.log_data(_current_state)    
        return sweep

    def state_measurement(self):
        state_data = []
        voltage_measurement = self._PVC.read_xyz_voltage()
        capacitive_measurement = self._CB.single_measurement()
        state_data = np.append(capacitive_measurement, voltage_measurement)
        return state_data
    
    def state_change(self, voltage_command):
        """
        Inputs: 1x3 numpy array of voltages. Voltages refer to the x, y, and z outputs of the piezo controller respectively
        """
        self._PVC.write_xyz_voltage(voltage_command)
        time.sleep(0.1)
        return
    
    def data_log_header(self):
        header = "Capacitance (pF), Loss (nS), Measurement Voltage (V), X Voltage (V), Y Voltage (V), Z Voltage (V)"
        return header
    
    def log_data(self, data_to_log):
        """
        Inputs: current data state
        """
        self.state_data_log = np.vstack((self.state_data_log, data_to_log))
        return self.state_data_log
    
    def print_data_log(self):
        return self.state_data_log
    
        
if __name__ == "__main__":
    i = 0
    # Resource names
    capacitance_bridge_resource = "GPIB0::28::INSTR"
    piezo_voltage_controller_resource = "COM3"

    # initializing capacitance bridge
    CB = AH2550A(capacitance_bridge_resource) # CB is Capacitance Bridge
    print(CB.read_identity())
    
    # initializing piezo voltage controller
    PVC = MDT693B("COM3") # PVC is Piezo Voltage Controller
    print(PVC.read_identity())
    
    ALIGN = ALIGNMENT_ALGORITHM(CB, PVC)
    
    voltage_sweep_limit = 5
    voltage_sweep_number = 6
    ALIGN.sweep_a_axis(voltage_sweep_limit, voltage_sweep_number)
    experiment_data = ALIGN.print_data_log()
    
    plt.plot(np.linspace(-voltage_sweep_limit, voltage_sweep_limit, voltage_sweep_number),experiment_data[:,0], label = "a-axis")
    
    ALIGN.state_data_log = np.empty((0,6), float)
    
    ALIGN.sweep_b_axis(voltage_sweep_limit, voltage_sweep_number)
    experiment_data = ALIGN.print_data_log()
    
    plt.plot(np.linspace(-voltage_sweep_limit, voltage_sweep_limit, voltage_sweep_number),experiment_data[:,0], label = "b-axis")
    
    ALIGN.state_data_log = np.empty((0,6), float)
    
    ALIGN.sweep_c_axis(voltage_sweep_limit, voltage_sweep_number)
    experiment_data = ALIGN.print_data_log()
    
    plt.plot(np.linspace(-voltage_sweep_limit, voltage_sweep_limit, voltage_sweep_number),experiment_data[:,0], label = "c-axis")
    plt.legend(loc = "upper right")
    plt.show()
    print(ALIGN.minimum_capacitance_to_distance(450))
    CB.__del__()
    PVC.__del__()
    
