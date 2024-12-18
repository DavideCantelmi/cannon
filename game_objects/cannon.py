
class Cannon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 45
        self.power = 50

    def adjust_angle(self, delta):
        """Modifica l'angolo del cannone."""
        self.angle += delta
        self.angle = max(0, min(self.angle, 90))

    def adjust_power(self, delta):
        """Modifica la potenza del cannone."""
        self.power += delta
        self.power = max(10, min(self.power, 100))

    def get_state(self):
        """Ritorna lo stato del cannone."""
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "power": self.power,
        }
