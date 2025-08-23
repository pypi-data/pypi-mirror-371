"""
TyStyle - Beautiful terminal styling with gradients and animations
Complete library in a single file for easy distribution and use.
"""

__version__ = "2.0.0"
__author__ = "Vortex"
__description__ = "Beautiful terminal styling with gradients and animations"

import os
import time
import threading
import random
import math
import shutil
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.box import Box

# Enable Windows color support
os.system('color')
os.environ['FORCE_COLOR'] = '1'
os.environ['COLORTERM'] = 'truecolor'

console = Console()

class CustomGradients:
    """Custom gradient system with ANSI and Rich support"""
    
    GRADIENTS = {
        # === Two-color gradients ===
        "red_to_blue":      [(255, 0, 0), (0, 0, 255)],
        "green_to_purple":  [(0, 255, 0), (128, 0, 128)],
        "cyan_to_pink":     [(0, 255, 255), (255, 192, 203)],
        "orange_to_teal":   [(255, 165, 0), (0, 128, 128)],
        "yellow_to_red":    [(255, 255, 0), (255, 0, 0)],
        "pink_to_blue":     [(255, 105, 180), (0, 191, 255)],

        # === Fire/warm colors ===
        "fire":             [(139, 0, 0), (255, 69, 0), (255, 165, 0), (255, 255, 0)],
        "sunset":           [(255, 94, 77), (255, 154, 0), (255, 206, 84)],
        "lava":             [(128, 0, 0), (255, 0, 0), (255, 140, 0)],
        "ember":            [(205, 92, 92), (255, 160, 122), (255, 218, 185)],
        "inferno":          [(0, 0, 4), (87, 15, 109), (188, 55, 84), (249, 142, 8), (252, 255, 164)],
        "magma":            [(0, 0, 4), (63, 7, 64), (118, 42, 131), (181, 54, 122), (246, 110, 92)],
        "volcanic":         [(25, 25, 25), (139, 0, 0), (255, 140, 0), (255, 215, 0)],
        "molten":           [(51, 17, 0), (102, 51, 0), (204, 85, 0), (255, 153, 51)],

        # === Cool/ocean colors ===
        "ocean":            [(0, 0, 139), (0, 191, 255), (173, 216, 230)],
        "ice":              [(176, 224, 230), (173, 216, 230), (240, 248, 255)],
        "arctic":           [(72, 61, 139), (106, 90, 205), (147, 112, 219)],
        "deep_sea":         [(0, 0, 128), (0, 100, 139), (0, 191, 255)],
        "glacier":          [(72, 118, 255), (135, 206, 250), (240, 248, 255)],
        "frost":            [(176, 224, 230), (224, 255, 255), (248, 248, 255)],
        "tundra":           [(70, 130, 180), (176, 196, 222), (230, 230, 250)],
        "frozen":           [(25, 25, 112), (106, 90, 205), (176, 224, 230)],

        # === Nature colors ===
        "forest":           [(34, 139, 34), (50, 205, 50), (144, 238, 144)],
        "jungle":           [(0, 100, 0), (34, 139, 34), (107, 142, 35)],
        "autumn":           [(139, 69, 19), (205, 133, 63), (255, 165, 0)],
        "spring":           [(154, 205, 50), (124, 252, 0), (173, 255, 47)],
        "meadow":           [(107, 142, 35), (154, 205, 50), (173, 255, 47)],
        "desert":           [(218, 165, 32), (244, 164, 96), (255, 228, 181)],
        "tropical":         [(0, 128, 128), (32, 178, 170), (127, 255, 212)],
        "rainforest":       [(0, 100, 0), (46, 125, 50), (76, 175, 80)],

        # === Neon/cyberpunk ===
        "neon_green":       [(0, 255, 0), (0, 255, 127), (127, 255, 212)],
        "neon_blue":        [(0, 191, 255), (30, 144, 255), (173, 216, 230)],
        "neon_pink":        [(255, 20, 147), (255, 105, 180), (255, 182, 193)],
        "cyberpunk":        [(255, 0, 255), (0, 255, 255), (0, 255, 0)],
        "matrix":           [(0, 255, 0), (0, 128, 0), (0, 64, 0)],
        "synthwave":        [(255, 71, 139), (138, 43, 226), (0, 255, 255)],
        "retro_neon":       [(255, 20, 147), (255, 0, 255), (138, 43, 226)],
        "electric":         [(0, 255, 255), (64, 224, 208), (127, 255, 212)],
        "holographic":      [(255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0)],

        # === Rainbow variations ===
        "rainbow":          [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (128, 0, 128)],
        "rainbow_soft":     [(255, 182, 193), (255, 218, 185), (255, 255, 224), (144, 238, 144), (173, 216, 230), (221, 160, 221)],
        "pride":            [(228, 3, 3), (255, 140, 0), (255, 237, 0), (0, 128, 38), (0, 77, 255), (117, 7, 135)],
        "pastel_rainbow":   [(255, 179, 186), (255, 223, 186), (255, 255, 186), (186, 255, 201), (186, 225, 255), (248, 187, 208)],
        "vibrant_rainbow":  [(255, 0, 0), (255, 127, 0), (255, 255, 0), (127, 255, 0), (0, 255, 127), (0, 127, 255), (127, 0, 255)],

        # === Monochrome ===
        "black_to_white":   [(0, 0, 0), (255, 255, 255)],
        "white_to_black":   [(255, 255, 255), (0, 0, 0)],
        "grey_to_white":    [(128, 128, 128), (255, 255, 255)],
        "grey_to_black":    [(128, 128, 128), (0, 0, 0)],
        "grey_scale":       [(0, 0, 0), (128, 128, 128), (255, 255, 255)],
        "charcoal":         [(54, 69, 79), (96, 125, 139), (176, 190, 197)],
        "graphite":         [(47, 79, 79), (119, 136, 153), (211, 211, 211)],

        # === Black blends ===
        "black_to_red":     [(0, 0, 0), (139, 0, 0), (255, 0, 0)],
        "black_to_blue":    [(0, 0, 0), (0, 0, 139), (0, 0, 255)],
        "black_to_green":   [(0, 0, 0), (0, 100, 0), (0, 255, 0)],
        "black_to_yellow":  [(0, 0, 0), (139, 139, 0), (255, 255, 0)],
        "black_to_purple":  [(0, 0, 0), (75, 0, 130), (128, 0, 128)],
        "black_to_orange":  [(0, 0, 0), (139, 69, 0), (255, 165, 0)],
        "black_to_pink":    [(0, 0, 0), (139, 69, 19), (255, 105, 180)],
        "black_to_cyan":    [(0, 0, 0), (0, 139, 139), (0, 255, 255)],
        "black_to_gold":    [(0, 0, 0), (184, 134, 11), (255, 215, 0)],
        "black_to_silver":  [(0, 0, 0), (128, 128, 128), (192, 192, 192)],

        # === White blends ===
        "white_to_red":     [(255, 255, 255), (255, 182, 193), (255, 0, 0)],
        "white_to_blue":    [(255, 255, 255), (173, 216, 230), (0, 0, 255)],
        "white_to_green":   [(255, 255, 255), (144, 238, 144), (0, 255, 0)],
        "white_to_yellow":  [(255, 255, 255), (255, 255, 224), (255, 255, 0)],
        "white_to_purple":  [(255, 255, 255), (221, 160, 221), (128, 0, 128)],
        "white_to_orange":  [(255, 255, 255), (255, 218, 185), (255, 165, 0)],
        "white_to_pink":    [(255, 255, 255), (255, 192, 203), (255, 105, 180)],
        "white_to_cyan":    [(255, 255, 255), (224, 255, 255), (0, 255, 255)],
        "white_to_gold":    [(255, 255, 255), (255, 248, 220), (255, 215, 0)],

        # === Dark to light blends ===
        "midnight_to_dawn": [(25, 25, 112), (70, 130, 180), (255, 218, 185)],
        "shadow_to_light":  [(47, 79, 79), (128, 128, 128), (245, 245, 245)],
        "charcoal_to_cream":[(54, 54, 54), (169, 169, 169), (255, 253, 208)],
        "obsidian_to_pearl":[(41, 36, 33), (105, 105, 105), (240, 234, 214)],
        "slate_to_ivory":   [(47, 79, 79), (112, 128, 144), (255, 255, 240)],

        # === Gradient variations ===
        "red_shades":       [(139, 0, 0), (220, 20, 60), (255, 99, 71)],
        "blue_shades":      [(0, 0, 139), (65, 105, 225), (135, 206, 235)],
        "purple_shades":    [(75, 0, 130), (138, 43, 226), (221, 160, 221)],
        "green_shades":     [(0, 100, 0), (34, 139, 34), (144, 238, 144)],
        "orange_shades":    [(139, 69, 0), (255, 140, 0), (255, 218, 185)],
        "pink_shades":      [(139, 69, 19), (255, 20, 147), (255, 182, 193)],

        # === Special effects ===
        "gold":             [(255, 215, 0), (255, 223, 0), (255, 255, 224)],
        "silver":           [(192, 192, 192), (211, 211, 211), (245, 245, 245)],
        "copper":           [(184, 115, 51), (205, 127, 50), (210, 180, 140)],
        "plasma":           [(128, 0, 128), (255, 0, 255), (255, 105, 180), (255, 255, 0)],
        "aurora":           [(0, 255, 127), (64, 224, 208), (138, 43, 226)],
        "galaxy":           [(25, 25, 112), (72, 61, 139), (123, 104, 238), (255, 20, 147)],
        "nebula":           [(25, 25, 112), (138, 43, 226), (255, 20, 147), (255, 140, 0)],
        "cosmic":           [(0, 0, 0), (25, 25, 112), (138, 43, 226), (255, 255, 255)],
        
        # === New Atmospheric Gradients ===
        "thunderstorm":     [(25, 25, 25), (75, 75, 150), (255, 255, 255), (255, 255, 0)],
        "lightning":        [(0, 0, 0), (138, 43, 226), (255, 255, 255), (255, 255, 0)],
        "tornado":          [(64, 64, 64), (128, 128, 128), (192, 192, 192), (255, 255, 255)],
        "blizzard":         [(135, 206, 250), (176, 224, 230), (240, 248, 255), (255, 255, 255)],
        "sandstorm":        [(205, 133, 63), (222, 184, 135), (245, 222, 179), (255, 248, 220)],
        "aurora_borealis":  [(0, 100, 0), (0, 255, 127), (64, 224, 208), (138, 43, 226), (255, 20, 147)],
        
        # === Gemstone Gradients ===
        "ruby":             [(139, 0, 0), (220, 20, 60), (255, 0, 0)],
        "emerald":          [(0, 100, 0), (0, 128, 0), (50, 205, 50)],
        "sapphire":         [(0, 0, 139), (65, 105, 225), (30, 144, 255)],
        "diamond":          [(224, 224, 224), (240, 240, 240), (255, 255, 255)],
        "amethyst":         [(128, 0, 128), (138, 43, 226), (186, 85, 211)],
        "topaz":            [(255, 140, 0), (255, 165, 0), (255, 215, 0)],
        "opal":             [(255, 255, 255), (255, 182, 193), (173, 216, 230), (221, 160, 221)],
        
        # === Food/Beverage Gradients ===
        "coffee":           [(101, 67, 33), (139, 69, 19), (160, 82, 45), (210, 180, 140)],
        "wine":             [(128, 0, 32), (139, 0, 0), (165, 42, 42)],
        "mint":             [(152, 251, 152), (0, 255, 127), (64, 224, 208)],
        "chocolate":        [(101, 67, 33), (139, 69, 19), (160, 82, 45)],
        "vanilla":          [(255, 255, 224), (255, 248, 220), (245, 245, 220)],
        "berry":            [(128, 0, 128), (139, 0, 139), (255, 20, 147)],
        "citrus":           [(255, 255, 0), (255, 165, 0), (255, 69, 0)],
        
        # === Mood/Emotion Gradients ===
        "calm":             [(135, 206, 235), (176, 224, 230), (240, 248, 255)],
        "energetic":        [(255, 69, 0), (255, 140, 0), (255, 255, 0)],
        "mysterious":       [(25, 25, 112), (72, 61, 139), (128, 0, 128)],
        "romantic":         [(255, 192, 203), (255, 105, 180), (220, 20, 60)],
        "peaceful":         [(144, 238, 144), (152, 251, 152), (240, 255, 240)],
        "dramatic":         [(0, 0, 0), (128, 0, 128), (255, 0, 0)],
        "cheerful":         [(255, 255, 0), (255, 182, 193), (255, 105, 180)],
        
        # === Seasonal Extended ===
        "winter":           [(176, 224, 230), (240, 248, 255), (255, 255, 255)],
        "summer":           [(255, 255, 0), (255, 165, 0), (255, 69, 0)],
        "fall":             [(139, 69, 19), (205, 133, 63), (255, 165, 0), (220, 20, 60)],
        "spring_bloom":     [(255, 182, 193), (255, 105, 180), (144, 238, 144), (173, 255, 47)],
    }

    @staticmethod
    def _interpolate(c1, c2, t):
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )

    @classmethod
    def horizontal(cls, colors, text):
        if not colors or not text: return text
        result, text_len, num_colors = "", len(text), len(colors)
        for i, char in enumerate(text):
            pos = i / max(text_len - 1, 1)
            seg_size = 1.0 / max(num_colors - 1, 1)
            seg = min(int(pos / seg_size), num_colors - 2)
            local = (pos - seg * seg_size) / seg_size
            r, g, b = cls._interpolate(colors[seg], colors[seg + 1], local)
            result += f"\033[38;2;{r};{g};{b}m{char}"
        return result + "\033[0m"

    @classmethod
    def vertical(cls, colors, text):
        lines = text.split("\n")
        if len(lines) <= 1:
            return cls.horizontal(colors, text)
        result_lines = []
        for i, line in enumerate(lines):
            pos = i / (len(lines) - 1)
            seg = min(int(pos * (len(colors) - 1)), len(colors) - 2)
            local = (pos * (len(colors) - 1)) - seg
            r, g, b = cls._interpolate(colors[seg], colors[seg + 1], local)
            result_lines.append(f"\033[38;2;{r};{g};{b}m{line}\033[0m")
        return "\n".join(result_lines)

    @classmethod
    def diagonal(cls, colors, text):
        """NEW: Diagonal gradient effect"""
        lines = text.split("\n")
        result_lines = []
        
        for line_idx, line in enumerate(lines):
            result_line = ""
            for char_idx, char in enumerate(line):
                total_pos = (line_idx + char_idx) / max(len(lines) + len(line) - 2, 1)
                seg = min(int(total_pos * (len(colors) - 1)), len(colors) - 2)
                local = (total_pos * (len(colors) - 1)) - seg
                r, g, b = cls._interpolate(colors[seg], colors[seg + 1], local)
                result_line += f"\033[38;2;{r};{g};{b}m{char}"
            result_lines.append(result_line + "\033[0m")
        return "\n".join(result_lines)

    @classmethod
    def radial(cls, colors, text):
        """NEW: Radial gradient from center outward"""
        lines = text.split("\n")
        max_len = max(len(line) for line in lines) if lines else 1
        center_y, center_x = len(lines) / 2, max_len / 2
        max_distance = math.sqrt(center_y**2 + center_x**2)
        
        result_lines = []
        for line_idx, line in enumerate(lines):
            result_line = ""
            for char_idx, char in enumerate(line):
                distance = math.sqrt((line_idx - center_y)**2 + (char_idx - center_x)**2)
                pos = min(distance / max_distance, 1.0)
                
                seg = min(int(pos * (len(colors) - 1)), len(colors) - 2)
                local = (pos * (len(colors) - 1)) - seg
                r, g, b = cls._interpolate(colors[seg], colors[seg + 1], local)
                result_line += f"\033[38;2;{r};{g};{b}m{char}"
            result_lines.append(result_line + "\033[0m")
        return "\n".join(result_lines)

    @classmethod
    def to_rich_text(cls, colors, text, direction="horizontal"):
        if not colors or not text: 
            return Text(text)

        if direction == "vertical":
            lines = text.split("\n")
            if len(lines) == 1:
                return cls.to_rich_text(colors, text, direction="horizontal")

            rich_text = Text()
            for i, line in enumerate(lines):
                pos = i / max(len(lines) - 1, 1)
                seg = min(int(pos * (len(colors) - 1)), len(colors) - 2)
                local = (pos * (len(colors) - 1)) - seg
                r, g, b = cls._interpolate(colors[seg], colors[seg + 1], local)
                rich_text.append(line, style=f"rgb({r},{g},{b})")
                if i < len(lines) - 1:
                    rich_text.append("\n")
            return rich_text
        elif direction == "diagonal":
            lines = text.split("\n")
            rich_text = Text()
            for line_idx, line in enumerate(lines):
                for char_idx, char in enumerate(line):
                    total_pos = (line_idx + char_idx) / max(len(lines) + len(line) - 2, 1)
                    seg = min(int(total_pos * (len(colors) - 1)), len(colors) - 2)
                    local = (total_pos * (len(colors) - 1)) - seg
                    r, g, b = cls._interpolate(colors[seg], colors[seg + 1], local)
                    rich_text.append(char, style=f"rgb({r},{g},{b})")
                if line_idx < len(lines) - 1:
                    rich_text.append("\n")
            return rich_text
        elif direction == "radial":
            lines = text.split("\n")
            max_len = max(len(line) for line in lines) if lines else 1
            center_y, center_x = len(lines) / 2, max_len / 2
            max_distance = math.sqrt(center_y**2 + center_x**2)
            
            rich_text = Text()
            for line_idx, line in enumerate(lines):
                for char_idx, char in enumerate(line):
                    distance = math.sqrt((line_idx - center_y)**2 + (char_idx - center_x)**2)
                    pos = min(distance / max_distance, 1.0)
                    
                    seg = min(int(pos * (len(colors) - 1)), len(colors) - 2)
                    local = (pos * (len(colors) - 1)) - seg
                    r, g, b = cls._interpolate(colors[seg], colors[seg + 1], local)
                    rich_text.append(char, style=f"rgb({r},{g},{b})")
                if line_idx < len(lines) - 1:
                    rich_text.append("\n")
            return rich_text
        else:
            rich_text = Text()
            text_len, num_colors = len(text), len(colors)
            for i, char in enumerate(text):
                pos = i / max(text_len - 1, 1)
                seg_size = 1.0 / max(num_colors - 1, 1)
                seg = min(int(pos / seg_size), num_colors - 2)
                local = (pos - seg * seg_size) / seg_size
                r, g, b = cls._interpolate(colors[seg], colors[seg + 1], local)
                rich_text.append(char, style=f"rgb({r},{g},{b})")
            return rich_text

    @classmethod
    def get(cls, gradient_name, text, direction="horizontal", rich=False):
        if gradient_name not in cls.GRADIENTS:
            return text
        colors = cls.GRADIENTS[gradient_name]
        
        if rich:
            return cls.to_rich_text(colors, text, direction)
        else:
            if direction == "vertical":
                return cls.vertical(colors, text)
            elif direction == "diagonal":
                return cls.diagonal(colors, text)
            elif direction == "radial":
                return cls.radial(colors, text)
            else:
                return cls.horizontal(colors, text)


class Animations:
    """Enhanced animation system for terminal text effects"""
    
    @staticmethod
    def clear_line():
        print('\r' + ' ' * 80 + '\r', end='', flush=True)
    
    @staticmethod
    def hide_cursor():
        print('\033[?25l', end='', flush=True)
    
    @staticmethod
    def show_cursor():
        print('\033[?25h', end='', flush=True)

    @staticmethod
    def get_terminal_width():
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80

    @classmethod
    def typewriter(cls, text, delay=0.05, gradient_name=None):
        cls.hide_cursor()
        try:
            for i in range(len(text) + 1):
                cls.clear_line()
                current_text = text[:i]
                if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                    colored_text = CustomGradients.get(gradient_name, current_text)
                    print(colored_text, end='', flush=True)
                else:
                    print(current_text, end='', flush=True)
                time.sleep(delay)
            print()
        finally:
            cls.show_cursor()

    @classmethod
    def wave_animation(cls, text, cycles=3, delay=0.1, gradient_name="ocean"):
        """Enhanced wave animation with actual wave effect on colors"""
        cls.hide_cursor()
        try:
            for cycle in range(cycles):
                for phase in range(20):  # More phases for smoother wave
                    cls.clear_line()
                    wave_text = ""
                    
                    for i, char in enumerate(text):
                        # Create wave effect with sine function
                        wave_offset = math.sin((i * 0.5) + (phase * 0.3)) * 0.5 + 0.5
                        
                        # Modify the gradient based on wave position
                        if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                            colors = CustomGradients.GRADIENTS[gradient_name]
                            # Use wave offset to pick color from gradient
                            color_index = int(wave_offset * (len(colors) - 1))
                            r, g, b = colors[color_index]
                            wave_text += f"\033[38;2;{r};{g};{b}m{char}"
                        else:
                            wave_text += char
                    
                    print(wave_text + "\033[0m", end='', flush=True)
                    time.sleep(delay)
            print()
        finally:
            cls.show_cursor()

    @classmethod
    def color_wave(cls, text, cycles=3, delay=0.1, gradient_name="rainbow"):
        """NEW: Color wave that moves through the text"""
        cls.hide_cursor()
        try:
            text_len = len(text)
            for cycle in range(cycles):
                for offset in range(text_len + 10):
                    cls.clear_line()
                    wave_text = ""
                    
                    for i, char in enumerate(text):
                        # Calculate distance from wave center
                        distance = abs(i - offset)
                        if distance <= 3:  # Wave width
                            intensity = 1.0 - (distance / 3.0)
                            if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                                colors = CustomGradients.GRADIENTS[gradient_name]
                                color_pos = (intensity + cycle * 0.3) % 1.0
                                color_index = int(color_pos * (len(colors) - 1))
                                r, g, b = colors[color_index]
                                # Brighten based on intensity
                                r = min(255, int(r * (0.5 + intensity * 0.5)))
                                g = min(255, int(g * (0.5 + intensity * 0.5)))
                                b = min(255, int(b * (0.5 + intensity * 0.5)))
                                wave_text += f"\033[38;2;{r};{g};{b}m{char}"
                            else:
                                wave_text += char
                        else:
                            wave_text += char
                    
                    print(wave_text + "\033[0m", end='', flush=True)
                    time.sleep(delay)
            print()
        finally:
            cls.show_cursor()

    @classmethod
    def rainbow_cycle(cls, text, cycles=5, delay=0.2):
        cls.hide_cursor()
        rainbow_gradients = ["red_to_blue", "fire", "sunset", "ocean", "forest", "cyberpunk"]
        try:
            for cycle in range(cycles):
                for gradient_name in rainbow_gradients:
                    cls.clear_line()
                    colored_text = CustomGradients.get(gradient_name, text)
                    print(colored_text, end='', flush=True)
                    time.sleep(delay)
            print()
        finally:
            cls.show_cursor()

    @classmethod
    def blink(cls, text, blinks=5, delay=0.5, gradient_name=None):
        cls.hide_cursor()
        try:
            for _ in range(blinks):
                if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                    colored_text = CustomGradients.get(gradient_name, text)
                    print(colored_text, end='', flush=True)
                else:
                    print(text, end='', flush=True)
                time.sleep(delay)
                
                cls.clear_line()
                time.sleep(delay)
            
            if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                colored_text = CustomGradients.get(gradient_name, text)
                print(colored_text)
            else:
                print(text)
        finally:
            cls.show_cursor()

    @classmethod
    def slide_in(cls, text, direction="left", delay=0.05, gradient_name=None):
        cls.hide_cursor()
        try:
            text_len = len(text)
            
            if direction == "left":
                for i in range(text_len + 1):
                    cls.clear_line()
                    spaces = " " * (text_len - i)
                    current_text = spaces + text[:i]
                    
                    if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                        colored_text = CustomGradients.get(gradient_name, current_text)
                        print(colored_text, end='', flush=True)
                    else:
                        print(current_text, end='', flush=True)
                    time.sleep(delay)
                    
            elif direction == "right":
                for i in range(text_len + 1):
                    cls.clear_line()
                    current_text = text[-i:] if i > 0 else ""
                    spaces = " " * (text_len - len(current_text))
                    display_text = current_text + spaces
                    
                    if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                        colored_text = CustomGradients.get(gradient_name, display_text)
                        print(colored_text, end='', flush=True)
                    else:
                        print(display_text, end='', flush=True)
                    time.sleep(delay)
            print()
        finally:
            cls.show_cursor()

    @classmethod
    def matrix_rain(cls, text, duration=3, gradient_name="matrix"):
        cls.hide_cursor()
        try:
            chars = "01ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            iterations = int(duration / 0.1)
            
            for _ in range(iterations):
                cls.clear_line()
                random_text = ''.join(random.choice(chars) for _ in range(len(text)))
                
                if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                    colored_text = CustomGradients.get(gradient_name, random_text)
                    print(colored_text, end='', flush=True)
                else:
                    print(random_text, end='', flush=True)
                time.sleep(0.1)
            
            cls.clear_line()
            if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                final_text = CustomGradients.get(gradient_name, text)
                print(final_text)
            else:
                print(text)
                
        finally:
            cls.show_cursor()

    @classmethod
    def pulse(cls, text, pulses=5, delay=0.3, gradient_name="neon_blue"):
        """NEW: Pulsing brightness effect"""
        cls.hide_cursor()
        try:
            for pulse in range(pulses):
                for intensity in [0.3, 0.6, 1.0, 0.6, 0.3]:
                    cls.clear_line()
                    if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                        colors = CustomGradients.GRADIENTS[gradient_name]
                        dimmed_colors = []
                        for r, g, b in colors:
                            dimmed_colors.append((
                                int(r * intensity),
                                int(g * intensity),
                                int(b * intensity)
                            ))
                        pulsed_text = CustomGradients.horizontal(dimmed_colors, text)
                        print(pulsed_text, end='', flush=True)
                    else:
                        print(text, end='', flush=True)
                    time.sleep(delay / 5)
            print()
        finally:
            cls.show_cursor()

    @classmethod
    def sparkle(cls, text, duration=3, gradient_name="gold"):
        """NEW: Random sparkle effect on characters"""
        cls.hide_cursor()
        try:
            iterations = int(duration / 0.1)
            for _ in range(iterations):
                cls.clear_line()
                sparkled_text = ""
                
                for i, char in enumerate(text):
                    if random.random() < 0.1:  # 10% chance to sparkle
                        if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                            colors = CustomGradients.GRADIENTS[gradient_name]
                            r, g, b = colors[-1]  # Use brightest color
                            sparkled_text += f"\033[38;2;{r};{g};{b}m{char}"
                        else:
                            sparkled_text += f"\033[1m{char}\033[0m"
                    else:
                        if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                            pos = i / max(len(text) - 1, 1)
                            colors = CustomGradients.GRADIENTS[gradient_name]
                            color_idx = int(pos * (len(colors) - 1))
                            r, g, b = colors[color_idx]
                            sparkled_text += f"\033[38;2;{r};{g};{b}m{char}"
                        else:
                            sparkled_text += char
                
                print(sparkled_text + "\033[0m", end='', flush=True)
                time.sleep(0.1)
            
            # Final display
            cls.clear_line()
            if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                final_text = CustomGradients.get(gradient_name, text)
                print(final_text)
            else:
                print(text)
        finally:
            cls.show_cursor()

    @classmethod
    def zoom_in(cls, text, steps=10, delay=0.1, gradient_name=None):
        """NEW: Zoom in effect by gradually revealing more characters"""
        cls.hide_cursor()
        try:
            center = len(text) // 2
            for step in range(steps + 1):
                cls.clear_line()
                radius = int((step / steps) * center)
                start = max(0, center - radius)
                end = min(len(text), center + radius + 1)
                
                spaces_before = " " * start
                visible_text = text[start:end]
                
                if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                    colored_text = CustomGradients.get(gradient_name, visible_text)
                    print(spaces_before + colored_text, end='', flush=True)
                else:
                    print(spaces_before + visible_text, end='', flush=True)
                time.sleep(delay)
            print()
        finally:
            cls.show_cursor()

    @classmethod
    def falling_letters(cls, text, delay=0.1, gradient_name="gravity"):
        """NEW: Letters fall into place from top"""
        if "gravity" not in CustomGradients.GRADIENTS:
            gradient_name = "blue_shades"
            
        cls.hide_cursor()
        try:
            final_positions = list(text)
            working_text = [' '] * len(text)
            
            for drop_step in range(len(text)):
                # Add a new letter at random position
                available_positions = [i for i, char in enumerate(working_text) if char == ' ' and final_positions[i] != ' ']
                if available_positions:
                    pos = random.choice(available_positions)
                    working_text[pos] = final_positions[pos]
                
                cls.clear_line()
                current_text = ''.join(working_text)
                
                if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                    colored_text = CustomGradients.get(gradient_name, current_text)
                    print(colored_text, end='', flush=True)
                else:
                    print(current_text, end='', flush=True)
                time.sleep(delay)
            print()
        finally:
            cls.show_cursor()

    @classmethod
    def neon_flicker(cls, text, flickers=10, gradient_name="neon_blue"):
        """NEW: Neon sign flicker effect"""
        cls.hide_cursor()
        try:
            for _ in range(flickers):
                # Random flicker pattern
                flicker_type = random.choice(["dim", "bright", "off"])
                
                if flicker_type == "off":
                    cls.clear_line()
                    print(" " * len(text), end='', flush=True)
                    time.sleep(0.05)
                elif flicker_type == "dim":
                    cls.clear_line()
                    if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                        colors = CustomGradients.GRADIENTS[gradient_name]
                        dim_colors = [(int(r*0.3), int(g*0.3), int(b*0.3)) for r, g, b in colors]
                        dimmed_text = CustomGradients.horizontal(dim_colors, text)
                        print(dimmed_text, end='', flush=True)
                    else:
                        print(text, end='', flush=True)
                    time.sleep(random.uniform(0.05, 0.15))
                else:  # bright
                    cls.clear_line()
                    if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                        bright_text = CustomGradients.get(gradient_name, text)
                        print(bright_text, end='', flush=True)
                    else:
                        print(f"\033[1m{text}\033[0m", end='', flush=True)
                    time.sleep(random.uniform(0.1, 0.3))
            
            # Final stable display
            cls.clear_line()
            if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                final_text = CustomGradients.get(gradient_name, text)
                print(final_text)
            else:
                print(text)
        finally:
            cls.show_cursor()


class Effects:
    """Enhanced text effects and styling utilities"""
    
    @staticmethod
    def shadow(text, gradient_name="black_to_white", offset=2):
        lines = text.split('\n')
        result = []
        
        for line in lines:
            shadow_line = ' ' * offset + '░' * len(line)
            result.append(shadow_line)
        
        for i, line in enumerate(lines):
            if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                colored_line = CustomGradients.get(gradient_name, line)
                result[i] = colored_line + '\n' + result[i]
            else:
                result[i] = line + '\n' + result[i]
        
        return '\n'.join(result)
    
    @staticmethod
    def outline(text, gradient_name="white_to_black", char='█'):
        lines = text.split('\n')
        if not lines:
            return text
        
        max_len = max(len(line) for line in lines)
        
        top_border = char * (max_len + 4)
        
        content_lines = []
        for line in lines:
            padded_line = line.ljust(max_len)
            if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                colored_line = CustomGradients.get(gradient_name, padded_line)
                content_lines.append(f"{char} {colored_line} {char}")
            else:
                content_lines.append(f"{char} {padded_line} {char}")
        
        bottom_border = char * (max_len + 4)
        
        return top_border + '\n' + '\n'.join(content_lines) + '\n' + bottom_border
    
    @staticmethod
    def glow(text, gradient_name="neon_blue", intensity=3):
        if gradient_name not in CustomGradients.GRADIENTS:
            return text
        
        result = []
        colors = CustomGradients.GRADIENTS[gradient_name]
        
        for layer in range(intensity, 0, -1):
            spaces = ' ' * layer
            layer_text = spaces + text + spaces
            if len(colors) > 1:
                layer_color = colors[-1] if layer == 1 else colors[0]
                faded_color = tuple(int(c * (0.3 + 0.7 * (intensity - layer) / intensity)) for c in layer_color)
                layer_gradient = [faded_color, layer_color] if layer > 1 else colors
                colored_layer = CustomGradients.horizontal(layer_gradient, layer_text)
                result.append(colored_layer)
        
        main_text = CustomGradients.get(gradient_name, text)
        return '\n'.join(result) + '\n' + main_text
    
    @staticmethod
    def box(text, gradient_name=None, title="", style="rounded"):
        if gradient_name and gradient_name in CustomGradients.GRADIENTS:
            rich_text = CustomGradients.to_rich_text(CustomGradients.GRADIENTS[gradient_name], text)
        else:
            rich_text = Text(text)
        
        box_style = Box.ROUNDED if style == "rounded" else Box.SQUARE
        panel = Panel(rich_text, title=title, box=box_style)
        
        with console.capture() as capture:
            console.print(panel)
        
        return capture.get()
    
    @classmethod
    def banner(cls, text, gradient_name="fire", width=60, char='='):
        lines = text.split('\n')
        max_len = max(len(line) for line in lines) if lines else 0
        banner_width = max(width, max_len + 4)
        
        top_border = char * banner_width
        
        content = []
        for line in lines:
            padding = (banner_width - len(line) - 2) // 2
            padded_line = f"{char}{' ' * padding}{line}{' ' * (banner_width - len(line) - padding - 2)}{char}"
            
            if gradient_name and gradient_name in CustomGradients.GRADIENTS:
                colored_line = CustomGradients.get(gradient_name, padded_line)
                content.append(colored_line)
            else:
                content.append(padded_line)
        
        bottom_border = char * banner_width
        
        return top_border + '\n' + '\n'.join(content) + '\n' + bottom_border

    @staticmethod
    def double_vision(text, gradient_name1="red_shades", gradient_name2="blue_shades", offset=2):
        """NEW: Double vision/3D effect with two colored layers"""
        lines = text.split('\n')
        result = []
        
        # First layer (background)
        for line in lines:
            spaces = ' ' * offset
            if gradient_name2 and gradient_name2 in CustomGradients.GRADIENTS:
                bg_line = CustomGradients.get(gradient_name2, spaces + line)
                result.append(bg_line)
            else:
                result.append(spaces + line)
        
        # Second layer (foreground) overlaid
        for i, line in enumerate(lines):
            if gradient_name1 and gradient_name1 in CustomGradients.GRADIENTS:
                fg_line = CustomGradients.get(gradient_name1, line)
                # Combine with background
                if i < len(result):
                    result[i] = fg_line + result[i][len(line):]
                else:
                    result.append(fg_line)
            else:
                if i < len(result):
                    result[i] = line + result[i][len(line):]
                else:
                    result.append(line)
        
        return '\n'.join(result)

    @staticmethod
    def mirror(text, gradient_name="silver", vertical=False):
        """NEW: Mirror effect"""
        if vertical:
            lines = text.split('\n')
            mirrored_lines = lines + ['─' * max(len(line) for line in lines)] + lines[::-1]
            mirrored_text = '\n'.join(mirrored_lines)
        else:
            lines = text.split('\n')
            mirrored_lines = []
            for line in lines:
                mirrored_lines.append(line + ' │ ' + line[::-1])
            mirrored_text = '\n'.join(mirrored_lines)
        
        if gradient_name and gradient_name in CustomGradients.GRADIENTS:
            return CustomGradients.get(gradient_name, mirrored_text)
        return mirrored_text

    @staticmethod
    def pixelate(text, gradient_name="retro_neon", block_char='█'):
        """NEW: Pixelated effect"""
        lines = text.split('\n')
        pixelated = []
        
        for line in lines:
            pixel_line = ""
            for char in line:
                if char.isspace():
                    pixel_line += "  "
                else:
                    pixel_line += block_char + block_char
            pixelated.append(pixel_line)
            pixelated.append(pixel_line)  # Duplicate for height
        
        pixelated_text = '\n'.join(pixelated)
        if gradient_name and gradient_name in CustomGradients.GRADIENTS:
            return CustomGradients.get(gradient_name, pixelated_text)
        return pixelated_text

    @staticmethod
    def emboss(text, gradient_name="metallic"):
        """NEW: Embossed/raised text effect"""
        if "metallic" not in CustomGradients.GRADIENTS:
            gradient_name = "silver"
            
        lines = text.split('\n')
        embossed = []
        
        # Top highlight
        for line in lines:
            highlight = ''.join('▀' if not c.isspace() else ' ' for c in line)
            embossed.append(highlight)
        
        # Main text
        for line in lines:
            embossed.append(line)
        
        # Bottom shadow
        for line in lines:
            shadow = ''.join('▄' if not c.isspace() else ' ' for c in line)
            embossed.append(shadow)
        
        embossed_text = '\n'.join(embossed)
        if gradient_name and gradient_name in CustomGradients.GRADIENTS:
            return CustomGradients.get(gradient_name, embossed_text)
        return embossed_text

    @staticmethod
    def distort(text, gradient_name="glitch", intensity=3):
        """NEW: Distortion/glitch effect"""
        if "glitch" not in CustomGradients.GRADIENTS:
            gradient_name = "cyberpunk"
            
        lines = text.split('\n')
        distorted = []
        
        for line_idx, line in enumerate(lines):
            distorted_line = ""
            for char_idx, char in enumerate(line):
                # Random chance to distort
                if random.random() < (intensity * 0.1):
                    # Choose random distortion
                    distortions = ['░', '▒', '▓', '█', char.upper(), char.lower()]
                    distorted_line += random.choice(distortions)
                else:
                    distorted_line += char
            
            # Sometimes shift entire line
            if random.random() < (intensity * 0.05):
                shift = random.randint(-2, 2)
                if shift > 0:
                    distorted_line = ' ' * shift + distorted_line
                elif shift < 0:
                    distorted_line = distorted_line[abs(shift):]
            
            distorted.append(distorted_line)
        
        distorted_text = '\n'.join(distorted)
        if gradient_name and gradient_name in CustomGradients.GRADIENTS:
            return CustomGradients.get(gradient_name, distorted_text)
        return distorted_text


class PatternEffects:
    """NEW: Pattern-based effects"""
    
    @staticmethod
    def checkerboard(text, gradient_name1="black_to_white", gradient_name2="white_to_black", size=2):
        """Checkerboard pattern effect"""
        lines = text.split('\n')
        result = []
        
        for line_idx, line in enumerate(lines):
            result_line = ""
            for char_idx, char in enumerate(line):
                # Determine checkerboard position
                check_x = char_idx // size
                check_y = line_idx // size
                
                if (check_x + check_y) % 2 == 0:
                    gradient = gradient_name1
                else:
                    gradient = gradient_name2
                
                if gradient in CustomGradients.GRADIENTS:
                    colors = CustomGradients.GRADIENTS[gradient]
                    r, g, b = colors[0]  # Use first color
                    result_line += f"\033[38;2;{r};{g};{b}m{char}"
                else:
                    result_line += char
            
            result.append(result_line + "\033[0m")
        
        return '\n'.join(result)

    @staticmethod
    def zebra_stripes(text, gradient_name1="black_to_white", gradient_name2="white_to_black"):
        """Zebra stripe pattern"""
        lines = text.split('\n')
        result = []
        
        for line_idx, line in enumerate(lines):
            gradient = gradient_name1 if line_idx % 2 == 0 else gradient_name2
            
            if gradient in CustomGradients.GRADIENTS:
                colored_line = CustomGradients.get(gradient, line)
                result.append(colored_line)
            else:
                result.append(line)
        
        return '\n'.join(result)

    @staticmethod
    def wave_pattern(text, gradient_name="ocean", frequency=2):
        """Wave pattern using sine function"""
        lines = text.split('\n')
        result = []
        
        for line_idx, line in enumerate(lines):
            result_line = ""
            for char_idx, char in enumerate(line):
                wave_value = math.sin((char_idx * frequency * math.pi) / len(line))
                normalized_wave = (wave_value + 1) / 2  # Normalize to 0-1
                
                if gradient_name in CustomGradients.GRADIENTS:
                    colors = CustomGradients.GRADIENTS[gradient_name]
                    color_idx = int(normalized_wave * (len(colors) - 1))
                    r, g, b = colors[color_idx]
                    result_line += f"\033[38;2;{r};{g};{b}m{char}"
                else:
                    result_line += char
            
            result.append(result_line + "\033[0m")
        
        return '\n'.join(result)


class AnimatedPatterns:
    """NEW: Animated pattern effects"""
    
    @classmethod
    def breathing_text(cls, text, cycles=5, gradient_name="calm", delay=0.1):
        """Text that 'breathes' by expanding and contracting spacing"""
        Animations.hide_cursor()
        try:
            base_spacing = 1
            max_spacing = 4
            
            for cycle in range(cycles):
                # Expand
                for spacing in range(base_spacing, max_spacing + 1):
                    Animations.clear_line()
                    spaced_text = ""
                    for char in text:
                        spaced_text += char + (" " * spacing)
                    
                    if gradient_name in CustomGradients.GRADIENTS:
                        colored_text = CustomGradients.get(gradient_name, spaced_text)
                        print(colored_text, end='', flush=True)
                    else:
                        print(spaced_text, end='', flush=True)
                    time.sleep(delay)
                
                # Contract
                for spacing in range(max_spacing, base_spacing - 1, -1):
                    Animations.clear_line()
                    spaced_text = ""
                    for char in text:
                        spaced_text += char + (" " * spacing)
                    
                    if gradient_name in CustomGradients.GRADIENTS:
                        colored_text = CustomGradients.get(gradient_name, spaced_text)
                        print(colored_text, end='', flush=True)
                    else:
                        print(spaced_text, end='', flush=True)
                    time.sleep(delay)
            
            print()
        finally:
            Animations.show_cursor()

    @classmethod
    def spiral_reveal(cls, text, delay=0.1, gradient_name="galaxy"):
        """Reveal text in a spiral pattern"""
        if not text.strip():
            return
            
        Animations.hide_cursor()
        try:
            # Convert to grid for spiral processing
            lines = text.split('\n')
            if not lines:
                return
                
            max_len = max(len(line) for line in lines)
            grid = []
            for line in lines:
                grid.append(list(line.ljust(max_len)))
            
            height, width = len(grid), max_len
            revealed = [[False] * width for _ in range(height)]
            
            # Spiral coordinates
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
            dir_idx = 0
            row, col = 0, 0
            
            for _ in range(height * width):
                if 0 <= row < height and 0 <= col < width and not revealed[row][col]:
                    revealed[row][col] = True
                    
                    # Display current state
                    current_text = ""
                    for r in range(height):
                        line = ""
                        for c in range(width):
                            if revealed[r][c]:
                                line += grid[r][c]
                            else:
                                line += " "
                        current_text += line + "\n"
                    
                    Animations.clear_line()
                    if gradient_name in CustomGradients.GRADIENTS:
                        colored_text = CustomGradients.get(gradient_name, current_text.rstrip())
                        print(colored_text, end='', flush=True)
                    else:
                        print(current_text.rstrip(), end='', flush=True)
                    
                    time.sleep(delay)
                
                # Move to next position
                dr, dc = directions[dir_idx]
                next_row, next_col = row + dr, col + dc
                
                # Check if we need to turn
                if (next_row < 0 or next_row >= height or 
                    next_col < 0 or next_col >= width or 
                    revealed[next_row][next_col]):
                    dir_idx = (dir_idx + 1) % 4
                    dr, dc = directions[dir_idx]
                
                row += dr
                col += dc
            
            print()
        finally:
            Animations.show_cursor()


# Enhanced helper functions
def gradient(name, text, direction="horizontal"): 
    return CustomGradients.get(name, text, direction, rich=False)

def gradient_rich(name, text, direction="horizontal"): 
    return CustomGradients.get(name, text, direction, rich=True)

def animate(effect, text, **kwargs):
    """Enhanced animate function with new effects"""
    if hasattr(Animations, effect):
        getattr(Animations, effect)(text, **kwargs)
    elif hasattr(AnimatedPatterns, effect):
        getattr(AnimatedPatterns, effect)(text, **kwargs)
    else:
        available_animations = [method for method in dir(Animations) if not method.startswith('_') and callable(getattr(Animations, method))]
        available_patterns = [method for method in dir(AnimatedPatterns) if not method.startswith('_') and callable(getattr(AnimatedPatterns, method))]
        print(f"Animation '{effect}' not found. Available animations: {', '.join(available_animations)}")
        print(f"Available patterns: {', '.join(available_patterns)}")

def pattern(effect, text, **kwargs):
    """Apply pattern effects"""
    if hasattr(PatternEffects, effect):
        return getattr(PatternEffects, effect)(text, **kwargs)
    else:
        available_patterns = [method for method in dir(PatternEffects) if not method.startswith('_') and callable(getattr(PatternEffects, method))]
        print(f"Pattern '{effect}' not found. Available patterns: {', '.join(available_patterns)}")
        return text

def effect(name, text, **kwargs):
    """Apply visual effects"""
    if hasattr(Effects, name):
        return getattr(Effects, name)(text, **kwargs)
    else:
        available_effects = [method for method in dir(Effects) if not method.startswith('_') and callable(getattr(Effects, method))]
        print(f"Effect '{name}' not found. Available effects: {', '.join(available_effects)}")
        return text

# Utility functions
def list_gradients():
    """List all available gradients"""
    print("\n=== Available Gradients ===")
    categories = {
        "Two-color": ["red_to_blue", "green_to_purple", "cyan_to_pink", "orange_to_teal", "yellow_to_red", "pink_to_blue"],
        "Fire/Warm": ["fire", "sunset", "lava", "ember", "inferno", "magma", "volcanic", "molten"],
        "Cool/Ocean": ["ocean", "ice", "arctic", "deep_sea", "glacier", "frost", "tundra", "frozen"],
        "Nature": ["forest", "jungle", "autumn", "spring", "meadow", "desert", "tropical", "rainforest"],
        "Neon/Cyber": ["neon_green", "neon_blue", "neon_pink", "cyberpunk", "matrix", "synthwave", "retro_neon", "electric", "holographic"],
        "Rainbow": ["rainbow", "rainbow_soft", "pride", "pastel_rainbow", "vibrant_rainbow"],
        "Monochrome": ["black_to_white", "white_to_black", "grey_scale", "charcoal", "graphite"],
        "Gemstones": ["ruby", "emerald", "sapphire", "diamond", "amethyst", "topaz", "opal"],
        "Food/Beverage": ["coffee", "wine", "mint", "chocolate", "vanilla", "berry", "citrus"],
        "Moods": ["calm", "energetic", "mysterious", "romantic", "peaceful", "dramatic", "cheerful"],
        "Weather": ["thunderstorm", "lightning", "tornado", "blizzard", "sandstorm", "aurora_borealis"],
        "Special": ["gold", "silver", "copper", "plasma", "aurora", "galaxy", "nebula", "cosmic"]
    }
    
    for category, gradients in categories.items():
        print(f"\n{category}:")
        for grad in gradients:
            if grad in CustomGradients.GRADIENTS:
                sample = CustomGradients.get(grad, f"  {grad}")
                print(sample)

def demo():
    """Show a demonstration of TyStyle features"""
    print(CustomGradients.get("fire", "🔥 TYSTYLE DEMONSTRATION 🔥"))
    print()
    
    # Gradient showcase
    print(CustomGradients.get("rainbow", "=== GRADIENT SHOWCASE ==="))
    print()
    
    sample_text = "Beautiful Gradients!"
    gradients_to_show = ["fire", "ocean", "cyberpunk", "galaxy", "aurora", "gold"]
    
    for grad in gradients_to_show:
        print(f"{grad:15}: {CustomGradients.get(grad, sample_text)}")
    
    print()
    print(CustomGradients.get("neon_blue", "=== DIRECTION SHOWCASE ==="))
    print()
    
    multiline_text = """MULTI
LINE
DEMO"""
    
    print("Horizontal:")
    print(CustomGradients.get("sunset", multiline_text, "horizontal"))
    print("\nVertical:")
    print(CustomGradients.get("sunset", multiline_text, "vertical"))
    print("\nDiagonal:")
    print(CustomGradients.get("sunset", multiline_text, "diagonal"))
    print("\nRadial:")
    print(CustomGradients.get("sunset", multiline_text, "radial"))
    
    print()
    print(CustomGradients.get("matrix", "=== EFFECTS SHOWCASE ==="))
    print()
    
    # Show some effects
    demo_text = "STYLED TEXT"
    
    print("Shadow Effect:")
    print(Effects.shadow(demo_text, "blue_shades"))
    print("\nOutline Effect:")
    print(Effects.outline(demo_text, "gold"))
    print("\nGlow Effect:")
    print(Effects.glow(demo_text, "neon_pink"))
    print("\nBanner Effect:")
    print(Effects.banner(demo_text, "cyberpunk"))
    
    print()
    print(CustomGradients.get("holographic", "Ready to create amazing terminal art! 🎨"))

def quick_gradient(text, colors_list):
    """Create a quick gradient from a list of RGB tuples"""
    if not isinstance(colors_list, list) or len(colors_list) < 2:
        return text
    
    return CustomGradients.horizontal(colors_list, text)

def random_gradient(text):
    """Apply a random gradient to text"""
    gradient_name = random.choice(list(CustomGradients.GRADIENTS.keys()))
    return CustomGradients.get(gradient_name, text)

def blend_gradients(gradient1, gradient2, text, ratio=0.5):
    """Blend two gradients together"""
    if gradient1 not in CustomGradients.GRADIENTS or gradient2 not in CustomGradients.GRADIENTS:
        return text
    
    colors1 = CustomGradients.GRADIENTS[gradient1]
    colors2 = CustomGradients.GRADIENTS[gradient2]
    
    # Blend the colors
    blended_colors = []
    max_colors = max(len(colors1), len(colors2))
    
    for i in range(max_colors):
        c1_idx = min(i, len(colors1) - 1)
        c2_idx = min(i, len(colors2) - 1)
        
        c1 = colors1[c1_idx]
        c2 = colors2[c2_idx]
        
        blended = (
            int(c1[0] * (1 - ratio) + c2[0] * ratio),
            int(c1[1] * (1 - ratio) + c2[1] * ratio),
            int(c1[2] * (1 - ratio) + c2[2] * ratio)
        )
        blended_colors.append(blended)
    
    return CustomGradients.horizontal(blended_colors, text)

class TextArt:
    """NEW: ASCII art and text art utilities"""
    
    @staticmethod
    def create_border(text, style="double", gradient_name="silver"):
        """Create decorative borders around text"""
        lines = text.split('\n')
        max_len = max(len(line) for line in lines) if lines else 0
        
        borders = {
            "single": {"h": "─", "v": "│", "tl": "┌", "tr": "┐", "bl": "└", "br": "┘"},
            "double": {"h": "═", "v": "║", "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝"},
            "rounded": {"h": "─", "v": "│", "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯"},
            "thick": {"h": "━", "v": "┃", "tl": "┏", "tr": "┓", "bl": "┗", "br": "┛"},
            "dotted": {"h": "┄", "v": "┆", "tl": "┌", "tr": "┐", "bl": "└", "br": "┘"}
        }
        
        if style not in borders:
            style = "double"
        
        b = borders[style]
        width = max_len + 4
        
        # Create bordered text
        result = []
        result.append(b["tl"] + b["h"] * (width - 2) + b["tr"])
        
        for line in lines:
            padded_line = f'{b["v"]} {line.ljust(max_len)} {b["v"]}'
            result.append(padded_line)
        
        result.append(b["bl"] + b["h"] * (width - 2) + b["br"])
        
        bordered_text = '\n'.join(result)
        
        if gradient_name in CustomGradients.GRADIENTS:
            return CustomGradients.get(gradient_name, bordered_text)
        return bordered_text

    @staticmethod
    def create_title(text, gradient_name="gold", width=60):
        """Create a fancy title"""
        text = text.upper()
        
        # Create decorative elements
        decoration = "◆" * ((width - len(text) - 2) // 2)
        title_line = f"{decoration} {text} {decoration}"
        
        if len(title_line) < width:
            title_line = title_line.center(width, "─")
        
        separator = "═" * width
        
        result = f"{separator}\n{title_line}\n{separator}"
        
        if gradient_name in CustomGradients.GRADIENTS:
            return CustomGradients.get(gradient_name, result)
        return result

    @staticmethod
    def progress_bar(percentage, width=40, gradient_name="green_shades", empty_char="░", full_char="█"):
        """Create a gradient progress bar"""
        filled_width = int((percentage / 100) * width)
        empty_width = width - filled_width
        
        bar = full_char * filled_width + empty_char * empty_width
        
        if gradient_name in CustomGradients.GRADIENTS:
            colored_bar = CustomGradients.get(gradient_name, bar)
            return f"[{colored_bar}] {percentage:3.0f}%"
        
        return f"[{bar}] {percentage:3.0f}%"

class InteractiveEffects:
    """NEW: Interactive and responsive effects"""
    
    @classmethod
    def typing_effect(cls, text, gradient_name="matrix", typing_delay=0.1, cursor_blink=True):
        """Interactive typing effect with cursor"""
        Animations.hide_cursor()
        cursor = "█" if cursor_blink else ""
        
        try:
            for i in range(len(text) + 1):
                Animations.clear_line()
                current_text = text[:i]
                
                if gradient_name in CustomGradients.GRADIENTS:
                    colored_text = CustomGradients.get(gradient_name, current_text)
                    print(colored_text + cursor, end='', flush=True)
                else:
                    print(current_text + cursor, end='', flush=True)
                
                time.sleep(typing_delay)
                
                # Blink cursor
                if cursor_blink and i == len(text):
                    for _ in range(3):
                        time.sleep(0.3)
                        Animations.clear_line()
                        if gradient_name in CustomGradients.GRADIENTS:
                            colored_text = CustomGradients.get(gradient_name, current_text)
                            print(colored_text, end='', flush=True)
                        else:
                            print(current_text, end='', flush=True)
                        time.sleep(0.3)
                        Animations.clear_line()
                        if gradient_name in CustomGradients.GRADIENTS:
                            colored_text = CustomGradients.get(gradient_name, current_text)
                            print(colored_text + cursor, end='', flush=True)
                        else:
                            print(current_text + cursor, end='', flush=True)
            
            print()
        finally:
            Animations.show_cursor()

    @classmethod
    def countdown(cls, seconds, gradient_name="fire", message=""):
        """Animated countdown timer"""
        Animations.hide_cursor()
        try:
            for i in range(seconds, -1, -1):
                Animations.clear_line()
                countdown_text = f"{message} {i:02d}" if message else f"{i:02d}"
                
                if gradient_name in CustomGradients.GRADIENTS:
                    colored_text = CustomGradients.get(gradient_name, countdown_text)
                    print(colored_text, end='', flush=True)
                else:
                    print(countdown_text, end='', flush=True)
                
                time.sleep(1)
            
            # Final message
            Animations.clear_line()
            final_text = f"{message} GO!" if message else "GO!"
            if gradient_name in CustomGradients.GRADIENTS:
                colored_text = CustomGradients.get(gradient_name, final_text)
                print(colored_text)
            else:
                print(final_text)
        finally:
            Animations.show_cursor()

# Auto-create direct-call functions for all gradients
def _register_gradient_functions():
    for name in CustomGradients.GRADIENTS.keys():
        globals()[name] = lambda text, n=name: gradient(n, text)
        globals()[f"{name}_rich"] = lambda text, n=name: gradient_rich(n, text)

_register_gradient_functions()

# Export everything for easy imports
__all__ = [
    'CustomGradients', 'Animations', 'Effects', 'PatternEffects', 'AnimatedPatterns',
    'TextArt', 'InteractiveEffects',
    'gradient', 'gradient_rich', 'animate', 'pattern', 'effect', 
    'list_gradients', 'demo', 'quick_gradient', 'random_gradient', 'blend_gradients',
    'console'
] + list(CustomGradients.GRADIENTS.keys()) + [f"{name}_rich" for name in CustomGradients.GRADIENTS.keys()]

