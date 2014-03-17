#-------------------------------------------------------------------------------
# Name:        BattleArena.py
# Purpose:     Battle Arena
#
# Author:      Alejandro Jimenez Encinas
#
# Created:     17/03/2014
# Copyright:   (c) Alejandro Jimenez Encinas 2014
# Licence:     CC BY-NC-SA
#-------------------------------------------------------------------------------
from Tkinter import Tk, Canvas, ALL
from random import uniform
from math import cos, sin, sqrt, pi, atan2
from operator import sub, pow

class Game:

    def __init__(self, w, h, num_agents):
        self.width = w
        self.height = h
        self.items = []
        for i in range(25):
            self.items.append(Item([uniform(0,w), uniform(0,h)], 5))
            while out_of_bounds(self.items[-1], w, h):
                self.items[-1] = Item([uniform(0,w), uniform(0,h)], 5)
        self.agents = []
        for i in range(num_agents):
            self.agents.append(Agent([uniform(0,w), uniform(0,h)], 0, 10))
        self.bullets = []

class Agent:

    def __init__(self, position, rotation, radius):
        self.position = position
        self.rotation = rotation
        self.radius = radius

        self.max_vision_angle = 180
        self.min_vision_angle = 1
        self.step_vision_angle = (self.max_vision_angle-self.min_vision_angle)/100.0
        self.max_vision_distance = 250
        self.min_vision_distance = 50
        self.step_vision_distance = (self.max_vision_distance-self.min_vision_distance)/100.0
        self.vision_distance = self.min_vision_distance
        self.vision_angle = self.max_vision_angle

        self.shoot_interval = 20
        self.shoot_actual = 0

    def move(self, direction):
        norm = sqrt(sum(direction[i]*direction[i] for i in range(len(direction))))
        direction = [ direction[i]/norm  for i in range(len(direction)) ]
        self.position = map(sum, zip(self.position, direction))

    def rotate(self, sign):
        self.rotation += sign
        self.rotation %= 360

    def look_distance(self, sign):
        if sign > 0:
            self.vision_distance += self.step_vision_distance
            self.vision_distance = min(self.vision_distance, self.max_vision_distance)
            self.vision_angle -= self.step_vision_angle
            self.vision_angle = max(self.vision_angle, self.min_vision_angle)
        else:
            self.vision_distance -= self.step_vision_distance
            self.vision_distance = max(self.vision_distance, self.min_vision_distance)
            self.vision_angle += self.step_vision_angle
            self.vision_angle = min(self.vision_angle, self.max_vision_angle)

    def look_angle(self, sign):
        if sign > 0:
            self.vision_angle += self.step_vision_angle
            self.vision_angle = min(self.vision_angle, self.max_vision_angle)
            self.vision_distance -= self.step_vision_distance
            self.vision_distance = max(self.vision_distance, self.min_vision_distance)
        else:
            self.vision_angle -= self.step_vision_angle
            self.vision_angle = max(self.vision_angle, self.min_vision_angle)
            self.vision_distance += self.step_vision_distance
            self.vision_distance = min(self.vision_distance, self.max_vision_distance)

    def shoot(self, direction):
        if self.shoot_actual > self.shoot_interval:
            norm = sqrt(sum(direction[i]*direction[i] for i in range(len(direction))))
            direction = [ direction[i]/norm  for i in range(len(direction)) ]
            angle = -(180+(atan2(-direction[1], -direction[0])*180/pi)) % 360
            if angle >= self.rotation - self.vision_angle/2.0 and angle <= self.rotation + self.vision_angle/2.0:
                bullet_position = [self.position[0]+(self.radius)*direction[0], self.position[1]+(self.radius)*direction[1]]
                bullet_direction = [direction[0]+uniform(-self.vision_angle/4.0,self.vision_angle/4.0)*pi/180, direction[1]+uniform(-self.vision_angle/4.0,self.vision_angle/4.0)*pi/180]
                norm = sqrt(sum(bullet_direction[i]*bullet_direction[i] for i in range(len(bullet_direction))))
                bullet_direction = [ bullet_direction[i]/norm  for i in range(len(bullet_direction)) ]
                game.bullets.append(Bullet(bullet_position, 2, bullet_direction, 5))
                self.shoot_actual = 0

    def update(self):

        self.shoot_actual += 1
        if out_of_bounds(self, game.width, game.height):
            game.agents.remove(self)

class Bullet:

    def __init__(self, position, radius, direction, speed):
        self.position = position
        self.radius = radius
        self.direction = direction
        self.speed = speed

    def move(self):
        self.position = map(sum, zip(self.position, [d*self.speed for d in self.direction]))

class Item:

    def __init__(self, position, radius):
        self.position = position
        self.radius = radius

def collision(obj1, obj2):
    return sum([element**2 for element in map(sub,obj2.position,obj1.position)]) < (obj1.radius + obj2.radius)**2

def out_of_bounds(obj, w, h):
    radius = min(w,h)
    return sum([element**2 for element in map(sub,[radius/2, radius/2],obj.position)]) > (obj.radius - radius/2)**2

def update():

    for agent in game.agents:
        agent.shoot([cos(-agent.rotation*pi/180), sin(-agent.rotation*pi/180)])
        agent.look_angle(-1)
        agent.rotate(1)
        agent.update()
    for bullet in game.bullets:
        bullet.move()
        if out_of_bounds(bullet, game.width, game.height):
            game.bullets.remove(bullet)
    for bullet in game.bullets:
        for item in game.items:
            if collision(bullet, item):
                game.items.remove(item)

def draw():

    for item in game.items:
        window.create_oval(item.position[0]-item.radius, item.position[1]-item.radius, item.position[0]+item.radius, item.position[1]+item.radius, fill="green")
    for agent in game.agents:
        window.create_oval(agent.position[0]-agent.radius, agent.position[1]-agent.radius, agent.position[0]+agent.radius, agent.position[1]+agent.radius, fill="blue")
        window.create_line(agent.position[0], agent.position[1], agent.position[0]+agent.radius*cos(-agent.rotation*pi/180), agent.position[1]+agent.radius*sin(-agent.rotation*pi/180), width=2, fill="red")
        window.create_arc(agent.position[0]-agent.vision_distance,agent.position[1]-agent.vision_distance,agent.position[0]+agent.vision_distance,agent.position[1]+agent.vision_distance, start=agent.rotation-agent.vision_angle/2, extent=agent.vision_angle)
    for bullet in game.bullets:
        window.create_oval(bullet.position[0]-bullet.radius, bullet.position[1]-bullet.radius, bullet.position[0]+bullet.radius, bullet.position[1]+bullet.radius, fill="red")
    window.create_oval(0,0,game.width,game.height)

def step():

    window.delete(ALL)

    update()
    draw()

    master.after(25, step)

def main():

    global game, master, window
    game = Game(800, 800, 1)

    master = Tk()
    window = Canvas(master, width=game.width, height=game.height)
    window.pack()
    master.after(1, step)
    master.mainloop()

if __name__ == "__main__":
    main()

