import pygame
import os
from os import environ
import random
import cv2
import time
from datetime import datetime
import pickle
import threading
import time
import webbrowser

def open_url(url):
    try:
        webbrowser.get('chrome').open_new(url)
    except:
        try:
            webbrowser.get('firefox').open_new_tab(url)
        except:
            try:
                webbrowser.open(url, new=1)
            except:
                return False
    return True

def out_text_file(surface, text, size, x, y, color, font_file, return_img = False, bk_color=None):
    try:
        font = pygame.font.Font(font_file, size)
    except OSError:
        font = pygame.font.SysFont(None, size)
    text_img = font.render(text, True, color, bk_color)
    if return_img:
        return text_img
    surface.blit(text_img, [x, y])


def fadeout(surface, page, x, y):
    path = os.path.join(DIR_TEMP_DATA, "welcome_screen.png")
    pygame.image.save(surface, path)
    temp_image = pygame.image.load(path)
    temp_image = temp_image.convert()
    temp_image2 = page.convert()
    i = 255
    i2 = 0
    while i > 0:
        temp_image.set_alpha(i)
        temp_image2.set_alpha(i2)
        surface.blit(temp_image2, [x, y])
        surface.blit(temp_image, [x, y])
        i -= 5
        i2 += 5
        pygame.display.update()

def createBluredImg(input_img, output_img, ksize=(7, 7), sigmaX=0):
    try:
        image = cv2.imread(input_img)
        Gaussian_blur = cv2.GaussianBlur(image, ksize, sigmaX)
        cv2.imwrite(output_img, Gaussian_blur)
    except:
        return False
    return True

def collision(maskFirst, maskSecond, maskFirstPos_x, maskFirstPos_y, maskSecondPos_x, maskSecondPos_y):
	offset = (int(maskFirstPos_x - maskSecondPos_x), int(maskFirstPos_y - maskSecondPos_y))
	result = maskSecond.overlap(maskFirst, offset)
	return result


def getListOfFiles(basepath, include_basepath=True):
    paths = []
    if include_basepath:
        with os.scandir(basepath) as entries:
            for entry in entries:
                path = os.path.join(basepath, entry.name)
                if os.path.isfile(path):
                    paths.append(os.path.join(basepath, entry.name))
    else:
        with os.scandir(basepath) as entries:
            for entry in entries:
                path = os.path.join(basepath, entry.name)
                if os.path.isfile(path):
                    paths.append(entry.name)
    return paths


def closeGame():
    os._exit(0)


def sortImagesPath(img_list, base_path, extantion='.png'):
    filePaths = []
    for name in img_list:
        filePaths.append(name.split('.')[0])
    filePaths.sort(key=int)
    for index in range(0, len(img_list)):
        filePaths[index] = os.path.join(base_path, (filePaths[index]+extantion))
    return filePaths

def custom_out_text(surface, text, x, x1, y, color, size, f_file):
    text_img = out_text_file(surface, text, size, 0, 0, color, f_file, True)
    put_point_x = x + ((x1 - x) // 2)
    put_point_x = put_point_x - (text_img.get_width() // 2)
    surface.blit(text_img, [put_point_x, y])

# Sound effacts names.
SOUND_BUTTON_CLICK = 1
SOUND_DIE = 2
SOUND_HIT = 3
SOUND_POINT = 4
SOUND_WING = 5
SOUND_BACKGROUND = 6


class SoundManager:
    sounds = {}  # this dict will store all sound file which is loaded in the game. and any object of this class can access.
    settingData = None

    def __init__(self):
        pass