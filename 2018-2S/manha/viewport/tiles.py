'''
Created on 30/10/2014

@author: Aluno
'''
import pygame
from pygame.rect import Rect
from pygame.surface import Surface

class Conversao(object):
    def __init__(self, ratio):
        self.ratio = ratio
        
    def get_world_to_pixels(self, pos):
        px = pos[0] * self.ratio[0]
        py = pos[1] * self.ratio[1]
        return px, py

    def get_pixels_to_world(self, pos):
        wx = int(pos[0] / self.ratio[0])
        wy = int(pos[1] / self.ratio[1])
        return wx, wy

    def get_pixels_to_world_gap(self, pos):
        gx = pos[0] % self.ratio[0]
        gy = pos[1] % self.ratio[1]
        return gx, gy


class TileSet(object):
    def __init__(self, jsonObj):
        self.name = jsonObj['name']
        self.firstgid = jsonObj['firstgid']
        self.image_width = jsonObj['imagewidth']
        self.image_height = jsonObj['imageheight']
        self.tile_width = jsonObj['tilewidth']
        self.tile_height = jsonObj['tileheight']
        self.margin = jsonObj['margin']
        self.spacing = jsonObj['spacing']
        self.tileoffset = jsonObj['tileoffset']
        self.columns = int(self.image_width / self.tile_width)
        self.lines = int(self.image_height / self.tile_height)
        self.image = pygame.image.load(jsonObj['image'])
        self.lastgid = self.firstgid - 1 + (self.columns * self.lines)

    def getTileByGId(self, gId):
        currentFrame = (gId - self.firstgid)
        column = currentFrame % self.columns
        line = int(currentFrame / self.columns)
        x = self.margin + ((self.tile_width + self.tileoffset["x"]) * column)
        y = self.spacing + ((self.tile_height + self.tileoffset["y"]) * line)
        w = self.tile_width
        h = self.tile_height
        r = Rect((x, y), (w, h))
        image = self.image.subsurface(r)
        brick = Brick(self, image, gId)
        return brick
      
    

class Brick(object):
    def __init__(self, tileset, imagem, gId):
        self.tileset = tileset
        self.image = imagem
        self.gId = gId  
        self.coluna = (gId - 1) % self.tileset.columns
        self.linha = (gId - 1) / self.tileset.columns   
        self.rect = Rect( (0,0), (imagem.get_width(), imagem.get_height()))  
        
        
class Layer(object):
    def __init__(self, json):
        self.name = json['name']
        self.type = json['type']
        self.width = json['width']
        self.height = json['height']
        self.visible = json['visible']
        self.opacity = json['opacity']
        self.__data = json['data']
        self.internal_structure = []
        self.conversion = {}
        
    def prepare(self, tile_set):
        self.conversion = Conversao((tile_set.tile_width, tile_set.tile_height))
        self.internal_structure = []
        for l in range(self.height):
            celulas = []
            for c in range(self.width):
                gid = self.__data[(l * self.width) + c]
                brk = Brick(tile_set,
                        Surface((tile_set.tile_width, tile_set.tile_height), 0, 32), 0)
                if gid > 0:
                    brk = tile_set.getTileByGId(gid)
                celulas.append(brk)
            self.internal_structure.append(celulas)


    def get_frame(self, c1, l1, c2, l2):
        cols = abs(c2 - c1)
        rows = abs(l2 - l1)        
        img = pygame.Surface(self.conversion.get_world_to_pixels((cols, rows)), 0, 32)
        for l in range(rows):
            for c in range(cols):
                b = self.internal_structure[l + l1][c + c1]
                pos = self.conversion.get_world_to_pixels((c, l))
                img.blit(b.image, pos)
        return img

    def get_frame_rect(self, r):
        (c1, l1) = self.conversion.get_pixels_to_world(r.topleft)
        (c2, l2) = self.conversion.get_pixels_to_world(r.bottomright)
        img = self.get_frame(c1, l1, c2 + 1, l2 + 1)
        gapTop = self.conversion.get_pixels_to_world_gap(r.topleft)
        imgFinal = img.subsurface(Rect(gapTop, r.size))
        return imgFinal
