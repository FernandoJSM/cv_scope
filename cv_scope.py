"""Base do osciloscópio"""

import os
import cv2
import numpy as np
from tqdm import tqdm
from config import Video
from knobs import VKnobs, HKnobs, TKnob
from waveforms import SineWave, SquareWave, GND
from text_panel import TextPanel


class CVScope:
    """
    Contém todos os elementos para simular o osciloscópio
    """

    def __init__(self):
        self.background = cv2.imread(os.path.join(Video.ASSETS_PATH, "scope_bg.png"))

        self.display_w = Video.DISPLAY_W
        self.display_h = Video.DISPLAY_H
        self.display_x0 = Video.DISPLAY_X0
        self.display_y0 = Video.DISPLAY_Y0

        self.vertical = VKnobs(scope=self)
        self.horizontal = HKnobs(scope=self)
        self.trigger = TKnob(scope=self)
        self.text = TextPanel(scope=self)

        self.wave = None

    def set_waveform(
        self,
        waveform,
        amplitude=None,
        frequency=None,
        duty_cycle=None,
        noise=False,
        peak_noise=False,
        color=(0, 255, 255),
    ):
        """
        Define o tipo de forma de onda que será exibida no osciloscópio
        """
        if waveform == "sinewave":
            self.wave = SineWave(self, amplitude, frequency, color, noise, peak_noise)
        elif waveform == "squarewave":
            self.wave = SquareWave(self, amplitude, frequency, duty_cycle, color, noise, peak_noise)
        elif waveform == "gndwave":
            self.wave = GND(self, color, noise, peak_noise)
        else:
            raise ValueError(f"Forma de onda '{waveform}' não foi implementada")

    def animate_knobs(self, frame):
        """
        Anima os knobs do osciloscópio
        """
        self.vertical.position.animate(frame)
        self.vertical.division.animate(frame)

        self.horizontal.position.animate(frame)
        self.horizontal.division.animate(frame)

        self.trigger.level.animate(frame)

    def draw_on_display(self, image, overlay_image, reverse_color):
        """
        Desenha uma imagem sobre o display
        """
        output = image.copy()

        # Cria máscara do tamanho do canvas
        mask = cv2.inRange(
            overlay_image, np.array(reverse_color), np.array(reverse_color)
        )
        mask_inv = cv2.bitwise_not(mask)

        # Recorte da imagem de fundo
        roi = output[
            self.display_y0 : self.display_y0 + self.display_h,
            self.display_x0 : self.display_x0 + self.display_w,
        ]

        # Aplica a máscara sobre as duas imagens
        img_canvas_bg = cv2.bitwise_and(roi, roi, mask=mask)
        img_function = cv2.bitwise_and(overlay_image, overlay_image, mask=mask_inv)

        # Combina e sobrepõe as imagens
        combined = cv2.add(img_canvas_bg, img_function)

        output[
            self.display_y0 : self.display_y0 + overlay_image.shape[0],
            self.display_x0 : self.display_x0 + overlay_image.shape[1],
        ] = combined

        return output

    def overlay_knobs(self, image):
        """
        Sobrepõe os knobs em cima da imagem de fundo, considerando o ângulo de cada um
        """
        image = self.vertical.position.overlay(image)
        image = self.vertical.division.overlay(image)

        image = self.horizontal.position.overlay(image)
        image = self.horizontal.division.overlay(image)

        image = self.trigger.level.overlay(image)

        return image

    def overlay_display(self, image, frame):
        """
        Desenha as imagens sobre o display do osciloscópio
        """
        image = self.wave.overlay(image)
        image = self.horizontal.position.draw_line(image, frame)
        image = self.vertical.position.draw_line(image, frame)
        image = self.trigger.level.draw_line(image, frame)

        return image

    def record(self, output_path):
        """
        Gera a animação frame a frame e salva em um vídeo
        """
        writer = cv2.VideoWriter_fourcc(*"mp4v")

        if self.wave is None:
            raise RuntimeError("Forma de onda não definida!")

        output = cv2.VideoWriter(
            output_path, writer, Video.FPS, (Video.WIDTH, Video.HEIGHT)
        )
        print(f"Renderizando {Video.LENGTH} segundos de vídeo..")

        for frame in tqdm(range(Video.TOTAL_FRAMES)):
            self.animate_knobs(frame)

            image = self.background.copy()
            image = self.overlay_knobs(image)
            image = self.overlay_display(image, frame)
            image = self.text.overlay_text(image)

            output.write(image)

        output.release()
        print(f"Vídeo salvo como '{output_path}'")
