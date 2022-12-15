class Monster:

    def __init__(self, health: float, attack: float):
        self.base_health = health
        self.health = health
        self.attack = attack
        
        self.level = health + attack
        self.lifetime = 1
        