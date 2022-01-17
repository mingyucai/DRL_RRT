import numpy as np
import gym
from gym import spaces
import time
import random
import math
import pygame

class RAEnv(gym.Env):
	metadata = {
		'render.modes': ['rgb_array'],
		'video.frames_per_second': 50
	}
	def __init__(self):
		self.action_space = spaces.Box(low=np.array([-1., -1.]), high=np.array([1., 1.]), dtype=np.float32)
		self.observation_space = spaces.Box(low=np.array([0., 0., -np.inf, -np.inf]), high=np.array([1., 1., np.inf, np.inf]), dtype=np.float32)
		self.viewer = None
		self._max_episode_steps = 600

	def reset(self):
		self.h = 600
		self.w = 600
		self.r = 15
		self.tr = 30
		self.x = 0.1
		self.y = 0.90
		self.vx = 0
		self.vy = 0
		self.g = -0.5
		self.dt = 0.05
		self.ground_el = 1.1
		self.t3_x = 0.3
		self.t3_y = 0.3
		self.t2_x = 0.85
		self.t2_y = 0.6
		self.t1_x, self.t1_y = 220 / 600, 500 / 600
		self.t4_x, self.t4_y = 80 / 600, 80 / 600
		self.t5_x, self.t5_y = 500 / 600, 60 / 600

		self.obs1_x, self.obs1_y = 0.5, 0.5
		self.obs2_x, self.obs2_y = 80 / 600, 400 / 600
		self.obs3_x, self.obs3_y = 450 / 600, 490 / 600
		self.obs4_x, self.obs4_y = 470 / 600, 200 / 600
		self.obs5_x, self.obs5_y = 295 / 600, 110 / 600
		self.obs6_x, self.obs6_y = 0.1, 0.1

		self.t1_crossed = False
		self.t2_crossed = False
		self.ball_circle = None
		self.ball_trans = None
		self.t1_circle = None
		self.t2_circle = None
		self.done = False
		self.episodes = 0

		return np.array([self.x, self.y, self.vx, self.vy])


	def init_pygame(self):
		self.MapWindowName = 'RRT path planning'
		pygame.display.set_caption(self.MapWindowName)
		self.map = pygame.display.set_mode((self.w, self.h))
		self.map.fill((255, 255, 255))


	def render(self, mode='rgb_array'):
		if self.episodes % 5 == 0:
			self.map.fill((255, 255, 255))
			pygame.draw.circle(self.map, (255, 0, 0), (self.x*self.w, self.y*self.h), self.r, 0)

			pygame.draw.circle(self.map, (0, 255, 0), (self.t5_x * self.w, self.t5_y * self.h), self.tr, 0)

			# pygame.draw.circle(self.map, (0, 0, 0), (self.obs1_x * self.w, self.obs1_y * self.h), self.tr*2, 0)
			# pygame.draw.circle(self.map, (0, 0, 0), (self.obs2_x * self.w, self.obs2_y * self.h), self.tr * 1.5, 0)
			# pygame.draw.circle(self.map, (0, 0, 0), (self.obs3_x * self.w, self.obs3_y * self.h), self.tr * 1.9, 0)
			# pygame.draw.circle(self.map, (0, 0, 0), (self.obs4_x * self.w, self.obs4_y * self.h), self.tr * 1, 0)
			# pygame.draw.circle(self.map, (0, 0, 0), (self.obs5_x * self.w, self.obs5_y * self.h), self.tr * 1, 0)
			# pygame.draw.circle(self.map, (0, 0, 0), (self.obs6_x * self.w, self.obs6_y * self.h), self.tr * 1.5, 0)

			pygame.display.update()
			pygame.event.clear()
			# pygame.event.wait(0)
		if self.done:
			pygame.quit()


	def step(self, a):
		reward = 0

		if not self.done:
			self.episodes += 1
			reward = 0
			ax, ay = np.clip(a, -1, 1)/20

			self.vx = self.vx + self.dt*ax
			self.vy = self.vy + self.dt*ay  #self.dt*(ay + self.g)

			self.x = self.x + self.vx*self.dt + 0.5 * ax * self.dt**2
			self.y = self.y + self.vy*self.dt + 0.5 * ay * self.dt**2  #0.5 * (ay + self.g) * self.dt**2

			if self.episodes == self._max_episode_steps:
				reward = -100
				self.done = True

			out_boundry = self.x < 0 or self.x > 1 or self.y < 0 or self.y > 1
			if out_boundry:
				reward = -100
				self.done = True

			self.y = np.clip(self.y, 0, 1)
			self.x = np.clip(self.x, 0, 1)

			# unsafe1 = (self.x - self.obs1_x) ** 2 + (self.y - self.obs1_y) ** 2 <= (self.tr*2 / self.w) ** 2
			# unsafe2 = (self.x - self.obs2_x) ** 2 + (self.y - self.obs2_y) ** 2 <= (self.tr*1.5 / self.w) ** 2
			# unsafe3 = (self.x - self.obs3_x) ** 2 + (self.y - self.obs3_y) ** 2 <= (self.tr*1.9 / self.w) ** 2
			# unsafe4 = (self.x - self.obs4_x) ** 2 + (self.y - self.obs4_y) ** 2 <= (self.tr*1.0 / self.w) ** 2
			# unsafe5 = (self.x - self.obs5_x) ** 2 + (self.y - self.obs5_y) ** 2 <= (self.tr*1.0 / self.w) ** 2
			# unsafe6 = (self.x - self.obs6_x) ** 2 + (self.y - self.obs6_y) ** 2 <= (self.tr * 1.5 / self.w) ** 2
			# unsafe = unsafe1 or unsafe2 or unsafe3 or unsafe4 or unsafe5 or unsafe6
			#
			# if unsafe:
			# 	reward = -100
			# 	self.done = True


			T5 = (self.x - self.t5_x)**2 + (self.y - self.t5_y)**2 <= (self.tr/self.w + self.r/self.w)**2


			if T5:
				reward = 200
				print('goal reach')
				self.done = True

		return np.array([self.x, self.y, self.vx, self.vy]), reward, self.done, {}

