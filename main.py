
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import math
from cannon import Cannon
from projectile import Bullet, Bombshell, Laser
from obstacles import Obstacle, Target
from levels import load_level

class CannonWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cannon = Cannon(position=(50, 50))
        self.sensitivity = 0.2
        self.last_touch_y = None
        self.projectiles = []
        
        self.score = 0
        self.shots_fired = 0
        self.current_level = 1
        self.load_level(self.current_level)
        self.start_time = Clock.get_time()
        
        self.shoot_sound = SoundLoader.load('sounds/shoot.wav')
        self.explosion_sound = SoundLoader.load('sounds/explosion.wav')
        self.hit_target_sound = SoundLoader.load('sounds/hit_target.wav')

        self.update_cannon()

    def load_level(self, level_num):
        """
        Carica gli ostacoli e i bersagli per il livello.
        """
        self.obstacles = load_level(level_num)

    def update_cannon(self):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1)

            x1, y1 = self.cannon.position
            length = 100
            angle_rad = math.radians(self.cannon.angle)

            x2 = x1 + length * math.cos(angle_rad)
            y2 = y1 + length * math.sin(angle_rad)

            Line(points=[x1, y1, x2, y2], width=2)

        self.draw_obstacles()

        self.update_projectiles()

    def draw_obstacles(self):
        """
        Disegna gli ostacoli e il bersaglio sullo schermo.
        """
        with self.canvas:
            Color(0, 1, 0)
            for obstacle in self.obstacles:
                ox, oy = obstacle.position
                Line(rectangle=(ox, oy, obstacle.width, obstacle.height))

    def update_projectiles(self):
        with self.canvas:
            Color(1, 0, 0)
            for projectile in self.projectiles:
                projectile.update(1 / 60.0)
                
                for obstacle in self.obstacles:
                    if obstacle.check_collision(projectile):
                        if isinstance(projectile, Bombshell):
                            projectile.explode()
                            if self.explosion_sound:
                                self.explosion_sound.play()
                        elif isinstance(projectile, Laser):
                            projectile.reflect()
                        if isinstance(obstacle, Target):
                            obstacle.hit()
                            if self.hit_target_sound:
                                self.hit_target_sound.play()
                            self.hit_target()
                        self.projectiles.remove(projectile)
                        break
                
                x, y = projectile.position
                Line(circle=(x, y, projectile.radius))

    def fire_projectile(self, projectile_type="bullet"):
        """
        Spara un nuovo proiettile in base al tipo.
        
        :param projectile_type: Il tipo di proiettile ("bullet", "bombshell", "laser").
        """
        velocity = self.cannon.velocity
        angle = self.cannon.angle
        
        if projectile_type == "bullet":
            new_projectile = Bullet(self.cannon.position, velocity, angle)
        elif projectile_type == "bombshell":
            new_projectile = Bombshell(self.cannon.position, velocity, angle)
        elif projectile_type == "laser":
            new_projectile = Laser(self.cannon.position, velocity, angle)
        
        if self.shoot_sound:
            self.shoot_sound.play()
        
        self.projectiles.append(new_projectile)
        self.shots_fired += 1

    def hit_target(self):
        """
        Azione da eseguire quando il bersaglio viene colpito. Calcola il punteggio e passa al livello successivo.
        """
        end_time = Clock.get_time()
        time_taken = end_time - self.start_time
        
        self.score += max(0, 1000 - (self.shots_fired * 100 + int(time_taken)))
        print(f"Livello {self.current_level} completato! Punteggio: {self.score}")

        self.current_level += 1
        self.load_level(self.current_level)
        self.shots_fired = 0
        self.start_time = Clock.get_time()

    def on_touch_move(self, touch):
        if self.last_touch_y is None:
            self.last_touch_y = touch.y

        delta_y = touch.y - self.last_touch_y
        self.last_touch_y = touch.y

        delta_angle = delta_y * self.sensitivity
        self.cannon.adjust_angle(delta_angle)

        self.update_cannon()

    def on_touch_up(self, touch):
        self.last_touch_y = None

    def on_touch_down(self, touch):
        self.fire_projectile("bombshell")


class CannonGameApp(App):
    def build(self):
        widget = CannonWidget()

        Clock.schedule_interval(lambda dt: widget.update_cannon(), 1.0 / 60.0)

        return widget


if __name__ == '__main__':
    CannonGameApp().run()
