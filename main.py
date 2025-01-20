from tkinter import Button
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
import math
import random
from constants import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

import os   
os.environ["KIVY_METAL"] = "0"

import json
import os

SCORES_FILE = "scores.json"

def load_scores():
    """Carica i punteggi dal file."""
    if not os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "w") as f:
            json.dump({"scores": []}, f)

    with open(SCORES_FILE, "r") as f:
        data = json.load(f)
    return data.get("scores", [])

def save_score(name, score):
    """Salva un nuovo punteggio nel file."""
    scores = load_scores()
    scores.append({"name": name, "score": score})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    with open(SCORES_FILE, "w") as f:
        json.dump({"scores": scores}, f)

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
        Color(1, 0, 0, 1)
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
                    Color(0.5, 0.5, 0.5, 1)
                elif obstacle["type"] == "Mirror":
                    Color(0, 0, 1, 1)
                elif obstacle["type"] == "Perpetio":
                    Color(1, 0, 0, 1)
                elif obstacle["type"] == "Movable":
                    Color(0, 1, 0, 1)
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
                            self.obstacles.remove(obstacle)
                        elif obstacle["type"] == "Mirror" and proj["type"] == "Laser":
                            proj["vx"] = -proj["vx"]
                        elif obstacle["type"] == "Perpetio":
                            pass
                        elif obstacle["type"] == "Movable":
                            self.obstacles.remove(obstacle)

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
        """Mostra un messaggio di fine gioco e salva il punteggio."""
        self.clear_widgets()

        # Messaggio di fine gioco
        game_over_label = Label(
            text="Hai completato il gioco!\nInserisci il tuo nome:",
            size_hint=(0.8, 0.4),
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            font_size=24,
            halign="center"
        )
        self.add_widget(game_over_label)

        # Input per il nome del giocatore
        name_input = TextInput(
            hint_text="Inserisci il tuo nome",
            size_hint=(0.6, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            multiline=False
        )
        self.add_widget(name_input)

        # Bottone per salvare il punteggio
        save_button = Button(
            text="Salva Punteggio",
            size_hint=(0.3, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.3},
            font_size=20
        )
        save_button.bind(on_release=lambda instance: self.save_score(name_input.text))
        self.add_widget(save_button)

    def save_score(self, name):
        """Salva il punteggio e torna al menu principale."""
        save_score(name, self.game.score)
        self.app.show_menu()
            
    


class CannonApp(App):
    def build(self):
        self.menu = MainMenu(self)
        return self.menu
    
    def start_game(self):
        """Avvia il gioco rimuovendo il menu principale."""
        self.root.clear_widgets()
        self.game_layout = GameLayout()
        self.root.add_widget(self.game_layout)
        Window.bind(on_key_down=self.on_key_down)
        Clock.schedule_interval(self.game_layout.game.update, 1 / 60)
        
    def load_game(self):
        """Placeholder per la funzionalità di caricamento partita."""
        print("Caricamento partita in arrivo...")

    def show_hall_of_fame(self):
        """Placeholder per la funzionalità Hall of Fame."""
        print("Visualizzazione Hall of Fame in arrivo...")
        
    def show_help(self):
        """Mostra la schermata di Help."""
        self.root.clear_widgets()
        self.help_screen = HelpScreen(self)
        self.root.add_widget(self.help_screen)
        
    def show_menu(self):
        """Mostra il menu principale."""
        self.root.clear_widgets()
        self.menu = MainMenu(self)
        self.root.add_widget(self.menu)
        
    def show_hall_of_fame(self):
        """Mostra la schermata della Hall of Fame."""
        self.root.clear_widgets()
        self.hall_of_fame_screen = HallOfFameScreen(self)
        self.root.add_widget(self.hall_of_fame_screen)

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Intercetta l'evento da tastiera e lo invia al gioco."""
        if hasattr(self, 'game_layout'):
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
                self.game_layout.game.on_key_down(key_map[key])
                
class HelpScreen(FloatLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        instructions = Label(
            text=(
                "Benvenuto nel gioco Cannon!\n"
                "Istruzioni:\n"
                "- Freccia Su/Giù: Modifica l'angolo del cannone.\n"
                "- Tasto A/D: Modifica la potenza del cannone.\n"
                "- Spazio: Spara un proiettile.\n"
                "- Tasto Q/E: Cambia il tipo di proiettile.\n"
            ),
            size_hint=(0.8, 0.6),
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            font_size=20,
            halign="center",
            valign="middle"
        )
        instructions.bind(size=instructions.setter("text_size"))

        back_button = Button(
            text="Torna al Menu",
            size_hint=(0.3, 0.1),
            pos_hint={"center_x": 0.5, "y": 0.1},
            font_size=20
        )
        back_button.bind(on_release=self.back_to_menu)

        self.add_widget(instructions)
        self.add_widget(back_button)

    def back_to_menu(self, instance):
        """Torna al menu principale."""
        self.app.show_menu()

from kivy.uix.gridlayout import GridLayout
class HallOfFameScreen(FloatLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        title = Label(
            text="Hall of Fame",
            size_hint=(1, 0.2),
            pos_hint={"center_x": 0.5, "top": 1},
            font_size=30,
            halign="center"
        )
        self.add_widget(title)

        score_layout = GridLayout(cols=2, size_hint=(0.8, 0.6), pos_hint={"center_x": 0.5, "center_y": 0.5})
        scores = load_scores()

        for entry in scores:
            name_label = Label(text=entry["name"], font_size=20)
            score_label = Label(text=str(entry["score"]), font_size=20)
            score_layout.add_widget(name_label)
            score_layout.add_widget(score_label)

        self.add_widget(score_layout)

        back_button = Button(
            text="Torna al Menu",
            size_hint=(0.3, 0.1),
            pos_hint={"center_x": 0.5, "y": 0.1},
            font_size=20
        )
        back_button.bind(on_release=self.back_to_menu)
        self.add_widget(back_button)

    def back_to_menu(self, instance):
        """Torna al menu principale."""
        self.app.show_menu()

class MainMenu(FloatLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        layout = BoxLayout(orientation='vertical', spacing=20, size_hint=(0.5, 0.6), pos_hint={"center_x": 0.5, "center_y": 0.5})

        start_button = Button(
            text="Inizia Gioco",
            font_size=24,
            size_hint=(1, 0.2)
        )
        start_button.bind(on_release=self.start_game)

        load_button = Button(
            text="Carica Partita",
            font_size=24,
            size_hint=(1, 0.2)
        )
        load_button.bind(on_release=self.load_game)

        hall_of_fame_button = Button(
            text="Hall of Fame",
            font_size=24,
            size_hint=(1, 0.2)
        )
        hall_of_fame_button.bind(on_release=self.show_hall_of_fame)
        
        help_button = Button(
            text="Help",
            font_size=24,
            size_hint=(1, 0.2)
        )
        help_button.bind(on_release=self.show_help)

        exit_button = Button(
            text="Esci",
            font_size=24,
            size_hint=(1, 0.2)
        )
        exit_button.bind(on_release=self.exit_game)

        layout.add_widget(start_button)
        layout.add_widget(load_button)
        layout.add_widget(hall_of_fame_button)
        layout.add_widget(help_button)
        layout.add_widget(exit_button)

        self.add_widget(layout)

    def start_game(self, instance):
        self.app.start_game()

    def load_game(self, instance):
        print("Funzione di Carica Partita non ancora implementata.")

    def show_hall_of_fame(self, instance):
        print("Funzione di Hall of Fame non ancora implementata.")
        
    def show_help(self, instance):
        self.app.show_help()

    def exit_game(self, instance):
        """Chiude l'applicazione."""
        App.get_running_app().stop()

if __name__ == "__main__":
    CannonApp().run()

