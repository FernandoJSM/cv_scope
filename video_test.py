import numpy as np
from cv_scope import CVScope

# Declarar constantes

if __name__ == "__main__":
    scope = CVScope()

    # Estado inicial do osciloscópio

    scope.horizontal.division.set_init(value=5e-3)
    scope.vertical.division.set_init(value=1)
    scope.trigger.level.set_init(value=0)
    # scope.trigger.level.set_value(v=3)
    # scope.trigger.show_cursor()
    # scope.cursor_a.show()
    # scope.cursor_b.hide()

    # Forma de onda do osciloscópio
    scope.set_waveform("squarewave", duty_cycle=0.1, amplitude=2, frequency=1 / 10e-3, noise = True, peak_noise=True)

    # Keyframes
    scope.horizontal.division.set_keyframes(
        start=1, end=4, target_value=1e-3, interpolation="linear"
    )
    scope.trigger.level.set_keyframes(
        start=5, end=9, target_value=1, interpolation="cosine"
    )

    # Gravação do vídeo
    scope.record(output_path="output.mp4")
