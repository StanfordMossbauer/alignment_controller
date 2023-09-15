import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time

from AH2550A import AH2550A
from AbsorberAttractorAssembly import *

micron_per_cm = 1e6/1e2
cap_to_sep = lambda c: 50*140/c  # very rough --> get real numbers from Albert

piezo_controller_port = 'COM5'
bridge_resource_name = 'GPIB0::28::INSTR'

AAA = AbsorberAttractorAssembly(piezo_controller_port)

for ch in range(1, 4):
    AAA.controller.set_mode('closed_loop', ch)
time.sleep(1)
#start_positions = AAA.get_positions()
# [7.54373489 8.78591983 7.67034529]
# [7.54373489 8.78591983 7.67034529]
'''
start_positions = np.array([8, 8, 8])
AAA.set_positions(start_positions)
#start_positions = AAA.rotate(0.00174148, 'theta', start_positions)
start_positions = AAA.rotate(0.0006707230709256351, 'phi', start_positions)
start_positions = AAA.rotate(-0.0006637566295534793, 'theta', start_positions)
start_positions = AAA.rotate(0.0007347445300662038, 'phi', start_positions)
start_positions = AAA.rotate(-0.0006637566295534793, 'theta', start_positions)
'''
start_positions = np.array([7.62373489, 8.86591983, 7.75034529])  # no rot
start_positions = np.array([7.43476669, 8.79207739, 7.69020661])  # theta rot
start_positions = np.array([7.43476669, 8.91813397, 7.56415003])  # phi rot

start_positions = np.array([7.63476669, 9.11813397, 7.76415003])  # 15 um
start_positions = np.array([7.63476669, 8.98837578, 7.89390822])  # phi rot
start_positions = np.array([7.65810102, 8.97670861, 7.88224105])  # theta rot

start_positions = np.array([7.73810102, 9.05670861, 7.96224105])  # 7 um
start_positions = np.array([7.73810102, 8.9954223,  8.02352736])  # phi rot
start_positions = np.array([7.73810102, 8.9425095,  8.07644016])  # phi rot
start_positions = np.array([7.72642688, 8.94834657, 8.08227723])  # theta rot

start_positions = np.array([7.74642688, 8.96834657, 8.10227723])  # 5.7 um
start_positions = np.array([7.74142688, 8.96334657, 8.09727723])  # 6.35 um
#start_positions = np.array([7.77068838, 8.94871582, 8.08264648])  # theta rot

AAA.set_positions(start_positions)

bridge = AH2550A(bridge_resource_name, timeout=1e4)
c, l, v = bridge.single_measurement(max_attempts=10)

initial_separation = cap_to_sep(c)

print('initial sep:', initial_separation, 'um')

test_angle_max = np.arcsin((initial_separation)/(two_piezo_distance_cm*micron_per_cm/2))  # keep plates from crashing
print(test_angle_max)

angles_to_try = np.linspace(-test_angle_max, test_angle_max, 11)
print(angles_to_try)

samples_per_angle = 10

filename_base = '20230915_1307_6um'
start_str = 'Radians\tpF\tLoss[nS]\tVolts'
print(start_str)

dfs = {}

print(start_positions)
time.sleep(1)
#for axis in ('phi',):

for axis in ('theta', 'phi'):
    print('\n', axis)
    outdata = []
    for angle in angles_to_try:
        for trial in range(samples_per_angle):
            AAA.rotate(angle, axis, start_positions)
            time.sleep(1)
            positions = AAA.get_positions()
            time.sleep(0.1)
            c, l, v = bridge.single_measurement(max_attempts=10)
            data_str = f'{positions}\t{angle}\t{c}\t{l}\t{v}\n'
            print(data_str)
            outdata.append(
                dict(
                    v0=positions[0],
                    v1=positions[1],
                    v2=positions[2],
                    angle=angle, capacitance=c, loss=l, position=v)
                )
    dfs[axis] = pd.DataFrame(outdata)
    dfs[axis].to_csv(filename_base + f'_{axis}.csv')
    plt.plot(dfs[axis].angle, dfs[axis].capacitance, '.', label=axis)
# todo set to minimum pos
AAA.set_positions(start_positions)  # return to start
print(start_positions)

#plt.xlabel('Distance 2 [um]')
plt.xlabel('angle [rad]')
plt.ylabel('capacitance [pF]')
plt.legend()
plt.savefig(filename_base + '.png')
plt.show()
