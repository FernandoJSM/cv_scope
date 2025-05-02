"""Botões do osciloscópio"""

import os
import cv2
import numpy as np
from config import Video


class BaseKnob:
    def __init__(
        self,
        scope,
        name,
        start_value,
        start_angle,
        x0,
        y0,
        image,
        value_map=None,
        toggle_line=False,
        hor_line=False,
        is_trigger=False,
    ):
        """
        Contém os elementos básicos dos botões
        """
        self.scope = scope
        self.name = name
        self.value = start_value
        self.center_angle = start_angle
        self.angle = start_angle
        self.x0 = x0
        self.y0 = y0
        self.image = cv2.imread(os.path.join(Video.ASSETS_PATH, image))
        self.width, self.height, _ = self.image.shape
        self.value_frames = np.full(Video.TOTAL_FRAMES, start_value).astype(np.float32)
        self.value_map = value_map
        self.animate_line = np.zeros(Video.TOTAL_FRAMES)
        self.toggle_line = toggle_line
        self.hor_line = hor_line
        self.is_trigger = is_trigger

    def get_vmap(self, value):
        """
        Realiza a busca dos valores definidos para os botões que possuem valores discretos
        """
        search = ((i, v) for i, v in enumerate(self.value_map) if v[0] == value)
        return next(search, None)

    def set_value(self, value):
        """
        Define o valor e ângulo do botão, conforme o valor definido
        """
        if self.value_map is None:
            # O valor é de -5 a 5 por conta das 10 divisões da tela do osciloscópio
            if value < -5 or value > 5:
                raise ValueError(f"Valor {value} fora do intervalo permitido (-5 a 5)")
            angle = 180 * -value / 5 + self.center_angle
        else:
            vmap = self.get_vmap(value)
            if vmap is None:
                raise ValueError(f"Valor {value} inválido para o botão '{self.name}'")
            angle = vmap[1][1]

        self.value = value
        self.angle = angle

    def set_init(self, value):
        """
        Define o valor inicial do botão
        """
        self.set_value(value)
        self.value_frames = np.full(Video.TOTAL_FRAMES, self.value).astype(np.float32)

    def remap_values(self, index_map):
        """
        Define o valor de um botão conforme o índice do vetor de entrada para os botões
        que possuem valores discretos
        """
        output = np.zeros(index_map.shape)
        for i, m in enumerate(index_map):
            output[i] = self.value_map[m][0]
        return output

    def set_keyframes(self, start, end, target_value, interpolation):
        """
        Cria os keyframes, conforme o tempo inicial/final, valor alvo e tipo de interpolação
        para a animação do botão
        """
        f_start = int(start * Video.FPS)
        f_end = int(end * Video.FPS)

        if f_end == Video.TOTAL_FRAMES:
            f_end = f_end - 1

        start_value = self.value_frames[f_start]

        if self.value_map is None:
            if interpolation == "linear":
                self.value_frames[f_start : f_end + 1] = np.linspace(
                    start_value, target_value, f_end - f_start + 1
                )
            elif interpolation == "cosine":
                amplitude = start_value - target_value
                cosine = np.cos(np.linspace(0, np.pi, f_end - f_start + 1))
                self.value_frames[f_start : f_end + 1] = (
                    amplitude / 2 * (cosine - 1) + start_value
                )

            else:
                raise ValueError(
                    f"Interpolação '{interpolation}' não implementada para o botão '{self.name}"
                )
            self.value_frames[f_end + 1 :] = target_value
            self.animate_line[f_start : f_end + 1] = 1
        else:
            start_map = self.get_vmap(start_value)
            target_map = self.get_vmap(target_value)
            if target_map is None:
                raise ValueError(
                    f"Valor {target_value} inválido para o botão '{self.name}'"
                )
            if interpolation == "linear":
                index_map = np.round(
                    np.linspace(start_map[0], target_map[0], f_end - f_start + 1)
                ).astype(int)
            elif interpolation == "cosine":
                amplitude = start_map[0] - target_map[0]
                cosine = np.cos(np.linspace(0, np.pi, f_end - f_start + 1))
                index_map = np.round(
                    (amplitude / 2 * (cosine - 1) + start_map[0])
                ).astype(int)
            else:
                raise ValueError(
                    f"Interpolação '{interpolation}' não implementada para o botão '{self.name}"
                )
            self.value_frames[f_start : f_end + 1] = self.remap_values(index_map)
            self.value_frames[f_end + 1 :] = target_map[1][0]

    def animate(self, frame):
        """
        Anima o botão conforme o frame inserido na função
        """
        self.set_value(
            value=self.value_frames[frame],
        )

    def overlay(self, image):
        """
        Sobrepõe a imagem do botão sobre a imagem de entrada, rotacionando o botão conforme o
        valor dele
        """
        img_button = self.image.copy()

        # Girar imagem
        img_center = (self.width / 2, self.height / 2)
        rot_mat = cv2.getRotationMatrix2D(img_center, self.angle, 1.0)
        img_button = cv2.warpAffine(
            img_button, rot_mat, (self.width, self.height), borderValue=(255, 255, 255)
        )

        output = image.copy()
        output[self.y0 : self.y0 + self.height, self.x0 : self.x0 + self.width] = (
            img_button
        )

        return output

    def draw_line(self, image, frame, cursor_color=(255, 255, 0)):
        """
        Desenha uma linha na tela do osciloscópio, conforme o valor do botão durante sua animação
        """
        if self.toggle_line is False:
            return image
        if self.animate_line[frame] == 0:
            return image

        if self.is_trigger:
            value = self.value + self.scope.vertical.position.value
        else:
            value = self.value

        if self.hor_line:
            y_pos = int(-value * self.scope.display_h / 10 + (self.scope.display_h) / 2)

            pt1_line = (0, y_pos)
            pt2_line = (0 + self.scope.display_w, y_pos)

            pt1_tri = (0, y_pos - 5)
            pt2_tri = (0 + 5, y_pos)
            pt3_tri = (0, y_pos + 5)
        else:
            x_pos = int(value * self.scope.display_w / 10 + (self.scope.display_w) / 2)

            pt1_line = (x_pos, 0)
            pt2_line = (x_pos, 0 + self.scope.display_h)

            pt1_tri = (x_pos - 5, 0)
            pt2_tri = (x_pos, 0 + 5)
            pt3_tri = (x_pos + 5, 0)

        triangle_cnt = np.array([pt1_tri, pt2_tri, pt3_tri])

        reverse_color = tuple(255 - x for x in cursor_color)
        function_canvas = np.full(
            (self.scope.display_h, self.scope.display_w, 3),
            reverse_color,
            dtype=np.uint8,
        )

        function_canvas = cv2.line(function_canvas, pt1_line, pt2_line, cursor_color, 1)
        function_canvas = cv2.drawContours(
            function_canvas, [triangle_cnt], 0, cursor_color, -1
        )

        output = self.scope.draw_on_display(image, function_canvas, reverse_color)

        return output


class VKnobs:
    """
    Define os botões para ajuste vertical
    """

    def __init__(self, scope):
        self.position = BaseKnob(
            scope=scope,
            name="Posição vertical",
            start_value=0,
            start_angle=90,
            x0=393,
            y0=108,
            image="base_knob.png",
            toggle_line=True,
            hor_line=True,
        )

        self.division = BaseKnob(
            scope=scope,
            name="Volts por divisão",
            start_value=1,
            start_angle=225,
            x0=372,
            y0=189,
            image="vdiv_knob.png",
            value_map=[
                (0.1, 0),
                (0.2, 45),
                (0.5, 90),
                (1, 135),
                (2, 180),
                (5, 225),
                (10, 270),
                (20, 315),
            ],
        )


class HKnobs:
    """
    Define os botões para ajuste horizontal
    """

    def __init__(self, scope):
        self.position = BaseKnob(
            scope=scope,
            name="Posição horizontal",
            start_value=0,
            start_angle=90,
            x0=512,
            y0=108,
            image="base_knob.png",
            toggle_line=True,
            hor_line=False,
        )

        self.division = BaseKnob(
            scope=scope,
            name="Tempo por divisão",
            start_value=5e-3,
            start_angle=0,
            x0=492,
            y0=189,
            image="hdiv_knob.png",
            value_map=[
                (1e-3, 0),
                (2e-3, 315),
                (5e-3, 270),
                (10e-3, 225),
                (20e-3, 180),
                (1, 135),
                (2, 90),
                (5, 45),
            ],
        )


class TKnob:
    """
    Define o botão do trigger
    """

    def __init__(self, scope):
        self.level = BaseKnob(
            scope=scope,
            name="Nível trigger",
            start_value=0,
            start_angle=90,
            x0=452,
            y0=353,
            image="base_knob.png",
            toggle_line=True,
            hor_line=True,
            is_trigger=True,
        )
