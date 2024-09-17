"""
ISPPJ1 2024
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from typing import List, Optional, Tuple, Any, Dict, Set

import pygame

import random

import settings 
from src.Tile import Tile
from src.Tile_power_up import Tile_power_up 


class Board:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.matches: List[List[Tile]] = []
        self.tiles: List[List[Tile]] = []
        self.__initialize_tiles()
        self.band_moving = False ##True indica cuando buscar matches
        self.score_power_up = 0

    def render(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                tile.render(surface, self.x, self.y)

    def __is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def __initialize_tiles(self) -> None:
        self.tiles = [
            [None for _ in range(settings.BOARD_WIDTH)]
            for _ in range(settings.BOARD_HEIGHT)
        ]
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                color = random.randint(0, settings.NUM_COLORS - 1)
                while self.__is_match_generated(i, j, color):
                    color = random.randint(0, settings.NUM_COLORS - 1)

                self.tiles[i][j] = Tile(
                    i, j, color, random.randint(0, settings.NUM_VARIETIES - 1)
                )
        
        while not self.is_match_board():
            self.randomize_board()

        ##para generar powerUp 
        #Prueba de combinacion de 5 tiles
        """self.tiles[1][0] = Tile(
            1,
            0,
            2,
            3,
        )
        self.tiles[1][1] = Tile(
            1,
            1,
            2,
            3,
        )
        self.tiles[1][3] = Tile(
            1,
            3,
            2,
            3,
        )
        self.tiles[1][4] = Tile(
            1,
            4,
            2,
            3,
        )
        self.tiles[2][2] = Tile(
            2,
            2,
            2,
            3,
        )
        self.tiles[0][1] = Tile(
            0,
            1,
            1,
            3,
        )
        self.tiles[2][1] = Tile(
            2,
            1,
            1,
            3,
        )
        self.tiles[3][1] = Tile(
            3,
            1,
            1,
            3,
        )"""
        ##Prueba de combinacion de 4 tiles
        """self.tiles[6][0] = Tile(
            6,
            0,
            1,
            3,
        )
        self.tiles[6][1] = Tile(
            6,
            1,
            1,
            3,
        )
        self.tiles[6][3] = Tile(
            6,
            3,
            1,
            3,
        )
        self.tiles[7][2] = Tile(
            7,
            2,
            1,
            3,
        )"""
        ##prueba de power_up cruz
        """self.tiles[5][0] = Tile(
            5,
            0,
            1,
            3,
        )
        self.tiles[5][1] = Tile(
            5,
            1,
            1,
            3,
        )"""

        ## prueba de power_up miscellaneo
        """self.tiles[0][0] = Tile(
            0,
            0,
            2,
            3,
        )
        self.tiles[0][1] = Tile(
            0,
            1,
            2,
            3,
        )"""

    def __calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack:
            return []

        self.in_stack.add(tile)

        color_to_match = tile.color

        ## Check horizontal match
        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        ## Check vertical match
        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        for t in match:
            match += self.__calculate_match_rec(t)

        self.in_stack.remove(tile)
        return match

    def calculate_matches_for(
        self, new_tiles: List[Tile]
    ) -> Optional[List[List[Tile]]]:
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile in self.in_match:
                continue
            match = self.__calculate_match_rec(tile)
            if len(match) > 0:
                self.matches.append(match)

        delattr(self, "in_match")
        delattr(self, "in_stack")

        return self.matches if len(self.matches) > 0 else None

    def remove_matches(self) -> None:
        for match in self.matches:
            for tile in match:
                if not isinstance(tile, Tile_power_up):
                    self.tiles[tile.i][tile.j] = None
                else:
                    if tile.variety == 0:
                        self.__power_up_cross(tile.i, tile.j)
                    elif tile.variety == 1:
                        self.__power_up_miscellaneous(tile.i, tile.j)

        self.matches = []

    def get_falling_tiles(self) -> Tuple[Any, Dict[str, Any]]:
        # List of tweens to create
        tweens: List[Tuple[Tile, Dict[str, Any]]] = []

        # for each column, go up tile by tile until we hit a space
        for j in range(settings.BOARD_WIDTH):
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]

                # if our previous tile was a space
                if space:
                    # if the current tile is not a space
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i

                        # set its prior position to None
                        self.tiles[i][j] = None

                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True

                    if space_i == -1:
                        space_i = i

                i -= 1

        # create a replacement tiles at the top of the screen
        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT):
                tile = self.tiles[i][j]

                if tile is None:
                    tile = Tile(
                        i,
                        j,
                        random.randint(0, settings.NUM_COLORS - 1),
                        random.randint(0, settings.NUM_VARIETIES - 1),
                    )
                    tile.y -= settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens

    def randomize_board(self) -> None:
        #change 8x8 matrix for an array
        tiles_r = [l for row in self.tiles for l in row]
        random.shuffle(tiles_r)

        #change array to an 8x8 matrix 
        self.tiles = [tiles_r[i * 8:(i + 1) * 8] for i in range(8)]

        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                self.tiles[i][j].i = i
                self.tiles[i][j].j = j
                self.tiles[i][j].x = j * settings.TILE_SIZE
                self.tiles[i][j].y = i * settings.TILE_SIZE

        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                if self.__is_match_generated(i, j, self.tiles[i][j].color):
                    self.randomize_board()

    def is_match_board(self) -> bool:
        self.matches = []
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH - 1):
                self.matches = []
                tile1 = self.tiles[i][j]
                tile2 = self.tiles[i][j+1]
                #swap tiles
                (
                    self.tiles[i][j],
                    self.tiles[i][j + 1],
                ) = (
                    self.tiles[i][j + 1],
                    self.tiles[i][j],
                )
                (tile1.i, tile1.j, tile2.i, tile2.j) = (
                    tile2.i,
                    tile2.j,
                    tile1.i,
                    tile1.j
                )
                
                (tile1.x, tile1.y, tile2.x, tile2.y) = (
                    tile2.x, 
                    tile2.y, 
                    tile1.x, 
                    tile1.y
                )
                matches_h = self.calculate_matches_for([tile1, tile2])

                #swap tiles
                (
                    self.tiles[i][j],
                    self.tiles[i][j + 1],
                ) = (
                    self.tiles[i][j + 1],
                    self.tiles[i][j],
                )
                (tile1.i, tile1.j, tile2.i, tile2.j) = (
                    tile2.i,
                    tile2.j,
                    tile1.i,
                    tile1.j
                )
                
                (tile1.x, tile1.y, tile2.x, tile2.y) = (
                    tile2.x, 
                    tile2.y, 
                    tile1.x, 
                    tile1.y
                )

                if matches_h is None:
                    pass
                else:
                    self.matches = []
                    return True

        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT - 1):
                self.matches = []

                tile1 = self.tiles[i][j]
                tile2 = self.tiles[i+1][j]

                #swap tiles
                (
                    self.tiles[i][j],
                    self.tiles[i+1][j],
                ) = (
                    self.tiles[i+1][j],
                    self.tiles[i][j],
                )
                (tile1.i, tile1.j, tile2.i, tile2.j) = (
                    tile2.i,
                    tile2.j,
                    tile1.i,
                    tile1.j
                )
                
                (tile1.x, tile1.y, tile2.x, tile2.y) = (
                    tile2.x, 
                    tile2.y, 
                    tile1.x, 
                    tile1.y
                )

                matches_v = self.calculate_matches_for([tile1, tile2])

                #swap tiles
                (
                    self.tiles[i][j],
                    self.tiles[i+1][j],
                ) = (
                    self.tiles[i+1][j],
                    self.tiles[i][j],
                )
                (tile1.i, tile1.j, tile2.i, tile2.j) = (
                    tile2.i,
                    tile2.j,
                    tile1.i,
                    tile1.j
                )
                
                (tile1.x, tile1.y, tile2.x, tile2.y) = (
                    tile2.x, 
                    tile2.y, 
                    tile1.x, 
                    tile1.y
                )

                if matches_v is None:
                    pass
                else:
                    self.matches = []
                    return True

        self.matches = []
        return False
    
    #determines when to generate a power up. Whether it is 4 tiles or 5
    def calculate_power_up(self, tiles) -> int:
        
        for l in range(2):
            color = tiles[l].color
            i = tiles[l].i
            j = tiles[l].j

            if (#power up b) of 5 tiles
                i >= 2 and i <= 5
                and self.tiles[i - 1][j].color == color
                and self.tiles[i - 2][j].color == color
                and self.tiles[i + 1][j].color == color
                and self.tiles[i + 2][j].color == color
            ):
                return Tile_power_up(
                    i, j, color, settings.NUM_VARIETIES_POWER_UPS - 1
                )
            elif (
                j >= 2 and j <= 5
                and self.tiles[i][j - 1].color == color
                and self.tiles[i][j - 2].color == color
                and self.tiles[i][j + 1].color == color
                and self.tiles[i][j + 2].color == color
            ):
                return Tile_power_up(
                    i, j, color, settings.NUM_VARIETIES_POWER_UPS - 1
                )
            elif (#power up a) of 4 tiles
                i >= 2 and i <= 6
                and self.tiles[i - 1][j].color == color
                and self.tiles[i - 2][j].color == color
                and self.tiles[i + 1][j].color == color
            ):
                return Tile_power_up(
                    i, j, color, settings.NUM_VARIETIES_POWER_UPS - 2
                )
            elif (
                j >= 2 and j <= 6
                and self.tiles[i][j - 1].color == color
                and self.tiles[i][j - 2].color == color
                and self.tiles[i][j + 1].color == color
            ):
                return Tile_power_up(
                    i, j, color, settings.NUM_VARIETIES_POWER_UPS - 2
                )
        
        return None

    def __power_up_cross(self, tile_i, tile_j):
        self.score_power_up = 0
        
        for j in range(settings.BOARD_WIDTH):
            self.tiles[tile_i][j] = None
            self.score_power_up += 8
        
        for i in range(settings.BOARD_HEIGHT):
            self.tiles[i][tile_j] = None
            self.score_power_up += 8

        self.score_power_up += 50

    def __power_up_miscellaneous(self, i: int, j: int) -> None:
        self.score_power_up = 0

        color = self.tiles[i][j].color

        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                if self.tiles[i][j] is not None:
                    if self.tiles[i][j].color == color:
                        self.tiles[i][j] = None
                        self.score_power_up += 16

        self.score_power_up += 50 #por gastar el power_up
