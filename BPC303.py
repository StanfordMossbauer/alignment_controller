import thorlabs_apt_protocol as apt
import serial
import atexit
import time


class BPC303:
    def __init__(self, serial_port):
        """Wrapper class for BPC303 3-axis piezo controller

        Annoyingly, this model uses the "APT" protocol (Thorlabs proprietary),
        so unlike its open-loop counterpart, you can't just send simple serial commands.
        Fortunately there's a pip-installable library to construct the required hex 
        commands.
        See https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf

        This just interfaces that with the device, so you can make any command byte-string 
        with apt.whatever() and do bpc.write(str), then bpc.read() to get an object out 
        that contains your info.

        There's also a package called thorlabs_apt_device that does a very similar thing,
        but it required enough modification that I figured simpler to make a new class.

        NOTE: you have to enable virtual com port for the device to have it show up on a
              COM port so you can use it. Device manager -> right-click the device -> 
              Properties -> Advanced -> enable virtual com, then unplug/replug the USB

        NOTE: There is some way to continuously stream all the positions (see
              MGMSG_HW_START_UPDATEMSGS in manual) but I couldn't figure it out.

        TODO: set SLEW RATE to fix voltage changes
        """
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
        self.unpacker = apt.unpacker.Unpacker(self.port)  # for reading the output
        # not sure why/if needed
        self.port.rts = True
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()
        self.port.rts = False

        self._blink()  # verify the connection by making all the channels flash

        atexit.register(self._atexit)  # autoclose port when program terminates

        self.microns_per_bit = 15/32767
        return

    def _atexit(self):
        print('Auto-closing connection')
        self.close()
        return

    def _blink(self):
        """Make each channel blink to show we're connected ;)"""
        for ch in range(1, 4):
            self.identify(ch)
            time.sleep(0.5)
        return

    def identify(self, ch):
        """Make the number on this channel blink"""
        cmd = apt.mod_identify(dest=self.RACK, source=self.HOST, chan_ident=ch)
        self.write(cmd)
        return

    def close(self):
        self.port.close()
        return

    def read(self):
        """Read/translate the APT-encoded output and return the decoded object

        I'm sure there's a less annoying way to do this, but this unpacker thing is
        built so you have to iterate over it.
        """
        try:
            r = self.unpacker.__next__()
        except StopIteration:
            r = None
        return r

    def write(self, cmd):
        # just for completeness
        self.port.write(cmd)
        return

    def bayid(self, ch):
        """Get the 'bay' id (hex) for a given channel

        For some commands, we need to reference the 'bay' instead of the channel.
        This has to do with the architecture of the device -- there's a central motherboard that
        talks to three cards, each of which controls one channel.
        """
        return getattr(self, 'BAY%d' % (ch - 1))

    def get_position(self, ch):
        # this uses bay=channel, channel=1 (see bayid function)
        cmd = apt.pz_req_outputpos(dest=self.bayid(ch), source=self.HOST, chan_ident=1)
        self.write(cmd)
        return self.read().position*self.microns_per_bit

    def set_position(self, pos, ch):
        posbit = int((pos/self.microns_per_bit) + 0.5)
        print(posbit)
        cmd = apt.pz_set_outputpos(dest=self.bayid(ch), source=self.HOST, chan_ident=1, position=posbit)
        self.write(cmd)
        return

    def get_voltage(self, ch):
        cmd = apt.pz_req_outputvolts(dest=self.bayid(ch), source=self.HOST, chan_ident=1)
        self.write(cmd)
        return self.read().voltage

    def set_voltage(self, v, ch):
        cmd = apt.pz_set_outputvolts(dest=self.bayid(ch), source=self.HOST, chan_ident=1, voltage=v)
        self.write(cmd)
        return

    def write_read(self, cmd):
        self.write(cmd)
        return self.read()

    def get_pi(self, ch):
        cmd = apt.pz_req_piconsts(dest=self.bayid(ch), source=self.HOST, chan_ident=1)
        r = self.write_read(cmd)
        return (r.PropConst, r.IntConst)

    def set_pi(self, p, i, ch):
        """Must be in the range 0-255"""
        cmd = apt.pz_set_piconsts(dest=self.bayid(ch), source=self.HOST, chan_ident=1, PropConst=p, IntConst=i)
        self.write(cmd)
        return

    def get_status(self, ch):
        """Get basic information about the channel"""
        cmd = apt.hw_start_updatemsgs(dest=self.bayid(ch), source=self.HOST)
        self.write(cmd)
        time.sleep(0.1)  # this command takes some time
        r = self.read()  # we could decode this in a useful way instead of just returning?
        for key, item in r._asdict().items():
            print(key + ':', item)
        return r

    def get_outputmaxvolts(self, ch):
        cmd = apt.pz_req_outputmaxvolts(dest=self.bayid(ch), source=self.HOST, chan_ident=1)
        r = self.write_read(cmd)
        return r.voltage/10  # somehow the unit is x10

    def set_outputmaxvolts(self, v, ch):
        cmd = apt.pz_set_outputmaxvolts(dest=self.bayid(ch), source=self.HOST, chan_ident=1, voltage=int(10*v))
        self.write(cmd)
        return

    def get_mode(self, ch):
        cmd = apt.pz_req_positioncontrolmode(dest=self.bayid(ch), source=self.HOST, chan_ident=1)
        r = self.write_read(cmd)
        rdict = {1: 'open_loop', 2: 'closed_loop'}
        return rdict[r.mode]

    def set_mode(self, mode, ch):
        rdict = {'open_loop': 3, 'closed_loop': 4}  # force smooth transitions
        cmd = apt.pz_set_positioncontrolmode(dest=self.bayid(ch), source=self.HOST, chan_ident=1, mode=rdict[mode])
        self.write(cmd)
        return


if __name__=='__main__':
    c = BPC303('COM5')
