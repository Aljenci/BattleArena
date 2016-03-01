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

from Tkinter import Tk, Canvas, ALL, W
from random import uniform
from math import cos, sin, sqrt, pi, atan2
from operator import sub, pow

class Game:

    def __init__(self, w, h, IAs):
        self.width = w
        self.height = h
        self.items = []
##        for i in range(25):
##            self.items.append(Item([uniform(0,w), uniform(0,h)], 5))
##            while self.out_of_bounds(self.items[-1]):
##                self.items[-1] = Item([uniform(0,w), uniform(0,h)], 5)
        self.agents = []
        for i in range(len(IAs)):
            self.agents.append(IAs[i]([uniform(0,w), uniform(0,h)], 0, 10))
            while self.out_of_bounds(self.agents[-1]):
                self.agents[-1] = IAs[i]([uniform(0,w), uniform(0,h)], 0, 10)
        self.bullets = []
        
        self.finish_agents = []

    def collision(self, obj1, obj2):
        return sum([element**2 for element in map(sub,obj2.position,obj1.position)]) < (obj1.radius + obj2.radius)**2

    def out_of_bounds(self, obj):
        radius = min(self.width,self.height)
        return sum([element**2 for element in map(sub,[radius/2, radius/2],obj.position)]) > (obj.radius - radius/2)**2

    def update(self):

        for agent in self.agents:
            agent.update()
            if agent.life <= 0:
                self.agents.remove(agent)
                #self.finish_agents.append((agent, actual_it))
        for bullet in self.bullets:
            bullet.move()
            if self.out_of_bounds(bullet):
                self.bullets.remove(bullet)
        for bullet in self.bullets:
            for agent in self.agents:
                if self.collision(bullet, agent):
                    agent.life -= 1
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)

    def draw(self):

        for item in self.items:
            window.create_oval(item.position[0]-item.radius, item.position[1]-item.radius, item.position[0]+item.radius, item.position[1]+item.radius, fill="green")
        for agent in self.agents:
            window.create_oval(agent.position[0]-agent.radius, agent.position[1]-agent.radius, agent.position[0]+agent.radius, agent.position[1]+agent.radius, fill="blue")
            window.create_line(agent.position[0], agent.position[1], agent.position[0]+agent.radius*cos(-agent.rotation*pi/180), agent.position[1]+agent.radius*sin(-agent.rotation*pi/180), width=2, fill="red")
            window.create_arc(agent.position[0]-agent.vision_distance,agent.position[1]-agent.vision_distance,agent.position[0]+agent.vision_distance,agent.position[1]+agent.vision_distance, start=agent.rotation-agent.vision_angle/2, extent=agent.vision_angle)
            window.create_oval(agent.position[0]-agent.radius*2.5, agent.position[1]-agent.radius*2.5, agent.position[0]+agent.radius*2.5, agent.position[1]+agent.radius*2.5)
        for bullet in self.bullets:
            window.create_oval(bullet.position[0]-bullet.radius, bullet.position[1]-bullet.radius, bullet.position[0]+bullet.radius, bullet.position[1]+bullet.radius, fill="red")
        window.create_oval(0,0,min(game.width,game.height),min(game.width,game.height))
        for agent in self.agents:
            window.create_rectangle(agent.position[0]-agent.radius, agent.position[1]-agent.radius-5, agent.position[0]+agent.radius, agent.position[1]-agent.radius-10, fill="red")
            window.create_rectangle(agent.position[0]-agent.radius, agent.position[1]-agent.radius-5, agent.position[0]-agent.radius+(agent.life/100.0)*agent.radius*2, agent.position[1]-agent.radius-10, fill="green")
            window.create_rectangle(agent.position[0]-agent.radius, agent.position[1]-agent.radius-5, agent.position[0]+agent.radius, agent.position[1]-agent.radius-10)

class Agent:

    def __init__(self, position, rotation, radius):
        self.life = 100

        self.position = position
        self.rotation = rotation
        self.radius = radius

        self.max_vision_angle = 180
        self.min_vision_angle = 5
        self.step_vision_angle = (self.max_vision_angle-self.min_vision_angle)/100.0
        self.max_vision_distance = 800
        self.min_vision_distance = 100
        self.step_vision_distance = (self.max_vision_distance-self.min_vision_distance)/100.0
        self.vision_distance = self.min_vision_distance
        self.vision_angle = self.max_vision_angle

        self.shoot_interval = 20
        self.shoot_actual = 20

    def move(self, direction):
        norm = sqrt(sum(direction[i]*direction[i] for i in range(len(direction))))
        direction = [ direction[i]/norm  for i in range(len(direction)) ]
        direction = [direction[0]*cos(self.rotation*pi/180) + direction[1]*sin(self.rotation*pi/180), -direction[0]*sin(self.rotation*pi/180) + direction[1]*cos(self.rotation*pi/180)]
        previous_position = self.position
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
            direction = [direction[0]*cos(self.rotation*pi/180) + direction[1]*sin(self.rotation*pi/180), -direction[0]*sin(self.rotation*pi/180) + direction[1]*cos(self.rotation*pi/180)]
            angle = -(180+(atan2(-direction[1], -direction[0])*180/pi)) % 360
            if angle >= self.rotation - self.vision_angle/2.0 and angle <= self.rotation + self.vision_angle/2.0:
                bullet_position = [self.position[0]+(self.radius)*direction[0], self.position[1]+(self.radius)*direction[1]]
                # Tiros imprecisos
                #bullet_direction = [direction[0]+uniform(-self.vision_angle/4.0,self.vision_angle/4.0)*pi/180, direction[1]+uniform(-self.vision_angle/4.0,self.vision_angle/4.0)*pi/180]
                #norm = sqrt(sum(bullet_direction[i]*bullet_direction[i] for i in range(len(bullet_direction))))
                #bullet_direction = [ bullet_direction[i]/norm  for i in range(len(bullet_direction)) ]
                bullet_direction = direction
                game.bullets.append(Bullet(bullet_position, 2, bullet_direction, 5))
                self.shoot_actual = 0

    def view_enemy(self):

        for agent in game.agents:
            if agent != self:
                if sum([element**2 for element in map(sub,agent.position,self.position)]) < (self.vision_distance + agent.radius)**2:
                    direction = map(sub,agent.position,self.position)
                    norm = sqrt(sum(direction[i]*direction[i] for i in range(len(direction))))
                    direction = [ direction[i]/norm  for i in range(len(direction)) ]
                    angle = -(180+(atan2(-direction[1], -direction[0])*180/pi)) % 360
                    if angle >= self.rotation - self.vision_angle/2.0 and angle <= self.rotation + self.vision_angle/2.0:
                        return True
        return False

    def view_bullet(self):

        for bullet in game.bullets:
            if sum([element**2 for element in map(sub,bullet.position,self.position)]) < (self.vision_distance + bullet.radius)**2:
                direction = map(sub,bullet.position,self.position)
                norm = sqrt(sum(direction[i]*direction[i] for i in range(len(direction))))
                direction = [ direction[i]/norm  for i in range(len(direction)) ]
                angle = -(180+(atan2(-direction[1], -direction[0])*180/pi)) % 360
                if angle >= self.rotation - self.vision_angle/2.0 and angle <= self.rotation + self.vision_angle/2.0:
                    return True
        return False

    def near_enemy(self):

        for agent in game.agents:
            if agent != self:
                if sum([element**2 for element in map(sub,agent.position,self.position)]) < (agent.radius*2.5)**2:
                    return True
        return False

    def get_sensors_info(self):

        enemy = self.view_enemy()
        bullet = self.view_bullet()
        can_shoot = self.shoot_actual > self.shoot_interval
        actual_position = self.position
        self.move([1,0])
        out_of_bounds = game.out_of_bounds(self)
        self.position = actual_position
        close_enemy = self.near_enemy()
        return enemy, bullet, can_shoot, out_of_bounds, close_enemy

    def brain(self):

        return False, False, False, False, False, False

    def update(self):

        shot, forward, left, right, more_angle, minus_angle = self.brain()
        if shot:
            self.shoot([1,0])
        if forward:
            if not game.out_of_bounds(self):
                self.move([1,0])
                if game.out_of_bounds(self):
                    self.move([-1,0])
        if left:
            self.rotate(1)
        if right:
            self.rotate(-1)
        if more_angle:
            self.look_angle(1)
        if minus_angle:
            self.look_angle(-1)
        self.shoot_actual += 1

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

def step():

    window.delete(ALL)

    game.update()
    game.draw()

    master.after(1, step)

class Border(Agent):

    def brain(self):

        enemy, bullet, can_shoot, out_of_bounds, close_enemy = self.get_sensors_info()
        shot = False
        left = False
        right = out_of_bounds
        minus_angle = False
        forward = not out_of_bounds
        more_angle = False

        return shot, forward, left, right, more_angle, minus_angle

class Chaser(Agent):

    def brain(self):

        enemy, bullet, can_shoot, out_of_bounds, close_enemy = self.get_sensors_info()
        shot = enemy
        left = False
        right = not enemy
        minus_angle = True
        forward = enemy
        more_angle = False

        return shot, forward, left, right, more_angle, minus_angle

class Killer(Agent):

    def brain(self):

        enemy, bullet, can_shoot, out_of_bounds, close_enemy = self.get_sensors_info()
        shot = enemy
        left = False
        right = not enemy or out_of_bounds
        minus_angle = enemy or self.vision_distance < (self.max_vision_distance + self.min_vision_distance) / 2
        forward = enemy and not close_enemy
        more_angle = not enemy and not self.vision_distance < (self.max_vision_distance + self.min_vision_distance) / 2

        return shot, forward, left, right, more_angle, minus_angle

class Avoider(Agent):

    def brain(self):

        enemy, bullet, can_shoot, out_of_bounds, close_enemy = self.get_sensors_info()
        shot = False
        left = not bullet
        right = False
        minus_angle = False
        forward = bullet
        more_angle = False

        return shot, forward, left, right, more_angle, minus_angle

class Learner(Agent):

    def __init__(self, position, rotation, radius):

        Agent.__init__(self, position, rotation, radius)
        self.ann = ANN(5, 6, [6, 6])

    def brain(self):

        enemy, bullet, can_shoot, out_of_bounds, close_enemy = self.get_sensors_info()

        self.ann.set_input([enemy, bullet, can_shoot, out_of_bounds, close_enemy])
        shot, forward, left, right, more_angle, minus_angle = self.ann.get_output()
        #print shot, forward, left, right, more_angle, minus_angle
        return shot, forward, left, right, more_angle, minus_angle

class Node:

    def __init__(self, input):

        self.input = input
        self.output = 0.0
        self.threeshold = 1.0
        self.weight = [uniform(0.0,1.0) for e in input]
        self.calculate()

    def calculate(self):
        if all(isinstance(n, Node) for n in self.input):
            net = sum([self.input[i].output*self.weight[i] for i in range(len(self.input))])
        else:
            net = sum(self.input)
        self.output = net >= self.threeshold

class ANN:

    def __init__(self, n_in, n_out, hidden_layers):

        self.layer = [[Node([1.0]) for n in range(n_in)]]
        for i in range(len(hidden_layers)):
            self.layer.append([Node(self.layer[-1]) for j in range(hidden_layers[i])])
        self.layer.append([Node(self.layer[-1]) for j in range(n_out)])

    def get_output(self):

        return [node.output for node in self.layer[-1]]

    def set_input(self, input):

        for i in range(len(self.layer[0])):
            self.layer[0][i].input = input[i]
        self.recalculate()

    def recalculate(self):

        for layer in self.layer[1:-1]:
            for node in layer:
                node.calculate()

def main():

    global game, master, window, IAs
    #global game, IAs, actual_it
    IAs = [Border, Learner, Chaser, Killer]
    game = Game(800, 800, IAs)

    master = Tk()
    window = Canvas(master, width=game.width, height=game.height)
    window.pack()
    master.after(1, step)
    master.mainloop()
    
    #num_it = 1000000
    #actual_it = 0
    #while actual_it < num_it and len(game.agents) > 1:
    #    game.update()
    #    actual_it = actual_it + 1
    #print game.agents[0].__class__.__name__, 10
    #for ia in reversed(game.finish_agents):
    #    print ia[0].__class__.__name__, (float(ia[1])/(actual_it-1)/2)*10

if __name__ == "__main__":
    main()
