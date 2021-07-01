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

        # creating variable for blink effact.
        """
        :param blink_start_time: this variable will store the time when blink effect start. so that 
                    i will beb able to track total blink time.
        :param bird_hide : this variable will decide when bird will hidden or not.
                            if the value of the variable if true then bird will hide and when the value if False
                            then bird will visible.
        :param blink_gap: this variable will decide what time will be between 1st and 2nd blink.
        :param blink: when the value of this variable will true then blink effect will run for decided time,
                      the time will start when this variable get True value.
        :param blink_time: this variable will decide how long the blink effect will run.
        :param bird_hidden_start_time: this variable store the time when bird gets hide.
        """
        self.blink = False
        self.blink_time = 5 # sec
        self.blink_gap = 0.10 # sec
        self.blink_start_time = None
        self.bird_hide = False
        self.bird_hidden_start_time = None

    def blink_start(self):
       if not self.blink:
           self.blink = True
           self.blink_start_time = time.time()

    def setSurface(self, surface):
        self.y_surface = surface

    def backMove_StopStart(self):
        if self.backMove:
            self.backMove = False
        else:
            self.propelSpeed = self.propelSpeed if self.propelSpeed < 0 else self.propelSpeed*-1
            self.backMove = True

    def forwardMove_StartStop(self):
        if self.forwardMove:
            self.forwardMove = False
        else:
            self.propelSpeed = self.propelSpeed if self.propelSpeed > 0 else self.propelSpeed*-1
            self.forwardMove = True

    def show(self):
        # blink effect system start.
        # this code will generate a blink effect.
        if self.blink:
            now_time = time.time()
            if (now_time-self.blink_start_time) <= self.blink_time:
                if self.bird_hidden_start_time is None:
                    self.bird_hidden_start_time = time.time()
                    self.bird_hide = True
                now_time = time.time()
                if self.bird_hide and (now_time-self.bird_hidden_start_time) >= self.blink_gap:
                    self.bird_hidden_start_time = time.time()
                    self.bird_hide = False
                if not self.bird_hide and (now_time-self.bird_hidden_start_time) >= self.blink_gap:
                    self.bird_hidden_start_time = time.time()
                    self.bird_hide = True
            else:
                self.bird_hide = False
                self.blink = False
                self.blink_start_time = None
                self.bird_hidden_start_time = None

        if not self.bird_hide:
            self.screen.blit(self.birds[self.counter], (self.x, self.y))

        if self.counter < self.totalBirds-1:
            self.counter += 1
        else:
            self.counter = 0
        if self.backMove or self.forwardMove:
            if self.propelSpeed > 0:
                if self.x+self.width < self.AREA_X+self.AREA_WIDTH:
                    self.x += self.propelSpeed
                else:
                    self.x = self.AREA_X+self.AREA_WIDTH-self.width
            if self.propelSpeed < 0:
                if self.x > self.AREA_X:
                    self.x += self.propelSpeed
                else:
                    self.x = self.AREA_X

        if self.pushUpActive and self.y <= self.AREA_Y:
            self.declineSpeed = 0
            self.y = self.AREA_Y
        else:
            self.declineSpeed += self.gravity
            if self.pushUpActive:
                self.declineSpeed = -10
            self.y += self.declineSpeed
        if self.y <= self.AREA_Y:
            self.y = self.AREA_Y
            self.declineSpeed = 0

    def pushUp(self):
        # if not self.gotHit:
        #     self.declineSpeed = -10
        if self.pushUpActive:
            self.pushUpActive = False
        else:
            self.play_sound(SOUND_WING)
            self.pushUpActive = True

class PolePair:
    def __init__(self, screen, poles, x, gap_start_end):
        self.screen = screen
        self.gapStartY, self.gapStarty1 = gap_start_end
        self.gapHeight = self.gapStarty1 - self.gapStartY
        self.TOP_POLE_IMG, self.BOTTOM_POLE_IMG = poles
        self.x = x
        self.POLE_WIDTH = self.TOP_POLE_IMG.get_width()
        self.POLE_HEIGHT = self.TOP_POLE_IMG.get_height()
        self.top_pole_y = self.gapStartY - self.POLE_HEIGHT
        self.bottom_pole_y = self.gapStarty1

    def show(self):
        self.screen.blit(self.TOP_POLE_IMG, [self.x, self.top_pole_y])
        self.screen.blit(self.BOTTOM_POLE_IMG, [self.x, self.bottom_pole_y])

class PolePair_Manager(SoundManager):
    def __init__(self, screen, bird, poles_img, scroll_speed, area, poles_distance, gap_height):
        self.poles = []
        self.bird = bird
        self.screen = screen
        self.POLE_IMGS = poles_img
        self.TOP_POLE_MASK = pygame.mask.from_surface(self.POLE_IMGS[0])
        self.BOTTOM_POLE_MASK = pygame.mask.from_surface(self.POLE_IMGS[1])
        self.MIN_GAP_HEIGHT, self.MAX_GAP_HEIGHT = gap_height
        self.pole_distance = poles_distance
        self.AREA_X, self.AREA_Y, self.AREA_WIDTH, self.AREA_HEIGHT = area
        self.scroll_speed = scroll_speed
        self.poles.insert(0, {"pole_pair": PolePair(self.screen, self.POLE_IMGS, self.AREA_X+self.AREA_WIDTH+5, self.get_gap_position()),
                              "score_counted": False, "collided": False})

        # creating variable to avoid continuous collision sound playing.
        self.top_continue_collision_check = True
        self.bottom_continue_collision_check = True
        self.score = 0

        # creating an variable to store how many pole_pair in poles list.
        self.lenth_poles_list = 1

        # creating an object of score manager.
        self.score_manager = Score()

        # creating an object of life pils.
        self.LifePil = LifePil(self.screen, "assets\\LifePils", 200, 0, (0, 0, window_x, window_y), 1.5)
        self.LifePil.expired = True
        self.LifePil_DropCounter = 0

    def manage(self):
        for pole_pair_dict in self.poles:
            pole_pair = pole_pair_dict["pole_pair"]
            pole_pair.x -= self.scroll_speed
            pole_pair.show()
            self.check_collision(pole_pair_dict)
            self.score_counter(pole_pair_dict)

        pole_pair = self.poles[0]['pole_pair']
        if pole_pair.x+pole_pair.POLE_WIDTH < self.AREA_X+self.AREA_WIDTH:
            pole_pair = PolePair(self.screen, self.POLE_IMGS, pole_pair.x+pole_pair.POLE_WIDTH+self.pole_distance, self.get_gap_position())
            self.poles.insert(0, {"pole_pair": pole_pair, "score_counted": False, "collided": False})
            self.poles[0]["pole_pair"].show()
            self.lenth_poles_list += 1

        last_index = self.lenth_poles_list-1
        if self.poles[last_index]["pole_pair"].x+self.poles[last_index]["pole_pair"].POLE_WIDTH < self.AREA_X:
            self.poles.pop()
            self.lenth_poles_list -= 1

        self.LifePil.show(self.bird.birds_mask[self.bird.counter], self.bird.x, self.bird.y)

        if self.LifePil_DropCounter >= 35:
            self.LifePil.reset_animation()
            self.LifePil.set_pos_x(200, window_x-100)
            self.LifePil_DropCounter = 0
            self.LifePil.LifePilUsed = False

    def get_gap_position(self):
        gap_height = random.randint(self.MIN_GAP_HEIGHT, self.MAX_GAP_HEIGHT)
        y = random.randint(self.AREA_Y + 50, (self.AREA_Y + self.AREA_HEIGHT) - (gap_height + 50))
        return y, y+gap_height

    def score_counter(self, pole_pair_dict):
        if self.bird.blink:
            if not pole_pair_dict["score_counted"]:
                pole_pair = pole_pair_dict["pole_pair"]
                if self.bird.x > pole_pair.x + pole_pair.POLE_WIDTH:
                    pole_pair_dict["score_counted"] = True
        else:
            if not pole_pair_dict["score_counted"]:
                pole_pair = pole_pair_dict["pole_pair"]
                if self.bird.x > pole_pair.x+pole_pair.POLE_WIDTH:
                    self.score += 1
                    self.LifePil_DropCounter += 1
                    self.score_manager.update_score(self.score)
                    self.play_sound(SOUND_POINT)
                    pole_pair_dict["score_counted"] = True

    def check_collision(self, pole_pair_dict):
        bird_mask = self.bird.birds_mask[self.bird.counter]
        pole_pair = pole_pair_dict["pole_pair"]

        # checking collision with top pole.
        if collision(self.TOP_POLE_MASK, bird_mask, pole_pair.x, pole_pair.top_pole_y, self.bird.x, self.bird.y):
            if not self.bird.blink:
                if not pole_pair_dict['collided']:
                    self.life.set_value(self.life.value-5)
                    self.play_sound(SOUND_HIT)
                    pole_pair_dict['collided'] = True
                    if not self.bird.blink:
                        self.bird.blink_start()

        # checking collision with bottom pole.
        if collision(self.BOTTOM_POLE_MASK, bird_mask, pole_pair.x, pole_pair.bottom_pole_y, self.bird.x, self.bird.y):
            if not self.bird.blink:
                if not pole_pair_dict['collided']:
                    self.life.set_value(self.life.value - 5)
                    self.play_sound(SOUND_HIT)
                    pole_pair_dict['collided'] = True
                    if not self.bird.blink:
                        self.bird.blink_start()

class ScrollingBackground:
    def __init__(self, screen, bird, ground, bottom_pole, top_pole, area):
        """
        :param ground: This is image of ground which will scroll continouslly at the bottom side.
        :param screen: This variable will store the object of screen on which will will put every thing.
        :param bottom_pole: Image of top pole ( piller )
        :param top_pole: Image of bottom ( pole )
        :param area: area in which this scroll background class will do every thing. actually this tuple like
                     (x, y, width, height) -> for this game it will look like (0, 0, 1200, 637)
        :param bird: the object of flying bird, i am storing the object of flying bird so that i could check
                        collided with pole or note. alo i will pass this object in pole PolePair_Manager and
                        PolePair_Manager manager will check bird collide with pole or not using this object.
        """
        self.bird = bird
        self.SCREEN = screen
        self.WIN_X, self.WIN_Y, self.WIN_WIDTH, self.WIN_HEIGHT = area # unpacking area tuple at here.
        self.GROUND_IMG = pygame.image.load(ground).convert_alpha() # loading ground image.
        self.ground_mask = pygame.mask.from_surface(self.GROUND_IMG)
        self.GROUND_WIDTH = self.GROUND_IMG.get_width() # getting ground image width.
        self.GROUND_HEIGHT = self.GROUND_IMG.get_height() # getting ground height.
        self.GROUND_Y = self.WIN_Y + self.WIN_HEIGHT - self.GROUND_IMG.get_height() # fixing ground y position.
        self.ground_x = self.WIN_X  # starting position of ground from where it will start to scroll to left side.
        self.BOTTOM_POLE = pygame.image.load(bottom_pole).convert_alpha() # loading bottom pole image.
        self.TOP_POLE = pygame.image.load(top_pole).convert_alpha() # loading top pole image.
        self.scrollSpeed = 5    # deciding the speed of scroll we can -- and ++ while playing game but user can't.
        self.second_ground_x = self.ground_x+self.GROUND_WIDTH
        """
        About second_ground_x variable.
        :param self.second_ground_x: i declared this variable because the lenth of ground image is equal to
                                     screen width so that i have to use same ground image for two time
                                     1st i will put ground image starting position of screen according to X coordinate
                                     and 2nd copy of same image "Starting_point_of_screen + ground_width" 
        """

        self.PolePair_Manager = PolePair_Manager(self.SCREEN, self.bird, (self.TOP_POLE, self. BOTTOM_POLE), self.scrollSpeed,
                                                 (self.WIN_X, self.WIN_Y, self.WIN_WIDTH, self.WIN_HEIGHT-self.GROUND_HEIGHT),
                                                 180, (150, 180))

    def set_Bird(self, bird):
        self.bird = bird
        self.PolePair_Manager.bird = bird

    def getGround_Y(self):
        return self.GROUND_Y

    def show(self):
         """
            This section controlling the poles of game which scroll's with ground of the game.
        """

        self.PolePair_Manager.manage()

        """
            This section of code controlling the ground of game which continous scroll while playing game at the
            bottom side.
        """
        self.SCREEN.blit(self.GROUND_IMG, [self.ground_x, self.GROUND_Y])
        self.SCREEN.blit(self.GROUND_IMG, [self.second_ground_x, self.GROUND_Y])
        self.ground_x -= self.scrollSpeed
        self.second_ground_x -= self.scrollSpeed
        if self.ground_x+self.GROUND_WIDTH < self.WIN_X:
            self.ground_x = self.second_ground_x + self.GROUND_WIDTH
        if self.second_ground_x + self.GROUND_WIDTH < self.WIN_X:
            self.second_ground_x = self.ground_x+self.GROUND_WIDTH

        """
        here checking the bird is collided with ground or not with the help of ground mask,
        i am applying perfect collision system i order to check collision with ground.
        """
        bird_mask = self.bird.birds_mask[self.bird.counter]
        if collision(bird_mask, self.ground_mask, self.bird.x, self.bird.y, self.ground_x, self.GROUND_Y) or \
            collision(bird_mask, self.ground_mask, self.bird.x, self.bird.y, self.second_ground_x, self.GROUND_Y):
            self.bird.blink_start()
            """
            Here system of countinious power loosing system.
            """
            self.PolePair_Manager.life.set_value(self.PolePair_Manager.life.value - 0.5)


"""
initialisation of game window.
"""
pygame.init()
infos = pygame.display.Info()
# global variable for window size window_x for width and window_y for height.
window_x = 1200
window_y = 600
environ['SDL_VIDEO_WINDOW_POS'] = str(int(infos.current_w / 2)-(window_x//2)) + ',' + str(int(infos.current_h / 2)-(window_y//2))
pygame.display.set_caption("Flappy Bird")
GameWindow = pygame.display.set_mode((window_x, window_y))

"""
Here I am defining all global variable and paths of all images which i will use in this game
"""
IMG_BACKGROUND = "assets\\background\\background_img.png"
IMG_TOP_POLE = "assets\\background\\top_pole.png"
IMG_BOTTOM_POLE = "assets\\background\\bottom_pole.png"
IMG_GROUND = "assets\\background\\scroll_ground.png"
IMG_SNOW_1 = "assets\\background\\snow_1.png"
IMG_SNOW_2 = "assets\\background\\snow_2.png"
IMG_MSG_BOX = "assets\\msg_box\\msg_box.png"
ICON_CROSS_ORANGE = "assets\\icon\\orange_close.png"
ICON_CROSS_WHITE = "assets\\icon\\white_close.png"
IMG_BOX_BOX_300x92 = "assets\\background\\black_box.png"
IMG_MULTICOLOR_BOX_300x92 = "assets\\background\\multi_color_box.png"
IMG_DARK_BLACK_COVER = "assets\\background\\black_cover_2.png"

# Images of Game Menu - Theme 1
IMG_GMENU_BACKGROUND_1_T1 = "assets\\GameMenu\\background\\Theme_1\\Menu_Background1.png"
IMG_GMENU_BACKGROUND_2_T1 = "assets\\GameMenu\\background\\Theme_1\\Menu_Background2.png"
IMG_GMENU_BACKGROUND_3_T1 = "assets\\GameMenu\\background\\Theme_1\\Menu_Background3.png"

# Image of Game Menu - Theme 2
IMG_GMENU_BACKGROUND_1_T2 = "assets\\GameMenu\\background\\Theme_2\\Menu_Background1.jpg"

IMG_MENU = "assets\\GameMenu\\menu\\menu.png"
IMG_LOGO = "assets\\GameMenu\\menu\\logo.png"

# Loading a image of 1 pixel size to check mouse collision.
PYIMG_MOUSE_COLLSISION_POINT_MASK = pygame.mask.from_surface(pygame.image.load("assets\\point\\point.png"))

PYIMG_BLACK_COVER = pygame.image.load("assets\\background\\black_cover.png").convert_alpha()
PYIMG_MSG_BOX = pygame.image.load(IMG_MSG_BOX).convert_alpha()

DIR_BIRD = "assets\\bird"
clock = pygame.time.Clock()  # to control the speed of game.

"""
Here i am defining dir paths where i will store file and create temp files.
"""
DIR_TEMP_DATA = "data\\temp_files"
FILE_SCORE = "data\\score.txt"
FILE_SETTING = "data\\setting.txt"

# Font files
Font_DroidSansMono = "assets\\font\\DroidSansMono.ttf"
Font_Quicksand_Regular = "assets\\font\\Quicksand-Regular.otf"
Font_sofiapro_light = "assets\\font\\sofiapro-light.otf"
Font_Kollektif = "assets\\font\\Kollektif.ttf"
Font_Quicksand_Bold = "assets\\font\\Quicksand-Bold.otf"

# Game data file
GameDataFile = "record.txt"
ScoreFile = "data\\score.txt"

# rbg color
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
PURPLE_COLOR = (146, 44, 110)
LIGHT_PURPLE = (208, 26, 144)
LIGHT_BLUE_COLOR = (0, 133, 255)
"""
creating function to put text on screen.
"""

"""
Info about author and game.
"""

AuthorName = "Harvindar Singh"
BrandName = "Brightgoal"
GameName = "Flappy Bird"


class Score:
    def __init__(self):
        self.score = 0
        self.get_score()

    def get_score(self):
        global ScoreFile
        try:
            file = open(ScoreFile, "rb");
            data = pickle.load(file)
            self.score = data.score
            return self.score
        except:
            self.score = 0
            return self.score

    def update_score(self, score):
        global ScoreFile
        try:
            if score > self.get_score():
                file = open(ScoreFile, "wb")
                self.score = score
                pickle.dump(self, file)
                file.close()
                return True
            return False
        except:
            return False

class Setting:
    def __init__(self):
        self.get()

    def update(self):
        try:
            fp = open(FILE_SETTING, "wb")
        except:
            return 404
        pickle.dump(self, fp)
        fp.close()

    def get(self):
        try:
            fp = open(FILE_SETTING, "rb")
            data = pickle.load(fp)
            fp.close()
        except:
            self.background_music_volume = 50
            self.sound_effact_volume = 50
            self.theme = 1
            self.game_sound = True
            SoundManager.settingData = self
            return

        self.background_music_volume = data.background_music_volume
        self.sound_effact_volume = data.sound_effact_volume
        self.theme = data.theme
        self.game_sound = data.game_sound
        SoundManager.settingData = self


class RadioButton(SoundManager):
    Groups = {}

    def __init__(self, screen, text, text_size, radio_img, active_img, hover_img, x, y, group=None, active_state=False,
                 text_color=WHITE_COLOR, font_style=Font_Quicksand_Regular):
        self.screen = screen

        # loading image
        self.radio_img = pygame.image.load(radio_img).convert_alpha()
        self.active_img = pygame.image.load(active_img).convert_alpha()
        self.hover_img = pygame.image.load(hover_img).convert_alpha()

        # creating button mask in order to check collision of mouse with button.
        self.button_mask = pygame.mask.from_surface(self.active_img)

        # position of radio button.
        self.x = x
        self.y = y

        # creating text image.
        self.row_text = text
        self.text = out_text_file(screen, text, text_size, 0, 0, text_color, font_style, True)

        # deciding position of text.
        self.text_x = self.x + self.active_img.get_width() + 10
        self.text_y = int((self.y + (self.active_img.get_height()/2)) - (text_size/2))-2

        # creating variable to state button state.
        self.active_state = active_state

        # creating group of radio buttons.
        self.group = group
        if group is not None:
            if group in self.Groups:
                self.Groups[group].append(self)
            else:
                self.Groups[group] = [self]

    def place_config(self, event):
        if self.active_state:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.y += 1
                    self.text_y += 1
                if event.key == pygame.K_UP:
                    self.y -= 1
                    self.text_y -= 1
                if event.key == pygame.K_LEFT:
                    self.x -= 1
                    self.text_x -= 1
                if event.key == pygame.K_RIGHT:
                    self.x += 1
                    self.text_x += 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Button :{self.row_text}, X :{self.x}, Y:{self.y}, Group:{self.group}")

    def collide(self, x, y):
        global PYIMG_MOUSE_COLLSISION_POINT_MASK
        if collision(PYIMG_MOUSE_COLLSISION_POINT_MASK, self.button_mask, x, y, self.x, self.y):
            return True
        else:
            return False

    def place(self, event=None):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.group is not None and event is not None:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.collide(mouse_x, mouse_y):
                    self.play_sound(SOUND_BUTTON_CLICK)
                    if not self.active_state:
                        for button in self.Groups[self.group]:
                            try:
                                button.active_state = False
                            except:
                                pass
                        self.active_state = True
                        return True

        if event is None:
            self.screen.blit(self.text, (self.text_x, self.text_y))
            if self.collide(mouse_x, mouse_y) and not self.active_state:
                self.screen.blit(self.hover_img, (self.x, self.y))
            elif self.active_state:
                self.screen.blit(self.active_img, (self.x, self.y))
            else:
                self.screen.blit(self.radio_img, (self.x, self.y))
        return False


class Button(SoundManager):
    def __init__(self, surface, image, hover_img, x, y, caption_text='', press_effact=False, button_text=None,
                 button_text_size=28, button_text_color=(255, 255, 255), text_file=Font_Kollektif,
                 list_menu=None, command=None, perfect_collision_check=True):

        self.linked_list = list_menu
        self.surface = surface
        self.command = command
        self.caption = caption_text
        self.press_effact = press_effact
        self.perfect_collision_check = perfect_collision_check
        if type(image) != str:
            self.image = image
        else:
            self.image = pygame.image.load(image).convert_alpha()
            self.image_mask = pygame.mask.from_surface(self.image)
            self.aspect_ration_x = self.image.get_width() / self.image.get_height()
        if type(hover_img) != str:
            self.hover_img = self.image
        else:
            self.hover_img = pygame.image.load(hover_img).convert_alpha()
        self.button_text = button_text
        self.button_text_size = button_text_size
        self.x = x
        self.y = y
        self.x1 = x+self.image.get_width()
        self.y1 = y+self.image.get_height()

        if press_effact:
            img = pygame.transform.scale(self.hover_img, ((self.hover_img.get_width()-4), (self.hover_img.get_height()-4))).convert_alpha()
            self.hover_img = img
        if button_text != None and type(button_text) == str:
            self.button_text_img = out_text_file(surface, button_text, button_text_size, 0, 0, button_text_color, text_file, True)
            self.button_text_x = (self.x+(self.image.get_width()/2))-(self.button_text_img.get_width()/2)
            self.button_text_y = (self.y+(self.image.get_height()/2))-(self.button_text_img.get_height()/2)

    def config_Place(self, event=None):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.surface.blit(self.image, (mouse_x, mouse_y))
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("MOUSE POS : ", event.pos,
                      ", Width : ", self.image.get_width(),
                      ", Height : ", self.image.get_height(),
                      ", Object_x : ", self.x,
                      ", Object_y : ", self.y)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    self.y -= 1
                if event.key == pygame.K_d:
                    self.y += 1
                if event.key == pygame.K_l:
                    self.x -= 1
                if event.key == pygame.K_r:
                    self.x += 1
                if event.key == pygame.K_DOWN:
                    img_height = self.image.get_height() - 5
                    self.image = pygame.transform.scale(self.hover_img, (int(self.aspect_ration_x*img_height),
                                                        img_height))
                if event.key == pygame.K_UP:
                    img_height = self.image.get_height() + 5
                    self.image = pygame.transform.scale(self.hover_img, (int(self.aspect_ration_x * img_height),
                                                        img_height))
        except:
            pass

    def collide(self, x, y, clicked=False):
        global PYIMG_MOUSE_COLLSISION_POINT_MASK
        if self.perfect_collision_check:
            if collision(PYIMG_MOUSE_COLLSISION_POINT_MASK, self.image_mask, x, y, self.x, self.y):
                if clicked:
                    self.play_sound(SOUND_BUTTON_CLICK)
                return True
            else:
                return False
        else:
            return self.rect_collision_check(x, y, clicked)

    def rect_collision_check(self, x, y, clicked=False):
        if (x > self.x) and (x < self.x1) and (y > self.y) and (y < self.y1):
            if clicked:
                self.play_sound(SOUND_BUTTON_CLICK)
            return True
        else:
            return False

    def config(self, config_dict):
        if type(config_dict) != dict:
            return
        if 'position' in config_dict:
            pos = config_dict['position']
            if type(pos) == list and len(pos) == 2:
                self.x, self.y = pos
            else:
                return

    def place(self, events=None):
        global Mouse_x
        global Mouse_y
        global event
        Mouse_x, Mouse_y = pygame.mouse.get_pos()
        #     if events != None:
        # if type(self.linked_list) == List_menu:
        #         for event in events:
        #             if event.type == pygame.MOUSEBUTTONDOWN:
        #                 if event.button == 1:
        #                     mouse_x, mouse_y = event.pos
        #                     if self.collide(mouse_x, mouse_y):
        #                         if self.linked_list.list_state:
        #                             self.linked_list.list_state = False
        #                         else:
        #                             self.linked_list.list_state = True
        if self.collide(Mouse_x, Mouse_y):
            if self.press_effact:
                self.surface.blit(self.hover_img, [self.x+2, self.y+2])
            else:
                self.surface.blit(self.hover_img, [self.x, self.y])
            if len(self.caption) != 0:
                caption(self.caption, self.x1+2, self.y-16)
        else:
            self.surface.blit(self.image, [self.x, self.y])
        if self.button_text != None and type(self.button_text) == str:
            self.surface.blit(self.button_text_img, [self.button_text_x, self.button_text_y])


class Scroll_Button:
    def __init__(self,surface, x, x1, y, bar_thickness, pointer_img, pointer_hover_img = None, zero_value_pinter_img = None,
                 zero_value_pointer_hover_img = None, defult_value = None, text_color=WHITE_COLOR, filled_bar_color=LIGHT_PURPLE,
                 non_filled_bar_color=WHITE_COLOR):

        self.surface = surface
        self.x = x
        self.x1 = x1
        self.y = y
        self.text_color = text_color
        self.filled_bar_color = filled_bar_color
        self.non_filled_bar_color = non_filled_bar_color
        self.thickness = bar_thickness
        self.pointer_img = pointer_img
        self.pointer_hover_img = pointer_hover_img if pointer_hover_img!=None else self.pointer_img
        self.zero_value_pointer_img = zero_value_pinter_img if zero_value_pinter_img!=None else self.pointer_img
        self.zero_value_pointer_hover_img = zero_value_pointer_hover_img if zero_value_pinter_img!=None and zero_value_pointer_hover_img!=None else self.zero_value_pointer_img if zero_value_pinter_img!=None else self.pointer_hover_img
        self.pointer_img = pygame.image.load(self.pointer_img).convert_alpha()
        self.pointer_img_mask = pygame.mask.from_surface(self.pointer_img)
        self.pointer_hover_img = pygame.image.load(self.pointer_hover_img).convert_alpha()
        self.zero_value_pointer_img = pygame.image.load(self.zero_value_pointer_img).convert_alpha()
        self.zero_value_pointer_hover_img = pygame.image.load(self.zero_value_pointer_hover_img).convert_alpha()
        self.value = float(0)
        self.pointer_width = self.pointer_img.get_width()
        self.pointer_height = self.pointer_img.get_height()
        self.step_value = 100/(((self.x1-self.x)+2)-self.pointer_width)
        self.pointer_x = self.x-1
        if defult_value != None:
            self.pointer_x = self.pointer_x+int(defult_value/self.step_value)
            self.value = defult_value
        self.pointer_y = (self.y + int(self.thickness/2))-int(self.pointer_height/2)
        self.move_pointer = False
        self.pointer_mouse_dis = 0
        self.font_size = self.thickness+15
        self.persentage_y = (self.y+(self.thickness/2))-(self.font_size/2+3)

    def collide(self, x, y):
        global PYIMG_MOUSE_COLLSISION_POINT_MASK
        if collision(PYIMG_MOUSE_COLLSISION_POINT_MASK, self.pointer_img_mask, x, y, self.pointer_x, self.pointer_y):
            return True
        else:
            return False

    def config_value(self, persentage):
        self.pointer_x = (self.x-1) + (int(persentage / self.step_value))
        self.value = persentage

    def place(self, events=None):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if events != None:
            if events.type == pygame.MOUSEBUTTONDOWN:
                if events.button == 1:
                    mouse_x, mouse_y = events.pos
                    if self.collide(mouse_x, mouse_y):
                        self.pointer_mouse_dis = mouse_x - self.pointer_x
                        self.move_pointer = True
            if events.type == pygame.MOUSEBUTTONUP:
                if events.button == 1:
                    self.move_pointer = False
        if self.move_pointer:
            if mouse_x-self.pointer_mouse_dis >= self.x and mouse_x-self.pointer_mouse_dis <= self.x1-self.pointer_width:
                self.pointer_x = mouse_x-self.pointer_mouse_dis
            if mouse_x-self.pointer_mouse_dis < self.x:
                self.pointer_x = self.x-1
            if mouse_x-self.pointer_mouse_dis > self.x1-self.pointer_width:
                self.pointer_x = self.x1-self.pointer_width+1
            self.value = (self.pointer_x - (self.x-1))*self.step_value
            if events == None:
                custom_out_text(self.surface, str(int(self.value)) + '%', self.x1 + 15, self.x1 + 45, self.persentage_y,
                                self.text_color, self.font_size, Font_Kollektif)

        if events == None:
            pygame.draw.rect(self.surface, self.non_filled_bar_color,
                             [self.x, self.y, self.x1 - self.x, self.thickness])
            pygame.draw.rect(self.surface, self.filled_bar_color, [self.x, self.y, self.pointer_x-self.x+2, self.thickness])

            if self.value <= 0:
                if self.move_pointer or self.collide(mouse_x, mouse_y):
                    self.surface.blit(self.zero_value_pointer_hover_img, [self.pointer_x, self.pointer_y])
                else:
                    self.surface.blit(self.zero_value_pointer_img, [self.pointer_x, self.pointer_y])
            else:
                if self.move_pointer or self.collide(mouse_x, mouse_y):
                    self.surface.blit(self.pointer_hover_img, [self.pointer_x, self.pointer_y])
                else:
                    self.surface.blit(self.pointer_img, [self.pointer_x, self.pointer_y])

class LifePil:
    def __init__(self, surface, sequence_images_dir, x, y, area, drop_speed=15):
        self.index = 0
        self.screen = surface
        self.WIN_X, self.WIN_Y, self.WIN_WIDTH, self.WIN_HEIGHT = area
        self.drop_speed = drop_speed
        self.animation = SequentialAnimation(surface, sequence_images_dir, x, y, self.WIN_X+self.WIN_WIDTH,
                                             self.WIN_Y+self.WIN_HEIGHT, create_mask=True)
        self.expired = False
        self.LifePilUsed = False

    def show(self, object_mask, x, y):
        if self.expired:
            return False
        else:
            if self.animation.collide(object_mask, x, y):
                self.LifePilUsed = True
                return False
            self.animation.show()
            if self.animation.y < self.WIN_Y+self.WIN_HEIGHT:
                self.animation.y += self.drop_speed
            elif not self.expired:
                self.expired = True

    def set_pos_x(self, point_1, point_2):
        self.animation.x = random.randint(point_1, point_2)

    def reset_animation(self):
        self.expired = False
        self.animation.y = 0

class Message:
    def __init__(self, surface, rect, message='', text_size = 17, text_color = (255, 255, 255), text_align = 'center', font_file = Font_sofiapro_light):
        global GameWindow
        self.message = message
        self.message_area = rect
        self.text_size = text_size
        self.color = text_color
        self.text_align = text_align
        self.message_status = False
        self.surface = surface
        self.message_list_img = []
        self.message_starting_y_point = 0
        if type(rect) == list or type(rect) == tuple:
            x, y, x1, y1 = rect
        else:
            return
        if len(message) == 0:
            return
        self.center_x = int(((x1 - x)/2) + x)
        message_list = message.split(',')
        rect_width = x1 - x
        rect_height = y1-y
        max_width_line = 0

        # define flags
        text_size_adjustment_flag = False
        while True:
            for e in message_list:
                img = out_text_file(surface, e, self.text_size, 0, 0, self.color, font_file, True)
                img = img.convert_alpha()
                if img.get_width() > rect_width:
                    text_size_adjustment_flag = True
                    break
                self.message_list_img.append(img)
            else:
                text_size_adjustment_flag = False
            if text_size_adjustment_flag:
                text_size_adjustment_flag = False
                max_width_line = 0
                self.text_size -= 1
                text_size -= 1
                self.message_list_img  = []
                if self.text_size < 8:
                    return
                continue
            # for e in message_list:
            #     img = out_text_file(surface, e, self.text_size, 0, 0, self.color, font_file, True)
            #     if img.get_width() > max_width_line:
            #         max_width_line = img.get_width()
            #     self.message_list_img.append(img)
            # if max_width_line > rect_width:
            #     max_width_line = 0
            #     self.text_size -= 1
            #     text_size -= 1
            #     self.message_list_img  = []
            #     if self.text_size < 8:
            #         return
            #     continue
            total_height = self.message_list_img[0].get_height()+1
            total_height = total_height*len(self.message_list_img)
            if total_height > rect_height:
                text_size -= 1
                self.text_size -= 1
                self.message_list_img = []
                if self.text_size < 8:
                    return
                continue
            else:
                break
        message_list_lenth = len(self.message_list_img)
        center_y = y + ((y1 - y)/2)
        if message_list_lenth % 2 == 0:
            starting_pos = (center_y - 2)
            half_msg = int((message_list_lenth) / 2)
        else:
            starting_pos = center_y - int(self.message_list_img[0].get_height()/2)
            half_msg = int((message_list_lenth-1)/2)
        line_height = self.message_list_img[0].get_height()
        while half_msg != 0:
            starting_pos -= line_height
            half_msg -= 1
        self.message_status = True
        self.message_starting_y_point = starting_pos