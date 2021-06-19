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

    def load_sound(self, name, sound_file, default_volume=None):
        if name in self.sounds:
            sound = self.sounds[name]
            sound.stop()
            self.sounds.pop(name)

        self.sounds[name] = pygame.mixer.Sound(sound_file)
        if default_volume != None:
            pygame.mixer.Sound.set_volume(self.sounds[name], default_volume)

    def play_sound(self, name, loop=0, maxmim_time=None):
        if self.settingData.game_sound:
            if name in self.sounds:
                if maxmim_time == None:
                    pygame.mixer.Sound.play(self.sounds[name], loop)
                else:
                    pygame.mixer.Sound.play(self.sounds[name], loop, maxmim_time)
            else:
                return "FNF"
                # File Not Found

    def set_volume(self, name, volume):
        # Max Value 1.0
        # Min Value 0.0
        if name in self.sounds:
            pygame.mixer.Sound.set_volume(self.sounds[name], volume)
        else:
            return "FNF"
            # File Not Found

    def clear_music(self):
        for key, sound in self.sounds.items():
            try:
                sound.stop()
                self.sounds.pop(key)
            except:
                pass

    def stop_sound(self, name='all'):
        if name == 'all':
            for key, sound in self.sounds.items():
                try:
                    sound.stop()
                except:
                    pass
        elif name in self.sounds:
            try:
                sound.stop()
            except:
                return "U_to_S"
            # unable to stop sound.
        else:
            return "FNF"
        # File Not Found

class SequentialAnimation:
    def __init__(self, screen, img_dir, x, y, screen_width, screen_height, auto_postion_at_center=False, create_mask=False):
        self.screen = screen

        # fetching path of all images which is available in side of img_dir.
        loader_images_path = getListOfFiles(img_dir, False)

        # sorting paths in acceding order.
        loader_images_path = sortImagesPath(loader_images_path, img_dir)

        # loading all image.
        self.loader_images = [pygame.image.load(image_path).convert_alpha() for image_path in loader_images_path]

        # creating mask of all images which i loaded in "self.loader_images" but when create_mask will be true.
        if create_mask:
            self.masked_images = []
            for image in self.loader_images:
                self.masked_images.append(pygame.mask.from_surface(image))

        # creating variable for maintaining the index of loader_images list.
        self.counter = 0

        # get height and width of sequence image.
        self.image_width = self.loader_images[self.counter].get_width()
        self.image_height = self.loader_images[self.counter].get_height()

        # creating system to fix location of animation in the center of the screen.
        if auto_postion_at_center:
            self.x = int((screen_width/2) - (self.image_width/2))
            self.y = int((screen_height/2) - (self.image_height/2))-25
        else:
            self.x = x
            self.y = y

        # this variable will store total number of images.
        self.total_images = len(self.loader_images)

        # loader will active until active_state variable will hold True.
        self.active_state = False

    def show(self):
        self.screen.blit(self.loader_images[self.counter], (self.x, self.y))
        self.counter += 1
        if self.counter >= self.total_images:
            self.counter = 0

    def collide(self, other_mask, x, y):
        if collision(self.masked_images[self.counter], other_mask, self.x, self.y, x, y):
            return True
        else:
            return False

class Loader(SequentialAnimation):
    def __init__(self, screen, img_dir, x, y, screen_width, screen_height, auto_postion_at_center=False):
        super(Loader, self).__init__(screen, img_dir, x, y, screen_width, screen_height, auto_postion_at_center)

    def start(self):
        sub = self.screen.subsurface((self.x, self.y, self.image_width, self.image_height))
        image_file = os.path.join(DIR_TEMP_DATA, "temp_img.jpg")
        pygame.image.save(sub, image_file)
        self.background_cover = pygame.image.load(image_file)
        while self.active_state:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    closeGame()

            self.screen.blit(self.background_cover, (self.x, self.y))
            self.show()
            pygame.display.update()
            clock.tick(60)
        self.counter = 0

class Bird(SoundManager):
    def __init__(self, screen, x, y, img_path, area):
        self.birds = []
        self.birds_mask = []
        self.screen = screen
        self.x = x
        self.y = y
        self.AREA_X, self.AREA_Y, self.AREA_WIDTH, self.AREA_HEIGHT = area
        self.y_surface = self.AREA_Y+self.AREA_HEIGHT
        birds = getListOfFiles(img_path, False)
        birds = sortImagesPath(birds, img_path)
        for bird in birds:
            bird_image = pygame.image.load(bird).convert_alpha()
            self.birds.append(bird_image)
            """creating mask for check collision between objects.
            i am creating different mask for different birds image because the picture of the bird changing every time."""
            self.birds_mask.append(pygame.mask.from_surface(bird_image))

        self.height = self.birds[0].get_height()
        self.width = self.birds[0].get_width()
        self.counter = 0
        self.gravity = 1 # default is 1
        self.declineSpeed = 0.1 # 0.1
        self.propelSpeed = 10  # speed of moving forward and backward.
        self.backMove = False
        self.forwardMove = False
        self.totalBirds = len(self.birds)
        self.pushUpActive = False