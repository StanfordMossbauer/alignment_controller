from BPC303 import BPC303
import numpy as np
import time

#volts_per_micron = 150.0/310  # 705 piezos
volts_per_micron = 150.0/1150  # 710 piezo
two_piezo_distance_cm = 9.128

class AbsorberAttractorAssembly:
    """Class to control the triangular absorber-attractor assembly

    TODO: calibration function, save to file
    TODO: ramp velocity

    The idea is anything that's geometrically specific to this assembly goes here (instead
    of in the underlying classes). This includes the matrix transformation between angles
    and piezo positions, and the physical meaning of the "microns" in the underlying BPC303
    class -- since this depends on the stroke of the piezo driven (and minus sign for
    whether it is amplified).
    """
    def __init__(self, controller_port, **kwargs):
        """Specifies information for the class and sets up the driver

        Two optional kwargs: 
        volts_per_micron: full Vin range of piezo stack / full stroke over that V range
        two_piezo_distance_cm: side length of the triangle formed by three piezo axes
        """
        self.controller = BPC303(controller_port)
        self.volts_per_micron = kwargs.get('volts_per_micron', volts_per_micron)  # using available stroke of piezo
        self.two_piezo_distance_cm = kwargs.get('two_piezo_distance_cm', two_piezo_distance_cm)  # from SW model
        # the matrices convert angles to vertical displacements
        # you still need a minus-sign if you want to convert to voltages on amplified piezos
        self.matrices = dict(
            theta = -1 * np.sqrt(3)/4 * np.array([1.0, -0.5, -0.5]),
            phi = np.array([0., -0.5, 0.5])
        )
        self.chs = range(1, 4)
        self.setup()
        return

    def setup(self):
        """Stuff we want to do whenever we initialize this assembly, but not necessarily
        whenever we use the BPC303 driver.
        """
        # HARDCODE WARNING
        # TODO: make voltage range, pi, etc all settings
        for ch in self.chs:
            self.controller.set_outputmaxvolts(150, ch)
            self.controller.set_pi(0, 1, ch)
        return

    def set_positions(self, position):
        """Sets positions of all three piezos

        position can be an array ([pos1, pos2, pos3]) or single value
        that gets applies to all three axes [pos, pos, pos]
        """
        if not hasattr(position, '__len__'):
            position = np.array([position]*3)
        for ch, pos in enumerate(position):
            self.controller.set_position(pos, ch+1)
        return

    def get_positions(self):
        """Get output positions on all three piezos

        Somehow if you do set-output-pos to some value, then get-output-pos, there's
        an offset. Get-output-pos is reading the actual strain gauge output, whereas
        "Set" is the PID algo's target value. I can't figure out if there's a way to
        read the target value instead. Otherwise we can accidentally drift if we set-
        read-set-read.
        """
        return np.array([self.controller.get_position(ch) for ch in self.chs])

    def rotate(self, angle, axis, start_position=None):
        # TODO angle definitions and documentation
        if start_position is None:
            start_position = self.get_positions()
        matrix = self.matrices[axis]
        print(angle)
        position_adjustments = -1 * matrix * np.sin(angle) * self.two_piezo_distance_cm * 1e4 * self.volts_per_micron
        print(position_adjustments)
        positions = start_position + (position_adjustments * (10/150))
        print(positions)
        self.set_positions(positions)
        return positions

    def translate(self, distance, start_position=None):
        """Note: for now we should supply a start position"""
        if start_position is None:
            start_position = self.get_positions()
        assert not hasattr(distance, '__len__'), 'send single value'
        positions = start_position + np.array([distance]*3)
        self.set_positions(positions)
        return positions

    def close_loops(self):
        for ch in self.chs:
            self.controller.set_mode('closed_loop', ch)
        return

    def open_loops(self):
        for ch in self.chs:
            self.controller.set_mode('open_loop', ch)
        return

    def _dance(self):
        """Makes the assembly do a hula dance just for fun

        Maximally separates the disks first, then sin-waves the full stroke
        with 2pi/3 phase shifts. Make sure no chance of disks hitting befor you
        do it. Made this a hidden function bc it's so stupid.
        """
        # make sure no chance of hitting!
        self.set_positions(0)
        time.sleep(10)
        A = 10  # amplitude "microns"
        wt = np.linspace(0, 10*np.pi, 500)
        a1s = wt
        a2s = wt - (2*np.pi/3)
        a3s = wt - (4*np.pi/3)
        a2s[a1s < 2*np.pi/3] = 0.0
        a3s[a1s < 4*np.pi/3] = 0.0
        for (a1, a2, a3) in zip(a1s, a2s, a3s):
            positions = A/2 + (A/2) * np.sin(np.array([a1, a2, a3]) - np.pi/2)
            self.set_positions(positions)
            time.sleep(0.01)
        print('switch')
        for (a1, a2, a3) in zip(a1s[::-1], a2s[::-1], a3s[::-1]):
            positions = A/2 + (A/2) * np.sin(np.array([a1, a2, a3]) - np.pi/2)
            self.set_positions(positions)
            time.sleep(0.01)
        self.set_positions(0)
        return

if __name__=='__main__':
    piezo_controller_port = 'COM5'

    if ('AAA' in locals()) or ('AAA' in globals()):
        AAA.piezo_controller.close()
    AAA = AbsorberAttractorAssembly(piezo_controller_port)

    for ch in range(1, 4):
        AAA.controller.set_mode('closed_loop', ch)
