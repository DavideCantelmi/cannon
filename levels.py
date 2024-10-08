# levels.py

from obstacles import Obstacle, Target

def load_level(level_num):
    """
    Carica gli ostacoli e i bersagli per il livello dato.
    
    :param level_num: Il numero del livello.
    :return: Una lista di ostacoli e bersagli.
    """
    if level_num == 1:
        return [
            Obstacle(position=(400, 200), width=50, height=50),
            Target(position=(700, 300))
        ]
    elif level_num == 2:
        return [
            Obstacle(position=(300, 150), width=100, height=20),
            Obstacle(position=(500, 250), width=50, height=50),
            Target(position=(750, 350))
        ]
    # Da qui si possono aggiungere altri livelli andando a creare un nuovo set di dati
    # Quello che bisogna fare è aggiungere tanti altri elif come quelli sopra, con i dati
    # degli ostacoli e dei bersagli per ogni livello.
