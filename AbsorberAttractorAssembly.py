from MDT693B import MDT693B
import numpy as np

volts_per_micron = 150.0/1150  # using available stroke of piezo
two_piezo_distance_cm = 9.128  # from SW model

class AbsorberAttractorAssembly:
    def __init__(self, controller_port):
        self.piezo_controller = MDT693B(controller_port)
        self.matrices = dict(
            theta=-1 * np.sqrt(3)/4 * two_piezo_distance_cm * 1e4 * np.array([1.0, -0.5, -0.5]),
            phi=two_piezo_distance_cm * 1e4 * np.array([0., -0.5, 0.5])
        )
        return

    def set_voltages(self, voltages):
        _ = self.piezo_controller.set_voltages(voltages)
        assert (_==[1,1,1]),"voltage setting failed"
        return

    def get_voltages(self):
        return self.piezo_controller.get_voltages()

    def rotate(self, angle, axis, start_voltage=None):
        if start_voltage is None:
            start_voltage = self.get_voltages()
        matrix = self.matrices[axis]
        distance_adjustment = matrix * np.sin(angle)
        voltage_adjustments = -1 * matrix * np.sin(angle) * volts_per_micron
        voltages = start_voltages + voltage_adjustments
        piezo_controller.set_voltages(voltages)
        return
