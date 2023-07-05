from AH2550A import AH2550A

import time

resource_name = 'GPIB0::28::INSTR'
timeout = 1e4

bridge = AH2550A(resource_name, timeout=timeout)

sleep_time = 0.1

print('C [pF]\tS [um]\tLoss [nS]\tdV [V]')
while 1:
    try:
        c, l, v = bridge.single_measurement(max_attempts=5, verbose=True)
        print('%.2f\t%.2f\t%.3f\t\t%.2f' % (c, 50*140/c, l, v))
    except IndexError as e:
        print(e)
        pass
    time.sleep(sleep_time)
