from tkinter import Button
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from functools import partial
import math
import random
from constants import *

import os   
os.environ["KIVY_METAL"] = "0"

from kivy.config import Config
Config.set('graphics', 'borderless', '1')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', str(Window.width))
Config.set('graphics', 'height', str(Window.height))
class CannonGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (Window.width, Window.height)
        self.cannon_x = 50
        self.cannon_y = 100
        self.cannon_angle = 45
        self.cannon_power = 300
        self.projectiles = []
        self.obstacles = []
        self.targets = []
        self.score = 0
        self.current_level = 1
        self.total_levels = 10
        self.max_projectiles = 100
        self.remaining_projectiles = self.max_projectiles
        self.timer_max = 30
        self.timer = self.timer_max

        self.projectile_types = ["Bullet", "Bombshell", "Laser"]
        self.current_projectile_index = 0

        self.generate_level()
        Clock.schedule_interval(self.update_timer, 1) 

    def generate_level(self):
        """Genera ostacoli e target casualmente."""
        self.obstacles = []
        self.targets = []

        if self.current_level > self.total_levels:
            self.parent.show_game_over()
            return

        num_obstacles = random.randint(3, 6)
        num_targets = random.randint(2, 5)

        for _ in range(num_obstacles):
            while True:
                obstacle_x = random.randint(200, Window.width - 100)
                obstacle_y = random.randint(50, Window.height - 50)
                obstacle_type = random.choice(["Rock", "Mirror", "Perpetio", "Movable"])
                new_obstacle = {"x": obstacle_x, "y": obstacle_y, "width": 50, "height": 50, "type": obstacle_type}
                if not self.check_overlap(new_obstacle, self.obstacles):
                    self.obstacles.append(new_obstacle)
                    break

        for _ in range(num_targets):
            while True:
                target_x = random.randint(200, Window.width - 100)
                target_y = random.randint(50, Window.height - 50)
                new_target = {"x": target_x, "y": target_y, "radius": 20}
                if not self.check_overlap_with_targets(new_target, self.obstacles):
                    self.targets.append(new_target)
                    break
                
        self.remaining_projectiles = self.max_projectiles
        self.timer = self.timer_max
        if self.parent:
            self.parent.update_projectiles(self.remaining_projectiles)
            self.parent.update_timer(self.timer)
        
    def update_timer(self, dt):
        if self.timer > 0:
            self.timer -= 1
            if self.parent:
                self.parent.update_timer(self.timer)
        else:
            if self.parent:
                self.parent.show_level_failed("Tempo scaduto!")

    def check_overlap(self, rect, others):
        """Verifica sovrapposizione tra rettangoli."""
        for other in others:
            if (rect["x"] < other["x"] + other["width"] and
                rect["x"] + rect["width"] > other["x"] and
                rect["y"] < other["y"] + other["height"] and
                rect["y"] + rect["height"] > other["y"]):
                return True
        return False

    def check_overlap_with_targets(self, target, obstacles):
        """Verifica che un target non si sovrapponga a ostacoli."""
        for obstacle in obstacles:
            if (target["x"] + target["radius"] > obstacle["x"] and
                target["x"] - target["radius"] < obstacle["x"] + obstacle["width"] and
                target["y"] + target["radius"] > obstacle["y"] and
                target["y"] - target["radius"] < obstacle["y"] + obstacle["height"]):
                return True
        return False

    def fire_projectile(self):
        if self.remaining_projectiles <= 0 and self.parent:
            self.parent.show_level_failed("Proiettili esauriti!")
            return

        self.remaining_projectiles -= 1
        if self.parent:
            self.parent.update_projectiles(self.remaining_projectiles)

        projectile_type = self.projectile_types[self.current_projectile_index]
        angle_rad = math.radians(self.cannon_angle)
        vx = self.cannon_power * math.cos(angle_rad)
        vy = self.cannon_power * math.sin(angle_rad)

        if projectile_type == "Bullet":
            radius = BULLET_RADIUS
        elif projectile_type == "Bombshell":
            radius = BOMB_RADIUS
        elif projectile_type == "Laser":
            radius = 5
            vx *= 2
        else:
            radius = 10

        self.projectiles.append({
            "x": self.cannon_x,
            "y": self.cannon_y,
            "vx": vx,
            "vy": vy,
            "radius": radius,
            "type": projectile_type
        })

    def update(self, dt):
        """Aggiorna lo stato del gioco."""
        self.canvas.clear()
        Color(1, 0, 0, 1)  # Colore rosso
        Line(rectangle=(0, 0, Window.width, Window.height), width=2)
        with self.canvas:
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=(0, 0), size=(self.width, self.height))

            Color(*CANNON_COLOR)
            Ellipse(pos=(self.cannon_x - 10, self.cannon_y - 10), size=(20, 20))
            Line(points=[
                self.cannon_x,
                self.cannon_y,
                self.cannon_x + 50 * math.cos(math.radians(self.cannon_angle)),
                self.cannon_y + 50 * math.sin(math.radians(self.cannon_angle)),
            ], width=2)

            for obstacle in self.obstacles:
                if obstacle["type"] == "Rock":
                    Color(0.5, 0.5, 0.5, 1)  # Grigio per Rock
                elif obstacle["type"] == "Mirror":
                    Color(0, 0, 1, 1)  # Blu per Mirror
                elif obstacle["type"] == "Perpetio":
                    Color(1, 0, 0, 1)  # Rosso per Perpetio
                elif obstacle["type"] == "Movable":
                    Color(0, 1, 0, 1)  # Verde per Movable Block
                Rectangle(pos=(obstacle["x"], obstacle["y"]), size=(obstacle["width"], obstacle["height"]))


            for target in self.targets:
                target["y"] += math.sin(target["x"] + Clock.get_time() * 2) * 2
                if target["y"] < 0:
                    target["y"] = 0
                elif target["y"] + target["radius"] * 2 > Window.height:
                    target["y"] = Window.height - target["radius"] * 2
                Color(*TARGET_COLOR)
                Ellipse(pos=(target["x"] - target["radius"], target["y"] - target["radius"]),
                        size=(target["radius"] * 2, target["radius"] * 2))

            for proj in self.projectiles[:]:
                proj["x"] += proj["vx"] * dt
                proj["y"] += proj["vy"] * dt
                if proj["type"] != "Laser":
                    proj["vy"] -= GRAVITY * dt
                proj["vy"] -= GRAVITY * dt
                Color(*PROJECTILE_COLOR)
                Ellipse(pos=(proj["x"] - proj["radius"], proj["y"] - proj["radius"]),
                        size=(proj["radius"] * 2, proj["radius"] * 2))

                for obstacle in self.obstacles:
                    if self.check_collision_with_obstacle(proj, obstacle):
                        if obstacle["type"] == "Rock":
                            self.obstacles.remove(obstacle)  # Distruggi Rock
                        elif obstacle["type"] == "Mirror" and proj["type"] == "Laser":
                            proj["vx"] = -proj["vx"]  # Riflette il laser invertendo la direzione orizzontale
                        elif obstacle["type"] == "Perpetio":
                            pass  # Perpetio è indistruttibile, non succede nulla
                        elif obstacle["type"] == "Movable":
                            self.obstacles.remove(obstacle)  # Distruggi il Movable Block

                        self.projectiles.remove(proj)
                        break


                for target in self.targets[:]:
                    if self.check_collision_with_target(proj, target):
                        self.targets.remove(target)
                        self.score += 50
                        if self.parent:
                            self.parent.update_score(self.score)
                        self.projectiles.remove(proj)
                        break

                if proj["y"] < 0 or proj["x"] > Window.width:
                    self.projectiles.remove(proj)

        if not self.targets:
            self.next_level()

    def check_collision_with_obstacle(self, proj, obstacle):
        """Verifica collisione con un ostacolo."""
        return (obstacle["x"] <= proj["x"] <= obstacle["x"] + obstacle["width"] and
                obstacle["y"] <= proj["y"] <= obstacle["y"] + obstacle["height"])

    def check_collision_with_target(self, proj, target):
        """Verifica collisione con un target."""
        dist = math.sqrt((proj["x"] - target["x"]) ** 2 + (proj["y"] - target["y"]) ** 2)
        return dist <= target["radius"]

    def change_projectile_type(self, direction):
        """Cambia il tipo di proiettile."""
        if direction == "next":
            self.current_projectile_index = (self.current_projectile_index + 1) % len(self.projectile_types)
        elif direction == "previous":
            self.current_projectile_index = (self.current_projectile_index - 1) % len(self.projectile_types)
        self.parent.update_projectile_type(self.projectile_types[self.current_projectile_index])

    def next_level(self):
        """Passa al livello successivo o termina il gioco."""
        self.current_level += 1
        if self.current_level > self.total_levels:
            self.parent.show_game_over()
        else:
            self.parent.update_level(self.current_level)
            self.generate_level()

    def on_key_down(self, keycode):
        """Gestisce gli input da tastiera."""
        if keycode == 'up':
            self.cannon_angle = min(self.cannon_angle + ANGLE_STEP, 90)
        elif keycode == 'down':
            self.cannon_angle = max(self.cannon_angle - ANGLE_STEP, 0)
        elif keycode == 'a':
            self.cannon_power = max(self.cannon_power - CANNON_POWER_STEP, 10)
        elif keycode == 'd':
            self.cannon_power = min(self.cannon_power + CANNON_POWER_STEP, 300)
        elif keycode == 'spacebar':
            self.fire_projectile()
        elif keycode == 'q':
            self.change_projectile_type("previous")
        elif keycode == 'e':
            self.change_projectile_type("next")


class GameLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = CannonGame()
        self.add_widget(self.game)

        self.score_label = Label(
            text="Punteggio: 0",
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.8, "top": 1},
            font_size=20,
            color=(1, 1, 1, 1),
        )
        self.add_widget(self.score_label)

        self.projectile_type_label = Label(
            text="Proiettile: Bullet",
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.8, "y": 0},
            font_size=20,
            color=(1, 1, 1, 1),
        )
        self.add_widget(self.projectile_type_label)

        self.instructions_label = Label(
            text="Freccia Su/Giù: Angolo | A/D: Potenza | Spazio: Spara | Q/E: Cambia Proiettile",
            size_hint=(0.8, 0.1),
            pos_hint={"x": 0.1, "y": 0.05},
            font_size=16,
            color=(1, 1, 1, 1),
        )
        self.add_widget(self.instructions_label)

        self.level_label = Label(
            text="Livello: 1",
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.0, "top": 1},
            font_size=20,
            color=(1, 1, 1, 1),
        )
        self.add_widget(self.level_label)
        
        self.projectiles_label = Label(
            text="Proiettili: 10",
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.6, "y": 0},
            font_size=20,
            color=(1, 1, 1, 1),
        )
        self.add_widget(self.projectiles_label)

        self.timer_label = Label(
            text="Timer: 30",
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.4, "y": 0},
            font_size=20,
            color=(1, 1, 1, 1),
        )
        self.add_widget(self.timer_label)
    
    def show_level_failed(self, message):
        print("Il livello è fallito")
        # crea un bottone per ricominciare il gioco ma prima cambia finestra
        self.clear_widgets()
        
        self.game.canvas.clear()
        with self.game.canvas:
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))
        game_over_label = Label(
            text=message,
            size_hint=(0.8, 0.4),
            pos_hint={"x": 0.1, "y": 0.3},
            font_size=30,
            color=(1, 1, 1, 1),
        )
        self.add_widget(game_over_label)
         

    def restart_game(self, instance):
        """Resetta il gioco e ricomincia dal primo livello."""
        self.clear_widgets()
        self.__init__() 

    def update_score(self, score):
        """Aggiorna il punteggio."""
        self.score_label.text = f"Punteggio: {score}"
        
    def update_projectiles(self, remaining_projectiles):
        self.projectiles_label.text = f"Proiettili: {remaining_projectiles}"

    def update_timer(self, timer):
        """Aggiorna il timer."""
        self.timer_label.text = f"Timer: {timer}"


    def update_projectile_type(self, projectile_type):
        """Aggiorna il tipo di proiettile."""
        self.projectile_type_label.text = f"Proiettile: {projectile_type}"

    def update_level(self, level):
        """Aggiorna il livello."""
        self.level_label.text = f"Livello: {level}"

    def show_game_over(self):
        """Mostra un messaggio di fine gioco."""
        game_over_label = Label(
            text="Hai completato il gioco!",
            size_hint=(0.8, 0.4),
            pos_hint={"x": 0.1, "y": 0.3},
            font_size=30,
            color=(1, 1, 1, 1),
        )
        self.add_widget(game_over_label)


class CannonApp(App):
    def build(self):
        layout = GameLayout()
        Window.bind(on_key_down=self.on_key_down)
        Clock.schedule_interval(layout.game.update, 1 / 60)
        return layout

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Intercetta l'evento da tastiera e lo invia al gioco."""
        key_map = {
            273: 'up',
            274: 'down',
            97: 'a',
            100: 'd',
            32: 'spacebar',
            113: 'q',
            101: 'e',
        }
        if key in key_map:
            self.root.game.on_key_down(key_map[key])


if __name__ == "__main__":
    CannonApp().run()

