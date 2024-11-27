import math

class Cannon:
    def __init__(self, position, angle=45, velocity=100):
        """
        Inizializzazione della classe Cannon.

        :param position: La posizione del cannone sullo schermo (es. (x, y)).
        :param angle: L'angolo di elevazione del cannone in gradi.
        :param velocity: La velocità iniziale del proiettile.
        """
        self.position = position
        self.angle = angle
        self.velocity = velocity

    def adjust_angle(self, delta_angle):
        """
        Modifica l'angolo del cannone.

        :param delta_angle: Cambiamento nell'angolo (positivo o negativo).
        """
        self.angle += delta_angle
        if self.angle < 0:
            self.angle = 0
        elif self.angle > 90:
            self.angle = 90

    def adjust_velocity(self, delta_velocity):
        """
        Modifica la velocità del proiettile.

        :param delta_velocity: Cambiamento nella velocità (positivo o negativo).
        """
        self.velocity += delta_velocity
        if self.velocity < 10:
            self.velocity = 10
        elif self.velocity > 500:
            self.velocity = 500

    def fire(self):
        """
        Calcola la traiettoria del proiettile e restituisce la velocità iniziale nei componenti x e y.

        :return: Una tupla con le componenti della velocità (vx, vy).
        """
        angle_rad = math.radians(self.angle)

        vx = self.velocity * math.cos(angle_rad)
        vy = self.velocity * math.sin(angle_rad)

        return vx, vy

