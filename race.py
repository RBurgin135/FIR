import pygame
from pygame import FULLSCREEN
import random
import copy
import math
import os


#window setup
import ctypes
user32 = ctypes.windll.user32
global scr_width
global scr_height
scr_width = user32.GetSystemMetrics(0)
scr_height = user32.GetSystemMetrics(1)
window = pygame.display.set_mode((scr_width,scr_height),FULLSCREEN)
pygame.display.set_caption("FIR")
pygame.font.init()
from pygame.locals import *
pygame.init()

#BOARD ======================
class Board:
    def __init__(self):
        self.RUN = True

        #particles
        self.particles = []
        self.particleshow = False

        #proglines
        self.proglines = []
        self.proglinesshow = False
        lineF = open("files\\progresslines\\"+trackset+".txt", "r")
        place = 1
        while True:
            lines = lineF.readline().strip()
            chunk = lines.split(",")
            if chunk[0] == "END":
                break
            else:
                self.proglines.append(ProgLine(place, [chunk[0], chunk[1]], chunk[2]))
                place += 1

        #cars
        self.cars = []
        self.gensize = 40
        self.startcoord = [int(chunk[1]), int(chunk[2])]
        for i in range(self.gensize):
            self.cars.append(Car(self.startcoord))

        trackcoord = [int(chunk[3]), int(chunk[4])]
        T.coord = trackcoord
        lineF.close()

        #colours
        self.backC = (33,44,48)
        self.baseC = (40,62,63)
        self.textC = (247,216,148)
        self.highC = (60,82,83)
        self.subC = (130,51,60)
        self.deadC = (193,193,193)

        #options
        OpFont = pygame.font.SysFont('', 25)
        save = [scr_width-200, 0, 200, 100]
        load = [scr_width-200, 100, 200, 100]
        hide = [scr_width-200, 200, 200, 100]
        self.optionplacement = [save,load,hide]
        self.optionstitles = [OpFont.render("SAVE", False, self.textC), OpFont.render("LOAD", False, self.textC), OpFont.render("HIDE", False, self.textC)]
        self.textbox = False
        self.textboxchoice = -1
        self.textboxtext = ""
        self.hideamount = 0
        self.HideSome()

        #subs
        self.SubFont = pygame.font.SysFont('', 25)
        self.subtexttitles = ["GENERATION: ", "HIGHEST LAP: ", "HIGHEST PROGRESS: ", "FASTEST LAP: ", "EFFECTS: ", "PROGRESS LINES: "]
        self.gen = 1
        self.maxlap = 0
        self.maxprogress = 0
        self.minlaptime = 9999999
        self.subcoord = [550, 0]

        #diag
        self.DiagFont = pygame.font.SysFont('', 25)
        X = scr_width - self.optionplacement[-1][2]/2
        Y = self.optionplacement[-1][1] + self.optionplacement[-1][3]
        self.diagcolumnsize = 20
        self.diaggap = (scr_height - Y)/self.diagcolumnsize
        self.diagstart = [X, Y]
        self.deadtext = self.DiagFont.render("XXXX", False,  self.deadC)
        self.netstart = [self.optionplacement[0][0] - 400, 100]

        #scoretracker
        self.socket = net.InitializeSender()

        #pause
        self.pause = False
        pausefont = pygame.font.SysFont('', 50)
        self.pausetext = pausefont.render("PAUSED", False,  self.textC)
        self.pausecoord = [scr_width/2-self.pausetext.get_width()/2, 400]

    def GenMonitor(self):
        query = True
        for i in self.cars:
            if not i.fail:
                query = False

        if query:
            self.particles = []

            #maxlaptime
            for i in self.cars:
                if i.laptime < self.minlaptime:
                    self.minlaptime = copy.deepcopy(i.laptime)

            #review
            for i in self.cars:
                i.scoringvalues = [i.progress, i.laptime]

            #reset cars
            newnets = neu.Review(self.cars)
            for i in range(self.gensize):
                self.cars[i].NewGenReset(newnets[i])

            self.gen += 1

            #performance
            self.HideSome()

            #scoretracker
            data = self.cars[0].Nn.score
            net.Send(data, self.socket)
        else:
            #scoretracker
            net.Send(False, self.socket)

    def Show(self):
        self.ShowOptions()
        self.ShowSubs()
        self.ShowDiag()
        self.ShowNet()
        if self.pause:
            self.ShowPause()

    def ShowOptions(self):
        #options=======
        M.highlight = -1
        #base
        for z in range(len(self.optionplacement)):
            i = self.optionplacement[z]
            
            #mouse over
            if (i[0] < M.coord[0] < i[0] + i[2]) and (i[1] < M.coord[1] < i[1] + i[3]):
                M.highlight = z
                pygame.draw.rect(window, self.highC, (i))
            else:
                pygame.draw.rect(window, self.baseC, (i))
        
            #text
            window.blit(self.optionstitles[z], (i[0]+i[2]//2-10, i[1]+i[3]//2))
        
        #texbox
        if self.textbox:
            #line
            l = self.optionplacement[0]
            coords = [[l[0]-200, l[1]+50], [l[0]-25, l[1]+50]]
            pygame.draw.line(window, self.baseC, coords[0], coords[1])

            #text
            BoxFont = pygame.font.SysFont('', 25)
            Text = BoxFont.render(self.textboxtext, False, self.baseC)
            window.blit(Text, (coords[0][0], coords[0][1]-17))

    def Textbox(self):
        act = False
        for event in pygame.event.get():
            #keys
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    act = True
                elif keys[pygame.K_BACKSPACE]:
                    self.textboxtext = self.textboxtext[:-1]
                else:
                    self.textboxtext += event.unicode

        #save + load
        if act:
            if self.textboxchoice == 0:
                neu.Write(self.gen, self.cars, self.textboxtext)
            elif self.textboxchoice == 1:
                try:
                    self.cars, self.gen = neu.Read(self.cars, self.textboxtext)
                except:
                    FileNotFoundError
            elif self.textboxchoice == 2:
                try:
                    self.hideamount = int(self.textboxtext)
                    self.HideSome()
                except:
                    ValueError
            self.textbox = False

    def HideSome(self):
        if self.hideamount:
            for i in self.cars:
                i.hide = True
            
            for i in range(self.hideamount):
                self.cars[i].hide = False
        else:
            for i in self.cars:
                i.hide = False

    def ShowSubs(self):
        X, Y = copy.deepcopy(self.subcoord)

        #maxlap + maxprogress + minlaptime
        for i in self.cars:
            if i.lap > self.maxlap:
                self.maxlap = copy.deepcopy(i.lap)-1
            if i.progress > self.maxprogress:
                self.maxprogress = copy.deepcopy(i.progress)

        data = [self.gen, self.maxlap, self.maxprogress, self.minlaptime]

        #effects
        if self.particleshow:
            data.append("ON")
        else:
            data.append("OFF")

        #lines
        if self.proglinesshow:
            data.append("ON")
        else:
            data.append("OFF")

        for i in range(len(self.subtexttitles)):
            text = self.SubFont.render(self.subtexttitles[i]+str(data[i]), False, self.subC)
            window.blit(text, (X, Y))
            Y += 25

    def ShowDiag(self):
        X, Y = self.diagstart
        index = 0
        for i in self.cars:
            index += 1
            

            #review states
            s = i.Nn.state
            if s == "new":
                colour = (255,174,201)#pink
            elif s == "processing":
                colour = (255,0,0)#red
            elif s == "cloned":
                colour = (255,242,0)#yellow
            elif s == "bred":
                colour = (34,177, 76)#green
            elif s == "mutated":
                colour = (63,72,204)#blue
            pygame.draw.rect(window, colour, (X, Y, 5, self.diaggap))
            

            
            #highlight + outline
            coord = [X  + 30, Y + self.diaggap/2]
            blit = [coord[0] - i.width/2, coord[1] - i.height/2]
            self.HighlightCheck(i, blit)
            if i.highlighted:
                window.blit(i.oresult, (coord[0] - i.odim[0]/2, coord[1] - i.odim[1]/2))

            #portrait
            window.blit(i.result, (blit))

            #text
            if i.fail:
                text = self.deadtext
            else:    
                text = self.DiagFont.render(str(round(i.vel))+" m/s", False,  self.textC)
            window.blit(text, (X + 50, Y+10))

            #spacing
            Y += self.diaggap
            if index == self.diagcolumnsize:
                index = 0
                X -= 100
                Y = self.diagstart[1]

    def HighlightCheck(self, car, coord):
        mouseover = True
        for i in range(2):
            if not (coord[i] < M.coord[i] < coord[i] + car.dim[i]):
                mouseover = False

        if mouseover:
            car.highlighted = True
        else:
            car.highlighted = False

    def ShowNet(self):
        for i in self.cars:
            if i.highlighted:
                X, Y = self.netstart
                net = i.Nn
                record = []
                for t in range(len(net.layers)): #cycles through topologies
                    record.append([])
                    for l in range(len(net.layers[t])): #cycles through layers
                        record[-1].append([])
                        for n in range(len(net.layers[t][l])): #cycles through neurons
                            X = self.netstart[0] + (100 * l)
                            Y = self.netstart[1] + (150 * t) + (50 * n)
                            active = net.layers[t][l][n].activated
                            record[-1][-1].append([X, Y, active, []])
                            for w in net.layers[t][l][n].weight: #cycles through weights
                                record[-1][-1][-1][-1].append(w)

                
                for t in record: #cycle through topologies
                    prevlayer = []
                    for l in t: #cycles through layers
                        thislayer = []
                        for n in l: #cycles through neurons
                            thislayer.append(n[:2])
                            if n[2]:
                                colour = (255,242,0) #yellow
                            else:
                                colour = (70, 70, 70) #grey
                            pygame.draw.circle(window, colour, (n[0], n[1]), 15)

                            if len(prevlayer) > 0:
                                for w in n[3]:
                                    #colour
                                    if w < 0:
                                        colour = (63,72,204) #blue
                                    else:
                                        colour = (255,0,0) #red

                                    p = prevlayer[n[3].index(w)]
                                    pygame.draw.line(window, colour, (n[:2]), p, round(abs(w*5)))
                        prevlayer = copy.deepcopy(thislayer)

    def ShowPause(self):
        window.blit(self.pausetext, self.pausecoord)

#MOUSE ======================
class Mouse:
    def __init__(self):
        self.coord = [0, 0]
        self.coord[0], self.coord[1] = pygame.mouse.get_pos()
        
        #buttons
        self.leftclick = False
        self.highlight = -1

    def Input(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            #mouse
            if event.type == pygame.MOUSEMOTION:
                self.coord[0], self.coord[1] = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    self.LClickDOWN()
            if event.type == pygame.MOUSEBUTTONUP:
                if self.leftclick:
                    self.LClickUP()

            #keys
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    if B.particleshow:
                        B.particles = []
                        B.particleshow = False
                    else:
                        B.particleshow = True
                if keys[pygame.K_l]:
                    if B.proglinesshow:
                        B.proglinesshow = False
                    else:
                        B.proglinesshow = True
                if keys[pygame.K_ESCAPE]:
                    if B.pause:
                        B.pause = False
                    else:
                        B.pause = True

    def LClickDOWN(self):
        if self.highlight != -1:
            self.leftclick = True

        #exit
        if self.coord[0] > scr_width-50 and self.coord[0] < scr_width and self.coord[1] < scr_height and self.coord[1] > scr_height-50:
            B.RUN = False

        #hide
        for i in B.cars:
            if i.highlighted:
                i.Eliminate()

    def LClickUP(self):
        if self.leftclick and self.highlight != -1:
            B.textbox = True
            B.textboxchoice = copy.deepcopy(self.highlight)
            B.textboxtext = ""

        self.leftclick = False

#ENTITIES ======================
class Car:
    def __init__(self, coord):
        #mechanics
        self.coord = copy.deepcopy(coord)
        self.blit = [0, 0]
        self.vel = 0
        self.deg = 90

        #images
        self.acc = pygame.image.load("images\\car\\accelerate.png").convert_alpha()
        self.brake = pygame.image.load("images\\car\\brake.png").convert_alpha()
        self.idle = pygame.image.load("images\\car\\idle.png").convert_alpha()
        self.dead = pygame.image.load("images\\car\\dead.png").convert_alpha()
        self.hidden = pygame.image.load("images\\car\\hidden.png").convert_alpha()
        self.image = self.idle
        self.hide = False

        #outline
        self.outline = pygame.image.load("images\\car\\outline.png").convert_alpha()
        self.odim = [0, 0]
        self.oblit = [0, 0]
        self.oresult = self.outline
        self.highlighted = False

        #diag
        self.result = self.image

        #collisions
        self.fail = False
        self.mask = pygame.mask.from_surface(self.result)

        #dimensions
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.dim = [self.width, self.height]

        #smoke
        self.time = 0

        #tiremarks
        self.tiredelay = [self.coord, self.coord]

        #netlines
        self.netlines = []
        for i in range(0,5):
            self.netlines.append(NetLine(self, 90 + (i*45)))

        #racing
        self.maxspeed = 10
        self.lap = 0
        self.progress = 0
        self.currentprogress = 0
        self.proglineexhausted = []
        self.laptime = 0

        #neural networking
        self.Nn = neu.NeuralNet()
        self.scoringvalues = [self.progress, self.laptime]

    def Calc(self):
        #AI
        self.Ai()

        #laptime
        self.laptime += 1

        #tiremarks
        self.TireDelayNote()

        #hidden
        if self.hide:
            self.image = self.hidden

        #displace
        pythag = [0,0]
        radians = math.radians(self.deg)
        pythag[0] = self.vel * math.sin(radians)
        pythag[1] = self.vel * math.cos(radians)

        #rotate
        self.result = pygame.transform.rotate(self.image, self.deg)
        self.width = self.result.get_width()
        self.height = self.result.get_height()
        self.dim = [self.width, self.height]

        #export
        for i in range(2):
            self.coord[i] += pythag[i]

        #highlight
        self.oresult = pygame.transform.rotate(self.outline, self.deg)
        self.odim = [self.oresult.get_width(), self.oresult.get_height()]

        #culling
        if self.vel == 0:
            self.Eliminate()

    def Show(self): 
        #locate
        self.blit = [0,0]
        for i in range(2):
            self.blit[i] = self.coord[i] - self.dim[i]/2

        #outline
        if self.highlighted:
            self.oblit = [0,0]
            for i in range(2):
                self.oblit[i] = self.coord[i] - self.odim[i]/2

            window.blit(self.oresult, self.oblit)

        #export
        window.blit(self.result, self.blit)
        self.mask = pygame.mask.from_surface(self.result)

        #smoke
        if B.particleshow:
            self.SmokeGen()  

    def Reset(self):
        if self.vel > 0:
            if self.vel -.03 < 0:
                self.vel = 0
            else:
                self.vel -= .03
        self.image = self.idle

    def Accelerate(self):
        if self.vel < self.maxspeed:
            self.vel += 0.05
        self.image = self.acc

    def Brake(self):
        if self.vel > 0:
            if self.vel -.05 < 0:
                self.vel = 0
            else:
                self.vel -= .05
        self.image = self.brake

        #tiremarks
        if B.particleshow and not self.hide:
            self.TireMarkGen()

    def SmokeGen(self):
        #smoke
        self.time += 1
        if self.time % 3 == 0:
            rad = math.radians(self.deg+180)
            change = [20 * math.sin(rad), 20 * math.cos(rad)]
            coord = [self.coord[0]+ change[0], self.coord[1]+ change[1]]
            B.particles.append(Smoke(coord))

    def TireMarkGen(self):
        rad = [math.radians(self.deg+150), math.radians(self.deg+210)]

        coord = []
        for i in range(2):
            change = [20 * math.sin(rad[i]), 20 * math.cos(rad[i])]
            coord .append([self.coord[0]+ change[0], self.coord[1]+ change[1]])
        for i in range(2):
            B.particles.append(TireMark(coord[i], self.tiredelay[i]))

    def TireDelayNote(self):
        rad = [math.radians(self.deg+150), math.radians(self.deg+210)]
        coord = copy.deepcopy(self.coord)

        self.tiredelay = []
        for i in range(2):
            change = [20 * math.sin(rad[i]), 20 * math.cos(rad[i])]
            self.tiredelay.append([coord[0]+ change[0], coord[1]+ change[1]])

    def NetlineScan(self):
        result = []
        for i in self.netlines:
            result.append(i.Scan())
        
        return result
    
    def Ai(self):
        #inputs
        netlineR = self.NetlineScan()
        velR = (self.vel/self.maxspeed) * 2 - 1


        #left
        leftinputs = [netlineR[3], netlineR[4]]
        #right
        rightinputs = [netlineR[0], netlineR[1]]
        #speedcontrol
        speedcontrolinputs = [netlineR[1], netlineR[2], netlineR[3], velR]

        #process
        inputs = [leftinputs, rightinputs, speedcontrolinputs]
        result = self.Nn.Forward(inputs)

        #outputs
        #turning
        if result[0] > 0:
            #turn left
            self.deg -= 2
        elif result[1] > 0:
            #turn right
            self.deg += 2


        #speedcontrol
        if result[2] >= 0.33333:
            self.Accelerate()
        elif 0.33333 > result[2] >= -0.33333:
            pass #freewheels
        elif -0.33333 > result[2]:
            self.Brake()

    def NewGenReset(self, newnet):
        #net
        self.Nn = newnet

        #mechanics
        self.coord = copy.deepcopy(B.startcoord)
        self.blit = [0, 0]
        self.vel = 0
        self.deg = 90

        #image
        self.image = self.idle
        self.result = self.image
        self.mask = pygame.mask.from_surface(self.result)

        #state
        self.hide = False
        self.fail = False

        #racing
        self.lap = 1
        self.progress = 0
        self.currentprogress = 0
        self.proglineexhausted = []
        self.laptime = 0
        self.currentlaptime = 0

        #outline
        self.oblit = [0, 0]
        self.oresult = self.outline
        self.highlighted = False

        #netlines
        self.netlines = []
        for i in range(0,5):
            self.netlines.append(NetLine(self, 90 + (i*45)))

        #tiremarks
        self.tiredelay = [self.coord, self.coord]

    def Eliminate(self):
        self.fail = True
        self.image = self.dead
        self.result = pygame.transform.rotate(self.image, self.deg)


        if self.lap != 4:
            self.laptime = 999999999

class Track:
    def __init__(self):
        #mask
        self.image = pygame.image.load("images\\tracks\\"+trackset+".png").convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.coord = [0, 0]

    def Show(self):
        window.blit(self.image, self.coord)
        self.BoundaryCheck()

    def BoundaryCheck(self):
        for i in B.cars:
            if not i.fail:
                offset = [0, 0]
                for z in range(2):
                    offset[z] = round(self.coord[z] - (i.coord[z]-i.dim[z]/2))
                result = i.mask.overlap_area(self.mask, offset)
                
                count = i.mask.count()
                if result != count:
                    i.Eliminate()

class NetLine:
    def __init__(self, car, orientation):
        #pass in
        self.coord = car.coord
        self.car = car
        self.orientation = orientation

        #image
        self.image = pygame.image.load("images\\lines\\netline.png").convert_alpha()
        self.result = self.image

        #dimensions
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.dim = [self.width, self.height]

        #intersection
        self.length = self.height/2
        self.intersect = False

    def Show(self):
        coord = [self.coord[0]-self.width/2, self.coord[1]-self.height/2]
        window.blit(self.result, (coord))

        if self.intersect:
            pygame.draw.circle(window, (70,70,70), self.intersect, 10)

    def Scan(self):
        #rotate
        self.result = pygame.transform.rotate(self.image, self.car.deg+self.orientation)
        self.width = self.result.get_width()
        self.height = self.result.get_height()
        self.dim = [self.width, self.height]
        self.mask = pygame.mask.from_surface(self.result)

        offset = [0, 0]
        for z in range(2):
            offset[z] = round(T.coord[z] - (self.coord[z]-self.dim[z]/2))
        area = self.mask.overlap_area(T.mask, offset)

        count = self.mask.count()
        result = ((1 - (area/count))*2) -1

        return result

class ProgLine:
    def __init__(self, place, coord, deg):
        #placement
        self.place = place
        self.coord = [int(coord[0]), int(coord[1])]
        self.deg = float(deg)

        #image
        image = pygame.image.load("images\\lines\\progline.png").convert_alpha()
        self.result = pygame.transform.rotate(image, self.deg)

        #dimensions
        self.width = self.result.get_width()
        self.height = self.result.get_height()
        self.dim = [self.width, self.height]

        #blit
        self.blit = [self.coord[0]-self.width/2, self.coord[1]-self.height/2]

        #collisions
        self.mask = pygame.mask.from_surface(self.result)

    def Show(self): 
        window.blit(self.result, (self.blit))

    def Scan(self):
        for i in B.cars:
            if not i.fail:
                offset = [0, 0]
                for z in range(2):
                    offset[z] = round(self.blit[z] - (i.coord[z]-i.dim[z]/2))
                result = i.mask.overlap_area(self.mask, offset)
                
                if result:
                    if self.place == i.currentprogress + 1:
                        i.progress += 1
                        i.currentprogress += 1
                        i.proglineexhausted.append(self.place)
                    elif not (self.place in i.proglineexhausted):
                        i.Eliminate()
                    elif self.place == 1 and i.currentprogress == len(B.proglines):
                        i.lap += 1
                        i.progress += 1
                        i.currentprogress = 1
                        i.proglineexhausted = [self.place]

                        #finish
                        if i.lap == 4:
                            i.Eliminate()
                            

#PARTICLES ======================
class Smoke:
    def __init__(self, coord):
        coord = copy.deepcopy(coord)
        self.coord = [coord[0] + random.randint(-10, 10), coord[1] + random.randint(-10, 10)]
        self.colour = (73,73,73)
        self.size = random.randint(5,10)

    def Show(self):
        pygame.draw.circle(window, self.colour, (int(self.coord[0]), int(self.coord[1])), int(self.size), 0)

        self.size -= .1
        if self.size <= 0:
            B.particles.remove(self) 

class TireMark:
    def __init__(self, start, end):
        start = copy.deepcopy(start)
        end = copy.deepcopy(end)
        self.points = [start, end]
        self.colour = (73,73,73)
        self.time = 0

    def Show(self):
        self.time += 1
        pygame.draw.line(window, self.colour, self.points[0], self.points[1], 5)

        if self.time == 100:
            B.particles.remove(self)

import neural as neu

if __name__ == '__main__':
    global trackset
    trackset = "track1"

    T = Track()
    B = Board()
    M = Mouse()



    while B.RUN:
        pygame.time.delay(1)
        window.fill(B.backC)
        
        #input
        if B.textbox:
            B.Textbox()
        else:
            M.Input()
        if not B.pause:
            for i in B.cars:
                if not i.fail:
                    i.Calc()
            for i in B.proglines:
                i.Scan()

        #show
        T.Show()
        B.Show()
        for i in B.proglines:
            if B.proglinesshow or i.place == 1:
                i.Show()
        if B.particleshow:
            for i in B.particles:
                i.Show()
        for i in B.cars:
            if not i.fail and not i.hide:
                i.Show()
            if i.highlighted:
                for x in i.netlines:
                    x.Show()

        #reset
        for i in B.cars:
            if not i.fail:
                i.Reset()
        B.GenMonitor()

        pygame.display.update()