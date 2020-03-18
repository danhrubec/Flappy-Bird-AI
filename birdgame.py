
import pygame
import neat
import time
import os
import random   
pygame.font.init()

# now we need to set up the width and height of the game, so 600 800?

WINDOW_W = 500
WINDOW_H = 800

#now load in all the images that we will need for the game.
Birds = [pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/danhr/Desktop/imgs", "bird1.png"))),
         pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/danhr/Desktop/imgs", "bird2.png"))),
         pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/danhr/Desktop/imgs", "bird3.png")))]

pipeimg = pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/danhr/Desktop/imgs", "pipe.png")))

bg = pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/danhr/Desktop/imgs", "bg.png")))

base = pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/danhr/Desktop/imgs", "base.png")))

scorefont = pygame.font.SysFont("comicsans",50)
#bird class, main control of the game

class Bird:
    IMGS = Birds
    Rotation = 25
    R_Velocity = 20
    Animation_T = 5

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.ticks = 0
        self.vel = 0
        self.height = self.y
        self.img_param = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -9.8
        self.ticks = 0
        self.height = self.y

    def move(self):
        self.ticks += 1
        #displacement
        d = self.vel * (self.ticks) + 0.5*(3)*(self.ticks)**2
        #creating bounds for the displacement

        if d >= 16:
            d = (d/abs(d)) * 16
        if d < 0:
            d -= 2

        #adjust our height
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.Rotation:
                self.tilt = self.Rotation
        else:  
            if self.tilt > -90:
                self.tilt -= self.R_Velocity

    def draw(self,win):
        self.img_param +=1

        if self.img_param < self.Animation_T:
            self.img = self.IMGS[0]
        elif self.img_param < self.Animation_T*2:
            self.img = self.IMGS[1]
        elif self.img_param < self.Animation_T*3:
            self.img = self.IMGS[2]
        elif self.img_param < self.Animation_T*4:
            self.img = self.IMGS[1]
        elif self.img_param == self.Animation_T*4 + 1:
            self.img = self.IMGS[0]
            self.img_param = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_param = self.Animation_T * 2

        rotated_image = pygame.transform.rotate(self.img,self.tilt)

        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center)
        win.blit(rotated_image, new_rect.topleft)


    def getMask(self):
        return pygame.mask.from_surface(self.img)



class Pipe:
    Gap = 144
    Vel = 5

    def __init__(self,x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPETOP = pygame.transform.flip(pipeimg,False,True)
        self.PIPEBOTTOM = pipeimg

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPETOP.get_height()
        self.bottom = self.height + self.Gap

    def move(self):
        self.x -= self.Vel

    def draw(self,win):
        win.blit(self.PIPETOP, (self.x,self.top))
        win.blit(self.PIPEBOTTOM, (self.x, self.bottom))

    def collide(self,bird,win):
        birdmask = bird.getMask()
        topmask = pygame.mask.from_surface(self.PIPETOP)
        bottommask = pygame.mask.from_surface(self.PIPEBOTTOM)

        topOffset = (self.x - bird.x, self.top - round(bird.y))
        bottomOffset = (self.x - bird.x, self.bottom - round(bird.y))

        bPoint = birdmask.overlap(bottommask,bottomOffset)
        tPoint = birdmask.overlap(topmask,topOffset)

        if tPoint or bPoint:
            return True

        return False

class Base:
    VEL = 5
    WIDTH = base.get_width()
    IMG = base

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self,win):
        win.blit(self.IMG, (self.x1,self.y))
        win.blit(self.IMG, (self.x2,self.y))



def drawWindow(win, bird,pipes,base,score):
        win.blit(bg,(0,0))
        for pipe in pipes:
            pipe.draw(win)
        base.draw(win)

        text = scorefont.render("Score: " + str(score),1,(255,255,255))
        win.blit(text, (WINDOW_W - 10 - text.get_width(),10))
        for b in bird:
            b.draw(win)
        pygame.display.update()



def main(genomes,config):

    nets = []
    ge = []

    flappy = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        flappy.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)


    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WINDOW_W,WINDOW_H))
    clock = pygame.time.Clock()

    score = 0
    
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():     
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        #flappy.move()

        pipe_ind = 0
        if len(flappy) > 0:
            if len(pipes) >1 and flappy[0].x > pipes[0].x + pipes[0].PIPETOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(flappy):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y,abs(bird.y - pipes[pipe_ind].height),abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()


        rem = []
        add_pipe = False
        

        for pipe in pipes:
            for x, bird in enumerate(flappy):
                if pipe.collide(bird,win):
                        ge[x].fitness -= 1
                        flappy.pop(x)
                        nets.pop(x)
                        ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPETOP.get_width() < 0:  
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score +=1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)
            
        for x, bird in enumerate(flappy):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                flappy.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        drawWindow(win, flappy,pipes,base,score)





def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))
    

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)