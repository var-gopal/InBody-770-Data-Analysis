import openpyxl
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


def main():
    # Get file name
    file_name = input('Enter file name: ')

    # Open the workbook
    wb = openpyxl.load_workbook(file_name + '.xlsx')

    # Get spectrum raw data
    spectrum_raw = wb['SPECTRUM (RAW)']

    # Get time domain raw data
    time_domain_raw = wb['TIME DOMAIN (RAW)']

    # store time domain raw data in numpy arrays
    time_raw = np.array([cell.value for cell in time_domain_raw['A'][2:]])
    x_raw = np.array([cell.value for cell in time_domain_raw['B'][2:]])
    y_raw = np.array([cell.value for cell in time_domain_raw['C'][2:]])
    z_raw = np.array([cell.value for cell in time_domain_raw['D'][2:]])

    # store spectrum raw data in numpy arrays
    frequency_raw = np.array([cell.value for cell in spectrum_raw['A'][2:]])
    x_spectrum_raw = np.array([cell.value for cell in spectrum_raw['B'][2:]])
    y_spectrum_raw = np.array([cell.value for cell in spectrum_raw['C'][2:]])
    z_spectrum_raw = np.array([cell.value for cell in spectrum_raw['D'][2:]])

    # Generate plots for time domain raw data for all axes, spectrum raw data for all axes. Make the plots look nice and well spaced. Save to png.
    plt.figure(1)
    plt.subplot(311)
    plt.plot(time_raw, x_raw)
    plt.title('X-Axis Time Domain Raw Data')
    plt.xlabel('Time (s)')
    plt.ylabel('Magnetic Field (uT)')
    plt.subplot(312)
    plt.plot(time_raw, y_raw)
    plt.title('Y-Axis Time Domain Raw Data')
    plt.xlabel('Time (s)')
    plt.ylabel('Magnetic Field (uT)')
    plt.subplot(313)
    plt.plot(time_raw, z_raw)
    plt.title('Z-Axis Time Domain Raw Data')
    plt.xlabel('Time (s)')
    plt.ylabel('Magnetic Field (uT)')
    plt.tight_layout()
    plt.savefig('time_domain_raw_data.png')


    plt.figure(2)
    plt.subplot(311)
    plt.plot(frequency_raw, x_spectrum_raw)
    plt.title('X-Axis Spectrum Raw Data')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnetic Field (uT)')
    plt.subplot(312)
    plt.plot(frequency_raw, y_spectrum_raw)
    plt.title('Y-Axis Spectrum Raw Data')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnetic Field (uT)')
    plt.subplot(313)
    plt.plot(frequency_raw, z_spectrum_raw)
    plt.title('Z-Axis Spectrum Raw Data')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnetic Field (uT)')
    plt.tight_layout()
    plt.savefig('spectrum_raw_data.png')

    prom = int(input('Enter prominence: '))

    # Find the peak frequencies and their corresponding heights in the spectrum raw data. Find peaks of minimum height 10 and prominence 1000.
    x_peaks, _ = find_peaks(x_spectrum_raw, height=10, prominence=prom)
    y_peaks, _ = find_peaks(y_spectrum_raw, height=10, prominence=prom)
    z_peaks, _ = find_peaks(z_spectrum_raw, height=10, prominence=prom)

    x_peak_frequencies = frequency_raw[x_peaks]
    y_peak_frequencies = frequency_raw[y_peaks]
    z_peak_frequencies = frequency_raw[z_peaks]

    # print to console the frequencies of the peaks (with their magnitude) along each axis
    print('X-Axis Peak Frequencies: ', x_peak_frequencies)
    print('Y-Axis Peak Frequencies: ', y_peak_frequencies)
    print('Z-Axis Peak Frequencies: ', z_peak_frequencies)



# loop the program until the user enters 'quit'
while True:
    main()
    if input('Enter "quit" to exit program. Enter anything else to run again: ') == 'quit':
        break