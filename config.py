"""Configuração básica do vídeo"""

from dataclasses import dataclass


@dataclass
class Video:
    """Definição de constantes"""

    FPS: int = 30
    WIDTH: int = 640
    HEIGHT: int = 480
    ASSETS_PATH: str = "./assets"
    LENGTH: int = 10
    DISPLAY_W: int = 300
    DISPLAY_H: int = 300
    DISPLAY_X0: int = 51
    DISPLAY_Y0: int = 72
    TOTAL_FRAMES: int = FPS * LENGTH
