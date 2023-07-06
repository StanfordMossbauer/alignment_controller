from MDT693B import MDT693B
import numpy as np


class AbsorberAttractorAssembly:
    def __init__(self, controller_port, **kwargs):
        self.piezo_controller = MDT693B(controller_port)
        self.volts_per_micron = kwargs.get('volts_per_micron', 150.0/1150)  # using available stroke of piezo
        self.two_piezo_distance_cm = kwargs.get('two_piezo_distance_cm', 9.128)  # from SW model
        self.matrices = dict(
            theta=-1 * np.sqrt(3)/4 * self.two_piezo_distance_cm * 1e4 * np.array([1.0, -0.5, -0.5]),
            phi=self.two_piezo_distance_cm * 1e4 * np.array([0., -0.5, 0.5])
        )
        return

    def set_voltages(self, voltage):
        if not hasattr(voltage, '__len__'):
            voltage = np.array([voltage]*3)
        _ = self.piezo_controller.set_voltages(voltage)
        assert (_==[1,1,1]),"voltage setting failed"
        return

    def get_voltages(self):
        return self.piezo_controller.get_voltages()

    def rotate(self, angle, axis, start_voltage=None):
        if start_voltage is None:
            start_voltage = self.get_voltages()
        matrix = self.matrices[axis]
        distance_adjustment = matrix * np.sin(angle)
        voltage_adjustments = -1 * matrix * np.sin(angle) * self.volts_per_micron
        voltages = start_voltages + voltage_adjustments
        self.set_voltages(voltages)
        return
