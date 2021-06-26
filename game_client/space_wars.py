#!/usr/bin/env python3
"""
Game name:		Space Wars (change to cooler name)
Author:			Dan Petersson
Github link:	https://github.com/DanPetersson/SpaceWars
Description:
---------------------------------------------------------
- Survive as long as possible as shoot as many aliens as possible to get good score
---------------------------------------------------------
Python:			3.8
PyGame:			1.9.6
Revision updates:
---------------------------------------------------------
Backlog_revision_history.txt
"""

from numpy.lib.index_tricks import fill_diagonal
import pandas as pd
import pygame
import random
import pickle
import numpy as np
import math
import os
import time
import sqlite3
from datetime import datetime
from high_scores import high_scores
import csv
import microgear.client as client
import logging
import time
import sqlite3
from datetime import datetime
from multiprocessing import Process, Lock, freeze_support
from multiprocessing.sharedctypes import Value, Array
import ctypes
#import space_wars_settings as sws

# initialize pygame
pygame.init()

# Initialize global fonts
font_huge	= pygame.font.Font('freesansbold.ttf', 128)
font_large	= pygame.font.Font('freesansbold.ttf', 64)
font_medium	= pygame.font.Font('freesansbold.ttf', 32)
font_small	= pygame.font.Font('freesansbold.ttf', 16)
font_tiny	= pygame.font.Font('freesansbold.ttf', 8)

# Initialize global Game Colors
black 			= (  0,   0,   0)
white 			= (255, 255, 255)

red 			= (200,   0,   0)
green 			= (  0, 200,   0)
blue 			= (  0,   0, 200)
yellow 			= (200, 200,   0)

light_red 		= (255,   0,   0)
Light_green 	= (  0, 255,   0)
light_blue 		= (  0,   0, 255)
light_yellow	= (255, 255,   0)


# ----------------------------
# 		Define Classes
# ----------------------------

class SpaceObject:

	def __init__(self, image, explosion_image, posX=0, posY=0, speedX = 0, speedY = 0, sizeX = 64, sizeY = 64,
					state = 'show', sound = ' ', hit_points = 1):
		#self.namme	= name
		self.image  = image
		self.explosion_image = explosion_image
		self.sizeX  = sizeX
		self.sizeY  = sizeY
		self.posX   = posX
		self.posY   = posY
		self.speedX = speedX
		self.speedY	= speedY
		self.state	= state		# 'hide', 'show'
		self.sound 	= sound
		self.explosion_counter = -1
		self.hit_points = hit_points

	def show(self):
		if self.state == 'show' and self.explosion_counter <= 0:
			screen.blit(self.image, (int(self.posX), int(self.posY)))
		elif self.explosion_counter > 0:
			screen.blit(self.explosion_image, (int(self.posX), int(self.posY)))

class SpaceShip(SpaceObject):

    # def __init__(self):
    #     super().__init__()

	def update_player_postion(self, screen_sizeX, screen_sizeY):

		# Update X position (update with min/max)
		self.posX += self.speedX
		if self.posX < 0:
			self.posX = 0
		elif self.posX > screen_sizeX-self.sizeX:
			self.posX = screen_sizeX-self.sizeX
		
		# Update Y position (update with min/max)
		self.posY += self.speedY
		if self.posY < 0:
			self.posY = 0
		elif self.posY > screen_sizeY-self.sizeY:
			self.posY = screen_sizeY-self.sizeY
		

class SpaceEnemy(SpaceObject):

	def update_enemy_position(self, screen_sizeX, screen_sizeY):

		# Update X position
		self.posX += self.speedX

		# Update Y position
		self.posY += self.speedY

class SpaceCoin(SpaceObject):

	def update_coin_position(self, screen_sizeX, screen_sizeY):

		# Update X position
		self.posX += self.speedX

		# Update Y position
		self.posY += self.speedY

class Bullet(SpaceObject):

	def update_bullet_position(self, screen_sizeX, screen_sizeY):

		# Update X position
		self.posX += self.speedX

		# Update Y position, and change state if outside screen
		self.posY += self.speedY
		if self.posY < -self.sizeY:
			self.state = 'hide'


	def fire_bullet(self, player):

		self.posX = player.posX + player.sizeX/2 - self.sizeX/2
		self.posY = player.posY
		self.sound.play()
		self.state = 'show'


class Button:

	def __init__(self, centerX, centerY, width, hight, text='', color=yellow, color_hoover=light_yellow,
		text_color=black, text_hoover=black, font=font_small):
		self.centerX 		= int(centerX)
		self.centerY		= int(centerY)
		self.width 			= int(width)
		self.hight 			= int(hight)
		self.X				= int(centerX - width/2)
		self.Y				= int(centerY - hight/2)

		self.text 			= text
		self.color 			= color
		self.color_hoover	= color_hoover
		self.text_color		= text_color
		self.text_hoover	= text_hoover
		self.font 			= font
		self.clicked		= False

	# internal only function ?
	def text_objects(text, font, color):
	    text_surface = font.render(text, True, color)
	    return text_surface, text_surface.get_rect()

	# internal only function ?
	def message_display_center(text, font, color, centerX, centerY):
	    text_surface, text_rectangle = text_objects(text, font, color)
	    text_rectangle.center = (centerX,centerY)
	    screen.blit(text_surface, text_rectangle)

	def show(self, mouse=(0,0)):
		if self.X < mouse[0] < self.X + self.width and self.Y < mouse[1] < self.Y + self.hight:
			pygame.draw.rect(screen, self.color_hoover, (self.X, self.Y, self.width, self.hight))
		else:
			pygame.draw.rect(screen, yellow, (self.X, self.Y, self.width, self.hight))
		message_display_center(self.text, self.font, black, self.centerX, self.centerY)

	def check_clicked(self, mouse, mouse_click):
		if self.X < mouse[0] < self.X + self.width and self.Y < mouse[1] < self.Y + self.hight and mouse_click[0] == 1:
			self.clicked = True
		else:
			self.clicked = False



# ----------------------------
# 		Define Procedures
# ----------------------------


def text_objects(text, font, color):
	# Mainly supporting for function message_dipslay
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()

def message_display_center(text, font, color, centerX, centerY):
    text_surface, text_rectangle = text_objects(text, font, color)
    text_rectangle.center = (centerX,centerY)
    screen.blit(text_surface, text_rectangle)

def message_display_left(text, font, color, leftX, centerY):
    text_surface, text_rectangle = text_objects(text, font, color)
    text_rectangle.midleft = (leftX, centerY)
    screen.blit(text_surface, text_rectangle)

def message_display_right(text, font, color, rightX, centerY):
    text_surface, text_rectangle = text_objects(text, font, color)
    text_rectangle.midright = (rightX, centerY)
    screen.blit(text_surface, text_rectangle)

def show_high_scores():

#	global db_connection

	high_scores_screen = True
	while high_scores_screen:

		screen.fill(background_color)
		screen.blit(background_image[0], (0,0))

		message_display_center('High Scores', font_large, yellow, int(screen_sizeX/2), int(screen_sizeY * 1/10))
		message_display_center('Press (D)elete or any other key to continue', font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *9/10))
		# print('game loop:', time.time())
		msg = msg_buffer.value
		top_5 = parse_message(msg)
		index = 0
		for entry in top_5:
			# name, score
			index += 1
			message_display_left(str(entry[1]), font_medium, yellow, int(screen_sizeX * 1/8), int(screen_sizeY *(2+index)/10))
			message_display_right(str(entry[0]), font_medium, yellow, int(screen_sizeX * 2/4), int(screen_sizeY *(2+index)/10))

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				# add even mouse click ?
				high_scores_screen = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_d:
					# Deletes high score db table and recreates empty one
					high_scores.high_scores_db_delete(db_connection)
					high_scores.high_scores_create_table(db_connection)
				else:
					high_scores_screen = False

		# Display intro screen
		pygame.display.update()


def menu():
	# into screen
	name_button_X = int(screen_sizeX*1/2)
	name_button_Y = 300
	name_text = ''
	name_button	= Button(name_button_X, name_button_Y, 130, 50, name_text)
	intro_screen = True
	while intro_screen:

		screen.fill(background_color)
		screen.blit(background_image[0], (0,0))

		message_display_center('SPACE WARS', font_large, yellow, int(screen_sizeX/2), int(screen_sizeY/3))
		message_display_center('New Game (Y/N)', font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *3/5))

		# get mouse position
		mouse = pygame.mouse.get_pos()
		mouse_click = pygame.mouse.get_pressed()

		# Define and draw buttons
		button_width 	= 130
		button_hight 	= 50

		# Define and draw "Name" Input Box
		name_button.show(pygame.mouse.get_pos())
		name_button.check_clicked(mouse, mouse_click)

		# Define and draw "Yes" button
		yes_button_X 	= int(screen_sizeX*1/4)
		yes_button_Y 	= 450
		yes_button 		= Button(yes_button_X, yes_button_Y, button_width, button_hight, 'Yes')
		yes_button.show(mouse)
		yes_button.check_clicked(mouse, mouse_click)

		# Define and draw "No" button
		no_button_X 	= int(screen_sizeX*2/4)
		no_button_Y 	= yes_button_Y
		no_button  		= Button(no_button_X,  no_button_Y,  button_width, button_hight, 'No')
		no_button.show(mouse)
		no_button.check_clicked(mouse, mouse_click)

		# Define and draw "High Scores" (hs) button
		hs_button_X 	= int(screen_sizeX*3/4)
		hs_button_Y 	= yes_button_Y
		hs_button  		= Button(hs_button_X,  hs_button_Y,  button_width, button_hight, 'High Scores')
		hs_button.show(mouse)
		hs_button.check_clicked(mouse, mouse_click)

		if yes_button.clicked:
			intro_screen = False
			quit_game = False
		if no_button.clicked:
			intro_screen = False
			quit_game = True

		if hs_button.clicked:
			show_high_scores()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				intro_screen = False
				quit_game = True

		# if 'Enter Name'
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_BACKSPACE:
					name_text = name_text[:-1]
				else:
					name_text += event.unicode
				global PLAYER_NAME 
				PLAYER_NAME = name_text
				name_button.text = name_text
				name_button.show(mouse)

		# Display intro screen
		pygame.display.update()

	return quit_game

def paused(screen_sizeX, screen_sizeY):

	largeText = pygame.font.SysFont("freesansbold",115)
	TextSurf, TextRect = text_objects("Paused", largeText)
	TextRect.center = ((screen_sizeX/2),(screen_sizeX/2))
	screen.blit(TextSurf, TextRect)

	pause = True
	while pause:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				# 'p' for unpause
				if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
					pause = False
		screen.blit(TextSurf, TextRect)
		pygame.display.update()



def enemy_respawn(enemy, level):
	enemy.explosion_counter = -1
	enemy.posX 	= random.randint(0, screen_sizeX - enemy.sizeX)
	enemy.posY 	= random.randint(-screen_sizeY, -100)
	if enemy.posX < screen_sizeX / 3:
		enemy.speedX = random.randint(0, 10) / 10 * enemy.speedY
	elif enemy.posX > screen_sizeX * 2 / 3:
		enemy.speedX = random.randint(-10, 0) / 10 * enemy.speedY
	else:
		enemy.speedX = random.randint(-5, 5) / 10 * enemy.speedY

#	enemy.speedY = level

def coin_respawn(coin, level):
	coin.explosion_counter = -1
	coin.posX 	= random.randint(0, screen_sizeX - coin.sizeX)
	coin.posY 	= random.randint(-screen_sizeY, -100)
	if coin.posX < screen_sizeX / 3:
		coin.speedX = random.randint(0, 10) / 10 * coin.speedY
	elif coin.posX > screen_sizeX * 2 / 3:
		coin.speedX = random.randint(-10, 0) / 10 * coin.speedY
	else:
		coin.speedX = random.randint(-5, 5) / 10 * coin.speedY

def is_collision(object1, object2):

	obj1_midX = object1.posX + object1.sizeX
	obj1_midY = object1.posY + object1.sizeY
	obj2_midX = object2.posX + object2.sizeX
	obj2_midY = object2.posY + object2.sizeY

	# think if I want to improve this...
	distance = math.sqrt(math.pow(obj1_midX-obj2_midX,2) + math.pow(obj1_midY-obj2_midY,2))
	collision_limit = (object1.sizeX + object1.sizeY + object2.sizeX + object2.sizeY) / 5

	return distance < collision_limit

def show_explosion(object, image):
	screen.blit(image, (int(object.posX), int(object.posY)))

    

def show_score(score, level, highest_score_1, highest_score_2, highest_score_3, screen_x, font_size = 16, x=10, y=10):
	score_font = pygame.font.Font('freesansbold.ttf', font_size)
	level_text = score_font.render("Level  : " + str(level), True, (255, 255, 0))
	score_text = score_font.render("Score : " + str(score), True, (255, 255, 0))
	highest_score_text_1 = score_font.render("1st : " + str(highest_score_1), True, (255, 255, 0))
	highest_score_text_2 = score_font.render("2nd : " + str(highest_score_2), True, (255, 255, 0))
	highest_score_text_3 = score_font.render("3rd : " + str(highest_score_3), True, (255, 255, 0))

	screen.blit(level_text, (x, y))
	screen.blit(score_text, (x, y + 5 + font_size))
	screen.blit(highest_score_text_1, (screen_x-150, y + 0))
	screen.blit(highest_score_text_2, (screen_x-157, y + 10 + font_size))
	screen.blit(highest_score_text_3, (screen_x-154, y + 35 + font_size))


def show_game_over(screen_sizeX, screen_sizeY, player_name, score, high_score_a, player_type):
    new_score = (score,PLAYER_NAME)
    if new_score in high_score_a:
        pass
    else:
        high_score_a.append(new_score)
        high_score_a.sort(reverse=True)
    highest_score_1 = high_score_a[0][1] + " - " + str(high_score_a[0][0])
    highest_score_2 = high_score_a[1][1] + " - " + str(high_score_a[1][0])
    highest_score_3 = high_score_a[2][1] + " - " + str(high_score_a[2][0])
    # Move enemies below screen (is there a better way?)
    for i in range(num_of_enemies):
        enemy[i].posY = screen_sizeY + 100
    # Display text and score
    message_display_center('GAME OVER', font_large, yellow, int(screen_sizeX/2), int(screen_sizeY * 2/10))
    message_display_center('Your Score : ' + str(score), font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *3/10))
    message_display_center('Your Style : ' + player_type, font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *4/10))
    message_display_center('1st : ' + str(highest_score_1), font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *5/10))
    message_display_center('2nd : ' + str(highest_score_2), font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *6/10))
    message_display_center('3rd : ' + str(highest_score_3), font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *7/10))
    message_display_center('Press any key to continue', font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *9/10))

# DATABASE = './gamedb.db'
# TEMP_FILE = './temp.pkl'

# initlize msg buffer (array of byte - size=100)
msg_buffer = Array('c', (" "*100).encode('utf-8'), lock=False)

def parse_message(msg):
	tokens = msg.decode('utf-8')[2:-1].split(',')
	highscores = [(int(tokens[i+1]), tokens[i]) for i in range(len(tokens)) if i%2==0]
	return highscores

def print_highscores(highscores):
    if highscores: 
        for s in highscores:
            print(f"{s[0]}: {s[1]} {s[2]}")
    else:
        print('no scores')

def callback_connect() :
    print ("Now I am connected with netpie")
    
def callback_message(topic, message) :
    print(topic, message)

def callback_error(msg) :
    print("error", msg)

def format_message(rs):
    return ','.join(map(lambda x: ','.join(map(str, x)),rs))


# Process 2
def highscore_subscriber(msg_buffer):

    def callback_connect():
        print ("Now I am connected with netpie")

    def callback_error(msg) :
        print("error", msg)

    def callback_message(topic, message) :
        # print(topic, message)
        msg_buffer.value = message.encode('utf-8')
    
    # NetPie client
    # key: sub-highscore
    appid = 'MookataGame'
    gearkey = 'Q1GXcLhGXDHKqLH'
    gearsecret = 'dojFgPxaY0yY901bwK4YmWx6V'

    client.create(gearkey,gearsecret,appid,{'debugmode': True})
    client.setalias("test-game-client")
    client.on_connect = callback_connect 
    client.on_message = callback_message
    client.on_error = callback_error
    client.subscribe("/highscore")
    client.connect(True)


#############################
#		Main Program		#
#############################
if __name__ == '__main__':
	
	p = Process(target=highscore_subscriber, args=(msg_buffer,))
	p.start()
	time.sleep(2)
	appid = 'MookataGame'
	gearkey = '5aTga8Ic047dpQI'
	gearsecret = 'icVIYaxXJp9ltF8XwMM5MAS3k'

	client.create(gearkey,gearsecret,appid,{'debugmode': True}) 
	client.setalias("highscore-pub")
	client.on_connect = callback_connect 
	client.on_message= callback_message 
	client.on_error = callback_error 
	client.connect(False)
	# # initialize pygame
	# pygame.init()

	# # Initialize fonts
	# font_huge	= pygame.font.Font('freesansbold.ttf', 128)
	# font_large	= pygame.font.Font('freesansbold.ttf', 64)
	# font_medium	= pygame.font.Font('freesansbold.ttf', 32)
	# font_small	= pygame.font.Font('freesansbold.ttf', 16)
	# font_tiny	= pygame.font.Font('freesansbold.ttf', 8)


	# Initialize Global CONSTANTS from space_wars_settings.py (sws)
	MUSIC 		= False 		#sws.MUSIC 		# True
	GAME_SPEED 	= 5 		#sws.GAME_SPEED 	# 1 to 5
	PLAYER_NAME	= 'PLAYER'		#sws.PLAYER_NAME	# 'DAN'


	# Initialize Global variables
	screen_sizeX = 800
	screen_sizeY = 600
	screen_size = (screen_sizeX, screen_sizeY)
	background_color = black
	# Initialize screen
	screen = pygame.display.set_mode((screen_sizeX, screen_sizeY))
	#screen = pygame.display.set_mode((screen_sizeX, screen_sizeY), flags=pygame.FULLSCREEN)


	# Get working directory and subdirectories
	dir_path = os.getcwd()
	images_path = os.path.join(dir_path, 'images')
	sounds_path = os.path.join(dir_path, 'sounds')


	# Initialize images
	icon_image			= pygame.image.load(os.path.join(images_path , 'icon_07.png'))
	player_image		= pygame.image.load(os.path.join(images_path, 'MilFal_03.png'))
	bullet_image		= pygame.image.load(os.path.join(images_path, 'bullet.png'))
	enemy_image	    	= [pygame.image.load(os.path.join(images_path, 'ufo_01.png')),
							pygame.image.load(os.path.join(images_path, 'ufo_02.png')),
							pygame.image.load(os.path.join(images_path, 'ufo_03.png')),
							pygame.image.load(os.path.join(images_path, 'ufo_04.png')),
							pygame.image.load(os.path.join(images_path, 'spaceship_03_usd.png')),
							pygame.image.load(os.path.join(images_path, 'spaceship_01_usd.png')),
							pygame.image.load(os.path.join(images_path, 'death_star_02.png')),
							pygame.image.load(os.path.join(images_path, 'death_star_03.png'))]
	explosion_image		= [pygame.image.load(os.path.join(images_path, 'explosion_01.png')),
							pygame.image.load(os.path.join(images_path, 'explosion_02.png'))]
	background_image	= [pygame.image.load(os.path.join(images_path, 'background_03.jpg')),
							pygame.image.load(os.path.join(images_path, 'background_03_usd.jpg'))]
	coin_image 			= pygame.image.load(os.path.join(images_path, 'dodgecoin.png'))
	background_image_hight = 600

	# Caption and Icon
	pygame.display.set_caption("Space Wars")
	pygame.display.set_icon(icon_image)

	# Initialize sounds
	bullet_sound		= pygame.mixer.Sound(os.path.join(sounds_path, 'laser.wav'))
	explosion_sound		= pygame.mixer.Sound(os.path.join(sounds_path, 'explosion.wav'))

	# Start backgound music
	if MUSIC:
		pygame.mixer.music.load(os.path.join(sounds_path, 'background.wav'))
		pygame.mixer.music.play(-1)

	# Initialize game speed settings
	frames_per_second = 20 + 10 * GAME_SPEED
	clock = pygame.time.Clock()

	# Initialize connection to high score database
	db_connection = high_scores.high_scores_connect_to_db('high_scores.db')
	high_scores.high_scores_create_table(db_connection)

	# Initialize settings
	player_maxSpeedX	= 3.5			# recommended: 3
	player_maxSpeedY	= 3.5			# recommended: 3
	enemy_maxSpeedX		= 2
	enemy_maxSpeedY		= 2
	bullet_speed		= 10
	session_high_score 	= 0

	# Player type dict
	seg_dict = { 0:'Hardcore achiever'
				,1:'Casual achiever'
				,2:'Hardcore killer'
				,3:'Casual killer'
				}

	# load minmax_scaler model and kmeans
	DIR_TRANSFORM_MODEL = './scaler_model.pkl'
	DIR_PREDICTION_MODEL = './kmeans_model.pkl'
	scaler_model = pickle.load(open(DIR_TRANSFORM_MODEL,'rb'))
	kmeans_model = pickle.load(open(DIR_PREDICTION_MODEL, 'rb'))

	# --------------------
	# Full Game Play Loop
	# --------------------
	
	csv_ls=[]
	quit_game = False
	game_round = 0

	while not quit_game:
		
		# Start manu
		quit_game = menu()

		# Game settings
		num_of_enemies	= 5				# recommended: 5
		num_of_coins	= 5
		level_change	= 1000			# recommended: 1000
		level_score_increase = 10
		level_enemy_increase = 5
		level_coin_increase = 10

		# initialize other variables / counters
		score 		 = 0
		level		 = 1
		level_iter	 = 0
		loop_iter	 = 0
		keyX_pressed = 0
		keyY_pressed = 0
		game_over 	 = False
		go_to_menu 	 = False
		not_sent_score = True
		backgound_Y_lower = 0
		backgound_Y_upper = backgound_Y_lower - background_image_hight
		upper_index = 0
		lower_index = 1


		# initialize player and bullet
		player = SpaceShip(player_image, explosion_image[0], screen_sizeX/2-32, screen_sizeY-100)
		bullet = Bullet(bullet_image, explosion_image[0], speedY = -bullet_speed, sound = bullet_sound, state = 'hide', sizeX = 32, sizeY = 32)
		
		# initialize enemies
		enemy = []
		enemy_image_index = 0
		for i in range(num_of_enemies):
			enemy.append(SpaceEnemy(enemy_image[enemy_image_index], explosion_image[1], speedY = level, hit_points = level))
			enemy_respawn(enemy[i], level)

		# initialize coins
		coin = []
		# coin_image_index = 0
		for i in range(num_of_coins):
			coin.append(SpaceCoin(coin_image, explosion_image[1], speedY = level, hit_points = level))
			coin_respawn(coin[i], level)

		# init high score process
		highest_score_from_df_1 = str()
		highest_score_from_df_2 = str()
		highest_score_from_df_3 = str()
		highest_score_from_df_4 = str()
		highest_score_from_df_5 = str()

		# --------------------
		# Main Game Play Loop
		# --------------------

		#initiate key focus metric
		
		bullet_count = 0
		coin_count = 0
		enemy_count = 0
		pos_x = 0
		pos_y = 0
		num_x = 0
		num_y = 0

		while not go_to_menu and not quit_game:
			# print('game loop:', time.time())
			msg = msg_buffer.value
			try:
				high_score_all = parse_message(msg)
			except:
				pass
			try:
				highest_score_from_df_1 = str(high_score_all[0][1]) + " " + str(high_score_all[0][0])
			except:
				highest_score_from_df_1 = str()
			try:
				highest_score_from_df_2 = str(high_score_all[1][1]) + " " + str(high_score_all[1][0])
			except:
				highest_score_from_df_2 = str()
			try:
				highest_score_from_df_3 = str(high_score_all[2][1]) + " " + str(high_score_all[2][0])
			except:
				highest_score_from_df_3 = str()


			# Fill screen and background image
			screen.fill(background_color)

			# Background images moving
			backgound_Y_lower += 1
			backgound_Y_upper += 1
			if backgound_Y_lower > screen_sizeY:
				backgound_Y_lower = backgound_Y_upper
				backgound_Y_upper = backgound_Y_lower - background_image_hight
				temp = upper_index
				upper_index = lower_index
				lower_index = temp
			screen.blit(background_image[upper_index], (0,backgound_Y_upper))
			screen.blit(background_image[lower_index], (0,backgound_Y_lower))

			# check if increase level
			level_iter += 1
			if level_iter > level_change and not game_over:
				level_iter = 0
				level += 1
				# increase number of enemies with higher speed
				enemy_image_index = (level -1) % len(enemy_image)
				for i in range(num_of_enemies, num_of_enemies+level_enemy_increase):
					enemy.append(SpaceEnemy(enemy_image[enemy_image_index], explosion_image[1], speedY = level, hit_points = level))
					enemy_respawn(enemy[i], level)
				num_of_enemies	+= level_enemy_increase

				for i in range(num_of_coins,num_of_coins+level_coin_increase):
					coin.append(SpaceCoin(coin_image, explosion_image[1], speedY = level, hit_points = level))
					coin_respawn(coin[i], level)
				num_of_coins += level_coin_increase

				# increase score when reaching new level
	#			score += level_score_increase

			# Check events and take action
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit_game = True

				# if key is pressed
				if event.type == pygame.KEYDOWN:

					# if Game Over and any key, go to menu
					if game_over:
						go_to_menu = True

					# 'p' or ESC' for pause
					elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
						paused(screen_sizeX, screen_sizeY)

					# 'arrow keys' for movement
					elif event.key == pygame.K_LEFT:
						player.speedX = -player_maxSpeedX
						keyX_pressed += 1
					elif event.key == pygame.K_RIGHT:
						player.speedX = player_maxSpeedX
						keyX_pressed += 1
					elif event.key == pygame.K_UP:
						player.speedY = -player_maxSpeedY
						keyY_pressed += 1
					elif event.key == pygame.K_DOWN:
						player.speedY = player_maxSpeedY
						keyY_pressed += 1

					# if space key, fire bullet
					elif (event.key == pygame.K_SPACE or event.key == pygame.K_a) and bullet.state == 'hide':
						bullet.fire_bullet(player)
						bullet_count +=1


				# if key is released, stop movement in a nice way
				if event.type == pygame.KEYUP:
					if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
						keyX_pressed -= 1
						if keyX_pressed == 0:
							player.speedX = 0
					if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
						keyY_pressed -= 1
						if keyY_pressed == 0:
							player.speedY = 0

			# Move player and check not out of screen
			player.update_player_postion(screen_sizeX, screen_sizeY)
			bullet.update_bullet_position(screen_sizeX, screen_sizeY)
			
			if game_over:
				
				# predict player type
				scaler_score = scaler_model.transform(np.array([enemy_count, coin_count]).reshape(1,-1))
				player_type = kmeans_model.predict(scaler_score)
				player_type = seg_dict[player_type[0]]

				player.explosion_counter = 0
				show_game_over(screen_sizeX, screen_sizeY, PLAYER_NAME, score, high_score_all, player_type)
				show_score(score, level, highest_score_from_df_1, highest_score_from_df_2, highest_score_from_df_3, screen_x = screen_sizeX)
				
				
				if not_sent_score:
					b = str(int(datetime.timestamp(now)))+","+PLAYER_NAME+","+str(score)+","+str(pos_x/num_x)+","+str(pos_y/num_y)+","+str(enemy_count)+","+str(coin_count)+","+str(bullet_count)+","+str(bullet_count-enemy_count)+","+str(int(datetime.timestamp(now)))
					client.publish('/score', b)
					not_sent_score = False
			else:

				# Move enemies and check collisions
				for i in range(num_of_enemies):

					# if enemy exploding
					if enemy[i].explosion_counter >= 1:
						enemy[i].explosion_counter -= 1
					elif enemy[i].explosion_counter == 0:
						enemy_respawn(enemy[i], level)
					else:
						enemy[i].update_enemy_position(screen_sizeX, screen_sizeY)
						if enemy[i].posY > screen_sizeY:
							enemy_respawn(enemy[i], level)
						enemy[i].show()

						# if enemy collision with player
						if is_collision(enemy[i], player):
							explosion_sound.play()
							player.explosion_counter = 5
							if score > session_high_score:
								session_high_score = score
							game_over = True

						# if bullet hits enemy
						elif bullet.state == 'show' and is_collision(enemy[i], bullet) :
							explosion_sound.play()
							enemy[i].explosion_counter = 10
							score += enemy[i].hit_points
							enemy_count += 1
							bullet.state = 'hide'

					# if coin exploding
					if coin[i].explosion_counter >= 1:
						coin[i].explosion_counter -= 1
					elif coin[i].explosion_counter == 0:
						coin_respawn(coin[i], level)
					else:
						coin[i].update_coin_position(screen_sizeX, screen_sizeY)
						if coin[i].posY > screen_sizeY:
							coin_respawn(coin[i], level)
						coin[i].show()

						# if coin collision with player
						if is_collision(coin[i], player):
							explosion_sound.play()
							coin[i].explosion_counter = 5
							score += coin[i].hit_points
							coin_count += 1
					now = datetime.now()
					pos_x += player.posX
					pos_y += player.posY
					num_x += 1
					num_y += 1

					enemy[i].show()
					coin[i].show()

				# show player
				bullet.show()
				player.show()
				show_score(score, level, highest_score_from_df_1, highest_score_from_df_2, highest_score_from_df_3, screen_x = screen_sizeX)

			pygame.display.flip()

			clock.tick(frames_per_second)
			

			if player.explosion_counter > 0 :
				# to freeze and show player explosion longer
				time.sleep(1)
			
		# Update High Score database
		if score > 0:
			high_scores.high_scores_update_db(db_connection, PLAYER_NAME, score)
		# b = str(int(datetime.timestamp(now)))+","+PLAYER_NAME+","+str(score)+","+str(pos_x/num_x)+","+str(pos_y/num_y)+","+str(enemy_count)+","+str(coin_count)+","+str(bullet_count)+","+str(bullet_count-enemy_count)+","+str(int(datetime.timestamp(now)))
		# client.publish('/score', b)
		#create dict for store focus metric
		try:
			a = {'player_name':PLAYER_NAME,
				'score':score,
				'player_x':str(pos_x/num_x),
				'player_y':str(pos_y/num_y),
				'enemy_count':str(enemy_count),
				'coin_count':str(coin_count),
				'bullet_count':str(bullet_count),
				'miss_bullet_count':str(bullet_count-enemy_count),
				'timestamp':str(int(datetime.timestamp(now)))
				}
		except ZeroDivisionError:
			continue
		csv_ls.append(a)
		
		fieldnames =['player_name','score','player_x','player_y','enemy_count','coin_count','bullet_count','miss_bullet_count','timestamp']
		with open(f'game_data.csv', 'a', encoding='UTF8', newline='') as f:
			writer = csv.DictWriter(f,fieldnames)
			writer.writerows([csv_ls[game_round]])
		game_round =+ 1
	db_connection.close()
	
	print('Successfully quit Space Wars!')