"""
CardioIA - Fase 3 - IR ALÉM 2
Modelo neuromórfico simples baseado em neurônios LIF.

A ideia é transformar uma janela temporal de batimentos cardíacos em contagens de
spikes geradas por neurônios com diferentes limiares. Essas features representam
uma leitura neuromórfica simples da série temporal.
"""
from __future__ import annotations

import numpy as np


class LIFSpikeEncoder:
    """Codificador de séries temporais usando neurônios Leaky Integrate-and-Fire."""

    def __init__(
        self,
        thresholds: list[float] | None = None,
        decay: float = 0.90,
        reset_value: float = 0.0,
        input_gain: float = 1.0,
    ) -> None:
        self.thresholds = np.array(thresholds or [0.85, 1.00, 1.15], dtype=float)
        self.decay = decay
        self.reset_value = reset_value
        self.input_gain = input_gain

    def encode_window(self, window: np.ndarray) -> np.ndarray:
        """Converte uma janela de BPM em features de spikes."""
        # Normalização centrada em 90 BPM. Valores acima disso geram maior corrente.
        current = (window.astype(float) - 70.0) / 50.0
        current = np.clip(current, 0, 2.0) * self.input_gain

        features: list[float] = []

        for threshold in self.thresholds:
            voltage = 0.0
            spike_times: list[int] = []
            voltage_trace: list[float] = []

            for t, value in enumerate(current):
                voltage = self.decay * voltage + value
                if voltage >= threshold:
                    spike_times.append(t)
                    voltage = self.reset_value
                voltage_trace.append(voltage)

            spike_count = len(spike_times)
            first_spike = spike_times[0] if spike_times else len(window)
            last_spike = spike_times[-1] if spike_times else -1
            mean_voltage = float(np.mean(voltage_trace)) if voltage_trace else 0.0

            if len(spike_times) >= 2:
                isi = float(np.mean(np.diff(spike_times)))
            else:
                isi = float(len(window))

            features.extend([spike_count, first_spike, last_spike, isi, mean_voltage])

        return np.array(features, dtype=float)

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transforma matriz (n_amostras, janela) em features neuromórficas."""
        return np.vstack([self.encode_window(row) for row in X])
