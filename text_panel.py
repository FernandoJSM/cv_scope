"""Textos do osciloscópio"""

import cv2
import numpy as np


class TextPanel:
    """
    Define o painel com todos o texto apresentado pelo osciloscópio
    """

    def __init__(self, scope):
        self.scope = scope

    @staticmethod
    def write_txt(image, text, position, color=(0, 0, 0), right_align=False):
        """
        Escreve o texto no painel conforme posição inserida
        """
        font = cv2.FONT_HERSHEY_DUPLEX
        if right_align:
            text_size = cv2.getTextSize(text, font, 0.5, 2)[0]
            position_x = position[0] - text_size[0]
            position = (position_x, position[1])

        image = cv2.putText(
            image, text, position, font, 0.5, color, 1, cv2.LINE_AA, False
        )
        return image

    def overlay_text(self, image):
        """
        Sobrepõe os textos dos valores configurados do osciloscópio
        """
        v_div_txt = str(self.scope.vertical.division.value) + " V/div"
        v_div_txt = v_div_txt.replace(".0", "")
        position = (50, 390)
        image = self.write_txt(image, v_div_txt, position)

        v_pos = self.scope.vertical.position.value * self.scope.vertical.division.value
        v_pos_txt = f"Offset: {v_pos:.1f} V"
        position = (50, 410)
        image = self.write_txt(image, v_pos_txt, position)

        if self.scope.horizontal.division.value >= 1:
            h_div = np.round(self.scope.horizontal.division.value)
            h_div_txt = f"{h_div}s/div".replace(".0", "")
        else:
            h_div = np.round(self.scope.horizontal.division.value * 1000)
            h_div_txt = f"{h_div}ms/div".replace(".0", "")
        position = (352, 390)
        image = self.write_txt(image, h_div_txt, position, right_align=True)

        h_pos = (
            self.scope.horizontal.position.value * self.scope.horizontal.division.value
        )
        if np.abs(h_pos) > 0.1:
            h_pos_txt = f"{h_pos:.1f}s/div"
        else:
            h_pos_txt = f"{h_pos*1000:.1f}ms/div"
        position = (352, 410)
        image = self.write_txt(image, h_pos_txt, position, right_align=True)

        triggered_txt = "TRIG'D" if self.scope.wave.triggered else "TRIG'D?"
        triggered_color = (0, 0, 0) if self.scope.wave.triggered else (0, 0, 255)
        position = (50, 430)

        image = self.write_txt(image, triggered_txt, position, color=triggered_color)

        trigger_lvl = (
            self.scope.trigger.level.value * self.scope.vertical.division.value
        )

        trigger_lvl_txt = f"Trigger Level: {trigger_lvl:.1f} V"
        position = (50, 450)
        image = self.write_txt(image, trigger_lvl_txt, position)

        return image
