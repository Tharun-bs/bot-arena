import pygame
import math
import random
import time
from enum import Enum
from typing import List, Optional

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
ARENA_WIDTH = 800
ARENA_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 107, 107)
BLUE = (78, 205, 196)
GREEN = (69, 183, 209)
YELLOW = (249, 202, 36)
PURPLE = (108, 92, 231)
ORANGE = (238, 90, 36)
GRAY = (128, 128, 128)
DARK_BLUE = (26, 26, 46)

class BotType(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    SNEAKY = "sneaky"
    BERSERKER = "berserker"

class Bot:
    """Main Bot class demonstrating OOP principles"""
    
    def __init__(self, x: float, y: float, color: tuple, name: str, bot_type: BotType):
        # Position and movement
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.direction = random.uniform(0, 2 * math.pi)
        
        # Visual properties
        self.color = color
        self.name = name
        self.bot_type = bot_type
        self.size = 20
        
        # Combat stats
        self.health = 100
        self.max_health = 100
        self.damage = 15
        self.speed = 2.0
        self.range = 150
        self.fire_rate = 60  # frames between shots
        self.last_shot = 0
        
        # AI state
        self.target: Optional['Bot'] = None
        self.last_target_update = 0
        self.turn_speed = 0.1
        
        # Customize stats based on type
        self._customize_stats()
    
    def _customize_stats(self):
        """Customize bot stats based on type"""
        if self.bot_type == BotType.BERSERKER:
            self.speed = 3.0
            self.damage = 25
            self.max_health = 60
            self.health = 60
        elif self.bot_type == BotType.DEFENSIVE:
            self.health = 120
            self.max_health = 120
            self.speed = 1.5
        elif self.bot_type == BotType.SNEAKY:
            self.speed = 2.5
            self.fire_rate = 45
    
    def update(self, bots: List['Bot']):
        """Main AI update loop"""
        if self.health <= 0:
            return
        
        self.last_shot += 1
        self.last_target_update += 1
        
        # Find target every 30 frames
        if self.last_target_update > 30:
            self._find_target(bots)
            self.last_target_update = 0
        
        # Execute behavior based on type
        if self.bot_type == BotType.AGGRESSIVE:
            self._aggressive_behavior()
        elif self.bot_type == BotType.DEFENSIVE:
            self._defensive_behavior()
        elif self.bot_type == BotType.SNEAKY:
            self._sneaky_behavior()
        elif self.bot_type == BotType.BERSERKER:
            self._berserker_behavior()
        
        self._move()
        self._constrain_to_bounds()
    
    def _find_target(self, bots: List['Bot']):
        """AI target selection logic"""
        closest = None
        closest_dist = float('inf')
        
        for bot in bots:
            if bot == self or bot.health <= 0:
                continue
            
            dist = self._distance_to(bot)
            if dist < closest_dist:
                closest = bot
                closest_dist = dist
        
        self.target = closest
    
    def _aggressive_behavior(self):
        """Aggressive AI - direct pursuit and attack"""
        if self.target:
            angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
            self.direction = angle
            
            if self._distance_to(self.target) < self.range:
                return self._shoot()
        return None
    
    def _defensive_behavior(self):
        """Defensive AI - maintain distance, strategic retreat"""
        if self.target:
            dist = self._distance_to(self.target)
            angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
            
            if dist < 100:
                # Retreat
                self.direction = angle + math.pi
            elif dist < self.range:
                # Shoot while maintaining distance
                projectile = self._shoot()
                self.direction += random.uniform(-0.2, 0.2)
                return projectile
        return None
    
    def _sneaky_behavior(self):
        """Sneaky AI - circle targets, careful approach"""
        if self.target:
            dist = self._distance_to(self.target)
            
            if self.range > dist > 80:
                # Circle around target
                angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
                self.direction = angle + math.pi/2
                return self._shoot()
            else:
                # Approach carefully
                angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
                self.direction = angle
                self.speed = 1.0  # Move slower when approaching
        return None
    
    def _berserker_behavior(self):
        """Berserker AI - high damage, fast movement, direct assault"""
        if self.target:
            angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
            self.direction = angle
            
            if self._distance_to(self.target) < self.range:
                return self._shoot()
        return None
    
    def _shoot(self) -> Optional['Projectile']:
        """Create a projectile if ready to shoot"""
        if self.last_shot < self.fire_rate or not self.target:
            return None
        
        angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
        self.last_shot = 0
        return Projectile(self.x, self.y, angle, self.damage, self)
    
    def _move(self):
        """Update position based on direction and speed"""
        self.vx = math.cos(self.direction) * self.speed
        self.vy = math.sin(self.direction) * self.speed
        
        self.x += self.vx
        self.y += self.vy
    
    def _constrain_to_bounds(self):
        """Keep bot within arena bounds"""
        self.x = max(self.size, min(ARENA_WIDTH - self.size, self.x))
        self.y = max(self.size, min(ARENA_HEIGHT - self.size, self.y))
    
    def take_damage(self, damage: int, attacker: 'Projectile'):
        """Handle taking damage from projectiles"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            return f"{self.name} destroyed by {attacker.owner.name}!"
        return f"{self.name} takes {damage} damage!"
    
    def _distance_to(self, other: 'Bot') -> float:
        """Calculate distance to another bot"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def draw(self, screen: pygame.Surface):
        """Render the bot on screen"""
        if self.health <= 0:
            return
        
        # Draw bot body
        bot_rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        pygame.draw.rect(screen, self.color, bot_rect)
        
        # Draw direction indicator
        end_x = self.x + math.cos(self.direction) * (self.size//2 + 5)
        end_y = self.y + math.sin(self.direction) * (self.size//2 + 5)
        pygame.draw.line(screen, WHITE, (self.x, self.y), (end_x, end_y), 3)
        
        # Draw health bar
        bar_width = self.size * 1.5
        bar_height = 4
        health_percent = self.health / self.max_health
        
        # Background bar
        bar_rect = pygame.Rect(self.x - bar_width//2, self.y - self.size - 10, bar_width, bar_height)
        pygame.draw.rect(screen, RED, bar_rect)
        
        # Health bar
        health_rect = pygame.Rect(self.x - bar_width//2, self.y - self.size - 10, 
                                bar_width * health_percent, bar_height)
        pygame.draw.rect(screen, GREEN, health_rect)
        
        # Draw name
        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y + self.size + 15))
        screen.blit(text, text_rect)

class Projectile:
    """Projectile class for bot weapons"""
    
    def __init__(self, x: float, y: float, angle: float, damage: int, owner: Bot):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * 5
        self.vy = math.sin(angle) * 5
        self.damage = damage
        self.owner = owner
        self.life = 120  # frames
        self.size = 3
    
    def update(self, bots: List[Bot]) -> tuple[bool, Optional[str]]:
        """Update projectile position and check collisions"""
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
        # Check collision with bots
        for bot in bots:
            if bot == self.owner or bot.health <= 0:
                continue
            
            dist = math.sqrt((self.x - bot.x)**2 + (self.y - bot.y)**2)
            if dist < bot.size:
                message = bot.take_damage(self.damage, self)
                return False, message  # Projectile destroyed
        
        # Check bounds
        if (self.x < 0 or self.x > ARENA_WIDTH or 
            self.y < 0 or self.y > ARENA_HEIGHT or 
            self.life <= 0):
            return False, None
        
        return True, None
    
    def draw(self, screen: pygame.Surface):
        """Render projectile"""
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)

class GameArena:
    """Main game class managing the arena"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("AI Bot Arena - Python Version")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.running = True
        self.game_active = False
        self.bots: List[Bot] = []
        self.projectiles: List[Projectile] = []
        self.messages: List[tuple[str, float]] = []
        self.winner: Optional[Bot] = None
        
        self._initialize_bots()
    
    def _initialize_bots(self):
        """Create initial bots with different types"""
        bot_configs = [
            (100, 100, RED, "Aggressor", BotType.AGGRESSIVE),
            (700, 100, BLUE, "Guardian", BotType.DEFENSIVE),
            (100, 500, GREEN, "Shadow", BotType.SNEAKY),
            (700, 500, YELLOW, "Berserker", BotType.BERSERKER),
            (400, 300, PURPLE, "Hunter", BotType.AGGRESSIVE)
        ]
        
        self.bots = [Bot(x, y, color, name, bot_type) 
                    for x, y, color, name, bot_type in bot_configs]
        
        self._add_message("Arena initialized with 5 bots!")
    
    def _add_message(self, text: str):
        """Add a message to the game log"""
        self.messages.append((text, time.time()))
        # Keep only last 10 messages
        if len(self.messages) > 10:
            self.messages.pop(0)
        print(f"[ARENA] {text}")
    
    def update(self):
        """Main game update loop"""
        if not self.game_active or self.winner:
            return
        
        # Update bots
        for bot in self.bots:
            bot.update(self.bots)
        
        # Update projectiles
        new_projectiles = []
        for projectile in self.projectiles:
            alive, message = projectile.update(self.bots)
            if alive:
                new_projectiles.append(projectile)
            elif message:
                self._add_message(message)
        
        # Add new projectiles from bots
        for bot in self.bots:
            if bot.health > 0:
                new_proj = None
                if bot.bot_type == BotType.AGGRESSIVE:
                    new_proj = bot._aggressive_behavior()
                elif bot.bot_type == BotType.DEFENSIVE:
                    new_proj = bot._defensive_behavior()
                elif bot.bot_type == BotType.SNEAKY:
                    new_proj = bot._sneaky_behavior()
                elif bot.bot_type == BotType.BERSERKER:
                    new_proj = bot._berserker_behavior()
                
                if new_proj:
                    new_projectiles.append(new_proj)
                    self._add_message(f"{bot.name} fires at {bot.target.name}!")
        
        self.projectiles = new_projectiles
        
        # Check for winner
        alive_bots = [bot for bot in self.bots if bot.health > 0]
        if len(alive_bots) <= 1:
            self.game_active = False
            if len(alive_bots) == 1:
                self.winner = alive_bots[0]
                self._add_message(f"🏆 {self.winner.name} wins the battle!")
            else:
                self._add_message("💥 Battle ended in a draw!")
    
    def draw(self):
        """Render everything on screen"""
        self.screen.fill(BLACK)
        
        # Draw arena background
        arena_rect = pygame.Rect(0, 0, ARENA_WIDTH, ARENA_HEIGHT)
        pygame.draw.rect(self.screen, DARK_BLUE, arena_rect)
        
        # Draw grid
        for i in range(0, ARENA_WIDTH, 50):
            pygame.draw.line(self.screen, GRAY, (i, 0), (i, ARENA_HEIGHT), 1)
        for i in range(0, ARENA_HEIGHT, 50):
            pygame.draw.line(self.screen, GRAY, (0, i), (ARENA_WIDTH, i), 1)
        
        # Draw arena border
        pygame.draw.rect(self.screen, WHITE, arena_rect, 3)
        
        # Draw bots
        for bot in self.bots:
            bot.draw(self.screen)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw UI
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_ui(self):
        """Draw user interface elements"""
        ui_x = ARENA_WIDTH + 20
        
        # Title
        title = self.font.render("🤖 AI Bot Arena", True, WHITE)
        self.screen.blit(title, (ui_x, 20))
        
        # Controls
        y_offset = 70
        controls = [
            "SPACE - Start/Pause",
            "R - Reset Arena",
            "A - Add Random Bot",
            "ESC - Quit"
        ]
        
        for control in controls:
            text = self.small_font.render(control, True, WHITE)
            self.screen.blit(text, (ui_x, y_offset))
            y_offset += 25
        
        # Bot stats
        y_offset += 20
        stats_title = self.font.render("Bot Stats:", True, WHITE)
        self.screen.blit(stats_title, (ui_x, y_offset))
        y_offset += 40
        
        for bot in self.bots:
            # Bot name and type
            bot_text = f"{bot.name} ({bot.bot_type.value})"
            text = self.small_font.render(bot_text, True, bot.color)
            self.screen.blit(text, (ui_x, y_offset))
            y_offset += 20
            
            # Health bar
            health_text = f"Health: {bot.health}/{bot.max_health}"
            text = self.small_font.render(health_text, True, WHITE)
            self.screen.blit(text, (ui_x, y_offset))
            
            # Visual health bar
            bar_width = 100
            bar_height = 10
            health_percent = bot.health / bot.max_health
            
            bar_rect = pygame.Rect(ui_x + 120, y_offset + 5, bar_width, bar_height)
            pygame.draw.rect(self.screen, RED, bar_rect)
            
            health_rect = pygame.Rect(ui_x + 120, y_offset + 5, 
                                    bar_width * health_percent, bar_height)
            pygame.draw.rect(self.screen, GREEN, health_rect)
            
            y_offset += 35
        
        # Messages
        if self.messages:
            y_offset += 20
            msg_title = self.font.render("Battle Log:", True, WHITE)
            self.screen.blit(msg_title, (ui_x, y_offset))
            y_offset += 30
            
            # Show last 5 messages
            for message, timestamp in self.messages[-5:]:
                text = self.small_font.render(message[:30], True, WHITE)
                self.screen.blit(text, (ui_x, y_offset))
                y_offset += 20
        
        # Winner announcement
        if self.winner:
            winner_text = f"🏆 {self.winner.name} WINS! 🏆"
            text = self.font.render(winner_text, True, YELLOW)
            text_rect = text.get_rect(center=(ARENA_WIDTH//2, ARENA_HEIGHT//2))
            
            # Background
            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, YELLOW, bg_rect, 3)
            
            self.screen.blit(text, text_rect)
        elif not self.game_active and not any(bot.health > 0 for bot in self.bots):
            draw_text = "💥 DRAW! 💥"
            text = self.font.render(draw_text, True, RED)
            text_rect = text.get_rect(center=(ARENA_WIDTH//2, ARENA_HEIGHT//2))
            
            # Background
            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, RED, bg_rect, 3)
            
            self.screen.blit(text, text_rect)
    
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game_active = not self.game_active
                    if self.game_active:
                        self._add_message("Battle started!")
                    else:
                        self._add_message("Battle paused!")
                
                elif event.key == pygame.K_r:
                    self._reset_arena()
                
                elif event.key == pygame.K_a:
                    self._add_random_bot()
                
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def _reset_arena(self):
        """Reset the arena to initial state"""
        self.game_active = False
        self.winner = None
        self.projectiles.clear()
        self.messages.clear()
        self._initialize_bots()
    
    def _add_random_bot(self):
        """Add a random bot to the arena"""
        bot_types = list(BotType)
        colors = [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE]
        
        x = random.randint(50, ARENA_WIDTH - 50)
        y = random.randint(50, ARENA_HEIGHT - 50)
        bot_type = random.choice(bot_types)
        color = random.choice(colors)
        name = f"Bot-{random.randint(100, 999)}"
        
        new_bot = Bot(x, y, color, name, bot_type)
        self.bots.append(new_bot)
        self._add_message(f"New bot {name} ({bot_type.value}) joined!")
    
    def run(self):
        """Main game loop"""
        print("🤖 AI Bot Arena - Python Version")
        print("Controls:")
        print("  SPACE - Start/Pause battle")
        print("  R - Reset arena")
        print("  A - Add random bot")
        print("  ESC - Quit")
        print("\nPress SPACE to start the battle!")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    # Check if pygame is available
    try:
        game = GameArena()
        game.run()
    except Exception as e:
        print(f"Error running the game: {e}")
        print("Make sure you have pygame installed: pip install pygame")