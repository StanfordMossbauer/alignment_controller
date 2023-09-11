from BPC303 import BPC303
import numpy as np

#volts_per_micron = 150.0/310  # 705 piezos
volts_per_micron = 150.0/1150  # 710 piezo
two_piezo_distance_cm = 9.128

class AbsorberAttractorAssembly:
    def __init__(self, controller_port, **kwargs):
        self.piezo_controller = BPC303(controller_port)
        self.volts_per_micron = kwargs.get('volts_per_micron', volts_per_micron)  # using available stroke of piezo
        self.two_piezo_distance_cm = kwargs.get('two_piezo_distance_cm', two_piezo_distance_cm)  # from SW model
        self.matrices = dict(
            theta=-1 * np.sqrt(3)/4 * self.two_piezo_distance_cm * 1e4 * np.array([1.0, -0.5, -0.5]),
            phi=self.two_piezo_distance_cm * 1e4 * np.array([0., -0.5, 0.5])
        )
        return

    def set_positions(self, position):
        if not hasattr(position, '__len__'):
            position = np.array([position]*3)
        for ch, pos in enumerate(positions)
            self.piezo_controller.set_position(pos, ch+1)
        return

    def get_positions(self):
        return np.array([self.piezo_controller.get_position(ch) for ch in range(1, 4)])

    def rotate(self, angle, axis, start_position=None):
        if start_position is None:
            start_position = self.get_positions()
        matrix = self.matrices[axis]
        distance_adjustment = matrix * np.sin(angle)
        position_adjustments = -1 * matrix * np.sin(angle) * self.volts_per_micron
        positions = start_positions + position_adjustments
        self.set_positions(positions)
        return
