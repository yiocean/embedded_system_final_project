import tkinter as tk
from tkinter import messagebox
from threading import Thread
import asyncio
from test2 import check_start, choose_song, load_game_data, game_loop
import time
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import subprocess
import math

class ModernDanceGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Dance Game")
        self.root.geometry("900x800")
        self.root.resizable(False, False)
        
        """Set modern color theme"""
        self.colors = {
            'bg_primary': '#667eea',      # Primary background
            'bg_secondary': '#764ba2',    # Secondary background  
            'card_bg': '#ffffff',         # Card background
            'card_shadow': '#00000020',   # Card shadow
            'text_primary': '#2c3e50',    # Primary text
            'text_secondary': '#7f8c8d',  # Secondary text
            'text_light': '#ffffff',      # Light text
            'accent': '#e74c3c',          # Accent color
            'success': '#27ae60',         # Success color
            'warning': '#f39c12',         # Warning color
            'glass': '#e0e6ed',         # Frosted glass effect
        }
        
        self.setup_background()
        
        self.main_frame = tk.Frame(self.root, bg='#667eea')
        self.main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        """Game state"""
        self.song_num = 0
        self.animation_frame = 0
        self.pulse_direction = 1
        
        """Create UI elements"""
        self.create_header()
        self.create_pose_section()
        self.create_status_section()
        self.create_info_cards()
        self.create_controls()
        
        """Start animations and game logic"""
        # self.start_animations()
        
        """Start game logic"""
        self.start_game_thread()

    def setup_background(self):
        self.create_gradient_background()
        
        bg_label = tk.Label(self.root)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.configure(image=self.bg_image)
        bg_label.image = self.bg_image

    def create_gradient_background(self):
        width, height = 900, 800
        
        gradient = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(gradient)
        
        for y in range(height):
            ratio = y / height
            # Interpolate colors
            r1, g1, b1 = int(self.colors['bg_primary'][1:3], 16), int(self.colors['bg_primary'][3:5], 16), int(self.colors['bg_primary'][5:7], 16)
            r2, g2, b2 = int(self.colors['bg_secondary'][1:3], 16), int(self.colors['bg_secondary'][3:5], 16), int(self.colors['bg_secondary'][5:7], 16)
            
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add subtle texture
        self.add_texture_overlay(gradient)
        
        self.bg_image = ImageTk.PhotoImage(gradient)

    def add_texture_overlay(self, image):
        """Add texture overlay"""
        width, height = image.size
        overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Add random dots as texture
        import random
        for _ in range(200):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            alpha = random.randint(10, 30)
            draw.ellipse([x, y, x+size, y+size], fill=(255, 255, 255, alpha))
        
        # Merge texture
        image.paste(overlay, (0, 0), overlay)

    def create_modern_frame(self, parent, **kwargs):
        """Create modern frame"""
        frame = tk.Frame(parent, **kwargs)
        frame.configure(
            bg=self.colors['card_bg'],
            relief='flat',
            bd=0,
            highlightthickness=0
        )
        return frame

    def create_glass_frame(self, parent, **kwargs):
        """Create frosted glass effect frame"""
        frame = tk.Frame(parent, **kwargs)
        frame.configure(
            bg=self.colors['glass'],
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightcolor=self.colors['glass'],
            highlightbackground=self.colors['glass']
        )
        return frame

    def create_header(self):
        """Create title area"""
        header_frame = self.create_glass_frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Main title
        self.label_title = tk.Label(
            header_frame,
            text="DANCE GAME",
            font=("Helvetica", 28, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['glass']
        )
        self.label_title.pack(pady=15)

    def create_pose_section(self):
        """Create pose display area"""
        pose_frame = self.create_modern_frame(self.main_frame)
        pose_frame.pack(pady=10)
        
        # Pose container - rounded corners effect
        pose_container = tk.Frame(
            pose_frame,
            bg=self.colors['card_bg'],
            relief='flat',
            bd=0,
            width=250,
            height=250
        )
        pose_container.pack(padx=20, pady=20)
        pose_container.pack_propagate(False)
        
        # Pose image
        self.pose_image = tk.Label(
            pose_container,
            bg=self.colors['card_bg'],
            text="🎭\nPose will appear here",
            font=("Helvetica", 14),
            fg=self.colors['text_secondary'],
            justify='center'
        )
        self.pose_image.pack(expand=True)

    def create_status_section(self):
        """Create status display area"""
        status_frame = self.create_glass_frame(self.main_frame)
        status_frame.pack(fill='x', pady=10)
        
        # Status label
        self.label_status = tk.Label(
            status_frame,
            text="🎤 Waiting for voice command...",
            font=("Helvetica", 16, "bold"),
            fg=self.colors['text_light'],
            bg=self.colors['glass']
        )
        self.label_status.pack(pady=15)

    def create_info_cards(self):
        """Create info cards"""
        cards_frame = tk.Frame(self.main_frame, bg='#667eea')
        cards_frame.pack(fill='x', pady=20)
        
        # First row of cards
        top_row = tk.Frame(cards_frame, bg='#667eea')
        top_row.pack(fill='x', pady=(0, 10))
        
        # Song card
        song_card = self.create_info_card(top_row, "CURRENT SONG", "Not selected")
        song_card.pack(side='left', padx=(0, 10), fill='x', expand=True)
        self.label_song = song_card.winfo_children()[1]  # Get value label
        
        # Total score card
        score_card = self.create_info_card(top_row, "TOTAL SCORE", "0")
        score_card.pack(side='right', padx=(10, 0), fill='x', expand=True)
        self.label_total_score = score_card.winfo_children()[1]
        
        # Second row of cards - Detailed scores
        bottom_row = tk.Frame(cards_frame, bg='#667eea')
        bottom_row.pack(fill='x')
        
        # Hit score card
        hit_card = self.create_info_card(bottom_row, "HIT SCORE", "0")
        hit_card.pack(side='left', padx=(0, 5), fill='x', expand=True)
        self.label_hit_score = hit_card.winfo_children()[1]
        
        # Pose score card
        pose_card = self.create_info_card(bottom_row, "POSE SCORE", "0")
        pose_card.pack(side='left', padx=5, fill='x', expand=True)
        self.label_pose_score = pose_card.winfo_children()[1]

    def create_info_card(self, parent, title, value):
        """Create info card"""
        card = self.create_modern_frame(parent)
        card.configure(relief='raised', bd=2)
        
        # Title
        title_label = tk.Label(
            card,
            text=title,
            font=("Helvetica", 10, "bold"),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg']
        )
        title_label.pack(pady=(10, 5))
        
        # Value
        value_label = tk.Label(
            card,
            text=value,
            font=("Helvetica", 18, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['card_bg']
        )
        value_label.pack(pady=(0, 10))
        
        return card

    def create_controls(self):
        """Create control buttons"""
        controls_frame = tk.Frame(self.main_frame, bg='#667eea')
        controls_frame.pack(pady=20)
        
        # Modern quit button
        self.quit_button = tk.Button(
            controls_frame,
            text="QUIT GAME",
            font=("Helvetica", 12, "bold"),
            fg=self.colors['text_light'],
            bg=self.colors['accent'],
            activeforeground=self.colors['text_light'],
            activebackground='#c0392b',
            relief='flat',
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2',
            command=self.quit_game
        )
        self.quit_button.pack()
        
        # Button hover effect
        self.quit_button.bind("<Enter>", lambda e: self.quit_button.configure(bg='#c0392b'))
        self.quit_button.bind("<Leave>", lambda e: self.quit_button.configure(bg=self.colors['accent']))

    def start_animations(self):
        """Start animation effects"""
        self.animate_title()
        self.animate_status()

    def animate_title(self):
        """Title animation effect"""
        self.animation_frame += 1
        
        # Pulse effect
        scale = 1.0 + 0.05 * math.sin(self.animation_frame * 0.1)
        size = int(28 * scale)
        
        self.label_title.configure(font=("Helvetica", size, "bold"))
        
        # Continue animation
        self.root.after(50, self.animate_title)

    def animate_status(self):
        """Status indicator animation"""
        current_text = self.label_status.cget('text')
        
        if "Listening" in current_text or "Waiting" in current_text:
            # Color pulse
            intensity = int(127 + 128 * math.sin(self.animation_frame * 0.15))
            color = f"#{intensity:02x}ff{intensity:02x}"
            self.label_status.configure(fg=color)
        
        # Continue animation
        self.root.after(100, self.animate_status)

    def quit_game(self):
        """Quit game"""
        if messagebox.askyesno("Quit Game", "Are you sure you want to quit?"):
            self.root.quit()

    # Keep original update methods but enhance visual effects
    def update_status(self, message):
        """Update status (enhanced version)"""
        if "Listening" in message:
            formatted_message = f"{message}"
            self.label_status.configure(fg=self.colors['success'])
        elif "recognized" in message or "Voice" in message:
            formatted_message = f"✅ {message}"
            self.label_status.configure(fg=self.colors['warning'])
        elif "Starting" in message:
            formatted_message = f"{message}"
            self.label_status.configure(fg=self.colors['accent'])
        elif "finished" in message:
            formatted_message = f"{message}"
            self.label_status.configure(fg=self.colors['success'])
        elif "start over" in message.lower():
            formatted_message = f"🔁 {message}"
            self.label_status.configure(fg=self.colors['warning'])
        else:
            formatted_message = f"ℹ{message}"
            self.label_status.configure(fg=self.colors['text_light'])
        
        self.label_status.config(text=formatted_message)
        self.root.update_idletasks()
        
        self.flash_status()

    def flash_status(self):
        """Status update flash effect"""
        original_bg = self.label_status.cget('bg')
        self.label_status.configure(bg=self.colors['text_light'])
        self.root.after(100, lambda: self.label_status.configure(bg=original_bg))

    def update_score(self, score, hit_score, pose_score):
        """Update score (enhanced version)"""
        self.label_total_score.config(text=str(score))
        self.label_hit_score.config(text=str(hit_score))
        self.label_pose_score.config(text=str(pose_score))
        
        self.animate_score_update()

    def animate_score_update(self):
        """Score update animation"""
        original_font = self.label_total_score.cget('font')
        self.label_total_score.configure(
            font=("Helvetica", 22, "bold"),
            fg=self.colors['success']
        )
        
        self.root.after(200, lambda: self.label_total_score.configure(
            font=("Helvetica", 18, "bold"),
            fg=self.colors['text_primary']
        ))

    def update_song(self, song_num):
        """Update song (enhanced version)"""
        self.song_num = song_num
        self.label_song.config(text=f"Song #{song_num}")
        
        # 歌曲更新動畫
        self.animate_song_update()

    def animate_song_update(self):
        """Song update animation"""
        self.label_song.configure(fg=self.colors['success'])
        self.root.after(1000, lambda: self.label_song.configure(fg=self.colors['text_primary']))

    def update_pose_image(self, pose_id):
        """Update pose image (enhanced version)"""
        try:
            # Load and process image
            image = Image.open(f"poses/pose{pose_id}.png")
            
            image = self.create_rounded_image(image, (220, 220), 20)
            photo = ImageTk.PhotoImage(image)
            
            self.pose_image.config(image=photo, text="")
            self.pose_image.image = photo
            
            self.animate_pose_update()
            
        except Exception as e:
            # If image loading fails, show text
            self.pose_image.config(
                image="",
                text=f"🎭\nPose #{pose_id}",
                font=("Helvetica", 16, "bold"),
                fg=self.colors['text_primary']
            )

    def create_rounded_image(self, image, size, radius):
        """Create rounded image"""
        image = image.resize(size, Image.Resampling.LANCZOS)
        
        # Create rounded mask
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, size[0], size[1]], radius=radius, fill=255)
        
        # Apply mask
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(image, (0, 0))
        output.putalpha(mask)
        
        return output

    def animate_pose_update(self):
        pose_frame = self.pose_image.master
        original_width = pose_frame.cget('width')
        original_height = pose_frame.cget('height')
        
        pose_frame.configure(width=int(original_width * 1.1), height=int(original_height * 1.1))
        
        self.root.after(150, lambda: pose_frame.configure(width=original_width, height=original_height))

    def start_game_thread(self):
        thread = Thread(target=self.start_game)
        thread.daemon = True
        thread.start()

    def start_game(self):
        self.update_status("Say 'Please start over' to start...")
        while not check_start():
            time.sleep(0.5)
        self.update_status("Voice recognized! Say 'I want song number 1/2/3, please' to select song.")

        self.song_num = 0
        while self.song_num <= 0:
            self.song_num = choose_song()

        self.update_song(self.song_num)
        self.update_status("Starting game...")
        game_data = load_game_data(f"{self.song_num}.json")

        # Start game loop
        asyncio.run(game_loop(game_data, self.song_num, 
                             update_score_callback=self.update_score, 
                             update_pose_image_callback=self.update_pose_image))

        self.update_status("Game finished.")

class DanceGameUI(ModernDanceGameUI):
    """Keep backward compatibility class name"""
    pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DanceGameUI(root)
    root.mainloop()