#!/usr/bin/env python3

import curses
import time
import random
import math
import os
from itertools import cycle
import subprocess
import sys

def load_environment():
    """Load environment variables from .env file"""
    try:
        from dotenv.main import load_dotenv
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-dotenv==1.0.1'])
        from dotenv.main import load_dotenv

    # Get the real path of the script, following symlinks
    script_path = os.path.realpath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # Look for .env in the script's actual directory
    env_path = os.path.join(script_dir, '.env')
    
    if not os.path.exists(env_path):
        print(f"Error: .env file not found at {env_path}")
        sys.exit(1)
    
    # Load the .env file
    load_dotenv(env_path)

# Import QGitConfig from qgit_config
try:
    script_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, script_dir)
    from qgits.qgit_config import QGitConfig
except ImportError:
    print("Error: Could not import QGitConfig. Please ensure qgits/qgit_config.py exists.")
    sys.exit(1)

QGIT_LOGO = """\
     ██████╗█╗██████╗ ██╗████████╗
    ██╔═══██╗██╔════╝ ██║╚══██╔══╝
    ██║   ██║██║  ███╗██║   ██║   
    ██║▄▄ ██║██║   ██║██║   ██║   
    ╚██████╔╝╚██████╔╝██║   ██║   
     ╚══▀▀═╝▄╚═════╝ ╚═╝   ╚═╝   """

class LoadingAnimation:
    """Class to handle various loading animations."""
    
    SPINNERS = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'line': ['|', '/', '-', '\\'],
        'braille': ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'],
        'pulse': ['█', '▉', '▊', '▋', '▌', '▍', '▎', '▏', '▎', '▍', '▌', '▋', '▊', '▉'],
    }
    
    TOOLKIT_FRAMES = [
        "⟦ Griffin's Toolkit ⟧",
        "⟪ Griffin's Toolkit ⟫",
        "『 Griffin's Toolkit 』",
        "《 Griffin's Toolkit 》",
        "【 Griffin's Toolkit 】",
        "《 Griffin's Toolkit 》",
        "『 Griffin's Toolkit 』", 
        "⟪ Griffin's Toolkit ⟫"
    ]
    
    QGIT_LOGO = QGIT_LOGO
    
    def __init__(self, stdscr, style='dots'):
        self.stdscr = stdscr
        self.spinner = cycle(self.SPINNERS[style])
        self.toolkit_spinner = cycle(self.TOOLKIT_FRAMES)
        self.running = False
        self.thread = None

class SecretSauceWindow:
    """Hidden window showing repository insights from SecretSauce."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        try:
            from qgits.secret_sauce import SecretSauce
            self.sauce = SecretSauce()
        except ImportError:
            print("Error: Could not import SecretSauce. Please ensure qgits/secret_sauce.py exists.")
            sys.exit(1)
    
    def draw_border(self, y, x, height, width):
        """Draw a stylish border around the window."""
        # Top border with title
        self.stdscr.addstr(y, x, "╭" + "─" * (width-2) + "╮", curses.color_pair(6))
        # Side borders
        for i in range(height-2):
            self.stdscr.addstr(y+i+1, x, "│", curses.color_pair(6))
            self.stdscr.addstr(y+i+1, x+width-1, "│", curses.color_pair(6))
        # Bottom border
        self.stdscr.addstr(y+height-1, x, "╰" + "─" * (width-2) + "╯", curses.color_pair(6))
    
    def show(self):
        """Display the secret sauce window with animations."""
        sauce_data = self.sauce.read_sauce()
        if not sauce_data:
            return
        
        max_y, max_x = self.stdscr.getmaxyx()
        window_height = 20
        window_width = 60
        start_y = (max_y - window_height) // 2
        start_x = (max_x - window_width) // 2
        
        # Animation for window appearance
        for i in range(window_height):
            self.stdscr.clear()
            current_height = min(i + 1, window_height)
            self.draw_border(start_y, start_x, current_height, window_width)
            
            if i >= 2:
                # Draw title
                title = "🔮 Secret Repository Insights 🔮"
                title_x = start_x + (window_width - len(title)) // 2
                self.stdscr.addstr(start_y + 1, title_x, title, curses.color_pair(3) | curses.A_BOLD)
            
            if i >= 4:
                self._draw_content(sauce_data, start_y + 3, start_x + 2, min(i - 3, window_height - 4))
            
            self.stdscr.refresh()
            time.sleep(0.05)
        
        # Wait for key press
        while True:
            key = self.stdscr.getch()
            if key in [27, ord('q')]:  # ESC or 'q'
                break
    
    def _draw_content(self, sauce_data, start_y, start_x, max_lines):
        """Draw the secret sauce content with animations."""
        current_y = start_y
        width = 56
        
        def add_section(title, content, color=4):
            nonlocal current_y
            if current_y - start_y >= max_lines:
                return
            self.stdscr.addstr(current_y, start_x, title, curses.color_pair(6) | curses.A_BOLD)
            current_y += 1
            
            if isinstance(content, dict):
                for key, value in content.items():
                    if current_y - start_y >= max_lines:
                        return
                    text = f"• {key}: {value}"
                    if len(text) > width:
                        text = text[:width-3] + "..."
                    self.stdscr.addstr(current_y, start_x + 2, text, curses.color_pair(color))
                    current_y += 1
            elif isinstance(content, list):
                for item in content:
                    if current_y - start_y >= max_lines:
                        return
                    if isinstance(item, dict):
                        text = f"{item['emoji']} {item['title']}: {item['value']}"
                    else:
                        text = f"• {item}"
                    if len(text) > width:
                        text = text[:width-3] + "..."
                    self.stdscr.addstr(current_y, start_x + 2, text, curses.color_pair(color))
                    current_y += 1
            current_y += 1
        
        # Draw insights sections
        if 'insights' in sauce_data:
            add_section("🎯 Repository Insights", {
                'Peak Activity': sauce_data['insights']['peak_productivity']['peak_period'].title(),
                'Commit Style': sauce_data['insights']['commit_style']['style'].title()
            })
        
        if 'fun_facts' in sauce_data:
            add_section("✨ Fun Facts", sauce_data['fun_facts'], color=3)
        
        if 'easter_eggs' in sauce_data:
            eggs = sauce_data['easter_eggs']
            if eggs:
                add_section("🥚 Easter Eggs", [
                    egg['reason'] if 'reason' in egg else egg['content']
                    for egg in eggs
                ], color=2)

class SparkEffect:
    """Class to handle electrical spark animations."""
    
    SPARK_CHARS = ['⚡', '✦', '✧', '⭒', '⭑', '∴', '∵', '*', '⋆', '★', '☆', '✬']
    COLORS = [46, 47, 48, 49, 50, 51, 82, 83, 84, 85, 86, 87, 118, 119, 120, 121]  # More bright colors
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.sparks = []
    
    def create_spark_at(self, x, y):
        """Create a spark at a specific position."""
        num_sparks = random.randint(3, 6)  # Create multiple sparks for button click effect
        
        for _ in range(num_sparks):
            spark = {
                'x': x + random.uniform(-2, 2),  # Add some random spread
                'y': y + random.uniform(-1, 1),
                'char': random.choice(self.SPARK_CHARS),
                'color': random.choice(self.COLORS),
                'life': 0,
                'max_life': random.randint(4, 10),
                'dx': random.uniform(-0.8, 0.8),
                'dy': random.uniform(-0.5, 0.5)
            }
            self.sparks.append(spark)
    
    def update(self):
        """Update and draw all active spark effects."""
        # Update existing sparks
        for spark in self.sparks[:]:
            # Update position with some acceleration
            spark['dx'] *= 1.05 if random.random() < 0.3 else 1.0
            spark['dy'] *= 1.05 if random.random() < 0.3 else 1.0
            spark['x'] += spark['dx']
            spark['y'] += spark['dy']
            spark['life'] += 1
            
            # Draw spark if it's still alive
            if spark['life'] < spark['max_life']:
                try:
                    x, y = int(spark['x']), int(spark['y'])
                    if 0 <= y < curses.LINES - 1 and 0 <= x < curses.COLS - 1:
                        # Create color pair for this spark
                        pair_num = 10 + (spark['color'] % 10)
                        curses.init_pair(pair_num, spark['color'], -1)
                        
                        # Draw spark with fading effect
                        fade = 1 - (spark['life'] / spark['max_life'])
                        attr = curses.color_pair(pair_num)
                        if fade < 0.3:  # Adjusted fade threshold
                            attr |= curses.A_DIM
                        elif fade > 0.7:  # Extra bright at start
                            attr |= curses.A_BOLD
                        
                        # Draw the spark
                        self.stdscr.addstr(y, x, spark['char'], attr | curses.A_BOLD)
                except curses.error:
                    pass
            else:
                self.sparks.remove(spark)

class MatrixRain:
    """Digital rain effect in the background."""
    
    CHARS = (
        # Japanese Hiragana
        "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
        # Japanese Katakana
        "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
        # Japanese Kanji (common ones)
        "日月火水木金土年月日時分秒天地人子女山川海空雨雪"
        # Rare Unicode symbols and box drawing
        "⌘⌥⇧⌃⎋⌫⏎⌦⇪⇥⌤⏏⎄⎆⎇⎈⎉⎊⎋⎌⎍⎎⎏⎐⎑⎒⎓⎔⎕"
        # Mathematical symbols
        "∀∁∂∃∄∅∆∇∈∉∊∋∌∍∎∏∐∑−∓∔∕∖∗∘∙√∛∜∝∞∟∠∡∢∣"
        # Currency and other symbols
        "₿¢£¥€₹₽¤฿₪₨₩₮₱₭₲₴₳₵₸₺₼₽₾₿"
        # Arrows and geometric shapes
        "←↑→↓↔↕↖↗↘↙▲▼◄►◆◇○●◐◑◒◓◔◕"
        # Block elements and shades
        "█▀▄▌▐░▒▓■□▢▣▤▥▦▧▨▩▪▫▬▭▮▯▰▱▲▼◄►◆◇○●"
        # Braille patterns (for texture)
        "⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟"
        # Ancient symbols and runes
        "ᚠᚡᚢᚣᚤᚥᚦᚧᚨᚩᚪᚫᚬᚭᚮᚯᚰᚱᚲᚳᚴᚵᚶᚷᚸᚹᚺᚻᚼᚽᚾᚿ"
        # Alchemical symbols
        "🜀🜁🜂🜃🜄🜅🜆🜇🜈🜉🜊🜋🜌🜍🜎🜏🜐🜑🜒🜓🜔🜕🜖🜗"
        # Numbers
        "0123456789"
    )
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.drops = []
        self.last_update = time.time()
        self.frame_time = 1.0 / 30.0  # Lock to 30 FPS for smoother animation
        self.accumulated_time = 0.0
        
        # Initialize more drops for denser rain
        width = curses.COLS
        for x in range(0, width, 2):  # Space out drops more densely
            if random.random() < 0.4:  # 40% chance for each column
                self.drops.append({
                    'x': x,
                    'y': random.randint(-20, 0),
                    'speed': random.uniform(0.3, 1.2),  # Varied speeds
                    'length': random.randint(4, 12),    # Longer trails
                    'chars': [random.choice(self.CHARS) for _ in range(12)],  # More characters per drop
                    'intensity': random.uniform(0.6, 1.0),
                    'color_shift': random.randint(0, 5),  # Add color variation
                    'last_y': None  # For interpolation
                })
    
    def update(self):
        """Update and draw matrix rain with improved smoothness."""
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.accumulated_time += delta_time
        
        if self.accumulated_time < self.frame_time:
            return
            
        self.last_update = current_time
        self.accumulated_time = 0.0
        height = curses.LINES
        
        # Update each drop with smoother motion
        for drop in self.drops:
            # Update position with smooth motion
            drop['y'] += drop['speed']
            
            # Reset if drop goes off screen
            if drop['y'] > height + drop['length']:
                drop['y'] = random.randint(-20, 0)
                drop['chars'] = [random.choice(self.CHARS) for _ in range(12)]
            
            # Draw the drop
            y = int(drop['y'])
            for i in range(drop['length']):
                if 0 <= y - i < height:
                    try:
                        char = drop['chars'][i % len(drop['chars'])]
                        intensity = 1.0 - (i / drop['length'])
                        if intensity > 0.7:
                            attr = curses.color_pair(2) | curses.A_BOLD
                        elif intensity > 0.3:
                            attr = curses.color_pair(2)
                        else:
                            attr = curses.color_pair(2) | curses.A_DIM
                        self.stdscr.addstr(y - i, drop['x'], char, attr)
                    except curses.error:
                        pass

class PulseWave:
    """Creates expanding wave effects from menu selection."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.waves = []
        
    def add_wave(self, center_y, center_x):
        """Add a new wave from the given center point."""
        self.waves.append({
            'x': center_x,
            'y': center_y,
            'radius': 0,
            'max_radius': 20,
            'age': 0,
            'max_age': 20
        })
    
    def update(self):
        """Update and draw all active waves."""
        for wave in self.waves[:]:
            wave['radius'] += 0.5
            wave['age'] += 1
            
            if wave['age'] >= wave['max_age']:
                self.waves.remove(wave)
                continue
            
            # Draw wave
            intensity = 1 - (wave['age'] / wave['max_age'])
            radius = int(wave['radius'])
            
            for angle in range(0, 360, 10):  # Draw points around the circle
                rad = math.radians(angle)
                x = int(wave['x'] + radius * math.cos(rad))
                y = int(wave['y'] + radius * math.sin(rad) * 0.5)  # Flatten circle to oval
                
                try:
                    if 0 <= y < curses.LINES - 1 and 0 <= x < curses.COLS - 1:
                        if intensity > 0.7:
                            attr = curses.color_pair(6) | curses.A_BOLD
                        elif intensity > 0.3:
                            attr = curses.color_pair(6)
                        else:
                            attr = curses.color_pair(6) | curses.A_DIM
                        self.stdscr.addstr(y, x, "·", attr)
                except curses.error:
                    pass

class BoxAnimation:
    """Creates an animated box effect around the selected menu item."""
    
    BOX_CHARS = {
        'corners': ['╭', '╮', '╰', '╯'],
        'sides': ['─', '│'],
        'corners_bold': ['┏', '┓', '┗', '┛'],
        'sides_bold': ['━', '┃'],
        'corners_double': ['╔', '╗', '╚', '╝'],
        'sides_double': ['═', '║']
    }
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_y = 0
        self.current_x = 0
        self.width = 0
        self.animation_start = 0
        self.is_animating = False
        self.frame_pos = 0
        self.last_update = time.time()
        self.frame_time = 1.0 / 60.0  # 60 FPS for smoother animation
        self.accumulated_time = 0.0
        self.transition_chars = {
            'corners': ['·', '∙', '○', '◎', '●'],
            'sides': ['⋅', '∘', '∙', '●', '━'],
            'vertical': ['⋅', '∘', '∙', '●', '┃']
        }
        self.prev_progress = 0.0  # For interpolation
    
    def start_animation(self, y, target_width):
        """Start a new box animation."""
        self.current_y = y
        self.width = target_width
        self.frame_pos = 0
        self.animation_start = time.time()
        self.is_animating = True
    
    def safe_addstr(self, y, x, char, attr):
        """Safely add a character at the given position with boundary checks."""
        max_y, max_x = self.stdscr.getmaxyx()
        try:
            if 0 <= y < max_y and 0 <= x < max_x:
                self.stdscr.addstr(y, x, char, attr)
        except curses.error:
            pass
    
    def update(self, menu_start_x):
        """Update and draw the animated box with improved smoothness."""
        if not self.is_animating:
            return
        
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.accumulated_time += delta_time
        
        # Calculate progress with smoother timing
        progress = min((current_time - self.animation_start) * 3.0, 1.0)
        
        # Enhanced easing function with smoother transitions
        eased_progress = 1 - pow(1 - progress, 4)  # Quartic easing for smoother finish
        
        # Calculate frame position
        self.frame_pos = int(eased_progress * 12)
        
        # Adjust x position to properly align with menu items
        x = menu_start_x
        y = self.current_y
        width = min(self.width + 8, self.stdscr.getmaxyx()[1] - x - 1)
        
        # Enhanced fade effect
        alpha = min((1.0 - progress) * 3, 1.0)
        
        def get_attr(is_corner, progress_point):
            if is_corner:
                if progress_point < 0.3:
                    return curses.color_pair(1) | curses.A_DIM
                elif progress_point < 0.7:
                    return curses.color_pair(1)
                else:
                    return curses.color_pair(1) | curses.A_BOLD
            else:
                if alpha > 0.7:
                    return curses.color_pair(1) | curses.A_BOLD
                elif alpha > 0.3:
                    return curses.color_pair(1)
                else:
                    return curses.color_pair(1) | curses.A_DIM
        
        def get_transition_char(char_type, local_progress):
            chars = self.transition_chars[char_type]
            idx = min(int(local_progress * len(chars)), len(chars) - 1)
            return chars[idx]
        
        # Draw the frame with enhanced transitions and boundary checking
        if self.frame_pos >= 1:  # Top left corner
            local_progress = min(self.frame_pos / 3, 1.0)
            char = get_transition_char('corners', local_progress) if local_progress < 1 else self.BOX_CHARS['corners'][0]
            self.safe_addstr(y - 1, x, char, get_attr(True, local_progress))
        
        if self.frame_pos >= 2:  # Top right corner
            local_progress = min((self.frame_pos - 1) / 3, 1.0)
            char = get_transition_char('corners', local_progress) if local_progress < 1 else self.BOX_CHARS['corners'][1]
            self.safe_addstr(y - 1, x + width - 1, char, get_attr(True, local_progress))
        
        if self.frame_pos >= 3:  # Bottom left corner
            local_progress = min((self.frame_pos - 2) / 3, 1.0)
            char = get_transition_char('corners', local_progress) if local_progress < 1 else self.BOX_CHARS['corners'][2]
            self.safe_addstr(y + 1, x, char, get_attr(True, local_progress))
        
        if self.frame_pos >= 4:  # Bottom right corner
            local_progress = min((self.frame_pos - 3) / 3, 1.0)
            char = get_transition_char('corners', local_progress) if local_progress < 1 else self.BOX_CHARS['corners'][3]
            self.safe_addstr(y + 1, x + width - 1, char, get_attr(True, local_progress))
        
        # Draw connecting lines with enhanced transitions
        if self.frame_pos >= 5:  # Top line
            local_progress = min((self.frame_pos - 4) / 3, 1.0)
            for i in range(1, width - 1):
                char = get_transition_char('sides', local_progress) if local_progress < 1 else self.BOX_CHARS['sides'][0]
                self.safe_addstr(y - 1, x + i, char, get_attr(False, local_progress))
        
        if self.frame_pos >= 6:  # Bottom line
            local_progress = min((self.frame_pos - 5) / 3, 1.0)
            for i in range(1, width - 1):
                char = get_transition_char('sides', local_progress) if local_progress < 1 else self.BOX_CHARS['sides'][0]
                self.safe_addstr(y + 1, x + i, char, get_attr(False, local_progress))
        
        if self.frame_pos >= 7:  # Left line
            local_progress = min((self.frame_pos - 6) / 3, 1.0)
            char = get_transition_char('vertical', local_progress) if local_progress < 1 else self.BOX_CHARS['sides'][1]
            self.safe_addstr(y, x, char, get_attr(False, local_progress))
        
        if self.frame_pos >= 8:  # Right line
            local_progress = min((self.frame_pos - 7) / 3, 1.0)
            char = get_transition_char('vertical', local_progress) if local_progress < 1 else self.BOX_CHARS['sides'][1]
            self.safe_addstr(y, x + width - 1, char, get_attr(False, local_progress))
        
        # Keep animating for a short while after completion for smooth transition
        if progress >= 1.0:
            self.is_animating = False

class DecryptionEffect:
    """Creates a decryption animation effect for text with enhanced visual effects."""
    
    CIPHER_CHARS = (
        "!@#$%^&*()_+-=[]{}|;:,.<>?/~`⚡✦✧⭒⭑∴∵⋆★☆✬"
        "⌘⌥⇧⌃⎋⌫⏎⌦⇪⇥⌤⏏⎄⎆⎇⎈⎉⎊⎋⎌⎍⎎⎏⎐⎑⎒⎓⎔⎕"
        "∀∁∂∃∄∅∆∇∈∉∊∋∌∍∎∏∐∑−∓∔∕∖∗∘∙√∛∜∝∞∟∠∡∢∣"
        "⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟"
    )
    
    REVEAL_SPEED = 0.03  # Time between character reveals
    WORD_DELAY = 0.1    # Delay between starting each word's decryption
    SCRAMBLE_RATE = 0.2  # How often to scramble unrevealed characters
    RIPPLE_SPEED = 0.15  # Speed of ripple effect
    PARTICLE_LIFE = 0.5  # Life duration of particles
    
    def __init__(self):
        self.decrypting_texts = {}
        self.revealed_positions = set()
        self.last_scramble = time.time()
        self.scrambled_chars = {}
        self.highlighted_positions = set()
        self.all_revealed = False
        self.particles = []  # Store active particles
        self.ripples = []   # Store active ripples
        self.glow_effects = {}  # Store glow effects
        self.last_effect_time = time.time()
        self.decryption_states = {}  # Track decryption state for each position
        self.frame_time = 1.0 / 60.0  # 60 FPS for smoother animation
        self.last_update = time.time()
        self.accumulated_time = 0.0
        self.prev_states = {}  # For interpolation
        
        # Enhanced visual effects
        self.PARTICLE_CHARS = ['∙', '●', '○', '◎', '◌', '◍', '◐', '◑', '◒', '◓', '◔', '◕']
        self.RIPPLE_CHARS = ['·', '∘', '○', '◎', '●', '◎', '○', '∘', '·']
        self.GLOW_LEVELS = [
            curses.A_DIM,
            curses.A_NORMAL,
            curses.A_BOLD,
            curses.A_BOLD | curses.A_REVERSE,
            curses.A_BOLD,
            curses.A_NORMAL
        ]
    
    def create_particle_burst(self, x, y, num_particles=8):
        """Create a burst of particles from a point."""
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(10, 20)
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed * 0.5,  # Flatten the effect vertically
                'char': random.choice(self.PARTICLE_CHARS),
                'life': self.PARTICLE_LIFE,
                'color': random.choice([1, 2, 3, 6])  # Use different color pairs
            })
    
    def create_ripple(self, x, y):
        """Create a ripple effect from a point."""
        self.ripples.append({
            'x': x,
            'y': y,
            'radius': 0,
            'max_radius': 10,
            'life': 1.0,
            'start_time': time.time()
        })
    
    def add_glow_effect(self, x, y, duration=0.5):
        """Add a glowing effect to a position."""
        self.glow_effects[(x, y)] = {
            'start_time': time.time(),
            'duration': duration,
            'level_index': 0,
            'update_time': time.time()
        }
    
    def start_decryption(self, x, y, text, delay=0, permanent=False):
        """Start decryption effect with enhanced visuals."""
        words, word_positions = self._split_into_words(text)
        pos = (x, y)
        
        # Create initial effects
        self.create_ripple(x + len(text) // 2, y)
        self.add_glow_effect(x, y)
        
        # Initialize decryption state
        self.decryption_states[pos] = {
            'decrypted': False,
            'time': time.time(),
            'progress': 0.0,
            'word_progress': [0.0] * len(words)
        }
        
        self.decrypting_texts[pos] = {
            'target': text,
            'current': [''] * len(text),
            'start_time': time.time() + delay,
            'words': words,
            'word_positions': word_positions,
            'word_index': 0,
            'permanent': permanent,
            'effect_chars': [random.choice(self.CIPHER_CHARS) for _ in range(len(text))],
            'effect_time': time.time()
        }
        self.scrambled_chars[pos] = {}
    
    def start_reencryption(self, x, y, text):
        """Start re-encryption effect for a position."""
        pos = (x, y)
        self.decryption_states[pos] = {
            'decrypted': False,
            'time': time.time(),
            'progress': 1.0,  # Start from fully decrypted
            'word_progress': [1.0] * len(text.split())  # Start all words as decrypted
        }
        
        # Reset scrambled chars for this position
        self.scrambled_chars[pos] = {
            i: random.choice(self.CIPHER_CHARS)
            for i in range(len(text))
            if not text[i].isspace()
        }
        
        # Create ripple effect for re-encryption
        self.create_ripple(x + len(text) // 2, y)
        
        # Start with decrypted text and gradually re-encrypt
        if pos in self.decrypting_texts:
            self.decrypting_texts[pos]['current'] = list(text)
            self.decrypting_texts[pos]['effect_time'] = time.time()
    
    def update_particles(self, current_time, dt):
        """Update particle positions and lifetimes."""
        for particle in self.particles[:]:
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
            
            # Update position with smoother deceleration
            particle['dx'] *= 0.95
            particle['dy'] *= 0.95
            particle['x'] += particle['dx'] * dt * 60  # Scale by target framerate
            particle['y'] += particle['dy'] * dt * 60
    
    def update_ripples(self, current_time):
        """Update ripple animations."""
        for ripple in self.ripples[:]:
            elapsed = current_time - ripple['start_time']
            ripple['radius'] = elapsed / self.RIPPLE_SPEED * 8
            ripple['life'] = max(0, 1.0 - (elapsed / (self.RIPPLE_SPEED * 10)))
            
            if ripple['life'] <= 0:
                self.ripples.remove(ripple)
    
    def update_glow_effects(self, current_time):
        """Update glow effect animations."""
        for pos, effect in list(self.glow_effects.items()):
            if current_time - effect['start_time'] > effect['duration']:
                del self.glow_effects[pos]
                continue
            
            if current_time - effect['update_time'] > 0.05:  # Update every 50ms
                effect['level_index'] = (effect['level_index'] + 1) % len(self.GLOW_LEVELS)
                effect['update_time'] = current_time
    
    def get_text(self, x, y, default_text):
        """Get the current state of text with enhanced visual effects."""
        pos = (x, y)
        current_time = time.time()
        
        # Start decryption if needed
        if pos not in self.decrypting_texts:
            self.start_decryption(x, y, default_text, permanent=True)
        
        data = self.decrypting_texts.get(pos)
        if not data:
            return default_text
        
        # Check if position is highlighted
        is_highlighted = pos in self.highlighted_positions or self.all_revealed
        
        # If highlighted, show decrypted or decrypting text
        if is_highlighted:
            # Return the current state of decryption
            if ''.join(data['current']).strip():  # If we have decrypted content
                text = ''.join(data['current'])
            else:  # If decryption hasn't started yet
                text = default_text
            
            # Apply glow effect if active
            if pos in self.glow_effects:
                effect = self.glow_effects[pos]
                glow_attr = self.GLOW_LEVELS[effect['level_index']]
                return (text, glow_attr)
            
            return text
        
        # If not highlighted, show encrypted text
        if pos not in self.scrambled_chars:
            self.scrambled_chars[pos] = {
                i: random.choice(self.CIPHER_CHARS)
                for i in range(len(default_text))
                if not default_text[i].isspace()
            }
        
        # Update scrambled characters periodically
        if current_time - data.get('effect_time', 0) > 0.05:
            self.scrambled_chars[pos] = {
                i: random.choice(self.CIPHER_CHARS)
                for i in range(len(default_text))
                if not default_text[i].isspace()
            }
            data['effect_time'] = current_time
        
        # Return scrambled text
        scrambled = []
        for i, char in enumerate(default_text):
            if char.isspace():
                scrambled.append(char)
            else:
                scrambled.append(self.scrambled_chars[pos].get(i, random.choice(self.CIPHER_CHARS)))
        return ''.join(scrambled)
    
    def start_reencryption(self, x, y, text):
        """Start re-encryption effect for a position."""
        pos = (x, y)
        self.decryption_states[pos] = {'decrypted': False, 'time': time.time()}
        
        # Reset scrambled chars for this position
        self.scrambled_chars[pos] = {
            i: random.choice(self.CIPHER_CHARS)
            for i in range(len(text))
            if not text[i].isspace()
        }
        
        # Create ripple effect for re-encryption
        self.create_ripple(x + len(text) // 2, y)
    
    def update(self):
        """Update decryption effects and animations with improved smoothness."""
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.accumulated_time += delta_time
        
        if self.accumulated_time < self.frame_time:
            return
        
        self.last_update = current_time
        self.accumulated_time = 0.0
        
        # Update decryption animations
        for pos, data in list(self.decrypting_texts.items()):
            if current_time < data['start_time']:
                continue
            
            # Only process highlighted positions
            if pos not in self.highlighted_positions and not self.all_revealed:
                data['current'] = [''] * len(data['target'])
                continue
            
            target = data['target']
            words = data['words']
            word_positions = data['word_positions']
            
            # Calculate which words should be decrypting
            time_elapsed = current_time - data['start_time']
            word_index = min(int(time_elapsed / self.WORD_DELAY), len(words))
            data['word_index'] = word_index
            
            # Update each word
            for w_idx in range(word_index):
                word = words[w_idx]
                positions = word_positions[w_idx]
                
                # Skip spaces
                if word.isspace():
                    data['current'][positions[0]] = word
                    continue
                
                # Calculate progress for each character
                word_time = time_elapsed - (w_idx * self.WORD_DELAY)
                chars_to_reveal = int(word_time / self.REVEAL_SPEED)
                
                # Update characters
                for i, pos_idx in enumerate(positions):
                    if i < chars_to_reveal:
                        data['current'][pos_idx] = target[pos_idx]
                    else:
                        data['current'][pos_idx] = random.choice(self.CIPHER_CHARS)
        
        # Update visual effects with smoother timing
        dt = current_time - self.last_effect_time
        self.last_effect_time = current_time
        
        self.update_particles(current_time, dt)
        self.update_ripples(current_time)
        self.update_glow_effects(current_time)
    
    def draw_effects(self, stdscr):
        """Draw all visual effects."""
        current_time = time.time()
        
        # Draw particles with smoother fade
        for particle in self.particles:
            try:
                x, y = int(particle['x']), int(particle['y'])
                if 0 <= y < curses.LINES - 1 and 0 <= x < curses.COLS - 1:
                    attr = curses.color_pair(particle['color'])
                    fade = particle['life'] / self.PARTICLE_LIFE
                    if fade < 0.3:
                        attr |= curses.A_DIM
                    elif fade > 0.7:
                        attr |= curses.A_BOLD
                    stdscr.addstr(y, x, particle['char'], attr)
            except curses.error:
                continue
        
        # Draw ripples with smoother transitions
        for ripple in self.ripples:
            try:
                radius = int(ripple['radius'])
                for angle in range(0, 360, 45):  # Draw 8 points around the circle
                    rad = math.radians(angle)
                    x = int(ripple['x'] + radius * math.cos(rad))
                    y = int(ripple['y'] + radius * math.sin(rad) * 0.5)
                    
                    if 0 <= y < curses.LINES - 1 and 0 <= x < curses.COLS - 1:
                        char_idx = int((1 - ripple['life']) * (len(self.RIPPLE_CHARS) - 1))
                        char = self.RIPPLE_CHARS[char_idx]
                        
                        attr = curses.color_pair(6)
                        if ripple['life'] < 0.3:
                            attr |= curses.A_DIM
                        elif ripple['life'] > 0.7:
                            attr |= curses.A_BOLD
                        
                        stdscr.addstr(y, x, char, attr)
            except curses.error:
                continue
    
    def highlight_position(self, x, y, delay=0):
        """Highlight a position with enhanced effects."""
        pos = (x, y)
        if pos not in self.decrypting_texts:
            self.start_decryption(x, y, "", delay, True)
        
        if pos not in self.highlighted_positions:
            self.highlighted_positions.add(pos)
            # Reset decryption state and start time for new highlight
            if pos in self.decrypting_texts:
                self.decrypting_texts[pos]['start_time'] = time.time() + delay
                self.decrypting_texts[pos]['current'] = [''] * len(self.decrypting_texts[pos]['target'])
            # Create visual effects
            self.create_ripple(x, y)
            self.add_glow_effect(x, y, 0.8)
    
    def unhighlight_position(self, x, y):
        """Remove highlight from a position and start re-encryption."""
        pos = (x, y)
        if pos in self.highlighted_positions:
            self.highlighted_positions.discard(pos)
            # Only start re-encryption if it was previously decrypted
            if pos in self.decryption_states and self.decryption_states[pos]['decrypted']:
                # Get the current text to re-encrypt
                text = self.decrypting_texts[pos]['target']
                self.start_reencryption(x, y, text)
            self.create_ripple(x, y)  # Create a final ripple effect
            self.add_glow_effect(x, y, 0.3)  # Quick fade-out glow
    
    def _split_into_words(self, text):
        """Split text into words and track their positions."""
        words = []
        positions = []
        current_word = []
        current_positions = []
        
        for i, char in enumerate(text):
            if char.isspace():
                if current_word:
                    words.append(''.join(current_word))
                    positions.append(current_positions)
                    current_word = []
                    current_positions = []
                words.append(char)
                positions.append([i])
            else:
                current_word.append(char)
                current_positions.append(i)
        
        if current_word:
            words.append(''.join(current_word))
            positions.append(current_positions)
        
        return words, positions
    
    def _store_prev_states(self):
        """Store previous states for interpolation."""
        self.prev_states = {
            'particles': [(p['x'], p['y']) for p in self.particles],
            'ripples': [(r['radius'], r['life']) for r in self.ripples]
        }
    
    def _interpolate_effects(self, alpha):
        """Interpolate visual effects between frames."""
        if not self.prev_states:
            return
            
        # Interpolate particle positions
        for i, particle in enumerate(self.particles):
            if i < len(self.prev_states['particles']):
                prev_x, prev_y = self.prev_states['particles'][i]
                particle['x'] = prev_x * (1 - alpha) + particle['x'] * alpha
                particle['y'] = prev_y * (1 - alpha) + particle['y'] * alpha
        
        # Interpolate ripple effects
        for i, ripple in enumerate(self.ripples):
            if i < len(self.prev_states['ripples']):
                prev_radius, prev_life = self.prev_states['ripples'][i]
                ripple['radius'] = prev_radius * (1 - alpha) + ripple['radius'] * alpha
                ripple['life'] = prev_life * (1 - alpha) + ripple['life'] * alpha

class LandingPage:
    """Interactive landing page for qgit."""
    
    MENU_ITEMS = QGitConfig.MENU_ITEMS
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.selected_item = 0
        self.loading_animation = LoadingAnimation(stdscr)
        self.spark_effect = SparkEffect(stdscr)
        self.matrix_rain = MatrixRain(stdscr)  # Initialize matrix rain
        self.pulse_wave = PulseWave(stdscr)
        self.box_animation = BoxAnimation(stdscr)
        self.decryption_effect = DecryptionEffect()
        self.last_click_time = 0
        self.last_click_pos = None
        self.help_text_visible = False
        self.sauce_window = None
        self.help_page = None
        self.menu_revealed = False  # Add this line to initialize menu_revealed
        
        # Enable keypad and hide cursor
        self.stdscr.keypad(1)
        curses.curs_set(0)
        
        # Initialize color pairs with -1 as background for transparency
        curses.start_color()
        curses.use_default_colors()  # Allow using terminal's default colors
        curses.init_pair(1, curses.COLOR_GREEN, -1)    # Green on default background
        curses.init_pair(2, curses.COLOR_CYAN, -1)     # Cyan on default background
        curses.init_pair(3, curses.COLOR_BLUE, -1)     # Blue on default background
        curses.init_pair(4, curses.COLOR_YELLOW, -1)   # Yellow on default background
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Magenta on default background
        curses.init_pair(6, curses.COLOR_WHITE, -1)    # White on default background
        
        # Clear screen with black background
        self.stdscr.bkgd(' ', curses.color_pair(0))
        self.stdscr.clear()
        
        # Enable mouse events
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        
        # Show initial loading screen
        self.show_loading_screen()
        
        # Configure terminal settings
        os.environ.setdefault('TERM', 'xterm-256color')
        
        # Enable mouse support
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        print('\033[?1003h')  # Enable mouse movement events
        
        # Check if SecretSauce is available and add stats menu item if it is
        try:
            from qgits.secret_sauce import SecretSauce
            self.MENU_ITEMS = QGitConfig.MENU_ITEMS + [
                ('stats', 'Repository analytics', '統')
            ]
        except ImportError:
            self.MENU_ITEMS = QGitConfig.MENU_ITEMS
        
        # Initialize other settings
        self.current_selection = 0
        self.effects_enabled = False  # Track if effects should be shown
        self.logo_click_time = 0
        self.logo_bounds = {'y1': 0, 'y2': 0, 'x1': 0, 'x2': 0}
        self.menu_bounds = {'y1': 0, 'y2': 0, 'x1': 0, 'x2': 0}
        self.last_click_time = 0
        self.click_cooldown = 0.2
        self.frame_time = 1.0 / 60.0  # 60 FPS for main loop
        self.last_frame = time.time()
        self.accumulated_time = 0.0
    
    def get_menu_y(self):
        """Calculate and return the starting Y position for the menu."""
        max_y, _ = self.stdscr.getmaxyx()
        menu_height = len(self.MENU_ITEMS) * 2 + 4
        return min(14, max_y - menu_height - 4)  # Ensure menu fits vertically

    def show_loading_screen(self):
        """Show an animated loading screen."""
        start_time = time.time()
        spinner = cycle(LoadingAnimation.SPINNERS['dots'])
        toolkit_spinner = cycle(LoadingAnimation.TOOLKIT_FRAMES)
        loading_duration = 1.5  # seconds
        
        while time.time() - start_time < loading_duration:
            self.stdscr.clear()
            
            # Draw logo
            logo_lines = [line for line in LoadingAnimation.QGIT_LOGO.split('\n') if line]
            logo_height = len(logo_lines)
            logo_width = len(logo_lines[0])
            logo_y = (curses.LINES - logo_height) // 2 - 2
            logo_x = (curses.COLS - logo_width) // 2
            
            # Draw border around logo
            self.draw_border(logo_y - 1, logo_x - 2, logo_height + 2, logo_width + 4)
            
            # Draw logo with pulsing effect
            pulse = abs(math.sin((time.time() - start_time) * 4))
            color_pair = curses.color_pair(2) | curses.A_BOLD if pulse > 0.5 else curses.color_pair(2)
            
            for i, line in enumerate(logo_lines):
                self.stdscr.addstr(logo_y + i, logo_x, line, color_pair)
            
            # Draw toolkit text with animation
            toolkit_frame = next(toolkit_spinner)
            toolkit_y = logo_y - 2
            toolkit_x = (curses.COLS - len(toolkit_frame)) // 2
            toolkit_color = curses.color_pair(6) | (curses.A_BOLD if pulse > 0.5 else 0)
            self.stdscr.addstr(toolkit_y, toolkit_x, toolkit_frame, toolkit_color)
            
            # Draw loading spinner and text
            spinner_frame = next(spinner)
            loading_text = "Initializing qgit"
            dots = "." * (int((time.time() - start_time) * 4) % 4)
            full_text = f"{spinner_frame} {loading_text}{dots}"
            
            loading_y = logo_y + logo_height + 2
            loading_x = (curses.COLS - len(full_text)) // 2
            self.stdscr.addstr(loading_y, loading_x, full_text, curses.color_pair(7) | curses.A_BOLD)
            
            self.stdscr.refresh()
            time.sleep(0.1)
    
    def draw_border(self, y, x, height, width):
        """Draw a stylish border around a region."""
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Ensure we're not drawing outside the terminal
        if y < 0 or x < 0 or y + height > max_y or x + width > max_x:
            return
        
        try:
            # Corners
            self.stdscr.addstr(y, x, "╭", curses.color_pair(5))
            self.stdscr.addstr(y, x + width - 1, "╮", curses.color_pair(5))
            self.stdscr.addstr(y + height - 1, x, "╰", curses.color_pair(5))
            self.stdscr.addstr(y + height - 1, x + width - 1, "╯", curses.color_pair(5))
            
            # Top and bottom borders
            for i in range(1, width - 1):
                self.stdscr.addstr(y, x + i, "─", curses.color_pair(5))
                self.stdscr.addstr(y + height - 1, x + i, "─", curses.color_pair(5))
            
            # Left and right borders
            for i in range(1, height - 1):
                self.stdscr.addstr(y + i, x, "│", curses.color_pair(5))
                self.stdscr.addstr(y + i, x + width - 1, "│", curses.color_pair(5))
        except curses.error:
            # If we still get an error, silently fail
            pass
            
    def draw_logo(self):
        """Draw the QGit logo with animation and improved click detection."""
        logo_lines = [line for line in LoadingAnimation.QGIT_LOGO.split('\n') if line]
        logo_height = len(logo_lines)
        logo_width = len(logo_lines[0])
        start_y = 2
        start_x = (curses.COLS - logo_width - 4) // 2  # -4 for border padding
        
        # Store logo boundaries with padding for better click detection
        self.logo_bounds = {
            'y1': start_y - 1,  # Include border in clickable area
            'y2': start_y + logo_height,
            'x1': start_x - 2,  # Include border in clickable area
            'x2': start_x + logo_width + 2
        }
        
        # Draw border around logo
        self.draw_border(start_y - 1, start_x - 2, logo_height + 2, logo_width + 4)
        
        # Draw logo with highlight effect if clicked recently
        highlight = self.effects_enabled and (time.time() - self.last_click_time < 0.5)
        for i, line in enumerate(logo_lines):
            attr = curses.color_pair(6 if highlight else 2) | curses.A_BOLD
            self.stdscr.addstr(start_y + i, start_x, line, attr)
    
    def handle_mouse_click(self, x, y):
        """Handle mouse click events with improved tracking."""
        current_time = time.time()
        
        # Enforce click cooldown to prevent accidental double clicks
        if current_time - self.last_click_time < self.click_cooldown:
            return
        
        # Check if click is within logo bounds (with small buffer)
        logo_buffer = 2
        is_logo_click = (
            self.logo_bounds['y1'] - logo_buffer <= y <= self.logo_bounds['y2'] + logo_buffer and 
            self.logo_bounds['x1'] - logo_buffer <= x <= self.logo_bounds['x2'] + logo_buffer
        )
        
        if is_logo_click:
            self.last_click_time = current_time
            self.effects_enabled = not self.effects_enabled  # Toggle effects instead of all_revealed
            
            # Reset decryption state for all menu items
            max_y, max_x = self.stdscr.getmaxyx()
            menu_start_y = min(14, max_y - len(self.MENU_ITEMS) * 2 - 8)
            menu_start_x = max(2, (max_x - 60) // 2)
            
            # Handle menu items based on effects_enabled state
            for i in range(len(self.MENU_ITEMS)):
                y = menu_start_y + i * 2
                action, description, emoji = self.MENU_ITEMS[i]
                
                # Prepare text for both action and description
                item_text = f"{emoji}  {action.ljust(10)}"
                delay = i * 0.05  # Cascading delay
                
                if self.effects_enabled:
                    # Start decryption for all items
                    self.decryption_effect.start_decryption(menu_start_x, y, item_text, delay=delay, permanent=True)
                    self.decryption_effect.start_decryption(menu_start_x + 20, y, description, delay=delay, permanent=True)
                    self.decryption_effect.highlight_position(menu_start_x, y, delay)
                    self.decryption_effect.highlight_position(menu_start_x + 20, y, delay)
                else:
                    # Only keep current selection highlighted when hiding
                    if i != self.current_selection:
                        self.decryption_effect.unhighlight_position(menu_start_x, y)
                        self.decryption_effect.unhighlight_position(menu_start_x + 20, y)
                    else:
                        self.decryption_effect.highlight_position(menu_start_x, y)
                        self.decryption_effect.highlight_position(menu_start_x + 20, y)
    
    def draw_menu(self):
        """Draw the interactive menu."""
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Calculate menu dimensions
        menu_width = min(60, max_x - 6)  # Leave room for borders
        menu_height = len(self.MENU_ITEMS) * 2 + 4
        
        # Ensure menu fits in terminal
        if menu_height > max_y - 16:  # Account for logo and margins
            menu_height = max_y - 16
        
        # Calculate starting positions
        menu_start_y = min(14, max_y - menu_height - 4)  # Ensure menu fits vertically
        menu_start_x = max(2, (max_x - menu_width) // 2)  # Center menu horizontally
        
        try:
            # Draw border around menu
            self.draw_border(menu_start_y - 3, menu_start_x - 2, menu_height + 2, menu_width + 4)
            
            # Draw menu title with decryption effect
            title = "Select an action:"
            title_x = menu_start_x + (menu_width - len(title)) // 2
            if menu_start_y - 2 >= 0:
                if not self.menu_revealed:
                    self.decryption_effect.start_decryption(title_x, menu_start_y - 2, title)
                title_text = self.decryption_effect.get_text(title_x, menu_start_y - 2, title)
                if isinstance(title_text, tuple):
                    text, attr = title_text
                    self.stdscr.addstr(menu_start_y - 2, title_x, text, curses.color_pair(6) | attr)
                else:
                    self.stdscr.addstr(menu_start_y - 2, title_x, title_text, curses.color_pair(6) | curses.A_BOLD)
            
            # Start decryption effect for menu items if not already started
            if not self.menu_revealed:
                for i, (action, description, emoji) in enumerate(self.MENU_ITEMS):
                    y = menu_start_y + i * 2
                    item_text = f"{emoji}  {action.ljust(10)}"
                    self.decryption_effect.start_decryption(menu_start_x, y, item_text, delay=i * 0.1, permanent=True)
                    self.decryption_effect.start_decryption(menu_start_x + 20, y, description, delay=i * 0.1, permanent=True)
                self.menu_revealed = True
            
            # Draw visible menu items
            visible_items = (menu_height - 4) // 2  # Calculate how many items can fit
            start_idx = max(0, min(self.current_selection - visible_items // 2, len(self.MENU_ITEMS) - visible_items))
            
            for i in range(start_idx, min(start_idx + visible_items, len(self.MENU_ITEMS))):
                action, description, emoji = self.MENU_ITEMS[i]
                y = menu_start_y + (i - start_idx) * 2
                
                if y + 1 >= max_y:  # Skip if we're at the bottom of the screen
                    break
                
                # Update highlighted positions based on selection and effects_enabled state
                if i == self.current_selection or self.effects_enabled:
                    self.decryption_effect.highlight_position(menu_start_x, y)
                    self.decryption_effect.highlight_position(menu_start_x + 20, y)
                else:
                    # Only unhighlight if easter egg is not activated
                    if not self.effects_enabled:
                        self.decryption_effect.unhighlight_position(menu_start_x, y)
                        self.decryption_effect.unhighlight_position(menu_start_x + 20, y)
                
                # Draw menu item with decryption effect
                item_text = f"{emoji}  {action.ljust(10)}"
                current_text = self.decryption_effect.get_text(menu_start_x, y, item_text)
                
                # Determine if this item should be decrypted
                should_decrypt = i == self.current_selection or self.effects_enabled
                
                if isinstance(current_text, tuple):
                    text, attr = current_text
                    if should_decrypt:
                        self.stdscr.addstr(y, menu_start_x, text, curses.color_pair(1) | attr)
                        desc_text = self.decryption_effect.get_text(menu_start_x + 20, y, description)
                        if isinstance(desc_text, tuple):
                            desc, desc_attr = desc_text
                            self.stdscr.addstr(y, menu_start_x + 20, desc, curses.color_pair(3) | desc_attr)
                        else:
                            self.stdscr.addstr(y, menu_start_x + 20, desc_text, curses.color_pair(3) | curses.A_BOLD)
                    else:
                        self.stdscr.addstr(y, menu_start_x, text, curses.color_pair(4) | attr)
                        desc_text = self.decryption_effect.get_text(menu_start_x + 20, y, description)
                        if isinstance(desc_text, tuple):
                            desc, desc_attr = desc_text
                            self.stdscr.addstr(y, menu_start_x + 20, desc, curses.color_pair(5) | desc_attr)
                        else:
                            self.stdscr.addstr(y, menu_start_x + 20, desc_text, curses.color_pair(5))
                else:
                    if should_decrypt:
                        self.stdscr.addstr(y, menu_start_x, current_text, curses.color_pair(1) | curses.A_BOLD)
                        desc_text = self.decryption_effect.get_text(menu_start_x + 20, y, description)
                        self.stdscr.addstr(y, menu_start_x + 20, desc_text, curses.color_pair(3) | curses.A_BOLD)
                    else:
                        self.stdscr.addstr(y, menu_start_x, current_text, curses.color_pair(4))
                        desc_text = self.decryption_effect.get_text(menu_start_x + 20, y, description)
                        self.stdscr.addstr(y, menu_start_x + 20, desc_text, curses.color_pair(5))
            
            # Draw all visual effects
            self.decryption_effect.draw_effects(self.stdscr)
            
        except curses.error:
            # If we still get an error, silently fail
            pass
    
    def draw_footer(self):
        """Draw footer with controls help."""
        footer_text = "↑/↓: Navigate   ⏎ Enter: Select   q: Quit"
        y = curses.LINES - 3
        x = (curses.COLS - len(footer_text)) // 2
        
        # Draw border around footer
        self.draw_border(y - 1, x - 2, 3, len(footer_text) + 4)
        
        # Draw footer text
        self.stdscr.addstr(y, x, footer_text, curses.color_pair(5) | curses.A_DIM)
    
    def show_help_page(self):
        """Show the help page with detailed information."""
        while True:
            self.stdscr.clear()
            
            # Draw matrix rain in background with reduced intensity
            self.matrix_rain.update()
            
            max_y, max_x = self.stdscr.getmaxyx()
            
            # Calculate dimensions
            help_width = min(80, max_x - 4)
            help_height = len(self.HELP_TEXT) + 4
            help_start_x = (max_x - help_width) // 2
            help_start_y = 2
            
            # Draw border around help content
            self.draw_border(help_start_y - 1, help_start_x - 1, help_height, help_width + 2)
            
            # Draw title
            title = "QGit Help"
            title_x = help_start_x + (help_width - len(title)) // 2
            self.stdscr.addstr(help_start_y, title_x, title, curses.color_pair(6) | curses.A_BOLD)
            
            # Draw help content
            current_y = help_start_y + 2
            for command, description in self.HELP_TEXT:
                if current_y >= max_y - 2:  # Prevent drawing outside screen
                    break
                    
                if not command and not description:  # Empty line
                    current_y += 1
                    continue
                    
                if not description:  # Section header
                    self.stdscr.addstr(current_y, help_start_x, command, curses.color_pair(3) | curses.A_BOLD)
                    current_y += 1
                    # Draw separator line
                    self.stdscr.addstr(current_y, help_start_x, "─" * help_width, curses.color_pair(5))
                    current_y += 1
                else:  # Command description
                    # Draw command
                    self.stdscr.addstr(current_y, help_start_x, command.ljust(15), curses.color_pair(2) | curses.A_BOLD)
                    # Draw description
                    desc_x = help_start_x + 20
                    max_desc_width = help_width - 20
                    if len(description) > max_desc_width:
                        description = description[:max_desc_width-3] + "..."
                    self.stdscr.addstr(current_y, desc_x, description, curses.color_pair(4))
                    current_y += 1
            
            # Draw footer
            footer_text = "Press 'q' or ESC to return to menu"
            footer_x = (max_x - len(footer_text)) // 2
            footer_y = max_y - 2
            self.stdscr.addstr(footer_y, footer_x, footer_text, curses.color_pair(5) | curses.A_DIM)
            
            # Update effects
            self.spark_effect.update()
            
            self.stdscr.refresh()
            
            # Handle input
            try:
                key = self.stdscr.getch()
                if key in [ord('q'), 27]:  # q or ESC
                    return
            except curses.error:
                continue
    
    def run(self):
        """Main loop for the landing page with improved frame timing."""
        try:
            while True:
                current_time = time.time()
                delta_time = current_time - self.last_frame
                self.accumulated_time += delta_time
                
                # Skip frame if we're ahead of schedule
                if self.accumulated_time < self.frame_time:
                    time.sleep(max(0, self.frame_time - self.accumulated_time))
                    continue
                
                self.last_frame = current_time
                self.accumulated_time = 0.0
                
                # Clear screen
                self.stdscr.clear()
                
                # Get terminal dimensions for menu positioning
                max_y, max_x = self.stdscr.getmaxyx()
                menu_width = min(60, max_x - 6)  # Leave room for borders
                menu_start_x = max(2, (max_x - menu_width) // 2)  # Center menu horizontally
                
                # Update matrix rain first for background effect
                self.matrix_rain.update()
                
                # Draw border
                self.draw_border(0, 0, self.height, self.width)
                
                # Draw logo
                self.draw_logo()
                
                # Draw menu
                self.draw_menu()
                
                # Draw footer
                self.draw_footer()
                
                # Update and draw effects
                self.spark_effect.update()
                self.pulse_wave.update()
                self.box_animation.update(menu_start_x)  # Use actual menu x position instead of width//4
                self.decryption_effect.update()
                self.decryption_effect.draw_effects(self.stdscr)
                
                # Refresh screen
                self.stdscr.refresh()
                
                # Adjust input timeout based on remaining frame time
                timeout_ms = int((self.frame_time - self.accumulated_time) * 1000)
                self.stdscr.timeout(max(1, timeout_ms))
                
                # Get input with timeout
                try:
                    key = self.stdscr.getch()
                except curses.error:
                    continue
                
                if key == curses.KEY_MOUSE:
                    try:
                        _, mx, my, _, button_state = curses.getmouse()
                        self.handle_mouse_click(mx, my)
                    except curses.error:
                        continue
                elif key == ord('q'):
                    return None
                elif key == ord('h'):
                    self.show_help_page()
                elif key == curses.KEY_UP and self.current_selection > 0:
                    # Unhighlight current selection before moving
                    menu_start_y = self.get_menu_y()
                    menu_start_x = max(2, (self.width - 60) // 2)
                    y = menu_start_y + self.current_selection * 2
                    self.decryption_effect.unhighlight_position(menu_start_x, y)
                    self.decryption_effect.unhighlight_position(menu_start_x + 20, y)
                    
                    self.current_selection -= 1
                    # Highlight new selection
                    y = menu_start_y + self.current_selection * 2
                    self.decryption_effect.highlight_position(menu_start_x, y)
                    self.decryption_effect.highlight_position(menu_start_x + 20, y)
                    
                    self.box_animation.start_animation(
                        menu_start_y + self.current_selection * 2,
                        len(self.MENU_ITEMS[self.current_selection][0]) + 30
                    )
                elif key == curses.KEY_DOWN and self.current_selection < len(self.MENU_ITEMS) - 1:
                    # Unhighlight current selection before moving
                    menu_start_y = self.get_menu_y()
                    menu_start_x = max(2, (self.width - 60) // 2)
                    y = menu_start_y + self.current_selection * 2
                    self.decryption_effect.unhighlight_position(menu_start_x, y)
                    self.decryption_effect.unhighlight_position(menu_start_x + 20, y)
                    
                    self.current_selection += 1
                    # Highlight new selection
                    y = menu_start_y + self.current_selection * 2
                    self.decryption_effect.highlight_position(menu_start_x, y)
                    self.decryption_effect.highlight_position(menu_start_x + 20, y)
                    
                    self.box_animation.start_animation(
                        menu_start_y + self.current_selection * 2,
                        len(self.MENU_ITEMS[self.current_selection][0]) + 30
                    )
                elif key == ord('\n'):
                    return self.MENU_ITEMS[self.current_selection][0].lower()
                
        except KeyboardInterrupt:
            return None
    
    def __del__(self):
        """Clean up mouse settings on exit."""
        print('\033[?1003l')  # Disable mouse movement events

    def get_menu_y(self):
        """Calculate and return the starting Y position for the menu."""
        max_y, _ = self.stdscr.getmaxyx()
        menu_height = len(self.MENU_ITEMS) * 2 + 4
        return min(14, max_y - menu_height - 4)  # Ensure menu fits vertically

class HelpPage:
    """Enhanced help page with tabs and scrolling support."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_tab = 0
        self.scroll_position = 0
        self.search_mode = False
        self.search_query = ""
        self.search_results = []
        self.search_index = 0
        self.max_scroll = 0
        self.content_width = 0
        self.content_height = 0
        self.selected_item = 0
        
        # Initialize tabs and content from qgit_dict
        try:
            from qgits.qgit_dict import get_all_commands
            commands = get_all_commands()
            
            # Define the tabs structure
            self.TABS = ["Commands", "Options", "Examples"]
            self.CONTENT = {
                "Commands": [],
                "Options": [],
                "Examples": []
            }
            
            # Populate Commands tab
            for cmd, details in commands.items():
                # Add command with description
                self.CONTENT["Commands"].append((
                    f"qgit {cmd}",
                    details['description'],
                    details['usage']
                ))
            
            # Populate Options tab
            for cmd, details in commands.items():
                if details['options']:
                    # Add command header
                    self.CONTENT["Options"].append((
                        f"qgit {cmd}",
                        "",
                        "Available options:"
                    ))
                    # Add each option
                    for opt, opt_desc in details['options'].items():
                        self.CONTENT["Options"].append((
                            "",
                            opt,
                            opt_desc
                        ))
            
            # Populate Examples tab with common usage patterns
            self.CONTENT["Examples"] = [
                ("Quick Commit", "qgit commit", "Stage and commit all changes"),
                ("Custom Message", "qgit commit -m 'Fix bug'", "Commit with specific message"),
                ("Sync Changes", "qgit sync", "Pull and push changes"),
                ("Save All", "qgit save", "Commit and sync in one step"),
                ("New Repository", "qgit first", "Initialize new git repository"),
                ("Security Scan", "qgit benedict", "Scan for sensitive files"),
                ("Quick Undo", "qgit undo", "Safely undo last operation"),
                ("Create Snapshot", "qgit snapshot", "Save current state"),
                ("View Stats", "qgit stats", "Show repository analytics")
            ]
            
        except ImportError:
            # Fallback content if qgit_dict is not available
            self.TABS = ["Basic Help"]
            self.CONTENT = {
                "Basic Help": [
                    ("Error", "Could not load command definitions", 
                     "Please ensure qgits/qgit_dict.py is available")
                ]
            }
    
    def draw_tabs(self, start_y, width):
        """Draw the tab bar with modern styling."""
        tab_width = width // len(self.TABS)
        for i, tab_name in enumerate(self.TABS):
            x = i * tab_width
            is_current = i == self.current_tab
            
            # Draw tab background
            for j in range(tab_width):
                attr = curses.color_pair(1 if is_current else 5)
                attr |= curses.A_BOLD if is_current else curses.A_DIM
                self.stdscr.addstr(start_y, x + j, " ", attr)
            
            # Draw tab content
            tab_text = f" {tab_name} "
            tab_x = x + (tab_width - len(tab_text)) // 2
            attr = curses.color_pair(6 if is_current else 4)
            attr |= curses.A_BOLD if is_current else 0
            self.stdscr.addstr(start_y, tab_x, tab_text, attr)
            
            # Draw separator unless it's the last tab
            if i < len(self.TABS) - 1:
                self.stdscr.addstr(start_y, x + tab_width - 1, "│", curses.color_pair(5))
    
    def draw_search_bar(self, y, width):
        """Draw the search interface."""
        if not self.search_mode:
            return
        
        # Draw search box
        self.stdscr.addstr(y, 0, "╭" + "─" * (width - 2) + "╮", curses.color_pair(5))
        self.stdscr.addstr(y + 1, 0, "│", curses.color_pair(5))
        self.stdscr.addstr(y + 1, 1, f" 🔍 {self.search_query}", curses.color_pair(6) | curses.A_BOLD)
        self.stdscr.addstr(y + 1, width - 1, "│", curses.color_pair(5))
        self.stdscr.addstr(y + 2, 0, "╰" + "─" * (width - 2) + "╯", curses.color_pair(5))
        
        # Draw search status if we have results
        if self.search_results:
            status = f" [{self.search_index + 1}/{len(self.search_results)}] "
            self.stdscr.addstr(y + 1, width - len(status) - 2, status, curses.color_pair(3))
    
    def draw_content(self, start_y, height, width):
        """Draw the content of the current tab with scrolling support."""
        current_tab_name = self.TABS[self.current_tab]
        current_content = self.CONTENT[current_tab_name]
        self.content_height = len(current_content) * 3  # 3 lines per item
        self.content_width = width - 4
        self.max_scroll = max(0, self.content_height - height)
        
        # Draw scrollbar if needed
        if self.max_scroll > 0:
            scrollbar_height = max(3, int(height * (height / self.content_height)))
            scrollbar_pos = int((height - scrollbar_height) * (self.scroll_position / self.max_scroll))
            for i in range(height):
                if scrollbar_pos <= i < scrollbar_pos + scrollbar_height:
                    self.stdscr.addstr(start_y + i, width - 1, "█", curses.color_pair(5))
                else:
                    self.stdscr.addstr(start_y + i, width - 1, "│", curses.color_pair(5) | curses.A_DIM)
        
        # Draw content
        y = start_y
        for i, item in enumerate(current_content):
            item_y = y - self.scroll_position
            if item_y + 2 < start_y:
                y += 3
                continue
            if item_y > start_y + height - 1:
                break
            
            is_selected = i == self.selected_item
            
            if isinstance(item, tuple):
                if len(item) == 3:
                    command, short_desc, long_desc = item
                    if 0 <= item_y < start_y + height:
                        self.stdscr.addstr(item_y, 2, command, 
                                         curses.color_pair(1 if is_selected else 2) | curses.A_BOLD)
                    if 0 <= item_y + 1 < start_y + height:
                        self.stdscr.addstr(item_y + 1, 4, short_desc,
                                         curses.color_pair(3 if is_selected else 4))
                    if 0 <= item_y + 2 < start_y + height:
                        self.stdscr.addstr(item_y + 2, 4, long_desc,
                                         curses.color_pair(5) | (curses.A_BOLD if is_selected else curses.A_DIM))
                else:
                    category, shortcut, desc = item
                    if category:  # Category header
                        if 0 <= item_y < start_y + height:
                            self.stdscr.addstr(item_y, 2, category,
                                             curses.color_pair(6) | curses.A_BOLD)
                    if 0 <= item_y + 1 < start_y + height:
                        if shortcut:
                            self.stdscr.addstr(item_y + (0 if not category else 1), 4,
                                             f"{shortcut.ljust(12)}{desc}",
                                             curses.color_pair(1 if is_selected else 4))
            y += 3
    
    def handle_input(self, key):
        """Handle user input for navigation and search."""
        if key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, button_state = curses.getmouse()
                self.handle_mouse_click(mx, my)
            except curses.error:
                pass
        elif key == ord('q'):
            return None
        elif key == ord('h'):
            self.show_help_page()
        elif key == curses.KEY_UP and self.current_selection > 0:
            # Unhighlight current selection before moving
            menu_start_y = self.get_menu_y()
            menu_start_x = max(2, (self.width - 60) // 2)
            y = menu_start_y + self.current_selection * 2
            self.decryption_effect.unhighlight_position(menu_start_x, y)
            self.decryption_effect.unhighlight_position(menu_start_x + 20, y)
            
            self.current_selection -= 1
            # Highlight new selection
            y = menu_start_y + self.current_selection * 2
            self.decryption_effect.highlight_position(menu_start_x, y)
            self.decryption_effect.highlight_position(menu_start_x + 20, y)
            
            self.box_animation.start_animation(
                menu_start_y + self.current_selection * 2,
                len(self.MENU_ITEMS[self.current_selection][0]) + 30
            )
        elif key == curses.KEY_DOWN and self.current_selection < len(self.MENU_ITEMS) - 1:
            # Unhighlight current selection before moving
            menu_start_y = self.get_menu_y()
            menu_start_x = max(2, (self.width - 60) // 2)
            y = menu_start_y + self.current_selection * 2
            self.decryption_effect.unhighlight_position(menu_start_x, y)
            self.decryption_effect.unhighlight_position(menu_start_x + 20, y)
            
            self.current_selection += 1
            # Highlight new selection
            y = menu_start_y + self.current_selection * 2
            self.decryption_effect.highlight_position(menu_start_x, y)
            self.decryption_effect.highlight_position(menu_start_x + 20, y)
            
            self.box_animation.start_animation(
                menu_start_y + self.current_selection * 2,
                len(self.MENU_ITEMS[self.current_selection][0]) + 30
            )
        elif key == ord('\n'):
            return self.MENU_ITEMS[self.current_selection][0].lower()
        
        return True

    def run(self):
        """Main loop for the help page."""
        while True:
            # Get terminal dimensions
            height, width = self.stdscr.getmaxyx()
            
            # Clear screen
            self.stdscr.clear()
            
            # Draw tabs at the top
            self.draw_tabs(1, width)
            
            # Draw search bar if in search mode
            search_height = 3 if self.search_mode else 0
            self.draw_search_bar(3, width)
            
            # Calculate content area
            content_start_y = 4 + search_height
            content_height = height - content_start_y - 1
            
            # Draw content
            self.draw_content(content_start_y, content_height, width)
            
            # Draw footer
            footer_text = "q: Back   ←/→: Switch tabs   ↑/↓: Navigate   /: Search   Enter: Select"
            footer_x = (width - len(footer_text)) // 2
            self.stdscr.addstr(height - 1, footer_x, footer_text, curses.color_pair(5) | curses.A_DIM)
            
            # Refresh screen
            self.stdscr.refresh()
            
            # Handle input
            try:
                key = self.stdscr.getch()
                if key == ord('q'):
                    break
                elif key == curses.KEY_LEFT and self.current_tab > 0:
                    self.current_tab -= 1
                    self.scroll_position = 0
                elif key == curses.KEY_RIGHT and self.current_tab < len(self.TABS) - 1:
                    self.current_tab += 1
                    self.scroll_position = 0
                elif key == curses.KEY_UP and self.scroll_position > 0:
                    self.scroll_position = max(0, self.scroll_position - 1)
                elif key == curses.KEY_DOWN and self.scroll_position < self.max_scroll:
                    self.scroll_position = min(self.max_scroll, self.scroll_position + 1)
                elif key == ord('/'):
                    self.search_mode = not self.search_mode
                    if not self.search_mode:
                        self.search_query = ""
                        self.search_results = []
                elif self.search_mode:
                    if key == 27:  # ESC
                        self.search_mode = False
                        self.search_query = ""
                        self.search_results = []
                    elif key == curses.KEY_BACKSPACE or key == 127:
                        self.search_query = self.search_query[:-1]
                    elif key == ord('n'):
                        if self.search_results:
                            self.search_index = (self.search_index + 1) % len(self.search_results)
                    elif key == ord('N'):
                        if self.search_results:
                            self.search_index = (self.search_index - 1) % len(self.search_results)
                    elif 32 <= key <= 126:  # Printable characters
                        self.search_query += chr(key)
            except curses.error:
                continue

def run_gui():
    """Run the qgit GUI interface."""
    def _run_landing_page(stdscr):
        landing_page = LandingPage(stdscr)
        return landing_page.run()
    
    return curses.wrapper(_run_landing_page)

def show_help():
    """Show the help page directly."""
    def _run_help_page(stdscr):
        help_page = HelpPage(stdscr)
        help_page.run()
    
    curses.wrapper(_run_help_page)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        show_help()
    else:
        action = run_gui()
        if action:
            print(f"Selected action: {action}")