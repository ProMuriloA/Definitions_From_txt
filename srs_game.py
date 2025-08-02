import os
import sys
import csv
import random
import time
import datetime
import json
import math
import pygame
import pygame.gfxdraw
from pygame import gfxdraw
from collections import deque
import warnings
import wave
import struct
import numpy as np

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Improved Color Scheme - Vibrant and Harmonious
PRIMARY = (70, 130, 180)  # Steel Blue (primary)
PRIMARY_LIGHT = (135, 206, 235)  # Sky Blue
PRIMARY_DARK = (65, 105, 225)  # Royal Blue
SECONDARY = (255, 140, 0)  # Dark Orange (secondary)
SECONDARY_LIGHT = (255, 165, 0)  # Orange
SECONDARY_DARK = (255, 69, 0)  # Red-Orange
BACKGROUND = (245, 245, 245)  # Off-white background
SURFACE = (255, 255, 255)  # White
ON_PRIMARY = (255, 255, 255)  # White
ON_SECONDARY = (255, 255, 255)  # White
ON_BACKGROUND = (50, 50, 50)  # Dark Gray
ON_SURFACE = (60, 60, 60)  # Dark Gray
SUCCESS = (46, 204, 113)  # Emerald Green
ERROR = (231, 76, 60)  # Alizarin Red
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Game Constants
INIT_SCREEN_WIDTH, INIT_SCREEN_HEIGHT = 1024, 768
TILE_SIZE = 64
PLAYER_SPEED = 5
FPS = 60
CAMERA_SMOOTHNESS = 0.1
CHUNK_SIZE = 16  # Chunks are 16x16 tiles
VIEW_DISTANCE = 3  # Number of chunks to render around player

# Material Design Parameters
SHADOW_COLOR = (0, 0, 0, 30)
SHADOW_RADIUS = 6
ELEVATION_LOW = 2
ELEVATION_MEDIUM = 6
ELEVATION_HIGH = 12
FONT_SM = 16
FONT_MD = 20
FONT_LG = 28
FONT_XL = 36
FONT_XXL = 48

# Environment Colors - More Natural and Vibrant
GRASS_GREEN = (124, 184, 71)  # Vibrant grass green
WATER_BLUE = (64, 164, 223)  # Bright water blue
SAND_YELLOW = (237, 201, 175)  # Warm sand
MEADOW_GREEN = (120, 200, 120)  # Lush meadow green
SKY_BLUE = (173, 216, 230)  # Light sky blue
FLOWER_COLORS = [
    (255, 107, 107),  # Coral red
    (255, 179, 71),  # Orange
    (255, 140, 180),  # Pink
    (100, 180, 255),  # Light blue
    (120, 220, 120)  # Light green
]

# Sound files - ensure these paths are correct
SOUND_PATHS = {
    "background": "sounds/background.wav",
    "battle": "sounds/battle.wav",
    "calm": "sounds/calm.wav",
    "victory": "sounds/victory.wav",
    "encounter": "sounds/encounter.wav",
    "move": "sounds/move.wav",
    "bird_chirp": "sounds/bird_chirp.wav",
    "water_stream": "sounds/water_stream.wav",
    "wind": "sounds/wind.wav"
}

# Create sounds directory if it doesn't exist
if not os.path.exists("sounds"):
    os.makedirs("sounds")


# Function to generate high-quality music files
def create_music_files():
    print("Generating sound files...")

    # Background music - calm and peaceful with pentatonic scale
    create_music_wav(SOUND_PATHS["background"],
                     base_freq=220,
                     duration=20.0,
                     chords=[
                         (0.0, [1.0, 1.25, 1.5]),  # Major chord
                         (5.0, [1.0, 1.2, 1.5]),  # Suspended chord
                         (10.0, [1.0, 1.33, 1.67]),  # Minor chord
                         (15.0, [1.0, 1.25, 1.5])  # Major chord
                     ],
                     amplitude=0.3,
                     scale_type="pentatonic")

    # Battle music - more intense with harmonic minor scale
    create_music_wav(SOUND_PATHS["battle"],
                     base_freq=440,
                     duration=15.0,
                     chords=[
                         (0.0, [1.0, 1.25, 1.5]),
                         (2.5, [1.0, 1.33, 1.67]),
                         (5.0, [1.2, 1.5, 1.8]),
                         (7.5, [1.0, 1.33, 1.67]),
                         (10.0, [1.0, 1.25, 1.5]),
                         (12.5, [1.0, 1.33, 1.67])
                     ],
                     amplitude=0.4,
                     tempo=140,
                     scale_type="harmonic_minor")

    # Calm music - for meditation with natural minor scale
    create_music_wav(SOUND_PATHS["calm"],
                     base_freq=110,
                     duration=20.0,
                     chords=[
                         (0.0, [1.0, 1.2, 1.5]),  # Suspended chord
                         (5.0, [1.0, 1.33, 1.67]),  # Minor chord
                         (10.0, [1.0, 1.25, 1.5]),  # Major chord
                         (15.0, [1.0, 1.33, 1.67])  # Minor chord
                     ],
                     amplitude=0.25,
                     tempo=60,
                     scale_type="natural_minor")

    # Victory sound - bright and positive
    create_tone_wav(SOUND_PATHS["victory"],
                    frequencies=[880, 1320, 1760],
                    duration=1.2,
                    sample_rate=44100,
                    amplitude=0.5,
                    envelope=True)

    # Encounter sound - attention-grabbing
    create_tone_wav(SOUND_PATHS["encounter"],
                    frequencies=[440, 880, 440, 660],
                    duration=0.8,
                    sample_rate=44100,
                    amplitude=0.6,
                    envelope=True)

    # Move sound - subtle feedback
    create_tone_wav(SOUND_PATHS["move"],
                    frequencies=[220, 330],
                    duration=0.15,
                    sample_rate=44100,
                    amplitude=0.4,
                    envelope=True)
    print("Sound files generated successfully!")


# Function to generate tone WAV files with envelope for natural fade
def create_tone_wav(filename, frequencies, duration=0.5, sample_rate=44100, amplitude=0.5, envelope=False):
    # Calculate number of frames
    num_frames = int(sample_rate * duration)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.setnframes(num_frames)

        for i in range(num_frames):
            # Calculate time in seconds
            t = i / float(sample_rate)

            # Generate multi-frequency tone
            value = 0
            for freq in frequencies:
                value += amplitude * math.sin(2.0 * math.pi * freq * t)
            value = value / len(frequencies)

            # Apply envelope for natural sound
            if envelope:
                # ADSR envelope (Attack, Decay, Sustain, Release)
                attack = 0.1
                decay = 0.1
                release = 0.2
                sustain_level = 0.7

                if t < attack:
                    # Attack phase
                    env = t / attack
                elif t < attack + decay:
                    # Decay phase
                    env = 1.0 - (1.0 - sustain_level) * ((t - attack) / decay)
                elif t < duration - release:
                    # Sustain phase
                    env = sustain_level
                else:
                    # Release phase
                    env = sustain_level * (1.0 - ((t - (duration - release)) / release))

                value *= env

            # Normalize value
            value = max(-1.0, min(1.0, value))

            # Convert to 16-bit integer
            sample = int(value * 32767)
            wav_file.writeframes(struct.pack('<h', sample))


# Function to generate more complex music with proper scales
def create_music_wav(filename, base_freq, duration, chords, amplitude=0.5, sample_rate=44100,
                     harmonics=True, tempo=120, scale_type="major"):
    num_frames = int(sample_rate * duration)
    beat_duration = 60.0 / tempo  # Duration of one beat in seconds

    # Define scales for melody
    scales = {
        "major": [1.0, 1.125, 1.25, 1.333, 1.5, 1.667, 1.875],
        "minor": [1.0, 1.125, 1.2, 1.333, 1.5, 1.6, 1.875],
        "harmonic_minor": [1.0, 1.125, 1.2, 1.333, 1.5, 1.6, 1.875, 2.0],
        "natural_minor": [1.0, 1.125, 1.2, 1.333, 1.5, 1.6, 1.8],
        "pentatonic": [1.0, 1.125, 1.25, 1.5, 1.667]
    }
    current_scale = scales.get(scale_type, scales["major"])

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.setnframes(num_frames)

        # Create an envelope function to avoid clicks
        def envelope(t, total_duration):
            # ADSR envelope with longer release
            attack = 0.05
            decay = 0.1
            release = 0.5
            sustain_level = 0.8

            if t < attack:
                return t / attack
            elif t < attack + decay:
                return 1.0 - (1.0 - sustain_level) * ((t - attack) / decay)
            elif t < total_duration - release:
                return sustain_level
            else:
                return sustain_level * (1.0 - ((t - (total_duration - release)) / release))

                # Add rhythm through amplitude modulation

        def rhythm(t):
            # Create a basic 4/4 rhythm pattern
            beat = (t / beat_duration) % 4
            if beat < 1:  # Strong beat
                return 1.0
            elif beat < 2:  # Weak beat
                return 0.9
            elif beat < 3:  # Medium beat
                return 0.95
            else:  # Weak beat
                return 0.85

        for i in range(num_frames):
            t = i / float(sample_rate)
            current_time = t % duration

            # Find current chord
            current_ratios = [1.0, 1.25, 1.5]  # Default to major chord
            for chord_start, ratios in chords:
                if current_time >= chord_start:
                    current_ratios = ratios

            # Generate chord tones
            value = 0
            for ratio in current_ratios:
                freq = base_freq * ratio
                # Add slight detuning for richer sound
                detune = 1.0 + random.uniform(-0.002, 0.002)
                value += amplitude * math.sin(2.0 * math.pi * freq * detune * t)

            # Apply envelope and normalize
            value = value / len(current_ratios) * envelope(current_time, duration)
            value = max(-1.0, min(1.0, value))

            # Apply rhythm
            value *= rhythm(t)

            # Add melody based on scale
            if i % int(sample_rate * 0.25) == 0:  # Every quarter second
                melody_note = random.choice(current_scale)
                melody_freq = base_freq * melody_note
                value += 0.15 * math.sin(2.0 * math.pi * melody_freq * t)

            # Add harmonics for richness
            if harmonics:
                harmonics_val = 0
                for harmonic in range(2, 6):  # 2nd to 5th harmonics
                    harmonics_val += 0.08 * math.sin(2.0 * math.pi * base_freq * harmonic * t)
                value = (value + harmonics_val) * 0.7

            # Convert to 16-bit integer
            sample = int(value * 32767)
            wav_file.writeframes(struct.pack('<h', sample))


# Create music files if they don't exist
sound_files_exist = all(os.path.exists(path) for path in SOUND_PATHS.values() if path != "sounds/water_stream.wav")
if not sound_files_exist:
    create_music_files()

# Try to load sound effects
try:
    victory_sound = pygame.mixer.Sound(SOUND_PATHS["victory"])
    encounter_sound = pygame.mixer.Sound(SOUND_PATHS["encounter"])
    move_sound = pygame.mixer.Sound(SOUND_PATHS["move"])
    print("Sound effects loaded successfully")
except Exception as e:
    print(f"Error loading sound effects: {e}")
    # Create silent sounds as fallback
    victory_sound = pygame.mixer.Sound(buffer=bytearray())
    encounter_sound = pygame.mixer.Sound(buffer=bytearray())
    move_sound = pygame.mixer.Sound(buffer=bytearray())

# Define these as global variables for access in classes
VICTORY_SOUND = victory_sound
ENCOUNTER_SOUND = encounter_sound
MOVE_SOUND = move_sound

# Load fonts with modern typography
try:
    # Modern Material Design-friendly fonts
    font_small = pygame.font.SysFont("Arial", FONT_SM)
    font_medium = pygame.font.SysFont("Arial", FONT_MD)
    font_large = pygame.font.SysFont("Arial", FONT_LG)
    font_xlarge = pygame.font.SysFont("Arial", FONT_XL, bold=True)
    font_title = pygame.font.SysFont("Arial", FONT_XXL, bold=True)
except:
    # Fallback to system fonts
    font_small = pygame.font.SysFont("Arial", FONT_SM)
    font_medium = pygame.font.SysFont("Arial", FONT_MD)
    font_large = pygame.font.SysFont("Arial", FONT_LG)
    font_xlarge = pygame.font.SysFont("Arial", FONT_XL)
    font_title = pygame.font.SysFont("Arial", FONT_XXL, bold=True)


# Helper function to draw Material Design shadows
def draw_shadow(surface, rect, elevation=ELEVATION_MEDIUM, radius=SHADOW_RADIUS, color=SHADOW_COLOR):
    shadow_surf = pygame.Surface((rect.width + radius * 2, rect.height + radius * 2), pygame.SRCALPHA)
    for i in range(elevation, 0, -1):
        alpha = max(0, color[3] - (i * 5))
        shadow_rect = pygame.Rect(radius - i, radius - i, rect.width + i * 2, rect.height + i * 2)
        pygame.draw.rect(shadow_surf, (color[0], color[1], color[2], alpha), shadow_rect, border_radius=radius)
    surface.blit(shadow_surf, (rect.x - radius, rect.y - radius))


# Helper function to draw Material Design cards
def draw_card(surface, rect, elevation=ELEVATION_MEDIUM, color=SURFACE, radius=12):
    # Draw shadow
    draw_shadow(surface, rect, elevation, radius)

    # Draw card surface
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, (200, 200, 200), rect, 1, border_radius=radius)


class SpacedRepetitionSystem:
    def __init__(self, deck_data):
        self.deck = deck_data
        self.card_status = {}
        self.load_progress()

        # Initialize card status for new cards
        for card in self.deck:
            card_id = str(card['id'])
            if card_id not in self.card_status:
                self.card_status[card_id] = {
                    'interval': 0,
                    'ease': 2.5,
                    'reps': 0,
                    'lapses': 0,
                    'due_date': datetime.datetime.now().isoformat(),
                    'last_reviewed': None
                }

    def save_progress(self):
        with open('srs_progress.json', 'w') as f:
            json.dump(self.card_status, f)
        print("Progress saved!")

    def load_progress(self):
        try:
            with open('srs_progress.json', 'r') as f:
                self.card_status = json.load(f)
            print("Progress loaded!")
        except FileNotFoundError:
            print("No progress file found. Starting fresh.")
            self.card_status = {}
        except Exception as e:
            print(f"Error loading progress: {e}")
            self.card_status = {}

    def get_due_cards(self):
        due_cards = []
        now = datetime.datetime.now()

        for card in self.deck:
            card_id = str(card['id'])
            status = self.card_status.get(card_id, {})
            due_date_str = status.get('due_date', datetime.datetime.now().isoformat())

            try:
                due_date = datetime.datetime.fromisoformat(due_date_str)
            except Exception as e:
                print(f"Error parsing due date: {e}")
                due_date = datetime.datetime.now()

            if due_date <= now:
                due_cards.append(card)

        return due_cards

    def process_review(self, card_id, quality):
        card_id = str(card_id)
        if card_id not in self.card_status:
            self.card_status[card_id] = {
                'interval': 0,
                'ease': 2.5,
                'reps': 0,
                'lapses': 0,
                'due_date': datetime.datetime.now().isoformat(),
                'last_reviewed': None
            }

        status = self.card_status[card_id]

        if quality >= 3:  # Correct response
            if status['reps'] == 0:
                status['interval'] = 1
            elif status['reps'] == 1:
                status['interval'] = 6
            else:
                status['interval'] = int(status['interval'] * status['ease'])

            status['ease'] = max(1.3, status['ease'] + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            status['reps'] += 1
        else:  # Incorrect response
            status['interval'] = 1
            status['lapses'] += 1
            status['reps'] = 0
            status['ease'] = max(1.3, status['ease'] - 0.2)

        # Calculate next review date
        next_review = datetime.datetime.now() + datetime.timedelta(days=status['interval'])
        status['due_date'] = next_review.isoformat()
        status['last_reviewed'] = datetime.datetime.now().isoformat()

        self.save_progress()

    def get_card_stats(self, card_id):
        card_id = str(card_id)
        return self.card_status.get(card_id, {
            'interval': 0,
            'ease': 2.5,
            'reps': 0,
            'lapses': 0,
            'due_date': datetime.datetime.now().isoformat(),
            'last_reviewed': None
        })


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 0.8
        self.height = TILE_SIZE * 0.8
        self.direction = "down"
        self.animation_frame = 0
        self.last_update = 0
        self.moving = False
        self.sprite_sheet = self.create_friendly_sprite_sheet()
        self.move_sound = MOVE_SOUND

    def create_friendly_sprite_sheet(self):
        sprite_sheet = pygame.Surface((TILE_SIZE * 4, TILE_SIZE * 4), pygame.SRCALPHA)
        skin_color = (255, 224, 189)  # Light skin tone
        hair_color = (101, 67, 33)  # Brown hair
        shirt_color = PRIMARY
        pants_color = (50, 50, 150)  # Dark blue pants

        for direction_idx, direction in enumerate(["down", "up", "left", "right"]):
            for frame in range(4):
                x_pos = frame * TILE_SIZE
                y_pos = direction_idx * TILE_SIZE

                # Head - simple circle
                pygame.draw.circle(sprite_sheet, skin_color,
                                   (x_pos + TILE_SIZE // 2, y_pos + TILE_SIZE // 4), 12)

                # Body - simple rectangle
                pygame.draw.rect(sprite_sheet, shirt_color,
                                 (x_pos + TILE_SIZE // 2 - 10, y_pos + TILE_SIZE // 3, 20, TILE_SIZE // 3))

                # Simple eyes
                eye_offset = 3 if direction in ["left", "right"] else 0
                pygame.draw.circle(sprite_sheet, WHITE,
                                   (x_pos + TILE_SIZE // 2 - 5, y_pos + TILE_SIZE // 4 - 2), 3)
                pygame.draw.circle(sprite_sheet, WHITE,
                                   (x_pos + TILE_SIZE // 2 + 5, y_pos + TILE_SIZE // 4 - 2), 3)

                # Simple smile
                smile_y = y_pos + TILE_SIZE // 4 + 5
                pygame.draw.arc(sprite_sheet, BLACK,
                                (x_pos + TILE_SIZE // 2 - 8, smile_y - 3, 16, 8),
                                0, math.pi, 2)

                # Legs - simple lines
                leg_swing = frame % 2 * 3 - 1.5
                leg_start_y = y_pos + TILE_SIZE // 2 + 30

                pygame.draw.line(sprite_sheet, pants_color,
                                 (x_pos + TILE_SIZE // 2 - 5, leg_start_y),
                                 (x_pos + TILE_SIZE // 2 - 5, y_pos + TILE_SIZE - 10 + leg_swing), 4)
                pygame.draw.line(sprite_sheet, pants_color,
                                 (x_pos + TILE_SIZE // 2 + 5, leg_start_y),
                                 (x_pos + TILE_SIZE // 2 + 5, y_pos + TILE_SIZE - 10 - leg_swing), 4)

                # Arms - simple lines
                arm_swing = frame % 2 * 4 - 2
                arm_start_x = x_pos + TILE_SIZE // 2
                arm_start_y = y_pos + TILE_SIZE // 3 + 10

                if direction == "down":
                    pygame.draw.line(sprite_sheet, skin_color,
                                     (arm_start_x - 10, arm_start_y),
                                     (arm_start_x - 15, arm_start_y + 15 + arm_swing), 4)
                    pygame.draw.line(sprite_sheet, skin_color,
                                     (arm_start_x + 10, arm_start_y),
                                     (arm_start_x + 15, arm_start_y + 15 - arm_swing), 4)
                elif direction == "up":
                    pygame.draw.line(sprite_sheet, skin_color,
                                     (arm_start_x - 10, arm_start_y),
                                     (arm_start_x - 15, arm_start_y - 15 - arm_swing), 4)
                    pygame.draw.line(sprite_sheet, skin_color,
                                     (arm_start_x + 10, arm_start_y),
                                     (arm_start_x + 15, arm_start_y - 15 + arm_swing), 4)
                elif direction == "left":
                    pygame.draw.line(sprite_sheet, skin_color,
                                     (arm_start_x - 10, arm_start_y),
                                     (arm_start_x - 25 - arm_swing, arm_start_y), 4)
                    pygame.draw.line(sprite_sheet, skin_color,
                                     (arm_start_x + 10, arm_start_y),
                                     (arm_start_x - 5 + arm_swing, arm_start_y + 15), 4)
                elif direction == "right":
                    pygame.draw.line(sprite_sheet, skin_color,
                                     (arm_start_x - 10, arm_start_y),
                                     (arm_start_x + 5 - arm_swing, arm_start_y + 15), 4)
                    pygame.draw.line(sprite_sheet, skin_color,
                                     (arm_start_x + 10, arm_start_y),
                                     (arm_start_x + 25 + arm_swing, arm_start_y), 4)

        return sprite_sheet


    def draw(self, screen, camera_x, camera_y):
        # Calculate screen position
        screen_x = self.x - camera_x - self.width // 2
        screen_y = self.y - camera_y - self.height // 2

        # Determine sprite sheet position based on direction
        direction_map = {
            "down": 0,
            "up": 1,
            "left": 2,
            "right": 3
        }
        row = direction_map.get(self.direction, 0)

        # Get the sprite frame
        sprite_rect = pygame.Rect(
            self.animation_frame * TILE_SIZE,
            row * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
        sprite = self.sprite_sheet.subsurface(sprite_rect)

        # Scale to player size
        scaled_sprite = pygame.transform.scale(sprite, (int(self.width), int(self.height)))
        screen.blit(scaled_sprite, (screen_x, screen_y))

    def move(self, dx, dy, world):
        # Set moving state
        self.moving = (dx != 0 or dy != 0)

        # Update direction
        if dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"
        elif dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"

        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy

        # Calculate player's feet position (bottom center) in tile coordinates
        feet_x = new_x // TILE_SIZE
        feet_y = (new_y + self.height // 2) // TILE_SIZE

        # Check if the tile at feet position is walkable
        tile_type = world.get_tile(int(feet_x), int(feet_y))
        if tile_type in ["grass", "sand", "meadow"]:  # Walkable surfaces
            self.x = new_x
            self.y = new_y

        # Animation update
        if self.moving and time.time() - self.last_update > 0.1:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.last_update = time.time()
            try:
                self.move_sound.play()
            except Exception as e:
                print(f"Error playing move sound: {e}")

        return True


class PokemonBattle:
    def __init__(self, card, srs_system, screen_width, screen_height):
        self.card = card
        self.srs_system = srs_system
        self.state = "question"  # question, answer, result
        self.user_answer = ""
        self.result = ""
        self.stats = srs_system.get_card_stats(card['id'])
        self.last_key_time = 0
        self.key_delay = 0.15
        self.pokemon_sprite = self.create_happy_pokemon_sprite()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.victory_sound = VICTORY_SOUND  # Use the global sound
        self.encounter_sound = ENCOUNTER_SOUND  # Use the global sound

        # Play battle music
        try:
            pygame.mixer.music.load(SOUND_PATHS["battle"])
            pygame.mixer.music.play(-1)
            try:
                self.encounter_sound.play()  # Use the class attribute
            except Exception as e:
                print(f"Error playing encounter sound: {e}")
            print("Battle music started")
        except Exception as e:
            print(f"Error loading battle music: {e}")

    def create_happy_pokemon_sprite(self):
        # Happy pokemon-like sprite with natural smile
        sprite = pygame.Surface((TILE_SIZE * 3, TILE_SIZE * 3), pygame.SRCALPHA)
        body_color = SECONDARY

        # Body (rounded shape)
        pygame.draw.circle(sprite, body_color, (TILE_SIZE * 1.5, TILE_SIZE * 1.5), TILE_SIZE)

        # Eyes (big and friendly)
        eye_size = TILE_SIZE * 0.25
        pygame.draw.circle(sprite, WHITE, (TILE_SIZE * 1.2, TILE_SIZE * 1.2), eye_size)
        pygame.draw.circle(sprite, WHITE, (TILE_SIZE * 1.8, TILE_SIZE * 1.2), eye_size)

        # Draw pupils
        pupil_size = eye_size * 0.5
        pygame.draw.circle(sprite, BLACK, (TILE_SIZE * 1.2, TILE_SIZE * 1.2), pupil_size)
        pygame.draw.circle(sprite, BLACK, (TILE_SIZE * 1.8, TILE_SIZE * 1.2), pupil_size)

        # Draw eye highlights (for sparkle)
        highlight_size = pupil_size * 0.4
        pygame.draw.circle(sprite, WHITE, (TILE_SIZE * 1.15, TILE_SIZE * 1.15), highlight_size)
        pygame.draw.circle(sprite, WHITE, (TILE_SIZE * 1.75, TILE_SIZE * 1.15), highlight_size)

        # Draw natural smile (gentle curve) - fixed to always smile
        smile_radius = TILE_SIZE * 0.5
        pygame.draw.arc(sprite, BLACK,
                        (TILE_SIZE * 1.0, TILE_SIZE * 1.3, TILE_SIZE, smile_radius),
                        math.pi, 2 * math.pi, 4)  # Natural upward curve

        # Draw blush marks
        blush_color = (255, 150, 150)
        blush_size = TILE_SIZE * 0.15
        pygame.draw.circle(sprite, blush_color, (TILE_SIZE * 1.0, TILE_SIZE * 1.4), blush_size)
        pygame.draw.circle(sprite, blush_color, (TILE_SIZE * 2.0, TILE_SIZE * 1.4), blush_size)

        return sprite

    def draw(self, screen):
        # Modern background
        screen.fill(SKY_BLUE)

        # Draw modern clouds
        for i in range(5):
            x = (i * 200 + pygame.time.get_ticks() // 50) % (self.screen_width + 400) - 200
            y = 80 + (i * 40) % 120
            self.draw_material_cloud(screen, x, y)

        # Calculate responsive dimensions
        arena_padding = max(40, min(80, self.screen_width // 20))
        arena_width = self.screen_width - arena_padding * 2
        arena_height = self.screen_height - arena_padding * 2

        # Draw Material Design card with shadow
        arena_rect = pygame.Rect(arena_padding, arena_padding, arena_width, arena_height)
        pygame.draw.rect(screen, SURFACE, arena_rect, border_radius=20)
        pygame.draw.rect(screen, (200, 200, 200), arena_rect, 2, border_radius=20)

        # Draw title
        title_size = max(28, min(48, self.screen_width // 30))
        title_font = pygame.font.SysFont("Arial", title_size, bold=True)
        title = title_font.render("POKÉMON ENCOUNTER", True, PRIMARY_DARK)
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, arena_padding + 30))

        # Draw pokemon with responsive scaling
        pokemon_size = min(TILE_SIZE * 3, self.screen_width // 4)
        pokemon_x = self.screen_width // 2 - pokemon_size // 2
        pokemon_y = arena_padding + 80

        # Scale the pokemon sprite
        scaled_pokemon = pygame.transform.scale(
            self.pokemon_sprite,
            (pokemon_size, pokemon_size)
        )
        screen.blit(scaled_pokemon, (pokemon_x, pokemon_y))

        # Content card - responsive
        content_top = arena_padding + 80 + pokemon_size + 20
        content_height = max(150, min(250, self.screen_height // 4))
        content_rect = pygame.Rect(arena_padding + 20, content_top, arena_width - 40, content_height)
        pygame.draw.rect(screen, SURFACE, content_rect, border_radius=16)
        pygame.draw.rect(screen, (200, 200, 200), content_rect, 2, border_radius=16)

        # Stats card - responsive
        stats_top = content_top + content_height + 20
        stats_height = max(80, min(120, self.screen_height // 8))
        stats_rect = pygame.Rect(arena_padding + 20, stats_top, arena_width - 40, stats_height)
        pygame.draw.rect(screen, PRIMARY_LIGHT, stats_rect, border_radius=16)
        pygame.draw.rect(screen, PRIMARY_DARK, stats_rect, 2, border_radius=16)

        # Draw sun with modern design
        sun_x = self.screen_width - 100
        sun_y = 100
        pygame.draw.circle(screen, SECONDARY_LIGHT, (sun_x, sun_y), 40)
        for i in range(8):
            angle = math.radians(i * 45)
            pygame.draw.line(screen, SECONDARY_LIGHT,
                             (sun_x + math.cos(angle) * 40, sun_y + math.sin(angle) * 40),
                             (sun_x + math.cos(angle) * 60, sun_y + math.sin(angle) * 60), 3)

        # Content based on state
        if self.state == "question":
            # Draw question with dynamic wrapping
            question_text = self.render_text(self.card['question'], content_rect.width - 40, font_medium)
            screen.blit(question_text, (content_rect.x + 20, content_rect.y + 20))

            # Answer input field
            input_height = max(30, min(50, self.screen_height // 20))
            input_rect = pygame.Rect(content_rect.x + 20, content_rect.y + 70, content_rect.width - 40, input_height)
            pygame.draw.rect(screen, BACKGROUND, input_rect, border_radius=8)
            pygame.draw.rect(screen, PRIMARY, input_rect, 2, border_radius=8)

            # Draw answer text
            answer_font = pygame.font.SysFont("Arial", max(16, min(24, self.screen_height // 40)))
            answer_text = answer_font.render(self.user_answer, True, ON_SURFACE)
            screen.blit(answer_text, (input_rect.x + 10, input_rect.y + (input_height - answer_text.get_height()) // 2))

            # Draw instruction
            instruction = font_small.render("Press ENTER to submit", True, SECONDARY)
            screen.blit(instruction, (content_rect.x + 20, content_rect.y + content_height - 30))

        elif self.state == "answer":
            # Draw question
            question_text = self.render_text(f"Question: {self.card['question']}", content_rect.width - 40, font_medium)
            screen.blit(question_text, (content_rect.x + 20, content_rect.y + 20))

            # Draw correct answer
            answer_text = self.render_text(f"Answer: {self.card['answer']}", content_rect.width - 40, font_medium)
            screen.blit(answer_text, (content_rect.x + 20, content_rect.y + 60))

            # Draw user answer
            user_answer_text = self.render_text(f"Your answer: {self.user_answer}", content_rect.width - 40,
                                                font_medium)
            screen.blit(user_answer_text, (content_rect.x + 20, content_rect.y + 100))

            # Draw instruction
            instruction = font_small.render("How well did you know this? (1-5)", True, SECONDARY)
            screen.blit(instruction, (content_rect.x + 20, content_rect.y + content_height - 30))

        elif self.state == "result":
            # Draw result
            result_size = max(24, min(40, self.screen_width // 30))
            result_font = pygame.font.SysFont("Arial", result_size, bold=True)
            result_color = SUCCESS if "CORRECT" in self.result else ERROR
            result_text = result_font.render(self.result, True, result_color)
            screen.blit(result_text, (content_rect.x + content_rect.width // 2 - result_text.get_width() // 2,
                                      content_rect.y + 30))

            # Draw stats
            stats_text = font_medium.render(f"Interval: {self.stats['interval']} days • Reps: {self.stats['reps']}",
                                            True, ON_SURFACE)
            screen.blit(stats_text, (content_rect.x + content_rect.width // 2 - stats_text.get_width() // 2,
                                     content_rect.y + 90))

            # Draw button-like instruction
            button_width = max(200, min(300, self.screen_width // 4))
            button_height = max(30, min(50, self.screen_height // 20))
            button_rect = pygame.Rect(content_rect.x + content_rect.width // 2 - button_width // 2,
                                      content_rect.y + content_height - button_height - 20,
                                      button_width, button_height)
            pygame.draw.rect(screen, PRIMARY, button_rect, border_radius=20)
            button_font = pygame.font.SysFont("Arial", max(16, min(24, self.screen_height // 40)))
            button_text = button_font.render("CONTINUE JOURNEY", True, ON_PRIMARY)
            screen.blit(button_text, (button_rect.x + button_rect.width // 2 - button_text.get_width() // 2,
                                      button_rect.y + (button_height - button_text.get_height()) // 2))

        # Draw stats title
        stats_title = font_large.render("LEARNING STATS", True, PRIMARY_DARK)
        screen.blit(stats_title, (stats_rect.x + stats_rect.width // 2 - stats_title.get_width() // 2,
                                  stats_rect.y + 10))

        # Draw stats content
        stats_info = font_small.render(
            f"Reviews: {self.stats['reps']} • Lapses: {self.stats['lapses']} • Ease: {self.stats['ease']:.2f}",
            True, ON_SURFACE
        )
        screen.blit(stats_info, (stats_rect.x + stats_rect.width // 2 - stats_info.get_width() // 2,
                                 stats_rect.y + 40))

        next_review = datetime.datetime.fromisoformat(self.stats['due_date'])
        next_review_text = font_small.render(
            f"Next review: {next_review.strftime('%Y-%m-%d')}",
            True, ON_SURFACE
        )
        screen.blit(next_review_text, (stats_rect.x + stats_rect.width // 2 - next_review_text.get_width() // 2,
                                       stats_rect.y + 70))

    def draw_material_cloud(self, surface, x, y):
        # Draw simplified cloud with geometric shapes
        cloud_color = SURFACE
        pygame.draw.circle(surface, cloud_color, (x, y), 30)
        pygame.draw.circle(surface, cloud_color, (x + 25, y - 15), 25)
        pygame.draw.circle(surface, cloud_color, (x + 25, y + 15), 25)
        pygame.draw.circle(surface, cloud_color, (x + 50, y), 30)

    def handle_input(self, event):
        current_time = time.time()

        if event.type == pygame.KEYDOWN:
            if self.state == "question":
                if event.key == pygame.K_RETURN:
                    self.state = "answer"
                elif event.key == pygame.K_BACKSPACE:
                    self.user_answer = self.user_answer[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return "exit"
                elif current_time - self.last_key_time > self.key_delay:
                    self.user_answer += event.unicode
                    self.last_key_time = current_time


            elif self.state == "answer":
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    quality = int(event.unicode)
                    self.srs_system.process_review(self.card['id'], quality)

                    if quality >= 3:
                        self.result = "CORRECT! You learned together!"
                        try:
                            self.victory_sound.play()  # Use the class attribute
                        except Exception as e:
                            print(f"Error playing victory sound: {e}")
                    else:
                        self.result = "ALMOST! Keep practicing!"
                    self.stats = self.srs_system.get_card_stats(self.card['id'])
                    self.state = "result"

            elif self.state == "result":
                if event.key == pygame.K_SPACE:
                    try:
                        pygame.mixer.music.stop()
                        try:
                            pygame.mixer.music.load(SOUND_PATHS["background"])
                            pygame.mixer.music.play(-1)
                        except Exception as e:
                            print(f"Error loading background music: {e}")
                    except:
                        pass
                    return "continue"
                elif event.key == pygame.K_ESCAPE:
                    try:
                        pygame.mixer.music.stop()
                        try:
                            pygame.mixer.music.load(SOUND_PATHS["background"])
                            pygame.mixer.music.play(-1)
                        except Exception as e:
                            print(f"Error loading background music: {e}")
                    except:
                        pass
                    return "exit"

        return None

    def render_text(self, text, max_width, font):
        """Render text with wrapping for responsiveness"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, ON_SURFACE)
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        lines.append(' '.join(current_line))

        # Create a surface to hold all lines
        line_height = font.get_linesize()
        total_height = line_height * len(lines)
        text_surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)

        # Render each line
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, ON_SURFACE)
            text_surface.blit(line_surface, (0, i * line_height))

        return text_surface


class PeacefulAnimal:
    def __init__(self, x, y, animal_type, screen_width, screen_height):
        self.x = x
        self.y = y
        self.type = animal_type
        self.speed = random.uniform(0.5, 2.0)
        self.direction = random.uniform(0, 2 * math.pi)
        self.sprite = self.create_material_sprite()
        self.move_timer = random.randint(60, 120)
        self.resting = False
        self.rest_timer = random.randint(120, 240)
        self.screen_width = screen_width
        self.screen_height = screen_height

    def create_material_sprite(self):
        size = TILE_SIZE
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)

        if self.type == "deer":
            # Modern deer design
            color = (180, 140, 100)
            # Body
            pygame.draw.ellipse(sprite, color, (size * 0.2, size * 0.3, size * 0.6, size * 0.4))
            # Neck and head
            pygame.draw.ellipse(sprite, color, (size * 0.6, size * 0.1, size * 0.3, size * 0.3))
            # Legs
            pygame.draw.rect(sprite, color, (size * 0.3, size * 0.7, size * 0.1, size * 0.3))
            pygame.draw.rect(sprite, color, (size * 0.6, size * 0.7, size * 0.1, size * 0.3))
            # Antlers
            pygame.draw.line(sprite, color, (size * 0.8, size * 0.1), (size * 0.9, size * 0.0), 3)
            pygame.draw.line(sprite, color, (size * 0.8, size * 0.1), (size * 0.9, size * 0.2), 3)
            # Modern smile (gentle curve) - fixed to always smile
            pygame.draw.arc(sprite, ON_SURFACE,
                            (size * 0.65, size * 0.15, size * 0.2, size * 0.1),
                            math.pi, 0, 2)  # Changed to upward curve

        elif self.type == "rabbit":
            # Modern rabbit design
            color = (150, 150, 150)
            # Body
            pygame.draw.ellipse(sprite, color, (size * 0.2, size * 0.4, size * 0.6, size * 0.4))
            # Head
            pygame.draw.circle(sprite, color, (size * 0.7, size * 0.3), size * 0.2)
            # Ears
            pygame.draw.ellipse(sprite, color, (size * 0.6, size * 0.1, size * 0.15, size * 0.3))
            pygame.draw.ellipse(sprite, color, (size * 0.75, size * 0.1, size * 0.15, size * 0.3))
            # Legs
            pygame.draw.rect(sprite, color, (size * 0.3, size * 0.7, size * 0.1, size * 0.2))
            pygame.draw.rect(sprite, color, (size * 0.6, size * 0.7, size * 0.1, size * 0.2))
            # Modern smile (gentle curve)
            pygame.draw.arc(sprite, ON_SURFACE,
                            (size * 0.65, size * 0.30, size * 0.1, size * 0.05),
                            math.pi, 0, 2)  # Changed to upward curve

        elif self.type == "bird":
            color = random.choice(FLOWER_COLORS)
            # Body
            pygame.draw.circle(sprite, color, (size * 0.5, size * 0.5), size * 0.2)
            # Wings
            pygame.draw.ellipse(sprite, color, (size * 0.3, size * 0.4, size * 0.4, size * 0.2))
            # Head
            pygame.draw.circle(sprite, color, (size * 0.7, size * 0.4), size * 0.15)
            # Beak
            pygame.draw.polygon(sprite, (230, 180, 50), [
                (size * 0.8, size * 0.4),
                (size * 0.9, size * 0.4),
                (size * 0.85, size * 0.45)
            ])
            # Modern smile (gentle curve)
            pygame.draw.arc(sprite, ON_SURFACE,
                            (size * 0.65, size * 0.37, size * 0.1, size * 0.05),
                            math.pi, 0, 1)  # Changed to upward curve

        return sprite

    def update(self):
        if not self.resting:
            # Move in current direction
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed

            # Change direction occasionally
            self.move_timer -= 1
            if self.move_timer <= 0:
                self.direction = random.uniform(0, 2 * math.pi)
                self.move_timer = random.randint(60, 120)
                self.rest_timer = random.randint(120, 240)

            # Boundary check
            if self.x < 0 or self.x > self.screen_width:
                self.direction = math.pi - self.direction
            if self.y < self.screen_height * 0.6 or self.y > self.screen_height:
                self.direction = -self.direction

            # Keep within bounds
            self.x = max(0, min(self.screen_width, self.x))
            self.y = max(self.screen_height * 0.6, min(self.screen_height, self.y))

            # Occasionally rest
            if random.random() < 0.01:
                self.resting = True
        else:
            # Rest for a while
            self.rest_timer -= 1
            if self.rest_timer <= 0:
                self.resting = False
                self.direction = random.uniform(0, 2 * math.pi)
                self.move_timer = random.randint(60, 120)

    def draw(self, screen):
        screen.blit(self.sprite, (self.x - self.sprite.get_width() // 2, self.y - self.sprite.get_height() // 2))



class MeditationMeadow:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.animals = []
        self.affirmations = [
            "Breathe in calm, breathe out stress",
            "This moment is perfect as it is",
            "You are exactly where you need to be",
            "Peace comes from within",
            "Your mind is clear and focused",
            "Every breath brings new energy",
            "You are safe and supported",
            "Release tension with each exhale"
        ]
        self.current_affirmation = random.choice(self.affirmations)
        self.affirmation_timer = 300
        self.flowers = self.create_material_flowers(screen_width, screen_height)
        self.butterflies = []
        self.breath_progress = 0
        self.breath_direction = 1  # 1 for inhale, -1 for exhale
        self.last_update = time.time()
        self.breath_cycle = 8  # seconds for full breath cycle

        # Create peaceful animals
        for _ in range(5):
            animal_type = random.choice(["deer", "rabbit", "bird"])
            x = random.randint(0, screen_width)
            y = random.randint(screen_height * 0.6, screen_height - 50)
            self.animals.append(PeacefulAnimal(x, y, animal_type, screen_width, screen_height))

        # Create butterflies
        for _ in range(10):
            self.butterflies.append({
                'x': random.randint(0, screen_width),
                'y': random.randint(0, screen_height // 2),
                'color': random.choice(FLOWER_COLORS),
                'speed': random.uniform(0.5, 1.5),
                'angle': 0
            })

        # Play calm music
        try:
            pygame.mixer.music.load(SOUND_PATHS["calm"])
            pygame.mixer.music.play(-1)
            print("Calm music started")
        except Exception as e:
            print(f"Error loading calm music: {e}")

    def create_nature_sounds(self):
        # Create bird chirp
        create_tone_wav("sounds/bird_chirp.wav",
                        frequencies=[880, 1320, 1760, 2200],
                        duration=0.3, amplitude=0.3, envelope=True)

        # Create water stream
        samples = []
        sample_rate = 44100
        duration = 5.0
        for i in range(int(sample_rate * duration)):
            t = i / float(sample_rate)
            # Water stream noise with gentle variations
            value = 0.2 * (random.random() - 0.5) + 0.1 * math.sin(2 * math.pi * 200 * t)
            samples.append(value)

        with wave.open("sounds/water_stream.wav", 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.setnframes(len(samples))
            for sample in samples:
                sample = max(-1.0, min(1.0, sample))
                sample = int(sample * 32767)
                wav_file.writeframes(struct.pack('<h', sample))

        # Create wind sound
        create_tone_wav("sounds/wind.wav",
                        frequencies=[200, 300, 400],
                        duration=3.0, amplitude=0.2, envelope=True)

    def create_material_flowers(self, screen_width, screen_height):
        flowers = []
        y_min = int(screen_height * 0.6)
        y_max = int(screen_height)
        for _ in range(100):
            x = random.randint(0, screen_width)
            y = random.randint(y_min, y_max)
            color = random.choice(FLOWER_COLORS)
            size = random.randint(15, 30)
            flower_type = random.choice(["daisy", "tulip", "rose", "sunflower", "violet"])
            flowers.append((x, y, color, size, flower_type))
        return flowers

    def draw_flower(self, surface, x, y, color, size, flower_type):
        if flower_type == "daisy":
            # Daisy with white petals and yellow center
            pygame.draw.circle(surface, (255, 255, 255), (x, y), size)
            pygame.draw.circle(surface, (255, 255, 0), (x, y), size // 3)
        elif flower_type == "tulip":
            # Tulip shape
            points = [
                (x, y - size),
                (x - size // 1.5, y),
                (x - size // 3, y + size // 2),
                (x + size // 3, y + size // 2),
                (x + size // 1.5, y),
            ]
            pygame.draw.polygon(surface, color, points)
        elif flower_type == "rose":
            # Rose with layered petals
            pygame.draw.circle(surface, color, (x, y), size // 1.5)
            for i in range(5):
                angle = math.radians(i * 72)
                px = x + math.cos(angle) * size
                py = y + math.sin(angle) * size
                pygame.draw.circle(surface, color, (px, py), size // 2)
            pygame.draw.circle(surface, (255, 200, 200), (x, y), size // 3)
        elif flower_type == "sunflower":
            # Sunflower with brown center and yellow petals
            pygame.draw.circle(surface, (139, 69, 19), (x, y), size // 1.5)
            for i in range(12):
                angle = math.radians(i * 30)
                px = x + math.cos(angle) * size
                py = y + math.sin(angle) * size
                pygame.draw.ellipse(surface, (255, 204, 0),
                                    (px - size // 2, py - size // 4, size, size // 2))
        elif flower_type == "violet":
            # Violet with multiple small flowers
            for i in range(5):
                offset_x = random.randint(-size, size)
                offset_y = random.randint(-size, size)
                pygame.draw.circle(surface, (138, 43, 226),
                                   (x + offset_x, y + offset_y), size // 2)

    def draw_butterfly(self, surface, x, y, color):
        # Draw a modern butterfly
        # Body
        pygame.draw.ellipse(surface, color, (x - 5, y - 2, 10, 4))
        # Wings
        wing_offset = math.sin(pygame.time.get_ticks() / 100) * 5
        pygame.draw.ellipse(surface, color, (x - 8, y - 8 - wing_offset, 8, 16))
        pygame.draw.ellipse(surface, color, (x, y - 8 + wing_offset, 8, 16))

    def update(self):
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time

        # Update breath progress
        self.breath_progress += delta_time / self.breath_cycle * self.breath_direction

        # Change breath direction at cycle ends
        if self.breath_progress >= 1.0:
            self.breath_progress = 1.0
            self.breath_direction = -1
        elif self.breath_progress <= 0.0:
            self.breath_progress = 0.0
            self.breath_direction = 1

        # Update animals
        for animal in self.animals:
            animal.update()

        # Update butterflies
        for butterfly in self.butterflies:
            butterfly['x'] += butterfly['speed']
            butterfly['y'] += math.sin(current_time) * 1.5

            # Reset if off screen
            if butterfly['x'] > self.screen_width + 50:
                butterfly['x'] = -50
            elif butterfly['x'] < -50:
                butterfly['x'] = self.screen_width + 50

            if butterfly['y'] > self.screen_height + 50:
                butterfly['y'] = -50
            elif butterfly['y'] < -50:
                butterfly['y'] = self.screen_height + 50

        # Rotate affirmations
        self.affirmation_timer -= 1
        if self.affirmation_timer <= 0:
            self.current_affirmation = random.choice(self.affirmations)
            self.affirmation_timer = 300

        # Play nature sounds randomly
        self.sound_timer += 1
        if self.sound_timer >= self.next_sound_time:
            sound_file = random.choice(self.nature_sounds)
            try:
                sound = pygame.mixer.Sound(sound_file)
                sound.play()
            except:
                pass
            self.sound_timer = 0
            self.next_sound_time = random.randint(100, 300)

    def draw(self, screen):
        # More realistic nature background
        # Sky gradient
        for y in range(0, self.screen_height // 2):
            # Gradient from light blue to lighter blue
            blue_val = 230 - int(y / (self.screen_height // 2) * 30)
            pygame.draw.line(screen, (173, 216, blue_val), (0, y), (self.screen_width, y))

        # Distant mountains
        for i in range(3):
            height = random.randint(100, 200)
            width = random.randint(300, 500)
            x = i * 400 - 100
            pygame.draw.polygon(screen, (120, 120, 120), [
                (x, self.screen_height // 2 - height),
                (x + width // 3, self.screen_height // 2 - height * 0.7),
                (x + width // 2, self.screen_height // 2 - height),
                (x + width, self.screen_height // 2)
            ])
            # Snow caps
            pygame.draw.polygon(screen, WHITE, [
                (x + width // 3, self.screen_height // 2 - height * 0.7),
                (x + width // 2, self.screen_height // 2 - height),
                (x + width // 2 - 30, self.screen_height // 2 - height * 0.8)
            ])

        # Meadow with gradient
        for y in range(self.screen_height // 2, self.screen_height):
            # Gradient from meadow green to darker green
            green_val = 200 - int((y - self.screen_height // 2) / (self.screen_height // 2) * 80)
            pygame.draw.line(screen, (120, green_val, 120), (0, y), (self.screen_width, y))

        # Draw flowers with responsive sizing
        for x, y, color, size, flower_type in self.flowers:
            self.draw_flower(screen, x, y, color,
                             max(10, min(30, size * self.screen_width // 1200)),
                             flower_type)

        # Draw butterflies
        for butterfly in self.butterflies:
            self.draw_butterfly(screen, butterfly['x'], butterfly['y'], butterfly['color'])

        # Draw animals
        for animal in self.animals:
            animal.draw(screen)

        # Responsive content card
        card_width = min(800, self.screen_width - 100)
        card_height = max(150, min(250, self.screen_height // 4))
        card_rect = pygame.Rect(self.screen_width // 2 - card_width // 2, 40, card_width, card_height)
        draw_card(screen, card_rect, ELEVATION_HIGH, SURFACE, 24)

        # Responsive title
        title_size = max(28, min(48, self.screen_width // 30))
        title_font = pygame.font.SysFont("Arial", title_size, bold=True)
        title = title_font.render("Peaceful Meadow", True, PRIMARY_DARK)
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 50))

        # Draw affirmation
        aff_size = max(20, min(32, self.screen_width // 40))
        aff_font = pygame.font.SysFont("Arial", aff_size)
        aff_text = aff_font.render(self.current_affirmation, True, ON_SURFACE)
        screen.blit(aff_text, (self.screen_width // 2 - aff_text.get_width() // 2, 100))

        # Draw breathing guide
        breath_time = (pygame.time.get_ticks() // 1000) % 8
        if breath_time < 4:
            breath_text = font_medium.render("Breathe in...", True, SECONDARY)
        else:
            breath_text = font_medium.render("Breathe out...", True, PRIMARY)
        screen.blit(breath_text, (self.screen_width // 2 - breath_text.get_width() // 2, 150))

        # Draw progress circle
        progress = breath_time / 8
        circle_size = max(70, min(100, self.screen_width // 15))
        circle_rect = pygame.Rect(self.screen_width // 2 - circle_size // 2, 180, circle_size, circle_size)
        pygame.draw.arc(screen, (200, 200, 200), circle_rect, 0, 2 * math.pi, 5)
        pygame.draw.arc(screen, SECONDARY if breath_time < 4 else PRIMARY,
                        circle_rect, -math.pi / 2, -math.pi / 2 + 2 * math.pi * progress, 8)

        # Button card
        button_width = max(300, min(400, self.screen_width // 3))
        button_height = max(40, min(60, self.screen_height // 15))
        button_rect = pygame.Rect(self.screen_width // 2 - button_width // 2,
                                  self.screen_height - 120,
                                  button_width, button_height)
        draw_card(screen, button_rect, ELEVATION_MEDIUM, PRIMARY, 30)

        # Draw button text
        button_font = pygame.font.SysFont("Arial", max(18, min(28, self.screen_width // 50)))
        button_text = button_font.render("CONTINUE JOURNEY", True, ON_PRIMARY)
        screen.blit(button_text, (button_rect.x + button_rect.width // 2 - button_text.get_width() // 2,
                                  button_rect.y + (button_height - button_text.get_height()) // 2))

    def draw_material_cloud(self, surface, x, y):
        # Draw simplified cloud
        cloud_color = SURFACE
        pygame.draw.circle(surface, cloud_color, (x, y), 30)
        pygame.draw.circle(surface, cloud_color, (x + 25, y - 15), 25)
        pygame.draw.circle(surface, cloud_color, (x + 25, y + 15), 25)
        pygame.draw.circle(surface, cloud_color, (x + 50, y), 30)


class InfiniteWorld:
    def __init__(self):
        self.chunks = {}
        self.tile_textures = self.create_material_tile_textures()
        self.seed = random.randint(0, 1000000)
        self.generated_chunks = set()

    def get_chunk_key(self, chunk_x, chunk_y):
        return f"{chunk_x},{chunk_y}"

    def generate_chunk(self, chunk_x, chunk_y):
        chunk_key = self.get_chunk_key(chunk_x, chunk_y)
        if chunk_key in self.chunks:
            return self.chunks[chunk_key]

        chunk = []
        random.seed(self.seed + chunk_x * 1000 + chunk_y)

        for y in range(CHUNK_SIZE):
            row = []
            for x in range(CHUNK_SIZE):
                # Global coordinates for consistent noise
                world_x = chunk_x * CHUNK_SIZE + x
                world_y = chunk_y * CHUNK_SIZE + y

                # Generate terrain based on noise
                nx = world_x / 50.0
                ny = world_y / 50.0

                # Generate elevation and moisture values
                elevation = self.noise(nx, ny, 0)
                moisture = self.noise(nx, ny, 1000)

                # River generation using a different noise
                river_value = self.noise(nx * 2, ny * 2, 5000)

                # Determine terrain type
                if river_value > 0.65 and river_value < 0.67:
                    tile_type = "water"
                elif river_value > 0.63 and river_value < 0.7:
                    tile_type = "sand"
                elif elevation < 0.2:
                    tile_type = "water"
                elif elevation < 0.25:
                    tile_type = "sand"
                elif elevation > 0.8:
                    tile_type = "rock"
                elif moisture > 0.6:
                    tile_type = "tree"
                elif random.random() < 0.1:  # 10% chance for meadow
                    tile_type = "meadow"
                else:
                    tile_type = "grass"

                row.append(tile_type)
            chunk.append(row)

        self.chunks[chunk_key] = chunk
        return chunk

    def noise(self, x, y, offset):
        # Improved noise function for better terrain
        n = int(x + y * 57 + offset)
        n = (n << 13) ^ n
        noise = (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)

        # Add some octaves for more natural terrain
        noise += 0.5 * (1.0 - ((n * 2 * (n * 2 * n * 2 * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)
        return noise * 0.5 + 0.5  # Normalize to 0-1 range

    # Rest of InfiniteWorld class remains the same...

    def generate_rivers_and_spots(self):
        # Create 2-3 winding rivers
        num_rivers = random.randint(2, 3)
        for _ in range(num_rivers):
            river = []
            # Start at a random point on the edge
            start_side = random.choice(['top', 'bottom', 'left', 'right'])
            if start_side == 'top':
                x, y = random.randint(0, 1000), 0
            elif start_side == 'bottom':
                x, y = random.randint(0, 1000), 1000
            elif start_side == 'left':
                x, y = 0, random.randint(0, 1000)
            else:  # right
                x, y = 1000, random.randint(0, 1000)

            # Create a winding path
            for _ in range(100):  # River length
                river.append((x, y))
                # Random direction with bias toward opposite side
                if start_side == 'top':
                    y += 10
                    x += random.randint(-15, 15)
                elif start_side == 'bottom':
                    y -= 10
                    x += random.randint(-15, 15)
                elif start_side == 'left':
                    x += 10
                    y += random.randint(-15, 15)
                else:  # right
                    x -= 10
                    y += random.randint(-15, 15)

                # Ensure we stay within reasonable bounds
                x = max(0, min(1000, x))
                y = max(0, min(1000, y))
            self.rivers.append(river)

        # Create meditation spots near rivers
        for river in self.rivers:
            for _ in range(3):  # 3 spots per river
                # Choose a random point along the river
                idx = random.randint(10, len(river) - 10)
                x, y = river[idx]

                # Create a clearing around it
                clearing = []
                for dx in range(-5, 6):
                    for dy in range(-5, 6):
                        if dx * dx + dy * dy <= 25:  # Circular clearing
                            clearing.append((x + dx * TILE_SIZE, y + dy * TILE_SIZE))
                self.meditation_spots.append(clearing)



    def get_tile(self, tile_x, tile_y):
        # Calculate chunk coordinates
        chunk_x = tile_x // CHUNK_SIZE
        chunk_y = tile_y // CHUNK_SIZE

        # Get the chunk
        chunk = self.generate_chunk(chunk_x, chunk_y)

        # Get local coordinates within chunk
        local_x = tile_x % CHUNK_SIZE
        local_y = tile_y % CHUNK_SIZE

        return chunk[local_y][local_x]

    def create_material_tile_textures(self):
        textures = {
            "grass": pygame.Surface((TILE_SIZE, TILE_SIZE)),
            "water": pygame.Surface((TILE_SIZE, TILE_SIZE)),
            "tree": pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA),
            "rock": pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA),
            "sand": pygame.Surface((TILE_SIZE, TILE_SIZE)),
            "meadow": pygame.Surface((TILE_SIZE, TILE_SIZE))
        }

        # Grass texture with modern pattern
        textures["grass"].fill(GRASS_GREEN)
        for _ in range(10):
            x = random.randint(0, TILE_SIZE - 1)
            y = random.randint(0, TILE_SIZE - 1)
            pygame.draw.circle(textures["grass"], (100, 180, 100), (x, y), random.randint(2, 4))

        # Water texture with wave pattern
        textures["water"].fill(WATER_BLUE)
        for y in range(0, TILE_SIZE, 8):
            offset = math.sin(y * 0.5) * 4
            pygame.draw.arc(textures["water"], (100, 180, 255),
                            (-10 + offset, y - 4, TILE_SIZE + 20, 8), math.pi, 0, 2)

        # Sand texture with modern pattern
        textures["sand"].fill(SAND_YELLOW)
        for _ in range(20):
            x = random.randint(0, TILE_SIZE - 1)
            y = random.randint(0, TILE_SIZE - 1)
            pygame.draw.circle(textures["sand"], (230, 190, 150), (x, y), random.randint(1, 3))

        # Tree texture (modern geometric tree)
        pygame.draw.rect(textures["tree"], (121, 85, 72), (TILE_SIZE // 2 - 6, TILE_SIZE // 2, 12, TILE_SIZE // 2))
        pygame.draw.circle(textures["tree"], (76, 175, 80), (TILE_SIZE // 2, TILE_SIZE // 2 - 10), TILE_SIZE // 3)

        # Add geometric details
        for angle in [0, 120, 240]:
            rad = math.radians(angle)
            dist = TILE_SIZE // 3
            x = TILE_SIZE // 2 + math.cos(rad) * dist
            y = TILE_SIZE // 2 - 10 + math.sin(rad) * dist
            pygame.draw.circle(textures["tree"], PRIMARY, (x, y), TILE_SIZE // 8)

        # Rock texture with geometric pattern
        pygame.draw.circle(textures["rock"], (158, 158, 158), (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 4)
        pygame.draw.polygon(textures["rock"], (189, 189, 189), [
            (TILE_SIZE // 2, TILE_SIZE // 4),
            (TILE_SIZE * 3 // 4, TILE_SIZE // 2),
            (TILE_SIZE // 2, TILE_SIZE * 3 // 4),
            (TILE_SIZE // 4, TILE_SIZE // 2)
        ])

        # Meadow texture (with geometric flowers)
        textures["meadow"].fill(MEADOW_GREEN)
        flower_types = ["daisy", "tulip", "rose", "sunflower", "violet"]

        for _ in range(12):  # More flowers per tile
            x = random.randint(5, TILE_SIZE - 5)
            y = random.randint(5, TILE_SIZE - 5)
            color = random.choice(FLOWER_COLORS)
            size = random.randint(6, 12)
            flower_type = random.choice(flower_types)

            # Draw different flower types
            if flower_type == "daisy":
                # Daisy with white petals and yellow center
                pygame.draw.circle(textures["meadow"], (255, 255, 255), (x, y), size)
                pygame.draw.circle(textures["meadow"], (255, 255, 0), (x, y), size // 3)
            elif flower_type == "tulip":
                # Tulip shape
                points = [
                    (x, y - size),
                    (x - size // 1.5, y),
                    (x - size // 3, y + size // 2),
                    (x + size // 3, y + size // 2),
                    (x + size // 1.5, y),
                ]
                pygame.draw.polygon(textures["meadow"], color, points)
            elif flower_type == "rose":
                # Rose with layered petals
                pygame.draw.circle(textures["meadow"], color, (x, y), size // 1.5)
                for i in range(5):
                    angle = math.radians(i * 72)
                    px = x + math.cos(angle) * size
                    py = y + math.sin(angle) * size
                    pygame.draw.circle(textures["meadow"], color, (px, py), size // 2)
                pygame.draw.circle(textures["meadow"], (255, 200, 200), (x, y), size // 3)
            elif flower_type == "sunflower":
                # Sunflower with brown center and yellow petals
                pygame.draw.circle(textures["meadow"], (139, 69, 19), (x, y), size // 1.5)
                for i in range(12):
                    angle = math.radians(i * 30)
                    px = x + math.cos(angle) * size
                    py = y + math.sin(angle) * size
                    pygame.draw.ellipse(textures["meadow"], (255, 204, 0),
                                        (px - size // 2, py - size // 4, size, size // 2))
            elif flower_type == "violet":
                # Violet with multiple small flowers
                for i in range(5):
                    offset_x = random.randint(-size, size)
                    offset_y = random.randint(-size, size)
                    pygame.draw.circle(textures["meadow"], (138, 43, 226),
                                       (x + offset_x, y + offset_y), size // 2)

        return textures

    def draw(self, screen, camera_x, camera_y, screen_width, screen_height):
        # Calculate visible tile range
        start_tile_x = max(0, int(camera_x // TILE_SIZE) - 1)
        start_tile_y = max(0, int(camera_y // TILE_SIZE) - 1)
        end_tile_x = int((camera_x + screen_width) // TILE_SIZE) + 2
        end_tile_y = int((camera_y + screen_height) // TILE_SIZE) + 2

        # Draw tiles
        for tile_y in range(start_tile_y, end_tile_y):
            for tile_x in range(start_tile_x, end_tile_x):
                tile_type = self.get_tile(tile_x, tile_y)
                texture = self.tile_textures[tile_type]

                screen_x = tile_x * TILE_SIZE - camera_x
                screen_y = tile_y * TILE_SIZE - camera_y

                screen.blit(texture, (screen_x, screen_y))


class PauseMenu:
    def __init__(self, screen_width, screen_height, game):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        self.options = ["Resume", "Settings", "Save Game", "Load Game", "Quit to Menu", "Quit Game"]
        self.settings_options = ["Music Volume", "Sound Effects", "Back"]
        self.current_menu = "main"
        self.selected_index = 0
        self.settings_volume = game.music_volume * 100  # Convert to percentage
        self.sound_enabled = True
        self.last_key_time = 0
        self.key_delay = 0.2  # Delay for key repeats

    def draw(self, screen):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Draw pause menu card
        card_width = min(400, self.screen_width - 200)
        card_height = min(400, self.screen_height - 200)
        card_rect = pygame.Rect(
            self.screen_width // 2 - card_width // 2,
            self.screen_height // 2 - card_height // 2,
            card_width,
            card_height
        )
        draw_card(screen, card_rect, ELEVATION_HIGH, SURFACE, 16)

        # Draw title
        title = font_xlarge.render("PAUSED", True, PRIMARY_DARK)
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, card_rect.y + 30))

        # Draw options based on current menu
        if self.current_menu == "main":
            options = self.options
        else:
            options = self.settings_options

        option_height = 40
        start_y = card_rect.y + 100

        for i, option in enumerate(options):
            color = PRIMARY if i == self.selected_index else ON_SURFACE
            text = font_medium.render(option, True, color)

            # Special rendering for settings options
            if self.current_menu == "settings":
                if option == "Music Volume":
                    # Draw volume slider
                    slider_width = 200
                    slider_rect = pygame.Rect(
                        self.screen_width // 2 + 20,
                        start_y + i * option_height,
                        slider_width,
                        20
                    )
                    pygame.draw.rect(screen, (200, 200, 200), slider_rect, border_radius=10)

                    # Draw filled portion
                    fill_width = int(self.settings_volume / 100 * slider_width)
                    fill_rect = pygame.Rect(slider_rect.x, slider_rect.y, fill_width, slider_rect.height)
                    pygame.draw.rect(screen, PRIMARY, fill_rect, border_radius=10)

                    # Draw volume percentage
                    vol_text = font_medium.render(f"{int(self.settings_volume)}%", True, color)
                    screen.blit(vol_text, (slider_rect.x + slider_width + 10, slider_rect.y - 5))

                    # Draw option label
                    screen.blit(text, (self.screen_width // 2 - 220, start_y + i * option_height))

                elif option == "Sound Effects":
                    # Draw toggle button
                    toggle_text = font_medium.render("ON" if self.sound_enabled else "OFF", True, color)
                    screen.blit(text, (self.screen_width // 2 - 220, start_y + i * option_height))
                    screen.blit(toggle_text, (self.screen_width // 2 + 100, start_y + i * option_height))
                else:
                    screen.blit(text, (self.screen_width // 2 - text.get_width() // 2, start_y + i * option_height))
            else:
                screen.blit(text, (self.screen_width // 2 - text.get_width() // 2, start_y + i * option_height))

    def handle_input(self, event):
        current_time = time.time()

        if event.type == pygame.KEYDOWN:
            if current_time - self.last_key_time < self.key_delay:
                return

            self.last_key_time = current_time

            if event.key == pygame.K_UP:
                if self.current_menu == "main":
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                else:
                    self.selected_index = (self.selected_index - 1) % len(self.settings_options)

            elif event.key == pygame.K_DOWN:
                if self.current_menu == "main":
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                else:
                    self.selected_index = (self.selected_index + 1) % len(self.settings_options)

            elif event.key == pygame.K_RETURN:
                if self.current_menu == "main":
                    selected_option = self.options[self.selected_index]

                    if selected_option == "Resume":
                        return "resume"
                    elif selected_option == "Settings":
                        self.current_menu = "settings"
                        self.selected_index = 0
                    elif selected_option == "Save Game":
                        self.game.srs_system.save_progress()
                        return "save"
                    elif selected_option == "Load Game":
                        self.game.srs_system.load_progress()
                        self.game.due_cards = deque(self.game.srs_system.get_due_cards())
                        return "load"
                    elif selected_option == "Quit to Menu":
                        return "quit_to_menu"
                    elif selected_option == "Quit Game":
                        return "quit_game"

                else:  # In settings menu
                    selected_option = self.settings_options[self.selected_index]

                    if selected_option == "Back":
                        self.current_menu = "main"
                        self.selected_index = 0
                    elif selected_option == "Sound Effects":
                        self.sound_enabled = not self.sound_enabled

            elif event.key == pygame.K_ESCAPE:
                if self.current_menu == "settings":
                    self.current_menu = "main"
                    self.selected_index = 0
                else:
                    return "resume"

            # Handle volume adjustment
            elif self.current_menu == "settings" and self.settings_options[self.selected_index] == "Music Volume":
                if event.key == pygame.K_LEFT:
                    self.settings_volume = max(0, self.settings_volume - 5)
                elif event.key == pygame.K_RIGHT:
                    self.settings_volume = min(100, self.settings_volume + 5)

                # Update music volume
                self.game.music_volume = self.settings_volume / 100.0
                pygame.mixer.music.set_volume(self.game.music_volume)

        return None


class Game:
    def __init__(self, deck_data):
        self.screen = pygame.display.set_mode((INIT_SCREEN_WIDTH, INIT_SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Pokemon Spaced Repetition Game")
        self.clock = pygame.time.Clock()
        self.screen_width, self.screen_height = INIT_SCREEN_WIDTH, INIT_SCREEN_HEIGHT

        # Create infinite world
        self.world = InfiniteWorld()

        # Initialize game elements - start player in the center of a walkable tile
        start_x = TILE_SIZE * 8
        start_y = TILE_SIZE * 8
        self.player = Player(start_x, start_y)
        self.srs_system = SpacedRepetitionSystem(deck_data)
        self.battle = None
        self.meditation = None
        self.pause_menu = None
        self.due_cards = deque(self.srs_system.get_due_cards())
        self.last_encounter_time = 0
        self.encounter_cooldown = 5  # seconds
        self.camera_x = self.player.x - self.screen_width // 2
        self.camera_y = self.player.y - self.screen_height // 2
        self.music_volume = 0.5  # Default volume (50%)
        self.playing_background_music = False
        self.start_background_music()

    def start_background_music(self):
        if not self.playing_background_music:
            try:
                # Check if music file exists
                if os.path.exists(SOUND_PATHS["background"]):
                    pygame.mixer.music.load(SOUND_PATHS["background"])
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(-1)
                    self.playing_background_music = True
                    print("Background music started")
                else:
                    print(f"Music file not found: {SOUND_PATHS['background']}")
            except Exception as e:
                print(f"Error loading background music: {e}")
                self.playing_background_music = False

    def toggle_music(self):
        if self.playing_background_music:
            pygame.mixer.music.pause()
            self.playing_background_music = False
            print("Music paused")
        else:
            pygame.mixer.music.unpause()
            self.playing_background_music = True
            print("Music resumed")

    def draw_hud(self):
        # Responsive app bar
        app_bar_height = max(40, min(60, self.screen_height // 15))
        app_bar = pygame.Rect(0, 0, self.screen_width, app_bar_height)
        pygame.draw.rect(self.screen, PRIMARY, app_bar)
        draw_shadow(self.screen, app_bar, ELEVATION_MEDIUM)

        # Responsive title
        title_size = max(20, min(32, self.screen_width // 40))
        title_font = pygame.font.SysFont("Arial", title_size, bold=True)
        title = title_font.render("Pokémon Learning", True, ON_PRIMARY)
        self.screen.blit(title, (20, (app_bar_height - title.get_height()) // 2))

        # Draw due cards counter
        due_count = len(self.due_cards)
        counter_width = max(80, min(120, self.screen_width // 12))
        counter_height = max(20, min(30, self.screen_height // 30))
        counter_bg = pygame.Rect(self.screen_width - counter_width - 20,
                                 (app_bar_height - counter_height) // 2,
                                 counter_width, counter_height)
        pygame.draw.rect(self.screen, SECONDARY if due_count > 0 else (150, 150, 150),
                         counter_bg, border_radius=14)
        counter_text = font_small.render(f"{due_count} to meet", True, ON_PRIMARY)
        self.screen.blit(counter_text, (counter_bg.x + counter_bg.width // 2 - counter_text.get_width() // 2,
                                        counter_bg.y + (counter_height - counter_text.get_height()) // 2))

        # Draw FAB (Floating Action Button) for meditation
        fab_size = max(40, min(60, self.screen_height // 15))
        fab_rect = pygame.Rect(self.screen_width - fab_size - 20,
                               self.screen_height - fab_size - 20,
                               fab_size, fab_size)
        draw_card(self.screen, fab_rect, ELEVATION_HIGH, SECONDARY, fab_size // 2)
        fab_font = pygame.font.SysFont("Arial", max(20, min(32, fab_size // 2)))
        fab_text = fab_font.render("F", True, ON_PRIMARY)
        self.screen.blit(fab_text, (fab_rect.x + fab_rect.width // 2 - fab_text.get_width() // 2,
                                    fab_rect.y + fab_rect.height // 2 - fab_text.get_height() // 2))

        # Draw coordinates in subtle style
        coords_text = font_small.render(f"Position: ({int(self.player.x)}, {int(self.player.y)})", True,
                                        (200, 200, 200))
        self.screen.blit(coords_text, (20, self.screen_height - 30))

    def draw(self):
        self.screen.fill(SKY_BLUE)

        if self.meditation:
            self.meditation.draw(self.screen)
        elif self.pause_menu:
            # Draw the game in the background
            self.world.draw(self.screen, self.camera_x, self.camera_y, self.screen_width, self.screen_height)
            self.player.draw(self.screen, self.camera_x, self.camera_y)
            self.draw_hud()
            # Draw pause menu on top
            self.pause_menu.draw(self.screen)
        else:
            # Draw world
            self.world.draw(self.screen, self.camera_x, self.camera_y, self.screen_width, self.screen_height)

            # Draw player
            self.player.draw(self.screen, self.camera_x, self.camera_y)

            # Draw HUD
            self.draw_hud()

            # Draw encounter notification
            current_time = time.time()
            if current_time - self.last_encounter_time < self.encounter_cooldown and not self.battle:
                notif_size = max(24, min(40, self.screen_width // 35))
                notif_font = pygame.font.SysFont("Arial", notif_size, bold=True)
                notification = notif_font.render("HAPPY POKEMON APPEARED!", True, SECONDARY)
                notif_width = notification.get_width() + 40
                notif_height = notification.get_height() + 20
                notif_rect = pygame.Rect(self.screen_width // 2 - notif_width // 2, 80, notif_width, notif_height)
                pygame.draw.rect(self.screen, (255, 255, 200, 180), notif_rect, border_radius=10)
                pygame.draw.rect(self.screen, PRIMARY, notif_rect, 3, border_radius=10)
                self.screen.blit(notification, (self.screen_width // 2 - notification.get_width() // 2,
                                                80 + (notif_height - notification.get_height()) // 2))

            # Draw battle if active
            if self.battle:
                self.battle.draw(self.screen)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Save progress before exiting
                self.srs_system.save_progress()
                return False

            # Handle window resizing
            if event.type == pygame.VIDEORESIZE:
                self.screen_width, self.screen_height = event.size
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)

                # If we're in battle or meditation, recreate them with new size
                if self.battle:
                    self.battle = PokemonBattle(self.battle.card, self.srs_system,
                                                self.screen_width, self.screen_height)
                if self.meditation:
                    self.meditation = MeditationMeadow(self.screen_width, self.screen_height)
                if self.pause_menu:
                    self.pause_menu = PauseMenu(self.screen_width, self.screen_height, self)

            if self.meditation:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.meditation = None
                        self.start_background_music()
                    elif event.key == pygame.K_ESCAPE:
                        self.meditation = None  # Just exit meditation, not the game
            elif self.pause_menu:
                result = self.pause_menu.handle_input(event)
                if result == "resume":
                    self.pause_menu = None
                elif result == "save":
                    # Already handled in pause menu
                    pass
                elif result == "load":
                    # Already handled in pause menu
                    pass
                elif result == "quit_to_menu":
                    self.srs_system.save_progress()
                    return "quit_to_menu"
                elif result == "quit_game":
                    self.srs_system.save_progress()
                    return False
            elif self.battle:
                battle_result = self.battle.handle_input(event)
                if battle_result == "exit":
                    self.srs_system.save_progress()
                    return False
                elif battle_result == "continue":
                    self.battle = None
                    self.start_background_music()
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.srs_system.save_progress()
                        return False
                    elif event.key == pygame.K_p:
                        # Toggle pause menu
                        self.pause_menu = PauseMenu(self.screen_width, self.screen_height, self)
                    elif event.key == pygame.K_m:
                        self.toggle_music()
                    elif event.key == pygame.K_f:
                        # Enter meditation meadow
                        self.meditation = MeditationMeadow(self.screen_width, self.screen_height)
                        if self.playing_background_music:
                            pygame.mixer.music.stop()
                            self.playing_background_music = False

        return True

    def update(self):
        if self.meditation:
            self.meditation.update()
            return

        if self.pause_menu:
            return

        # Update camera to follow player (with smoothing)
        target_x = self.player.x - self.screen_width // 2
        target_y = self.player.y - self.screen_height // 2
        self.camera_x += (target_x - self.camera_x) * CAMERA_SMOOTHNESS
        self.camera_y += (target_y - self.camera_y) * CAMERA_SMOOTHNESS

        if not self.battle:
            # Handle player movement
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0

            if keys[pygame.K_LEFT]:
                dx = -PLAYER_SPEED
            if keys[pygame.K_RIGHT]:
                dx = PLAYER_SPEED
            if keys[pygame.K_UP]:
                dy = -PLAYER_SPEED
            if keys[pygame.K_DOWN]:
                dy = PLAYER_SPEED

            if dx != 0 or dy != 0:
                self.player.move(dx, dy, self.world)

                # Random encounter with due cards
                if self.due_cards and time.time() - self.last_encounter_time > self.encounter_cooldown:
                    # Equal chance everywhere except water
                    tile_x = int(self.player.x // TILE_SIZE)
                    tile_y = int(self.player.y // TILE_SIZE)
                    tile_type = self.world.get_tile(tile_x, tile_y)

                    encounter_chance = 0.005  # Base chance

                    # Lower chance in water
                    if tile_type == "water":
                        encounter_chance = 0.001

                    if random.random() < encounter_chance:
                        self.battle = PokemonBattle(self.due_cards.popleft(), self.srs_system,
                                                    self.screen_width, self.screen_height)
                        self.last_encounter_time = time.time()
                        if self.playing_background_music:
                            pygame.mixer.music.stop()
                            self.playing_background_music = False

    def run(self):
        running = True
        while running:
            result = self.handle_events()

            if result == "quit_to_menu":
                return "menu"
            elif result is False:
                running = False

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def load_tsv_deck(file_path):
    deck = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for i, row in enumerate(reader):
                # Create a card with question and answer
                card = {
                    'id': i,
                    'question': row.get('question', row.get('front', '')),
                    'answer': row.get('answer', row.get('back', ''))
                }
                deck.append(card)
    except Exception as e:
        print(f"Error loading deck: {e}")
        return None

    return deck


# Tab completion function for CLI
def tab_completer(text, state):
    # Get current directory contents
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.tsv')]
    # Filter files that match the text
    matches = [f for f in files if f.startswith(text)]

    # Return the match based on state
    if state < len(matches):
        return matches[state]
    return None


def main():
    # Set up tab completion
    try:
        import readline
        readline.set_completer(tab_completer)
        readline.parse_and_bind("tab: complete")
        print("Tab completion enabled. Press TAB to auto-complete file names.")
    except ImportError:
        print("Readline module not available. Tab completion disabled.")

    while True:
        # Ask for TSV file path with tab completion
        print("\n" + "=" * 50)
        print("Peaceful Pokémon Learning Adventure")
        print("=" * 50)
        print("Features:")
        print("- Infinite procedurally generated world")
        print("- Meditation Meadow for peaceful reflection")
        print("- Auto-generated background music and sound effects")
        print("- Automatic progress saving")
        print("- Resizable window")
        print("- Positive, abuse-free environment")
        print("- Pause menu with settings and save/load")
        print("\nControls:")
        print("P: Pause Menu")
        print("F: Meditation Meadow")
        print("M: Toggle Music")
        print("Arrow Keys: Move Player")
        print("\nEnter the path to your Anki deck (.tsv file):")
        print("(Press TAB for auto-completion)")

        try:
            file_path = input("> ").strip()
        except EOFError:
            print("\nExiting...")
            return

        # Load deck
        deck = load_tsv_deck(file_path)
        if not deck:
            print("Failed to load deck. Please try again.")
            continue

        print(f"Loaded {len(deck)} cards from deck.")
        print("Generating infinite world...")

        # Initialize and run game
        game = Game(deck)
        result = game.run()

        if result != "menu":
            break


if __name__ == "__main__":
    main()