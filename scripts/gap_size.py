import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from pymba import*
import numpy as np
import cv2
from typing import Optional
from pymba import*
import numpy as np
import cv2
from typing import Optional
import matplotlib.pyplot as plt
import time
from tqdm import tqdm
from AH2550A import AH2550A
from AbsorberAttractorAssembly import *
import pandas as pd

def display_frame(frame, delay: int = 1) -> None:
    print('frame: {}'.format(frame.data.frameID))
    img = frame.buffer_data_numpy()
    cv2.imshow('Image', img)
    cv2.waitKey(delay)

def rgb_to_gray(img):
    return np.dot(img[..., :3], [0.2989, 0.5870, 0.1140])

piezo_controller_port = 'COM4'
bridge_resource_name = 'GPIB0::28::INSTR'

#if ('AAA' in locals()) or ('AAA' in globals()):
    #AAA.piezo_controller.close()

AAA = AbsorberAttractorAssembly(piezo_controller_port)
bridge = AH2550A(bridge_resource_name, timeout=1e4)

fig, ax = plt.subplots(1, 1)

for stepsize, samples_per_voltage in zip(
        (1,),# 1, 0.1, 0.1, 0.01),
        (2,)):# 2, 5, 5, 10)):
    basename = '{dt}_voltagescan_{stepsize}Vstep'.format(
        dt=time.strftime('%Y%m%d_%H%M%S'),
        stepsize=stepsize)

    voltages, step = np.linspace(0, 150, int(150*(1/stepsize)) + 1, retstep=True)
    assert step==stepsize, "something wrong with linspace"

    for direction in ('decreasing', 'increasing'):
        voltages = voltages[::-1]
        outfilebase = basename + f'_{direction}V'
        outdata = []

        for i in tqdm(range(len(voltages))):
            AAA.set_voltages(voltages[i])
            time.sleep(0.1)
            print('opening camera')
            with Vimba() as vimba:
                vimba.startup()
                camera = vimba.camera(0)
                camera.open()

                camera.arm('SingleFrame')
                frame = camera.acquire_frame()
                image = frame.buffer_data_numpy()
                #display_frame(frame, 0)
                np.save(f'image_{i}', image)
                camera.disarm()
                camera.close()
            print('camera closed')
            img = np.load(f'image_{i}.npy')
            print('image loaded')
            if img.ndim == 3:
                img = rgb_to_gray(img)

            column_intensity = img.sum(axis=0)
            pixel_size = 2.06
            x_in_microns = np.arange(img.shape[1]) * pixel_size
            num_high_intensity_columns = np.sum(column_intensity > 5e4)
            gap_size = num_high_intensity_columns * x_in_microns
            print(num_high_intensity_columns)
            #plt.figure()
            #plt.plot(x_in_microns, column_intensity)
            #plt.title(f'Sum of pixel intensities for each column, {num_high_intensity_columns} columns above 2*10^5')
            #plt.xlabel('Position (microns)')
            #plt.ylabel('Sum of intensities')
            #plt.show()
            print('beans')
            try:
                c, l, v = bridge.n_measurements(samples_per_voltage, max_attempts=100)
            except IndexError as e:
                print(e)
                print('Ending loop early')
                break

            outdict = dict(
                voltage=voltages[i], cmean=c.mean(), cstd=c.std(), 
                lmean=l.mean(), lstd=l.std(), vmean=v.mean(), vstd=v.std(),
                distance=num_high_intensity_columns,
                )
            outdata.append(outdict)

            with open(outfilebase + '.dat', 'a') as f:
                f.write(' '.join(map(str, list(outdict.values()))) + '\n')

        df = pd.DataFrame(outdata)
        df.to_csv(outfilebase + '.csv')
        plt.plot(df.voltage, 1.0/df.cmean, '.', label=f'{direction} voltage')
    ax2 = ax.twinx()
    plt.plot(df.voltage, df.distance, 'k.')

    plt.xlabel('piezo voltage')
    plt.ylabel('1/C [pF-1]')
    plt.legend()
    plt.savefig(basename + '.png')
