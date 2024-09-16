"""
ISPPJ1 2024
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings

from src.Tile_power_up import Tile_power_up


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Position in the grid which we are highlighting
        self.board_highlight_i1 = -1
        self.board_highlight_j1 = -1
        self.board_highlight_i2 = -1
        self.board_highlight_j2 = -1

        self.highlighted_tile = False

        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 1000

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.board.band_moving:
            aux = self.board.is_match_board()
            while not aux:
                self.board.randomize_board()
                aux = self.board.is_match_board()
            self.board.band_moving = False

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        if self.highlighted_tile:
            x = self.highlighted_j1 * settings.TILE_SIZE + self.board.x
            y = self.highlighted_i1 * settings.TILE_SIZE + self.board.y
            surface.blit(self.tile_alpha_surface, (x, y))

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active: 
            return

        if input_id == "mouse_up": 
            if input_data.buttons[0] == 1:
                pos_x, pos_y = input_data.position
                pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                i = (pos_y - self.board.y) // settings.TILE_SIZE
                j = (pos_x - self.board.x) // settings.TILE_SIZE

                ##mouse motion up
                if 1 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                    self.__mouse_moving(0, i, j) ##up 0, down 1, left 2, right 3

        elif input_id == "mouse_down":
            if input_data.buttons[0] == 1:
                pos_x, pos_y = input_data.position
                pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                i = (pos_y - self.board.y) // settings.TILE_SIZE
                j = (pos_x - self.board.x) // settings.TILE_SIZE

                ##mouse motion down
                if 0 <= i < settings.BOARD_HEIGHT - 1 and 0 <= j < settings.BOARD_WIDTH:
                    self.__mouse_moving(1, i, j) ##up 0, down 1, left 2, right 3

        elif input_id == "mouse_left":
            if input_data.buttons[0] == 1:
                pos_x, pos_y = input_data.position
                pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                i = (pos_y - self.board.y) // settings.TILE_SIZE
                j = (pos_x - self.board.x) // settings.TILE_SIZE

                ##mouse motion left
                if 0 <= i < settings.BOARD_HEIGHT and 1 <= j < settings.BOARD_WIDTH:
                    self.__mouse_moving(2, i, j) ##up 0, down 1, left 2, right 3

        elif input_id == "mouse_right":
            if input_data.buttons[0] == 1:
                pos_x, pos_y = input_data.position
                pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                i = (pos_y - self.board.y) // settings.TILE_SIZE
                j = (pos_x - self.board.x) // settings.TILE_SIZE

                ##mouse motion right
                if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH - 1:
                    self.__mouse_moving(3, i, j) ##up 0, down 1, left 2, right 3

        ##Solo para probar la funcion randomize_board
        """elif input_id == "randomize":
            self.board.randomize_board()"""

    def __mouse_moving(self, dir, i, j) -> None: ##up 0, down 1, left 2, right 3
        if not self.highlighted_tile:
            if dir == 0: ##up
                self.highlighted_tile = True
                self.highlighted_i1 = i
                self.highlighted_j1 = j
                self.highlighted_i2 = i - 1
                self.highlighted_j2 = j
                self.active = False
            elif dir == 1: ##down:
                self.highlighted_tile = True
                self.highlighted_i1 = i
                self.highlighted_j1 = j
                self.highlighted_i2 = i + 1 
                self.highlighted_j2 = j
            elif dir == 2:
                self.highlighted_tile = True
                self.highlighted_i1 = i
                self.highlighted_j1 = j
                self.highlighted_i2 = i
                self.highlighted_j2 = j- 1
            elif dir == 3:
                self.highlighted_tile = True
                self.highlighted_i1 = i
                self.highlighted_j1 = j
                self.highlighted_i2 = i
                self.highlighted_j2 = j + 1

            tile1 = self.board.tiles[self.highlighted_i1][
                self.highlighted_j1
            ]
            tile2 = self.board.tiles[self.highlighted_i2][
                self.highlighted_j2
            ]
            
            def arrive():
                tile1 = self.board.tiles[self.highlighted_i1][
                    self.highlighted_j1
                ]
                tile2 = self.board.tiles[self.highlighted_i2][
                    self.highlighted_j2
                ]
                (
                    self.board.tiles[tile1.i][tile1.j],
                    self.board.tiles[tile2.i][tile2.j],
                ) = (
                    self.board.tiles[tile2.i][tile2.j],
                    self.board.tiles[tile1.i][tile1.j],
                )
                (tile1.i, tile1.j, tile2.i, tile2.j) = (
                    tile2.i,
                    tile2.j,
                    tile1.i,
                    tile1.j,
                )

                matches = self.board.calculate_matches_for([tile2, tile1])

                if matches is None:
                    def bad_move():
                        (
                            self.board.tiles[tile1.i][tile1.j],
                            self.board.tiles[tile2.i][tile2.j],
                        ) = (
                            self.board.tiles[tile2.i][tile2.j],
                            self.board.tiles[tile1.i][tile1.j],
                        )
                        tile1.i, tile1.j, tile2.i, tile2.j = (
                            tile2.i,
                            tile2.j,
                            tile1.i,
                            tile1.j,
                        )
                        self.active = True
                        self.highlighted_tile = False
                    Timer.after(
                        0.50,
                        lambda: Timer.tween(
                            0.25,
                            [
                                (tile1, {"x": tile2.x, "y": tile2.y}),
                                (tile2, {"x": tile1.x, "y": tile1.y}),
                            ],
                            on_finish=bad_move,
                        )
                    )
                else:
                    self.highlighted_tile = False
                    self.__calculate_matches([tile1, tile2])

            # Swap tiles
            Timer.tween(
                0.25,
                [
                    (tile1, {"x": tile2.x, "y": tile2.y}),
                    (tile2, {"x": tile1.x, "y": tile1.y}),
                ],
                on_finish=arrive,
            )

    def __calculate_matches(self, tiles: List) -> None:
        matches = self.board.calculate_matches_for(tiles)

        if matches is None:
            self.board.band_moving = True
            self.active = True
            return

        tile_power_up = self.board.calculate_power_up(tiles[0].i, tiles[0].j)
        
        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        for match in matches:
            self.score += len(match) * 50

        self.score += self.board.score_power_up

        self.board.remove_matches()

        if tile_power_up is not None:
            i = tile_power_up.i
            j = tile_power_up.j

            self.board.tiles[i][j] = tile_power_up

        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.50,
            falling_tiles,
            on_finish=lambda: self.__calculate_matches(
                [item[0] for item in falling_tiles]
            ),
        )
