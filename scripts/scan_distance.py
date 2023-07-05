import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from tqdm import tqdm

from AH2550A import AH2550A
from AbsorberAttractorAssembly import *

micron_per_cm = 1e6/1e2
cap_to_sep = lambda c: 50*140/c  # very rough --> get real numbers from Albert

piezo_controller_port = 'COM3'
bridge_resource_name = 'GPIB0::28::INSTR'

basename = '20230705_voltagescan_1Vstep'

AAA = AbsorberAttractorAssembly(piezo_controller_port)

bridge = AH2550A(bridge_resource_name, timeout=1e4)

stepsize = 1  # Volts
samples_per_voltage = 2

voltages, step = np.linspace(0, 150, int(150*(1/stepsize)) + 1, retstep=True)
assert step==stepsize, "something wrong with linspace"


for direction in ('decreasing', 'increasing'):
    voltages = voltages[::-1]
    outfilebase = basename + f'_{direction}V'
    outdata = []
    for i in tqdm(range(len(voltages))):
        AAA.set_voltages(np.array([voltages[i]]*3))
        time.sleep(0.1)
        try:
            c, l, v = bridge.n_measurements(samples_per_voltage, max_attempts=100)
        except IndexError as e:
            print(e)
            print('Ending loop early')
            break
        outdict = dict(
            voltage=voltages[i],
            cmean=c.mean(),
            cstd=c.std(),
            lmean=l.mean(),
            lstd=l.std(),
            vmean=v.mean(),
            vstd=v.std(),
        )
        print(outdict)
        outdata.append(outdict)
        with open(outfilebase+'.dat', 'a') as f:
            f.write(' '.join(map(str, list(outdict.values()))) + '\n')
    df = pd.DataFrame(outdata)
    df.to_csv(outfilebase+'.csv')
    plt.plot(df.voltage, 1.0/df.cmean, '.', label=f'{direction} voltage')

plt.xlabel('piezo voltage')
plt.ylabel('1/C [pF-1]')
plt.legend()
plt.savefig(basename + '.png')
plt.show()
