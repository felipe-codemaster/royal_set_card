import pygame
import random
import sys
import time
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants for easy adjustments
WIDTH = 800
HEIGHT = 600
CARD_WIDTH = 100
CARD_HEIGHT = 140
DICE_SIZE = 40
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40

# Colors defined as RGB tuples
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_GREY = (200, 200, 200)
DARK_GREY = (100, 100, 100)
GOLD = (247, 193, 43)

# Get absolute path to resources (for PyInstaller compatibility)
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Window settings
screen = pygame.display.set_mode((800, 600))  # Width, Height
pygame.display.set_caption("Royal Card Game")
# Load background image
background_image = pygame.image.load(resource_path("assets/first.jpg"))  # Load the image
background_image = pygame.transform.scale(
    background_image, (800, 600)
)  # Scale to screen size

background = pygame.image.load(resource_path("assets/casino_background.jpg"))  # Path to your background image
background = pygame.transform.scale(background, (800, 600))

playbutton_image = pygame.image.load(resource_path("assets/playbutton_image.png"))
# Display the background
screen.blit(background, (0, 0))

# Fonts for text display
font = pygame.font.SysFont("arial", 36, bold=True)
suit_font = pygame.font.SysFont("arial", 60, bold=True)
little_font = pygame.font.SysFont("helvetica", 28, bold=True)
big_font = pygame.font.SysFont("arial", 48, bold=True)
small_font = pygame.font.SysFont("arial", 24, bold=True)
button_font = pygame.font.SysFont("arial", 20, bold=True)

# Game assets
SUITS = ["H", "D", "C"]
RANKS = ["9", "10", "J", "Q", "K", "A"]
POKER_DICE = ["9", "10", "J", "Q", "K", "A"]
values = {"9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11}

# dice_roll = pygame.mixer.Sound('./assets/dice_roll.mp3')
background_sound = pygame.mixer.Sound(resource_path("assets/casino.mp3"))
mouse_click = pygame.mixer.Sound(resource_path("assets/mouse_click.mp3"))
game_over_sound = pygame.mixer.Sound(resource_path("assets/game_over.mp3"))
background_nature = pygame.mixer.Sound(resource_path("assets/nature_birds.mp3"))

# Set up the display and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Royal Set Poker")

clock = pygame.time.Clock()

# Card class with enhanced graphics
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = values[rank]
        self.image_path = resource_path(f"assets/{rank}{suit}.png")  # Image file path
        self.image = pygame.image.load(self.image_path)  # Load the image
        self.image = pygame.transform.scale(
            self.image, (CARD_WIDTH, CARD_HEIGHT)
        )  # Resize

    def draw(self, screen, x, y, selected=False):
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        screen.blit(self.image, (x, y))

        # Border
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=5)

        # Shadow for selected card
        if selected:
            shadow_surf = pygame.Surface(
                (CARD_WIDTH + 8, CARD_HEIGHT + 8), pygame.SRCALPHA
            )
            pygame.draw.rect(
                shadow_surf,
                (0, 0, 0, 100),
                (4, 4, CARD_WIDTH, CARD_HEIGHT),
                border_radius=5,
            )
            screen.blit(shadow_surf, (x - 4, y - 4))
            pygame.draw.rect(screen, CYAN, rect, 4, border_radius=5)


# Deck class to manage cards
class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS] * 3
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, count):
        if len(self.cards) < count:
            self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS] * 3
            self.shuffle()
        return [self.cards.pop() for _ in range(count)]

# Dice class with corrected mechanics
class Dice:
    def __init__(self, count):
        self.count = count
        self.dice = []
        self.kept = [False] * count

    def roll(self):
        self.dice = [random.choice(POKER_DICE) for _ in range(self.count)]
        self.kept = [False] * self.count

    def reroll(self, game):
        if game.score >= 5 and self.count == 3 and any(not kept for kept in self.kept):
            game.score -= 5
            for i in range(self.count):
                if not self.kept[i]:
                    self.dice[i] = random.choice(POKER_DICE)

    def toggle_keep(self, index):
        if 0 <= index < self.count:
            self.kept[index] = not self.kept[index]

# GameState class
class GameState:
    def __init__(self, max_holes):
        self.round = 1
        self.score = 0
        self.high_scores = {3: 0, 9: 0, 18: 0, 36: 0, 54: 0, 72: 0}
        self.max_holes = max_holes
        self.deck = Deck()
        self.hand = self.deck.deal(3)
        self.dice = Dice(3)
        self.selected = [False] * 3
        self.rolled = False
        self.roll_count = 0
        self.max_rolls = 2
        self.discarded = False

    def update_max_rolls(self):
        hand_size = len(self.hand)
        if hand_size == 3:
            self.max_rolls = 2
            self.dice = Dice(3)
        elif hand_size == 2:
            self.max_rolls = 1
            self.dice = Dice(2)
        elif hand_size == 1:
            self.max_rolls = 1
            self.dice = Dice(1)
        else:
            self.max_rolls = 0
            self.dice = Dice(0)
        self.rolled = False
        self.roll_count = 0


# Scoring functions
def score_hand(hand):
    if not hand:
        return "Nothing", 0
    ranks = [card.rank for card in hand]
    suits = [card.suit for card in hand]
    rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
    suit_counts = {suit: suits.count(suit) for suit in set(suits)}
    rank_order = "910JQKA"
    rank_indices = sorted([rank_order.index(rank) for rank in ranks])
    is_straight = (
        len(rank_indices) == 3
        and rank_indices[2] - rank_indices[0] == 2
        and len(set(rank_indices)) == 3
    )

    # Royal Set: Three of a kind, all same suit
    if len(set(ranks)) == 1 and len(set(suits)) == 1:
        return "Royal Set", 50
    # Royal Flush: A, K, Q same suit
    if set(ranks) == {"A", "K", "Q"} and len(set(suits)) == 1:
        return "Royal Flush", 40
    # Straight Flush: Three consecutive ranks, same suit
    if is_straight and len(set(suits)) == 1:
        return "Straight Flush", 30
    # Triple Double: Three of a kind, two same suit
    if (
        3 in rank_counts.values()
        and len(set(suits)) == 2
        and max(suit_counts.values()) == 2
    ):
        return "Triple Double", 20
    # Trips: Three of a kind, all different suits
    if 3 in rank_counts.values() and len(set(suits)) == 3:
        return "Trips", 25
    # Paired Flush: Flush with a pair
    if len(set(suits)) == 1 and 2 in rank_counts.values():
        return "Paired Flush", 15
    # Flushed Pair: Pair with same suit, third different
    if 2 in rank_counts.values():
        pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
        pair_suits = [s for r, s in zip(ranks, suits) if r == pair_rank]
        if len(set(pair_suits)) == 1 and len(set(suits)) > 1:
            return "Flushed Pair", 10
    # Flush: Three cards, same suit (no pair or straight)
    if len(set(suits)) == 1 and 2 not in rank_counts.values() and not is_straight:
        return "Flush", 5
    # Straight: Three consecutive ranks, mixed suits
    if is_straight and len(set(suits)) > 1:
        return "Straight", 3
    # Pair: Two cards same rank
    if 2 in rank_counts.values():
        return "Pair", 2
    # High Card: None of the above
    return "High Card", 1


def calc_multiplier(hand, dice):
    if not dice.dice:
        return 1
    hand_ranks = set(card.rank for card in hand)
    dice_ranks = set(dice.dice)
    matches = len(hand_ranks & dice_ranks)
    max_matches = len(hand)
    if matches == max_matches:
        return 8
    elif matches == 2:
        return 4
    elif matches == 1:
        return 2
    return 1


# Drawing functions
def draw_background():
    for y in range(HEIGHT):
        shade = int(50 + (y / HEIGHT) * 50)
        pygame.draw.line(screen, (0, shade, 0), (0, y), (WIDTH, y))
    pygame.draw.rect(screen, DARK_GREEN, (0, 0, WIDTH, HEIGHT), 10)

    ### Score


def draw_scoreboard(game):
    round_text = font.render(f"HOLE: {game.round}/{game.max_holes}", True, CYAN)
    score_text = font.render(f"SCORE: {game.score}", True, YELLOW)
    high_text = font.render(f"HIGH: {game.high_scores[game.max_holes]}", True, GREEN)
    screen.blit(round_text, (20, 20))
    screen.blit(score_text, (20, 60))
    screen.blit(high_text, (20, 100))


def draw_hand(game):

    hand_size = len(game.hand)
    total_width = hand_size * (CARD_WIDTH + 5) - 5
    start_x = (WIDTH - total_width) // 2
    for i, card in enumerate(game.hand):
        x = start_x + i * (CARD_WIDTH + 5)
        card.draw(
            screen, x, HEIGHT // 2 - CARD_HEIGHT / 2 - 20, game.selected[i]
        )  # start draw x = 290, 365, 440 range 75
    background_sound.play()


def draw_dice_row(game):
    if game.rolled:

        STOP_SOUND_EVENT = pygame.USEREVENT + 1
        # dice_roll.play()

        dice_count = game.dice.count
        total_width = dice_count * (DICE_SIZE + 10) - 10
        start_x = (WIDTH - total_width) // 2
        for i in range(dice_count):
            x = start_x + i * (DICE_SIZE + 10)
            die = game.dice.dice[i]
            matched = die in [card.rank for card in game.hand]
            kept = game.dice.kept[i]
            rect = pygame.draw.rect(
                screen,
                BLACK,
                (x, HEIGHT // 2 + 70, DICE_SIZE, DICE_SIZE),
                border_radius=1,
            )
            color = GREEN if matched else MAGENTA

            pygame.draw.rect(screen, DARK_GREY, rect)
            pygame.draw.polygon(
                screen,
                LIGHT_GREY,
                [
                    (x, y)
                    for x, y in [
                        (rect.left, rect.top),
                        (rect.right, rect.top),
                        (rect.right - 5, rect.top + 5),
                        (rect.left + 5, rect.top + 5),
                    ]
                ],
            )
            pygame.draw.polygon(
                screen,
                BLACK,
                [
                    (x, y)
                    for x, y in [
                        (rect.left, rect.bottom),
                        (rect.right, rect.bottom),
                        (rect.right - 2, rect.bottom - 2),
                        (rect.left + 2, rect.bottom - 2),
                    ]
                ],
            )
            pygame.draw.rect(screen, color, rect, 1, border_radius=5)
            if kept:
                pygame.draw.rect(
                    screen, CYAN, rect.inflate(1, 1), 1, border_radius=5
                )  # dice_card cover cyan color
            text = small_font.render(die, True, WHITE)
            screen.blit(text, (x + 12, HEIGHT // 2 + 78))


def update_score_display(game):
    hand_name, base_score = score_hand(game.hand)
    multiplier = calc_multiplier(game.hand, game.dice) if game.rolled else 1
    text = f"{hand_name} - {base_score} x{multiplier}"
    font = pygame.font.SysFont("arial", 30, bold=True)
    hand_text = font.render(text, True, GOLD)  # high card score
    glow_surf = pygame.Surface((280, 40), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, (255, 0, 255, 50), (0, 0, 280, 40), border_radius=5)
    screen.blit(glow_surf, (WIDTH // 2 - 140, HEIGHT // 2 + 120))
    pygame.draw.rect(
        screen, GOLD, (WIDTH // 2 - 140, HEIGHT // 2 + 120, 280, 40), 2, border_radius=5
    )
    rect = pygame.Rect(WIDTH // 2 - 140, HEIGHT // 2 + 120, 280, 40)
    hand_text_rect = hand_text.get_rect()
    hand_text_rect.center = rect.center
    screen.blit(hand_text, hand_text_rect)
    # screen.blit(hand_text, (WIDTH // 2 - 95, HEIGHT // 2 + 120))

    ##### draw discard, reroll, lock in


def draw_buttons(game, mouse_pos):
    discard_rect = pygame.Rect(150, 500, BUTTON_WIDTH, BUTTON_HEIGHT)
    active = not game.discarded and not game.rolled
    if active and discard_rect.collidepoint(mouse_pos):
        glow_surf = pygame.Surface(
            (BUTTON_WIDTH + 10, BUTTON_HEIGHT + 10), pygame.SRCALPHA
        )
        pygame.draw.rect(
            glow_surf,
            (0, 255, 255, 100),
            (5, 5, BUTTON_WIDTH, BUTTON_HEIGHT),
            border_radius=5,
        )
        screen.blit(glow_surf, (145, 495))
        pygame.draw.rect(screen, RED, discard_rect, 0, border_radius=5)
    else:
        pygame.draw.rect(screen, RED, discard_rect, 2, border_radius=5)
    discard_text = button_font.render("DISCARD", True, BLACK)
    screen.blit(discard_text, (160, 510))

    STOP_SOUND_EVENT = pygame.USEREVENT + 1

    def diceroll_sound():
        # dice_roll.play()
        pygame.time.set_timer(STOP_SOUND_EVENT, 2000)

    # reroll
    roll_label = "REROLL" if game.rolled else "ROLL"
    roll_rect = pygame.Rect(
        WIDTH // 2 - BUTTON_WIDTH // 2, 500, BUTTON_WIDTH, BUTTON_HEIGHT
    )

    # Updated roll button logic
    roll_active = False
    if not game.rolled:
        roll_active = True
    elif game.rolled and game.roll_count < game.max_rolls:
        if len(game.hand) == 3:
            # For 3-card hands: allow two free rolls
            roll_active = any(not k for k in game.dice.kept)
        elif len(game.hand) == 2:
            # For 2-card hands: only one roll allowed
            roll_active = False
        elif len(game.hand) == 1:
            # For 1-card hands: only one roll allowed
            roll_active = False

    if roll_active and roll_rect.collidepoint(mouse_pos):
        diceroll_sound()
        glow_surf = pygame.Surface(
            (BUTTON_WIDTH + 10, BUTTON_HEIGHT + 10), pygame.SRCALPHA
        )
        pygame.draw.rect(
            glow_surf,
            (0, 255, 255, 100),
            (5, 5, BUTTON_WIDTH, BUTTON_HEIGHT),
            border_radius=5,
        )
        screen.blit(glow_surf, (WIDTH // 2 - BUTTON_WIDTH // 2 - 5, 495))
        pygame.draw.rect(screen, GOLD, roll_rect, 0, border_radius=5)
    else:
        pygame.draw.rect(screen, GOLD, roll_rect, 2, border_radius=5)
    roll_text = button_font.render(roll_label, True, BLACK)
    screen.blit(roll_text, (WIDTH // 2 - 25, 510))
    pygame.time.set_timer(STOP_SOUND_EVENT, 2000)  # Cancel the timer

    # lock in
    lock_rect = pygame.Rect(650 - BUTTON_WIDTH, 500, BUTTON_WIDTH, BUTTON_HEIGHT)
    if game.rolled and lock_rect.collidepoint(mouse_pos):
        glow_surf = pygame.Surface(
            (BUTTON_WIDTH + 10, BUTTON_HEIGHT + 10), pygame.SRCALPHA
        )
        pygame.draw.rect(
            glow_surf,
            (0, 255, 255, 100),
            (5, 5, BUTTON_WIDTH, BUTTON_HEIGHT),
            border_radius=5,
        )
        screen.blit(glow_surf, (645 - BUTTON_WIDTH, 495))
        pygame.draw.rect(screen, WHITE, lock_rect, 0, border_radius=5)
        # dice_roll.stop()
    else:
        pygame.draw.rect(screen, WHITE, lock_rect, 2, border_radius=5)
    lock_text = button_font.render("LOCK IN", True, BLACK)
    screen.blit(lock_text, (665 - BUTTON_WIDTH, 510))

# State handling functions
def handle_menu(high_scores):
    background_nature.play()
    screen.blit(background_image, (0, 0))
    modes = [3, 9, 18, 36, 54, 72]
    button_rects = []
    for i, mode in enumerate(modes):
        y = 100 + i * 80
        rect = playbutton_image.get_rect(center=(WIDTH // 2 + 250, y + 30))
        text = little_font.render(f"Play { mode } Holes", True, BLACK)
        high_text = small_font.render(f"High: {high_scores[mode]}", True, YELLOW)
        if rect.collidepoint(pygame.mouse.get_pos()):
            screen.blit(playbutton_image, rect.topleft)
        else:
            screen.blit(playbutton_image, rect.topleft)

        screen.blit(text, (WIDTH // 2 + 160, y + 10))
        button_rects.append((rect, mode))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit", None
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            for rect, mode in button_rects:
                if rect.collidepoint(x, y):
                    mouse_click.play()
                    return "playing", GameState(mode)
    return "menu", None

def handle_playing(game):
    background_nature.stop()
    screen.blit(background, (0, 0))

    draw_scoreboard(game)
    draw_hand(game)
    draw_dice_row(game)
    update_score_display(game)
    mouse_pos = pygame.mouse.get_pos()
    draw_buttons(game, mouse_pos)

    back_rect = pygame.Rect(680, 30, 100, 60)
    mouse_pos = pygame.mouse.get_pos()
    if back_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, CYAN, back_rect, 0, border_radius=2)
    else:
        pygame.draw.rect(screen, CYAN, back_rect, 2, border_radius=2)
    back_text = font.render("MENU", True, BLACK)
    screen.blit(back_text, (685, 40))  # back to menu letter

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit", game
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if (
                not game.discarded
                and not game.rolled
                and HEIGHT // 2 - CARD_HEIGHT // 2
                <= y
                <= HEIGHT // 2 + CARD_HEIGHT // 2
            ):
                hand_size = len(game.hand)
                total_width = hand_size * (CARD_WIDTH + 5) - 5
                start_x = (WIDTH - total_width) // 2
                for i in range(hand_size):
                    card_rect = pygame.Rect(
                        start_x + i * (CARD_WIDTH + 5),
                        HEIGHT // 2 - CARD_HEIGHT / 2,
                        CARD_WIDTH,
                        CARD_HEIGHT,
                    )
                    if card_rect.collidepoint(x, y):
                        game.selected[i] = not game.selected[i]
            if game.rolled and HEIGHT // 2 + 70 <= y <= HEIGHT // 2 + 70 + DICE_SIZE:
                dice_count = game.dice.count
                total_width = dice_count * (DICE_SIZE + 10) - 10
                start_x = (WIDTH - total_width) // 2
                for i in range(dice_count):
                    dice_rect = pygame.Rect(
                        start_x + i * (DICE_SIZE + 10),
                        HEIGHT // 2 + 70,
                        DICE_SIZE,
                        DICE_SIZE,
                    )
                    if dice_rect.collidepoint(x, y):
                        game.dice.toggle_keep(i)
            if back_rect.collidepoint(x, y):
                background_sound.stop()
                return "menu", game
            if 500 <= y <= 540:
                if 150 <= x <= 250 and not game.discarded and not game.rolled:
                    selected_indices = [i for i, s in enumerate(game.selected) if s]
                    if selected_indices:
                        new_hand = [
                            card
                            for i, card in enumerate(game.hand)
                            if i not in selected_indices
                        ]
                        discards = len(selected_indices)
                        new_cards = game.deck.deal(discards)
                        game.hand = new_hand + new_cards
                        game.discarded = True
                        game.selected = [False] * len(game.hand)
                        game.update_max_rolls()
                elif (
                    WIDTH // 2 - BUTTON_WIDTH // 2
                    <= x
                    <= WIDTH // 2 + BUTTON_WIDTH // 2
                ):
                    if not game.rolled:
                        game.dice.roll()
                        game.rolled = True
                        game.roll_count = 1
                    elif game.roll_count < game.max_rolls:
                        # Free reroll for 3-card hands (max 2 free rolls)
                        if len(game.hand) == 3 and game.roll_count < 2:
                            if any(not k for k in game.dice.kept):
                                game.dice.dice = [
                                    random.choice(POKER_DICE) if not kept else die
                                    for die, kept in zip(game.dice.dice, game.dice.kept)
                                ]
                                game.roll_count += 1
                        # Free reroll for 2-card hands (max 1 free roll)
                        elif len(game.hand) == 2 and game.roll_count < 1:
                            if any(not k for k in game.dice.kept):
                                game.dice.dice = [
                                    random.choice(POKER_DICE) if not kept else die
                                    for die, kept in zip(game.dice.dice, game.dice.kept)
                                ]
                                game.roll_count += 1
                        # Paid reroll (costs 5 points)
                        elif game.score >= 5 and any(not k for k in game.dice.kept):
                            game.score -= 5
                            game.dice.dice = [
                                random.choice(POKER_DICE) if not kept else die
                                for die, kept in zip(game.dice.dice, game.dice.kept)
                            ]
                            game.roll_count += 1
                elif 650 - BUTTON_WIDTH <= x <= 650 and game.rolled:
                    hand_name, base_score = score_hand(game.hand)
                    multiplier = calc_multiplier(game.hand, game.dice)
                    game.score += base_score * multiplier
                    game.high_scores[game.max_holes] = max(
                        game.high_scores[game.max_holes], game.score
                    )
                    game.round += 1
                    if game.round > game.max_holes:
                        return "game_over", game
                    game.hand = game.deck.deal(3)
                    game.dice = Dice(3)
                    game.selected = [False] * 3
                    game.rolled = False
                    game.roll_count = 0
                    game.discarded = False
                    game.update_max_rolls()
            # Add mulligan button handling
            # if (game.mulligans_remaining > 0 and not game.used_mulligan_this_hole
            #     and 150 <= x <= 250 and 450 <= y <= 490):
            #     # Using a mulligan allows either:
            #     # 1. An extra discard if haven't discarded yet
            #     # 2. An extra reroll if already rolled
            #     game.mulligans_remaining -= 1
            #     game.used_mulligan_this_hole = True
            #     if game.rolled:

    # # Reset mulligan usage when moving to next hole
    # if game.round > game.max_holes:
    #     game.used_mulligan_this_hole = False

    return "playing", game


def handle_game_over(game, high_scores):
    background_sound.stop()
    screen.fill(DARK_GREEN)

    if not hasattr(handle_game_over, "game_over_sound"):
        handle_game_over.game_over_sound = False

    over_text = big_font.render("GAME OVER", True, RED)
    score_text = font.render(f"Score: {game.score}", True, YELLOW)
    high_text = font.render(
        f"High Score: {game.high_scores[game.max_holes]}", True, GREEN
    )
    back_rect = pygame.Rect(WIDTH // 2 - 123, HEIGHT - 100, 250, 60)
    mouse_pos = pygame.mouse.get_pos()
    if back_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, CYAN, back_rect, 0, border_radius=5)
    else:
        pygame.draw.rect(screen, CYAN, back_rect, 2, border_radius=5)
    back_text = font.render("BACK TO MENU", True, BLACK)
    screen.blit(over_text, (WIDTH // 2 - 120, 100))
    screen.blit(score_text, (WIDTH // 2 - 80, 200))
    screen.blit(high_text, (WIDTH // 2 - 120, 250))
    screen.blit(back_text, (WIDTH // 2 - 110, HEIGHT - 90))  # back to menu letter

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over_sound.play()
            time.sleep(2)
            game_over_sound.stop()
            handle_game_over.game_over_sound = False
            return "quit", None
        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_rect.collidepoint(event.pos):
                background_sound.stop()
                return "menu", None
    if not handle_game_over.game_over_sound:

        handle_game_over.game_over_sound = True
    return "game_over", game


# Main game loop
def main():
    high_scores = {3: 0, 9: 0, 18: 0, 36: 0, 54: 0, 72: 0}
    state = "menu"
    game = None
    running = True

    while running:
        if state == "menu":
            state, game = handle_menu(high_scores)
        elif state == "playing":
            state, game = handle_playing(game)
        elif state == "game_over":
            state, game = handle_game_over(game, high_scores)
        if state == "quit":
            running = False
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
