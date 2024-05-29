from collections import deque
from typing import Final

import pyxel as px
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from src.helper.vec import Vec2
from src.simulation.garden import Garden
from src.widgets.garden_widget import GardenWidget
from src.widgets.image import Image
from src.widgets.label import Label


class App:
    __WIDTH = 460
    __HEIGHT = 400
    __FPS = 30

    __GARDEN_BORDER: Final = px.COLOR_WHITE
    __GARDEN_SIZE: Final = (70, 100)
    __GARDEN_POSITION: Final = Vec2(30, 30)

    logger.info(f"App: window size: {__WIDTH}x{__HEIGHT}")
    logger.info(f"App: FPS: {__FPS}")

    def __init__(self):
        px.init(self.__WIDTH, self.__HEIGHT, quit_key=None, title="Gravity", display_scale=2, fps=self.__FPS)
        px.load("./res.pyxres")

        self.w_garden = GardenWidget(Garden(self.__GARDEN_SIZE, self.__GARDEN_BORDER), self.__GARDEN_POSITION)
        self.garden_draw_modes = deque([
            "draw_plants",
            "draw_energy",
            "draw_shadow",
            "draw_plants_id"
        ])
        self.garden_draw_mode_names = {
            "draw_plants": "normal",
            "draw_energy": "energy",
            "draw_shadow": "shadow",
            "draw_plants_id": "id"
        }
        self.garden_draw_mode = self.garden_draw_modes[0]

        self.l_mode = Label(Vec2(0, -10), [f"Draw mode: {self.garden_draw_mode_names[self.garden_draw_mode]}"],
                            px.COLOR_WHITE, self.w_garden)

        self.l_help = Label(Vec2(15, px.height - 50), [
            "R - reset garden",
            "T - switch between rendering modes",
            "F - simulate one step (If paused)",
            "Space - pase/unpause"
        ], px.COLOR_GRAY)

        self.l_size = Label(Vec2(self.w_garden.size[0] - 60, -10),
                            [f"Size: {self.w_garden.garden.size[0]}x{self.w_garden.garden.size[1]}"],
                            px.COLOR_WHITE, self.w_garden)

        self.larrow = Image(8, 8, 16, 0, 0, 0)
        self.rarrow = Image(-8, 8, 16, 0, 0, 0)

        self.active = True

    def run(self):
        px.run(self.update, self.draw)

    def switch_render_mode(self):
        self.garden_draw_modes.rotate()
        self.garden_draw_mode = self.garden_draw_modes[0]
        self.l_mode.set_text(f"Draw mode: {self.garden_draw_mode_names[self.garden_draw_mode]}")

        logger.info(f"Render mode changed to {self.garden_draw_mode}")

    def reset_garden(self):
        self.w_garden.garden = Garden(self.__GARDEN_SIZE, self.__GARDEN_BORDER)

        logger.info("Garden reset")

    def toggle_pause(self):
        self.active = not self.active

        if self.active:
            logger.info("App unpaused")
        else:
            logger.info("App paused")

    def update(self):
        if self.active:
            self.w_garden.update()

        if px.btnp(px.KEY_R):
            self.reset_garden()

        if px.btnp(px.KEY_T):
            self.switch_render_mode()

        if px.btnp(px.KEY_SPACE):
            self.toggle_pause()

        if px.btnp(px.KEY_F, hold=10, repeat=5) and not self.active:
            self.w_garden.update()

    def draw(self):
        px.cls(px.COLOR_BLACK)
        px.rect(*(self.w_garden.position - Vec2(15, 15)).as_tuple,
                *(Vec2(*self.w_garden.size) + Vec2(30, 45)).as_tuple, px.COLOR_NAVY)
        px.rect(*(self.w_garden.position - Vec2(16, 14)).as_tuple,
                *(Vec2(*self.w_garden.size) + Vec2(32, 43)).as_tuple, px.COLOR_NAVY)

        if self.w_garden.garden.has_plants:
            px.circb(10, 7, 2, px.COLOR_RED)
        else:
            px.circ(10, 7, 2, px.COLOR_RED)

        if self.active:
            px.circb(20, 7, 2, px.COLOR_YELLOW)
            px.circ(30, 7, 2, px.COLOR_GREEN)
        else:
            px.circ(20, 7, 2, px.COLOR_YELLOW)
            px.circb(30, 7, 2, px.COLOR_GREEN)

        self.w_garden.draw(self.garden_draw_mode)
        self.l_mode.draw()
        self.l_help.draw()
        self.l_size.draw()
        self.larrow.draw(self.w_garden.position.x,
                         self.w_garden.position.y + self.w_garden.size[1] + 2)
        self.rarrow.draw(self.w_garden.position.x + self.w_garden.size[0] - 8,
                         self.w_garden.position.y + self.w_garden.size[1] + 2)


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("__main__ level exception")
