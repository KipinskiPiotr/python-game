import pygame as pg
from src.Assets import settings
import pygame
from pygame import *
from src.Engine.Client import Client
from src.Entities.Enemy import Enemy
from threading import Lock
from src.Entities.BigEnemy import BigEnemy
class Game:
    def __init__(self, player, entities, collisionDetector, bg, window):
        self.clock = pygame.time.Clock()
        self.player = player
        self.players = {}
        self.entities = entities
        self.bg = bg
        self.collisionDetector = collisionDetector
        self.window = window
        self.client = -1
        self.lock = Lock()

    def start_communication(self):
        self.client = Client(self.player, self.players, self.collisionDetector.enemies, self.lock)
        self.client.run()

    def run(self):
        while self.player.is_alive():
            for e in pygame.event.get():
                if e.type == QUIT:
                    if self.client != -1:
                        self.client.running = False
                    return
                if e.type == KEYDOWN and e.key == K_ESCAPE:
                    if self.client != -1:
                        self.client.running = False
                    return
            self.entities.update()
            self.player.update_relative_position(self.player.rect.right + self.entities.cam.x)
            self.collisionDetector.update()
            self.window.blit(self.bg, (0, 0))
            self.draw_projectiles()
            self.entities.draw(self.window)
            self.draw_enemies()
            self.draw_players()
            self.draw_hud()
            pygame.display.update()
            self.clock.tick(settings.FPS)
            print("MY POSITION: " + str([self.player.rect.x, self.player.rect.y]) + "\n")

        self.player.stats["health"] = 100

    def draw_projectiles(self):
        for projectile in self.player.projectiles:
            if abs(projectile.rect.x - self.player.rect.x) > 800:
                self.player.projectiles.pop(self.player.projectiles.index(projectile))
            projectile.update()
            self.window.blit(projectile.image, (projectile.rect.x + self.entities.cam.x, projectile.rect.y))
        for enemy in self.collisionDetector.enemies:
            if isinstance(enemy, BigEnemy):
                for projectile in enemy.projectiles:
                    if abs(projectile.rect.x - enemy.rect.x) > 1500:
                        enemy.projectiles.pop(enemy.projectiles.index(projectile))
                    projectile.update()
                    self.window.blit(projectile.image, (projectile.rect.x + self.entities.cam.x, projectile.rect.y))

    def draw_players(self):
        # print("OTHER PLAYERS:")
        self.lock.acquire()
        for id, pos in self.players.items():
            # print(f"Player {id} : {pos}")
            if(self.client.id != id):
                self.window.blit(self.player.image, (pos[0] + self.entities.cam.x, pos[1]))
        self.lock.release()
        # print()

    def draw_enemies(self):
        for enemy in self.collisionDetector.enemies:
            if enemy.is_alive() and not isinstance(enemy, BigEnemy):
                enemy.update(self.player)
                self.window.blit(enemy.image, (enemy.rect.x + self.entities.cam.x, enemy.rect.y))
                pygame.draw.rect(self.window, (255, 0, 0), (enemy.rect.x + self.entities.cam.x, enemy.rect.y + 10,
                                                        enemy.stats["health"] // 4, 10))
            elif enemy.is_alive() and isinstance(enemy, BigEnemy):
                enemy.update(self.player)
                self.window.blit(enemy.image, (enemy.rect.x + self.entities.cam.x, enemy.rect.y))
                pygame.draw.rect(self.window, (255, 0, 0), (enemy.rect.x + self.entities.cam.x, enemy.rect.y + 10,
                                                            enemy.stats["health"] // 250, 10))
    def draw_hud(self):
        pygame.draw.rect(self.window, (255, 0, 0), (40, 20, self.player.stats["health"] * 2, 18))

