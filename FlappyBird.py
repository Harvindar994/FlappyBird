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