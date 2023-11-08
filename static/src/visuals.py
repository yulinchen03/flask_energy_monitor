import copy
import math

import pandas as pd

from static.src.meter_data import MeterData
from matplotlib.dates import DateFormatter
from datetime import datetime
from static.src.signals import Signal
import matplotlib.pyplot as plt
import numpy as np


def fft(powers):
    fft_data = np.fft.fft(powers)
    threshold_real = 0.5e6
    fft_data[abs(fft_data) < threshold_real] = 0
    denoised_data = np.fft.ifft(fft_data)
    return np.real(denoised_data)


def plot_powers_bar(powers, labels, filename):
    sizes = [100*(sum(power)/np.sum([sum(power) for power in powers])) for power in powers]
    sorted_sizes = []
    sorted_labels = []
    high_consumption_appliances = []
    size = len(sizes)
    sizes_copy = copy.deepcopy(sizes)
    while len(sorted_labels) < size:
        max_power = np.min(sizes)
        max_index = sizes_copy.index(max_power)
        sorted_sizes.append(max_power)
        sizes.remove(max_power)
        sorted_labels.append(labels[max_index])
    plt.barh(sorted_labels, sorted_sizes, color='green')
    plt.title('Proportion of energy consumption per appliance')
    plt.ylabel('Appliance')
    plt.xlabel('Proportion (%)')

    for size in reversed(sorted_sizes):
        print(size)
        label = labels[sizes_copy.index(size)]
        if size > 20:
            if label != "Other":
                high_consumption_appliances.append({'appliance': label, 'share': float("{0:.2f}".format(size))})
        else:
            break

    filename = filename.split('.')[0] + '.png'
    plotpath = f'static/plots/bar/{filename}'
    plt.savefig(plotpath, bbox_inches='tight')
    plt.close()

    return high_consumption_appliances, plotpath


def plot_powers_pie(powers, labels, filename):
    sizes = [sum(power) for power in powers[1:]]
    pie = plt.pie(sizes, textprops={'fontsize': 10})
    plt.xlabel('', fontsize=6)
    plt.ylabel('', fontsize=6)
    plt.title('')

    for label, t in zip(labels[1:], pie[1]):
        x, y = t.get_position()
        angle = int(math.degrees(math.atan2(y, x)))
        ha = "left"

        if x < 0:
            angle -= 180
            ha = "right"

        plt.annotate(label, xy=(x, y), rotation=angle, ha=ha, va="center", rotation_mode="anchor", size=6)

    plt.legend(labels, bbox_to_anchor=(0.1, 1), loc="center right", fontsize=8,
               bbox_transform=plt.gcf().transFigure)
    filename = filename.split('.')[0] + '.png'
    plotpath = f'static/plots/pie/{filename}'
    plt.savefig(plotpath, bbox_inches='tight')
    plt.close()

    return plotpath


def plot_powers_stack(times, powers, labels, filename, smooth=False):
    formatted_times = [datetime.fromtimestamp(time) for time in times]
    fig, ax = plt.subplots(figsize=(10, 4))

    if smooth:
        powers = fft(powers)

    ax.stackplot(formatted_times, powers, labels=labels, alpha=0.6)
    ax.legend(labels, bbox_to_anchor=(0.81, 0.5), loc="center left", fontsize=8,
               bbox_transform=plt.gcf().transFigure)
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    ax.grid(True)

    ax.set_xlabel('Time')
    ax.set_ylabel('Energy Consumption (Wh)')
    ax.set_title('Energy Disaggregation')

    plt.tight_layout()
    filename = filename.split('.')[0] + '.png'
    plotpath = f'static/plots/stackplot/{filename}'
    fig.savefig(plotpath, bbox_inches='tight')
    plt.close()

    return plotpath


def plot_signal(signal: Signal):
    plt.plot(signal.format_times(), signal.vals)
    plt.figure(figsize=(12, 3))
    plt.show()


def plot(data: MeterData, show_tags=True):
    _, axs = plt.subplots(3, 1, figsize=(10, 8))

    _plot_power(data, axs[0], lambda p: p.real(), 'Real Power (W)')
    _plot_power(data, axs[1], lambda p: p.reactive(), 'Reactive power (VAR)')
    _plot_power(data, axs[2], lambda p: p.factor(), 'Power factor')
    # _plot_hf(data, axs[3])

    for ax in axs:
        if show_tags and data.tags is not None:
            _add_device_tags(data, ax)

    plt.tight_layout(h_pad=2)
    plt.show()


def _plot_hf(data: MeterData, ax):
    times = data.hf.format_times()
    ax.imshow(np.transpose(data.hf.vals),
              aspect='auto', origin='lower',
              extent=[times[0], times[-1], 0, 1e6])

    freqs = np.linspace(0, 1e6, 6)
    ax.set_yticks(freqs)
    ax.set_yticklabels([f"{int(f / 1e3)}K" for f in freqs])
    ax.set_ylabel('Frequency KHz')

    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    ax.set_title('High Frequency Noise')
    ax.grid(True)


def _plot_power(data: MeterData, ax, consumer, title):
    ax.plot(data.l1.format_times(), consumer(data.l1), 'c')
    ax.plot(data.l2.format_times(), consumer(data.l2))

    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    ax.set_title(title)
    ax.grid(True)


def _add_device_tags(data: MeterData, ax):
    y_steps, y_idx = np.arange(0.2, 0.8, 0.2), 0

    for tag in data.tags:
        _add_device_line(ax, tag.label, tag.on, tag.off, y_steps[y_idx])
        y_idx = (y_idx + 1) % len(y_steps)


def _add_line(ax, name, time, color, y_step):
    xlims, ylims = ax.get_xlim(), ax.get_ylim()
    line_x = datetime.fromtimestamp(time)
    text_x = datetime.fromtimestamp(time + (xlims[1] - xlims[0]) * 500)
    text_y = (ylims[1] - ylims[0]) * y_step + ylims[0]
    ax.axvline(x=line_x, color=color, linestyle='--')
    ax.text(text_x, text_y, name, fontsize='xx-small')


def _add_device_line(ax, name, on_time, off_time, y_step):
    _add_line(ax, f'ON-{name}', on_time, 'g', y_step)
    _add_line(ax, f'OFF-{name}', off_time, 'r', y_step + 0.1)
