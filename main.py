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
from kivy.core.window import Window
from cannon import Cannon
from projectile import Bullet, Bombshell, Laser
from obstacles import Obstacle, Target
from levels import load_level
from kivy.uix.button import Button




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
        self.start_time = Clock.get_time()

        self.shoot_sound = SoundLoader.load('sounds/shoot.wav')
        self.explosion_sound = SoundLoader.load('sounds/explosion.wav')
        self.hit_target_sound = SoundLoader.load('sounds/hit_target.wav')

        with self.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(pos=self.pos, size=self.size)

        self.ui_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=50,
            pos_hint={'top': 1}
        )

        with self.ui_layout.canvas.before:
            Color(0.2, 0.2, 0.2, 0.8)
            Rectangle(size=self.ui_layout.size, pos=self.ui_layout.pos)
        self.ui_layout.bind(size=self._update_ui_background, pos=self._update_ui_background)

        self.score_label = Label(
            text=f"Punteggio: {self.score}",
            size_hint=(0.5, 1),
            font_size=20,
            color=(1, 1, 1, 1)
        )
        self.level_label = Label(
            text=f"Livello: {self.current_level}",
            size_hint=(0.5, 1),
            font_size=20,
            color=(1, 1, 1, 1)
        )

        self.ui_layout.add_widget(self.level_label)
        self.ui_layout.add_widget(self.score_label)

        self.add_widget(self.ui_layout)

        self.obstacles = []
        self.load_level(self.current_level)

        Clock.schedule_interval(self.update_cannon, 1.0 / 60.0)
        Window.bind(on_key_down=self.on_key_down)

        self.bind(size=self._update_ui_background, pos=self._update_ui_background)
        
    def _update_ui_background(self, *args):
        """
        Aggiorna lo sfondo del layout della UI.
        """
        for instruction in self.ui_layout.canvas.before.children:
            if isinstance(instruction, Rectangle):
                instruction.size = self.ui_layout.size
                instruction.pos = self.ui_layout.pos

    def load_level(self, level_num):
        """
        Carica il livello specifico.
        """
        self.current_level = level_num
        self.obstacles = load_level(level_num)
        self.update_ui()
        
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """
        Cambia il tipo di proiettile in base al tasto premuto.
        """
        if key == ord('1'):
            self.current_projectile_type = "bullet"
            print("Tipo di proiettile cambiato a: Bullet")
        elif key == ord('2'):
            self.current_projectile_type = "bombshell"
            print("Tipo di proiettile cambiato a: Bombshell")
        elif key == ord('3'):
            self.current_projectile_type = "laser"
            print("Tipo di proiettile cambiato a: Laser")
        else:
            print(f"Tasto non associato a un proiettile: {chr(key)}")

    def update_ui(self):
        """
        Aggiorna le informazioni dell'interfaccia utente per livello e punteggio.
        """
        self.score_label.text = f"Punteggio: {self.score}"
        self.level_label.text = f"Livello: {self.current_level}"

    def update_cannon(self, dt):
        """
        Aggiorna il cannone e la grafica della scena.
        """
        self.canvas.clear()
        with self.canvas:
            Color(0.2, 0.6, 0.8)
            Ellipse(pos=(self.cannon.position[0] - 15, self.cannon.position[1] - 15), size=(30, 30))
            Color(1, 1, 0)
            x1, y1 = self.cannon.position
            length = 100
            angle_rad = math.radians(self.cannon.angle)
            x2 = x1 + length * math.cos(angle_rad)
            y2 = y1 + length * math.sin(angle_rad)
            Line(points=[x1, y1, x2, y2], width=4)
        self.draw_obstacles()
        self.update_projectiles()
        self.update_ui()

    def draw_obstacles(self):
        """
        Disegna gli ostacoli con angoli arrotondati.
        """
        with self.canvas:
            for obstacle in self.obstacles:
                ox, oy = obstacle.position
                width, height = obstacle.width, obstacle.height
                radius = 10

                Color(0.3, 0.8, 0.3, 0.7)
                Rectangle(pos=(ox + radius, oy), size=(width - 2 * radius, height))
                Rectangle(pos=(ox, oy + radius), size=(width, height - 2 * radius))
                Ellipse(pos=(ox, oy), size=(2 * radius, 2 * radius))
                Ellipse(pos=(ox + width - 2 * radius, oy), size=(2 * radius, 2 * radius))
                Ellipse(pos=(ox, oy + height - 2 * radius), size=(2 * radius, 2 * radius))
                Ellipse(pos=(ox + width - 2 * radius, oy + height - 2 * radius), size=(2 * radius, 2 * radius))

                Color(0, 0.5, 0, 1)
                Line(rectangle=(ox + radius, oy, width - 2 * radius, height), width=2)
                Line(rectangle=(ox, oy + radius, width, height - 2 * radius), width=2)

    def update_projectiles(self):
        with self.canvas:
            for projectile in self.projectiles:
                x, y = projectile.position
                radius = projectile.radius

                if isinstance(projectile, Bullet):
                    Color(0, 0, 1, 1)
                    Ellipse(pos=(x - radius, y - radius), size=(2 * radius, 2 * radius))
                    Color(0, 0, 0, 0.8)
                    Line(circle=(x, y, radius), width=2)

                elif isinstance(projectile, Bombshell):
                    Color(1, 0, 0, 1)
                    Ellipse(pos=(x - radius * 1.5, y - radius * 1.5), size=(3 * radius, 3 * radius))
                    Color(1, 0.5, 0, 0.7)
                    Line(circle=(x, y, radius * 1.5), width=3)

                elif isinstance(projectile, Laser):
                    Color(0, 1, 0, 0.8)
                    Line(points=[x, y, x + 50, y], width=5)
                    Color(1, 1, 0, 0.6)
                    Line(points=[x, y, x + 50, y], width=8)

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

    def change_projectile_type(self, new_type):
        if new_type in ["bullet", "bombshell", "laser"]:
            self.current_projectile_type = new_type
            print(f"Tipo di proiettile cambiato a: {self.current_projectile_type}")
        else:
            print("Tipo di proiettile non valido!")
        
    def hit_target(self):
        """
        Incrementa il punteggio e passa al livello successivo se tutti i bersagli sono colpiti.
        """
        self.obstacles = [obstacle for obstacle in self.obstacles if not isinstance(obstacle, Target)]
        self.score += 100
        print(f"Livello {self.current_level} completato! Punteggio: {self.score}")
        print(len(self.obstacles), "lunghezza ostacoli rimasti")
        if not self.obstacles:
            self.current_level += 1
            self.load_level(self.current_level)

    def explode_effect(self, position):
        """
        Crea un effetto visivo di esplosione.
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

    def fire_projectile(self, projectile_type="bullet"):
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


class CannonGameApp(App):
    def build(self):
        widget = CannonWidget()
        return widget


if __name__ == '__main__':
    CannonGameApp().run()
