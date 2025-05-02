"""Formas de onda para o osciloscópio"""

import cv2
import numpy as np
from scipy import signal


class BaseWave:
    """
    Base de uma forma de onda
    """

    def __init__(
        self, scope, color, active_trigger=False, noise=False, peak_noise=False
    ):
        self.scope = scope
        self.color = color
        self.function = None
        self.amplitude = None
        self.frequency = None
        self.duty_cycle = None
        self.active_trigger = active_trigger
        self.triggered = False
        self.noise = noise
        self.peak_noise = peak_noise

    def overlay(self, image):
        """
        Desenha a forma de onda no display do osciloscópio
        """
        if self.active_trigger:
            trigger_lvl = (
                self.scope.trigger.level.value * self.scope.vertical.division.value
            )
            if np.abs(trigger_lvl) < self.amplitude:
                self.triggered = True
                # import ipdb; ipdb.set_trace()
                if isinstance(self, SineWave):
                    trigger_offset = -np.arcsin(trigger_lvl / self.amplitude) / (
                        2 * np.pi * self.frequency
                    )
                else:
                    trigger_offset = 0
            else:
                self.triggered = False
                trigger_offset = np.random.rand() / self.frequency
        timespan = self.scope.horizontal.division.value * 10
        time_offset = (
            self.scope.horizontal.position.value * self.scope.horizontal.division.value
        ) + trigger_offset
        time_ax = (
            np.linspace(-timespan / 2, timespan / 2, self.scope.display_w) - time_offset
        )

        v_scale = (self.scope.display_h / 10) / self.scope.vertical.division.value
        v_offset = (
            self.scope.vertical.position.value * self.scope.vertical.division.value
        )

        function_plot = np.zeros(time_ax.shape)

        rand_index = np.random.choice(
            len(time_ax), size=np.random.randint(5, 16), replace=False
        )
        for i, t in enumerate(time_ax):
            peak = 0
            noise = 0
            if self.peak_noise and (i in rand_index):
                if np.random.rand() > 0.5:
                    peak = (np.random.rand() - 0.5) * self.amplitude * 10
            if self.noise:
                noise = (np.random.rand() - 0.5) * self.amplitude
            # Adiciona um pouco de ruído para passar a impressão de realismo
            function_plot[i] = v_scale * (self.function(t) + v_offset) + noise + peak

        reverse_color = tuple(255 - x for x in self.color)
        function_canvas = np.full(
            (self.scope.display_h, self.scope.display_w, 3),
            reverse_color,
            dtype=np.uint8,
        )

        # Desenhar a funcao
        for x in range(self.scope.display_w - 1):
            function_canvas = cv2.line(
                function_canvas,
                (x, int(self.scope.display_h // 2 - function_plot[x])),
                (x + 1, int(self.scope.display_h // 2 - function_plot[x + 1])),
                self.color,
                1,
            )

        output = self.scope.draw_on_display(image, function_canvas, reverse_color)

        return output


class GND(BaseWave):
    """
    Define uma forma de onda aterrada (linha 0V)
    """

    def __init__(self, scope, color, noise, peak_noise):
        super().__init__(scope, color, noise, peak_noise)
        self.function = lambda t: 0


class SineWave(BaseWave):
    """
    Define uma senoide
    """

    def __init__(
        self,
        scope,
        amplitude,
        frequency,
        color,
        noise,
        peak_noise,
        active_trigger=True,
    ):
        super().__init__(scope, color, active_trigger, noise, peak_noise)
        if amplitude is None:
            raise ValueError("Não foi inserido o valor de amplitude")
        if frequency is None:
            raise ValueError("Não foi inserido o valor de frequência")
        self.frequency = frequency
        self.amplitude = amplitude
        self.function = lambda t: amplitude * np.sin(2 * np.pi * frequency * t)


class SquareWave(BaseWave):
    """
    Define uma onda quadrada
    """

    def __init__(
        self,
        scope,
        amplitude,
        frequency,
        duty_cycle,
        color,
        noise,
        peak_noise,
        active_trigger=True
    ):
        super().__init__(scope, color, active_trigger, noise, peak_noise)
        if amplitude is None:
            raise ValueError("Não foi inserido o valor de amplitude")
        if frequency is None:
            raise ValueError("Não foi inserido o valor de frequência")
        if duty_cycle is None:
            raise ValueError("Não foi inserido o valor de duty cycle")
        self.frequency = frequency
        self.amplitude = amplitude
        self.duty_cycle = duty_cycle
        self.function = lambda t: amplitude * signal.square(
            2 * np.pi * frequency * t, duty_cycle
        )
