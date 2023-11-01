import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
from static.src.signals import Power


class Analyser:

    def __init__(self, signal: Power, state='reactive'):
        self.signal = signal
        self.state = state
        self.data = self._get_type()
        self.positive = self._check_positive()

    def length(self):
        return self.signal.times[-1] - self.signal.times[0]

    def high_state(self):
        un_noised = self._denoise()
        mean_value = np.mean(un_noised)
        std_dev = np.std(un_noised)
        return mean_value + std_dev

    def low_state(self):
        un_noised = self._denoise()
        mean_value = np.mean(un_noised)
        std_dev = np.std(un_noised)
        return mean_value - std_dev

    def top_line(self):
        return max(self._denoise())

    def bottom_line(self):
        return min(self._denoise())

    def distal_line(self):
        if self.positive:
            return 0.9 * self.top_line()
        else:
            return 1.1 * self.top_line()

    def mesial_line(self):
        if self.positive:
            return 0.5 * self.top_line()
        else:
            return 1.5 * self.top_line()

    def pulse_width(self):
        _, start, fst = self.rise_time()
        _, lst, end = self.fall_time()

        rise_diffs = [abs(self.mesial_line() - val) for val in self.data[start:fst]]
        fall_diffs = [abs(self.mesial_line() - val) for val in self.data[lst:end]]

        rise_idx = rise_diffs.index(min(rise_diffs))
        fall_idx = fall_diffs.index(min(fall_diffs))

        return self.signal.times[end - fall_idx] - self.signal.times[start + rise_idx]

    def rise_time(self):
        un_noised = self._denoise()
        peaks, _ = find_peaks(un_noised, self.mesial_line())

        start = peaks[0]
        prev_val = self.data[start]
        while start >= 0:
            start -= 1
            new_val = self.data[start]
            if abs((prev_val - new_val)) < 1 and new_val < prev_val:
                break
            else:
                prev_val = new_val

        rise_time = self.signal.times[peaks[0]] - self.signal.times[start]

        return rise_time, start, peaks[0]

    def fall_time(self):
        un_noised = self._denoise()
        peaks, _ = find_peaks(un_noised, self.mesial_line())

        end = peaks[-1]
        prev_val = self.data[end]
        while end < len(self.data):
            end += 1
            new_val = self.data[end]
            if abs((prev_val - new_val)) < 1 and new_val < prev_val:
                break
            else:
                prev_val = new_val

        fall_time = self.signal.times[end] - self.signal.times[peaks[-1]]

        return fall_time, peaks[-1], end

    def _check_positive(self):
        if self.top_line() <= 0:
            return False
        else:
            return True

    def _find_threshold(self):
        mean = np.mean(self.data)
        std_dev = np.std(self.data)
        return mean + 5 * std_dev

    def _denoise(self):
        un_noised = np.fft.fft(self.data)
        threshold = self._find_threshold()
        un_noised[abs(un_noised) < threshold] = 0
        return np.fft.ifft(un_noised)

    def _get_type(self):
        if self.state == 'reactive':
            return self.signal.reactive()
        elif self.state == 'real':
            return self.signal.real()
        elif self.state == 'apparent':
            return self.signal.apparent()
        else:
            raise Exception("Available types: 'reactive', 'real', 'apparent'.")
