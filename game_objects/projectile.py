# projectile.py

import math
from constants import BULLET_MASS, BULLET_RADIUS, BOMB_MASS, BOMB_RADIUS, BOMB_DRILL, LASER_VEL, LASER_DIST


class Projectile:
    def __init__(self, x, y, angle, velocity, mass, radius):
        self.x = x
        self.y = y
        self.angle = angle
        self.velocity = velocity
        self.mass = mass
        self.radius = radius
        self.vx = velocity * math.cos(math.radians(angle))
        self.vy = velocity * math.sin(math.radians(angle))

    def update(self, gravity):
        """Aggiorna la posizione del proiettile."""
        self.vy -= gravity * 0.1
        self.x += self.vx
        self.y += self.vy

    def get_position(self):
        """Ritorna la posizione del proiettile."""
        return self.x, self.y


class Bullet(Projectile):
    def __init__(self, x, y, angle, velocity):
        super().__init__(x, y, angle, velocity, BULLET_MASS, BULLET_RADIUS)


class Bombshell(Projectile):
    def __init__(self, x, y, angle, velocity):
        super().__init__(x, y, angle, velocity, BOMB_MASS, BOMB_RADIUS)
        self.drill_distance = BOMB_DRILL


class Laser(Projectile):
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle, LASER_VEL, 0, 1)
        self.distance_traveled = 0

    def update(self, gravity):
        self.x += self.vx
        self.y += self.vy
        self.distance_traveled += self.vx
        if self.distance_traveled > LASER_DIST:
            self.x, self.y = -1, -1
