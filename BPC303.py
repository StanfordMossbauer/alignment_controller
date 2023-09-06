import thorlabs_apt_protocol as apt
import serial


class BPC303:
    def __init__(self, serial_port):
        # copied from thorlabs_apt_device.enum
        endpoints = dict(
            HOST=0x01,
            RACK=0x11,
            BAY0=0x21,
            BAY1=0x22,
            BAY2=0x23,
            BAY3=0x24,
            BAY4=0x25,
            BAY5=0x26,
            BAY6=0x27,
            BAY7=0x28,
            BAY8=0x29,
            BAY9=0x2A,
            USB=0x50,
        )
        self.__dict__.update(endpoints)
        self.port = serial.Serial(serial_port, 115200, rtscts=True, timeout=0.1)
        self.unpacker = apt.unpacker.Unpacker(self.port)
        # not sure why/if needed
        self.port.rts = True
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()
        self.port.rts = False

        self.full_range = 1000 # um
        return

    def read(self):
        try:
            r = self.unpacker.__next__()
        except StopIteration:
            r = None
        return r

    def bayid(self, channel):
        """For some commands, we need to reference the 'bay' instead of the channel.
        This has to do with the architecture of the device -- there's a central motherboard that
        talks to three cards, each of which controls one channel.
        """
        return getattr(self, 'BAY%d' % (channel - 1))

    def get_position(self, channel):
        cmd = apt.pz_req_outputpos(dest=self.bayid(channel), source=self.HOST, chan_ident=1)
        self.port.write(cmd)
        return self.read().position

