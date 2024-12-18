
class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def check_collision(self, projectile):
        """Verifica se il proiettile collide con l'ostacolo."""
        if (self.x <= projectile.x <= self.x + self.width and
                self.y <= projectile.y <= self.y + self.height):
            return True
        return False
