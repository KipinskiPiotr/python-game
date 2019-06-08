import pygame
import pygame.locals
import socket
import select
import random
import time
from src.Assets import settings

def get_constants(prefix):
    """Create a dictionary mapping socket module constants to their names."""
    return dict( (getattr(socket, n), n)
                 for n in dir(socket)
                 if n.startswith(prefix)
                 )

class GameClient():
  def __init__(self, entities, window, bg, addr="127.0.0.1", serverport=8080):
    families = get_constants('AF_')
    types = get_constants('SOCK_')
    protocols = get_constants('IPPROTO_')
    # Create a TCP/IP socket
    self.sock = socket.create_connection((addr, serverport))
    self.sock.setblocking(0)
    print ('Family  :', families[self.sock.family])
    print ('Type    :', types[self.sock.type])
    print ('Protocol:', protocols[self.sock.proto])

    self.entities = entities
    self.screen = window
    self.setup_pygame()
    self.players = []
    self.bg = bg

  def add_player(self, player):
    self.players.append(player)
    player.rect = player.image.get_rect(topleft=settings.STARTING_POS)
  
  def setup_pygame(self):    
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.locals.QUIT,
                              pygame.locals.KEYDOWN])

  def parse_msg(self, msg):
    for position in msg.decode().split('|'):
        x, sep, y = position.partition(',')
        print(int(x))
        print(int(y))
        #self.entities.update()
        self.players[0].rect.left = int(x)
        self.players[0].rect.top = int(y)

  def run(self):
    running = True
    clock = pygame.time.Clock()    

    print("Waiting...")
    try:
      # Initialize connection to server
      self.sock.send(b'c\n')
      while running:
        clock.tick(settings.FPS)
        while True:
          try:
            msg = self.sock.recv(32)
          except BlockingIOError:
            continue
          break
        self.parse_msg(msg)

        self.players[0].update_relative_position(self.players[0].rect.right + self.entities.cam.x)
        self.screen.blit(self.bg, (0,0))
        self.entities.draw(self.screen)
        pygame.display.update()

        for event in pygame.event.get():
          if event.type == pygame.QUIT or event.type == pygame.locals.QUIT:
            running = False
            break
          elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_UP:
              self.sock.send(b'uu\n')
            elif event.key == pygame.locals.K_LEFT:
              self.sock.send(b'ul\n')
            elif event.key == pygame.locals.K_RIGHT:
              self.sock.send(b'ur\n')
            elif event.key == pygame.locals.K_ESCAPE:
              return
            pygame.event.clear(pygame.locals.KEYDOWN)
    finally:
      self.sock.send(b'd\n')
      self.sock.close()
      print("Socket closed")