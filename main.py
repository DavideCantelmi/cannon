from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
import math
from cannon import Cannon
from projectile import Bullet, Bombshell, Laser
from obstacles import Obstacle, Target
from levels import load_level


class CannonWidget(FloatLayout):
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

        # Suoni
        self.shoot_sound = SoundLoader.load('sounds/shoot.wav')
        self.explosion_sound = SoundLoader.load('sounds/explosion.wav')
        self.hit_target_sound = SoundLoader.load('sounds/hit_target.wav')

        # UI
        self.ui_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
        self.score_label = Label(text=f"Punteggio: {self.score}", size_hint=(0.5, 1))
        self.timer_label = Label(text="Tempo: 0", size_hint=(0.5, 1))
        self.ui_layout.add_widget(self.score_label)
        self.ui_layout.add_widget(self.timer_label)

        self.add_widget(self.ui_layout)

        # Aggiungi sfondo
        self.background = Image(source='background.jpg', allow_stretch=True, keep_ratio=False)
        self.background.size_hint = (1, 1)
        self.add_widget(self.background)

        Clock.schedule_interval(self.update_cannon, 1.0 / 60.0)

    def load_level(self, level_num):
        """
        Carica gli ostacoli e i bersagli per il livello.
        """
        self.obstacles = load_level(level_num)

    def update_cannon(self, dt):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1)

            # Linea del cannone
            x1, y1 = self.cannon.position
            length = 100
            angle_rad = math.radians(self.cannon.angle)

            x2 = x1 + length * math.cos(angle_rad)
            y2 = y1 + length * math.sin(angle_rad)

            Line(points=[x1, y1, x2, y2], width=3)

        self.draw_obstacles()
        self.update_projectiles()
        self.update_timer()

    def draw_obstacles(self):
        """
        Disegna gli ostacoli e il bersaglio sullo schermo.
        """
        with self.canvas:
            for obstacle in self.obstacles:
                Color(0, 1, 0)
                ox, oy = obstacle.position
                Rectangle(pos=(ox, oy), size=(obstacle.width, obstacle.height))

    def update_projectiles(self):
        with self.canvas:
            for projectile in self.projectiles:
                Color(1, 0, 0)
                projectile.update(1 / 60.0)
                
                for obstacle in self.obstacles[:]:
                    if obstacle.check_collision(projectile):
                        if isinstance(projectile, Bombshell):
                            self.explode_effect(projectile.position)
                            if self.explosion_sound:
                                self.explosion_sound.play()
                        elif isinstance(projectile, Laser):
                            projectile.reflect()

                        if isinstance(obstacle, Target):
                            obstacle.hit()
                            if self.hit_target_sound:
                                self.hit_target_sound.play()
                            self.hit_target()

                        if obstacle in self.obstacles:
                            self.obstacles.remove(obstacle)
                        
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                        break
                    
                x, y = projectile.position
                Ellipse(pos=(x - projectile.radius, y - projectile.radius),
                        size=(2 * projectile.radius, 2 * projectile.radius))

    
    def update_timer(self):
        """
        Aggiorna il tempo nella UI in tempo reale.
        """
        current_time = Clock.get_time()
        time_elapsed = int(current_time - self.start_time)
        self.timer_label.text = f"Tempo: {time_elapsed}"

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

        self.score_label.text = f"Punteggio: {self.score}"

        self.current_level += 1
        self.load_level(self.current_level)
        self.shots_fired = 0
        self.start_time = Clock.get_time()

    def explode_effect(self, position):
        """
        Crea un effetto di esplosione visiva alla posizione specificata.
        """
        with self.canvas:
            Color(1, 0.5, 0)
            Ellipse(pos=(position[0] - 30, position[1] - 30), size=(60, 60))

    def on_touch_move(self, touch):
        if self.last_touch_y is None:
            self.last_touch_y = touch.y

        delta_y = touch.y - self.last_touch_y
        self.last_touch_y = touch.y

        delta_angle = delta_y * self.sensitivity
        self.cannon.adjust_angle(delta_angle)

        self.update_cannon(0)

    def on_touch_up(self, touch):
        self.last_touch_y = None

    def on_touch_down(self, touch):
        self.fire_projectile("bombshell")


class CannonGameApp(App):
    def build(self):
        widget = CannonWidget()
        return widget


if __name__ == '__main__':
    CannonGameApp().run()
