import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from tqdm import tqdm

from AH2550A import AH2550A
from AbsorberAttractorAssembly import *

piezo_controller_port = 'COM5'
bridge_resource_name = 'GPIB0::28::INSTR'

if ('AAA' in locals()) or ('AAA' in globals()):
    AAA.piezo_controller.close()
AAA = AbsorberAttractorAssembly(piezo_controller_port)
bridge = AH2550A(bridge_resource_name, timeout=1e4)

for ch in range(1, 4):
    AAA.controller.set_mode('closed_loop', ch)
AAA.set_positions(10)

stepsize = 0.1  # "microns"
samples_per_position = 5
sleep_time = 1

basename = '{dt}_positionscan_{stepsize}Vstep'.format(
    dt=time.strftime('%Y%m%d_%H%M%S'),
    stepsize=stepsize,
)

positions, step = np.linspace(0, 10, int(10*(1/stepsize)) + 1, retstep=True)
assert step==stepsize, "something wrong with linspace"


fig = plt.figure()

for direction in ('decreasing', 'increasing'):
    positions = positions[::-1]
    outfilebase = basename + f'_{direction}V'
    outdata = []
    for i in tqdm(range(len(positions))):
        AAA.set_positions(positions[i])
        time.sleep(sleep_time)
        try:
            c, l, v = bridge.n_measurements(samples_per_position, max_attempts=100)
        except IndexError as e:
            print(e)
            print('Ending loop early')
            break
        outdict = dict(
            position=positions[i],
            cmean=c.mean(),
            cstd=c.std(),
            lmean=l.mean(),
            lstd=l.std(),
            vmean=v.mean(),
            vstd=v.std(),
        )
        #print(outdict)
        outdata.append(outdict)
        with open(outfilebase+'.dat', 'a') as f:
            f.write(' '.join(map(str, list(outdict.values()))) + '\n')
    df = pd.DataFrame(outdata)
    df.to_csv(outfilebase+'.csv')
    plt.plot(df.position, 1.0/df.cmean, '.', label=f'{direction} position')

plt.xlabel('piezo position')
plt.ylabel('1/C [pF-1]')
plt.legend()
plt.savefig(basename + '.png')
#plt.show()
