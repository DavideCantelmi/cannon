
import math

class Projectile:
    def __init__(self, position, velocity, angle, mass, radius, gravity=9.81):
        """
        Inizializza un proiettile con parametri di base.
        
        :param position: Posizione iniziale (x, y).
        :param velocity: Velocità iniziale.
        :param angle: Angolo in gradi.
        :param mass: Massa del proiettile.
        :param radius: Raggio d'azione (danno).
        :param gravity: Accelerazione di gravità.
        """
        self.position = list(position)
        self.velocity = velocity
        self.angle = math.radians(angle)
        self.mass = mass
        self.radius = radius
        self.gravity = gravity

        self.vx = self.velocity * math.cos(self.angle)
        self.vy = self.velocity * math.sin(self.angle)

    def update(self, dt):
        """
        Aggiorna la posizione del proiettile nel tempo dt.
        
        :param dt: Delta time (tempo trascorso tra un frame e l'altro).
        """
        self.vy -= self.gravity * dt
        
        self.position[0] += self.vx * dt
        self.position[1] += self.vy * dt

class Bullet(Projectile):
    def __init__(self, position, velocity, angle):
        """
        Proiettile di tipo Bullet con una massa e raggio fissi.
        """
        super().__init__(position, velocity, angle, mass=10, radius=5)

class Bombshell(Projectile):
    def __init__(self, position, velocity, angle):
        """
        Proiettile di tipo Bombshell con una massa maggiore e raggio di esplosione più grande.
        """
        super().__init__(position, velocity, angle, mass=20, radius=10)

    def explode(self):
        print("Bombshell esplosa! Danno ad area")

class Laser(Projectile):
    def __init__(self, position, velocity, angle):
        """
        Proiettile di tipo Laser, non influenzato dalla gravità.
        """
        super().__init__(position, velocity, angle, mass=0, radius=2, gravity=0)

    def update(self, dt):
        """
        Aggiorna la posizione del laser (solo linea retta, senza gravità).
        """
        self.position[0] += self.vx * dt
        self.position[1] += self.vy * dt

    def reflect(self):
        """
        Rimbalza contro un ostacolo riflettente (es. specchi).
        """
        self.vx = -self.vx
        print("Laser riflesso!")
