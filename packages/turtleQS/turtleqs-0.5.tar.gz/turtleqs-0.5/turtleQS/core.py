from turtle import Turtle
import math as m

class TurtleQS:

  def __init__(self, limit):
    if limit > 15: 
      print(f"Setting grid limit: {15}")    
      self.lx = 15 * -1
      self.ly = 15 * -1
      self.ux = 15
      self.uy = 15
    else:
      print(f"Setting grid limit: {limit}")    
      self.lx = abs(limit) * -1
      self.ly = abs(limit) * -1
      self.ux = abs(limit)
      self.uy = abs(limit)
    self.t = Turtle()
    return None

  def mainloop(self):
    self.t.screen.mainloop()

  def start(self, tracerOn, showGrid):
    screen = self.t.getscreen()
    screen.tracer(tracerOn)
    screen.setup(400, 400)
    screen.bgcolor("white")
    screen.setworldcoordinates(self.lx, self.ly, self.ux, self.uy)
    self.t.speed(0)  # Fastest speed

    if showGrid:
      self.drawGrid()

    self.t.hideturtle()
    return self.t

  def drawGrid(self):
    self.t.penup()
    x = self.lx
    for i in range((self.ux * 2) + 1):
      # print(f"x: {x}")
      if i == ((self.ux * 2) / 2):
        self.t.pencolor("red")
      else:
        self.t.pencolor("black")
      self.t.goto(x, self.uy)
      self.t.pendown()
      self.t.goto(x, self.ly)
      self.t.penup()
      x += 1

    self.t.penup()
    y = self.ly
    for i in range((self.uy * 2) + 1):
      # print(f"y: {y}")
      if i == (self.uy * 2) / 2:
        self.t.pencolor("red")
      else:
        self.t.pencolor("black")
      self.t.goto(self.lx, y)
      self.t.pendown()
      self.t.goto(self.ux, y)
      self.t.penup()
      y += 1
