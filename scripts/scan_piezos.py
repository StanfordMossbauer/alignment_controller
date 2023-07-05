import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time

from AH2550A import AH2550A
from AbsorberAttractorAssembly import *

micron_per_cm = 1e6/1e2
cap_to_sep = lambda c: 50*140/c  # very rough --> get real numbers from Albert

piezo_controller_port = 'COM3'
bridge_resource_name = 'GPIB0::28::INSTR'

AAA = AbsorberAttractorAssembly(piezo_controller_port)

bridge = AH2550A(bridge_resource_name, timeout=1e4)
c, l, v = bridge.single_measurement()

initial_separation = cap_to_sep(c)

test_angle_max = 6*np.arcsin((initial_separation)/(two_piezo_distance_cm*micron_per_cm/2))  # keep plates from crashing

angles_to_try = np.linspace(-test_angle_max, test_angle_max, 11)


samples_per_angle = 2

filename_base = '20230628_thetascan_30umsep_1'
start_str = 'Radians\tpF\tLoss[nS]\tVolts'
print(start_str)

dfs = {}
start_voltages = piezo_controller.get_voltages()
#for axis in ('phi',):
for axis in ('theta', 'phi'):
	outdata = []
	for angle in angles_to_try:
		for trial in range(samples_per_angle):
            AAA.rotate(angle, axis, start_voltages)
            time.sleep(0.1)
			c, l, v = bridge.single_measurement()
			data_str = f'{voltages}\t{angle}\t{c}\t{l}\t{v}\n'
			print(data_str)
			outdata.append(
				dict(
					dist1=distance_adjustment[1],
					v0=voltages[0],
					v1=voltages[1],
					v2=voltages[2],
					angle=angle, capacitance=c, loss=l, voltage=v)
				)
	dfs[axis] = pd.DataFrame(outdata)
	dfs[axis].to_csv(filename_base + f'_{axis}.csv')
	plt.plot(dfs[axis].dist1, dfs[axis].capacitance, '.', label=axis)
piezo_controller.set_voltages(start_voltages)  # return to start

plt.xlabel('Distance 2 [um]')
plt.ylabel('capacitance [pF]')
plt.legend()
plt.savefig(filename_base + '.png')
plt.show()
