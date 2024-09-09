
class Obstacle:
    def __init__(self, position, width, height):
        """
        Inizializza un ostacolo.

        :param position: La posizione dell'ostacolo (x, y).
        :param width: La larghezza dell'ostacolo.
        :param height: L'altezza dell'ostacolo.
        """
        self.position = position
        self.width = width
        self.height = height

    def check_collision(self, projectile):
        """
        Verifica se il proiettile collide con l'ostacolo.

        :param projectile: L'oggetto proiettile.
        :return: True se c'è una collisione, False altrimenti.
        """
        x, y = projectile.position
        ox, oy = self.position
        if ox <= x <= ox + self.width and oy <= y <= oy + self.height:
            return True
        return False


class Target(Obstacle):
    def __init__(self, position, width=30, height=30):
        """
        Il bersaglio del gioco, che deve essere colpito dal proiettile.
        """
        super().__init__(position, width, height)

    def hit(self):
        """
        Azione da eseguire quando il bersaglio viene colpito.
        """
        print("Bersaglio colpito!")
