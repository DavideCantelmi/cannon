
class Target:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def check_hit(self, projectile):
        """Verifica se il proiettile colpisce il bersaglio."""
        dist = ((self.x - projectile.x) ** 2 + (self.y - projectile.y) ** 2) ** 0.5
        return dist <= self.radius
