import numpy as np
from cv_scope import CVScope

# Declarar constantes

if __name__ == "__main__":
    scope = CVScope()

    # Estado inicial do osciloscópio

    scope.horizontal.division.set_init(value=5e-3)
    scope.vertical.division.set_init(value=1)
    scope.trigger.level.set_init(value=0)

    # Forma de onda do osciloscópio
    scope.set_waveform("sinewave", amplitude=2, frequency=1 / 10e-3, noise = True, peak_noise=True)

    # Gravação do vídeo
    scope.record(output_path="output.mp4")
