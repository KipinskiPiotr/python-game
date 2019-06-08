import socket
import select
import sys
from src.Assets import settings
from src.Entities.Player import Player
import pygame
import pygame.locals

# Messages:
#  Client->Server
#   One or two characters. First character is the command:
#     c: connect
#     u: update position
#     d: disconnect
#   Second character only applies to position and specifies direction (udlr)
#
#  Server->Client
#   '|' delimited pairs of positions to draw the players (there is no
#     distinction between the players - not even the client knows where its
#     player is.

class GameServer(object):
  def __init__(self, entities, collisionDetector, port=8080, max_num_players=5):
    self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.serversocket.bind(('127.0.0.1', port))
    self.serversocket.listen(1)
    self.serversocket.setblocking(0)
    self.serversocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    self.players = {}
    self.entities = entities
    self.collisionDetector = collisionDetector
    
  def do_movement(self, mv, player):
    print(f"Server got message from player {player} to move: {mv}")
    p = self.players[player]

    if mv == 'u':
      p.vel.y = -p.speed
    elif mv == 'l':
      p.vel.x = -p.speed
    elif mv == 'r':
      p.vel.x = p.speed
    
  def parse_msg(self, msg, addr):
    if len(msg) >= 1:
      cmd = chr(msg[0])
      if cmd == 'c':  # New Connection
        self.players[addr] = Player((settings.TILE_SIZE, settings.WINDOW_HEIGHT - settings.TILE_SIZE))
        self.collisionDetector.add_player(self.players[addr])
        #if len(self.players) > 1:
        # self.entities.add(self.players[addr])
        print(f"New connection from fileno: {addr}")
      elif cmd == 'u':  # Movement Update
        if len(msg) >= 2 and addr in self.players:
          # Second char of message is direction (udlr)
          self.do_movement(chr(msg[1]), addr)
      elif cmd == 'd':  # Player Quitting
        if addr in self.players:
          self.collisionDetector.del_player(self.players[addr])
          del self.players[addr]
          print(f"Player with adress: {addr} disconnected")
      else:
        print("Unexpected: {0}".format(msg))

  def run(self):
    try:
      while True:
          try:
            conn, addr = self.serversocket.accept()
          except BlockingIOError:
            print("Waiting for connection")
            continue
          break
      while True:
        for e in pygame.event.get():
                if e.type == pygame.locals.QUIT:
                    return
                if e.type == pygame.locals.KEYDOWN and e.key == pygame.locals.K_ESCAPE:
                    return

        msg = conn.recv(32)
        self.parse_msg(msg, addr)
        self.entities.update()
        for player in self.players.values():
          player.update_relative_position(player.rect.right + self.entities.cam.x)
        self.collisionDetector.update()
        for addr, player in self.players.items():
          send = []
          #for pos in self.players:
          send.append("{0},{1}".format(player.rect.left, player.rect.top))
          conn.sendto('|'.join(send).encode(), addr)
    except KeyboardInterrupt as e:
      pass
    finally:
      self.serversocket.close()
      print("Server closed")