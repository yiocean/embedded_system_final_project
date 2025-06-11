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
        
        # 設定現代化顏色主題
        self.colors = {
            'bg_primary': '#667eea',      # 主背景色
            'bg_secondary': '#764ba2',    # 次背景色  
            'card_bg': '#ffffff',         # 卡片背景
            'card_shadow': '#00000020',   # 卡片陰影
            'text_primary': '#2c3e50',    # 主要文字
            'text_secondary': '#7f8c8d',  # 次要文字
            'text_light': '#ffffff',      # 亮色文字
            'accent': '#e74c3c',          # 強調色
            'success': '#27ae60',         # 成功色
            'warning': '#f39c12',         # 警告色
            'glass': '#e0e6ed',         # 毛玻璃效果
        }
        
        # 設定漸層背景
        self.setup_background()
        
        # 創建主容器
        self.main_frame = tk.Frame(self.root, bg='#667eea')
        self.main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # 遊戲狀態
        self.song_num = 0
        self.animation_frame = 0
        self.pulse_direction = 1
        
        # 創建UI元素
        self.create_header()
        self.create_pose_section()
        self.create_status_section()
        self.create_info_cards()
        self.create_controls()
        
        # 啟動動畫
        # self.start_animations()
        
        # 啟動遊戲邏輯
        self.start_game_thread()

    def setup_background(self):
        """設定漸層背景"""
        # 創建漸層背景圖片
        self.create_gradient_background()
        
        # 設定背景
        bg_label = tk.Label(self.root)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.configure(image=self.bg_image)
        bg_label.image = self.bg_image

    def create_gradient_background(self):
        """創建漸層背景圖片"""
        width, height = 900, 800
        
        # 創建漸層圖片
        gradient = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(gradient)
        
        # 從上到下的漸層
        for y in range(height):
            ratio = y / height
            # 插值計算顏色
            r1, g1, b1 = int(self.colors['bg_primary'][1:3], 16), int(self.colors['bg_primary'][3:5], 16), int(self.colors['bg_primary'][5:7], 16)
            r2, g2, b2 = int(self.colors['bg_secondary'][1:3], 16), int(self.colors['bg_secondary'][3:5], 16), int(self.colors['bg_secondary'][5:7], 16)
            
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # 添加微妙的紋理
        self.add_texture_overlay(gradient)
        
        self.bg_image = ImageTk.PhotoImage(gradient)

    def add_texture_overlay(self, image):
        """添加紋理覆蓋層"""
        width, height = image.size
        overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 添加一些隨機點作為紋理
        import random
        for _ in range(200):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            alpha = random.randint(10, 30)
            draw.ellipse([x, y, x+size, y+size], fill=(255, 255, 255, alpha))
        
        # 合併紋理
        image.paste(overlay, (0, 0), overlay)

    def create_modern_frame(self, parent, **kwargs):
        """創建現代化框架"""
        frame = tk.Frame(parent, **kwargs)
        frame.configure(
            bg=self.colors['card_bg'],
            relief='flat',
            bd=0,
            highlightthickness=0
        )
        return frame

    def create_glass_frame(self, parent, **kwargs):
        """創建毛玻璃效果框架"""
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
        """創建標題區域"""
        header_frame = self.create_glass_frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # 主標題
        self.label_title = tk.Label(
            header_frame,
            text="DANCE GAME",
            font=("Helvetica", 28, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['glass']
        )
        self.label_title.pack(pady=15)

    def create_pose_section(self):
        """創建姿勢顯示區域"""
        pose_frame = self.create_modern_frame(self.main_frame)
        pose_frame.pack(pady=10)
        
        # 姿勢容器 - 圓角效果
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
        
        # 姿勢圖片
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
        """創建狀態顯示區域"""
        status_frame = self.create_glass_frame(self.main_frame)
        status_frame.pack(fill='x', pady=10)
        
        # 狀態標籤
        self.label_status = tk.Label(
            status_frame,
            text="🎤 Waiting for voice command...",
            font=("Helvetica", 16, "bold"),
            fg=self.colors['text_light'],
            bg=self.colors['glass']
        )
        self.label_status.pack(pady=15)

    def create_info_cards(self):
        """創建資訊卡片"""
        cards_frame = tk.Frame(self.main_frame, bg='#667eea')
        cards_frame.pack(fill='x', pady=20)
        
        # 第一行卡片
        top_row = tk.Frame(cards_frame, bg='#667eea')
        top_row.pack(fill='x', pady=(0, 10))
        
        # 歌曲卡片
        song_card = self.create_info_card(top_row, "CURRENT SONG", "Not selected")
        song_card.pack(side='left', padx=(0, 10), fill='x', expand=True)
        self.label_song = song_card.winfo_children()[1]  # 獲取數值標籤
        
        # 總分卡片
        score_card = self.create_info_card(top_row, "TOTAL SCORE", "0")
        score_card.pack(side='right', padx=(10, 0), fill='x', expand=True)
        self.label_total_score = score_card.winfo_children()[1]
        
        # 第二行卡片 - 詳細分數
        bottom_row = tk.Frame(cards_frame, bg='#667eea')
        bottom_row.pack(fill='x')
        
        # 命中分數卡片
        hit_card = self.create_info_card(bottom_row, "HIT SCORE", "0")
        hit_card.pack(side='left', padx=(0, 5), fill='x', expand=True)
        self.label_hit_score = hit_card.winfo_children()[1]
        
        # 姿勢分數卡片
        pose_card = self.create_info_card(bottom_row, "POSE SCORE", "0")
        pose_card.pack(side='left', padx=5, fill='x', expand=True)
        self.label_pose_score = pose_card.winfo_children()[1]

    def create_info_card(self, parent, title, value):
        """創建資訊卡片"""
        card = self.create_modern_frame(parent)
        card.configure(relief='raised', bd=2)
        
        # 標題
        title_label = tk.Label(
            card,
            text=title,
            font=("Helvetica", 10, "bold"),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg']
        )
        title_label.pack(pady=(10, 5))
        
        # 數值
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
        """創建控制按鈕"""
        controls_frame = tk.Frame(self.main_frame, bg='#667eea')
        controls_frame.pack(pady=20)
        
        # 現代化退出按鈕
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
        
        # 按鈕懸停效果
        self.quit_button.bind("<Enter>", lambda e: self.quit_button.configure(bg='#c0392b'))
        self.quit_button.bind("<Leave>", lambda e: self.quit_button.configure(bg=self.colors['accent']))

    def start_animations(self):
        """啟動動畫效果"""
        self.animate_title()
        self.animate_status()

    def animate_title(self):
        """標題動畫效果"""
        self.animation_frame += 1
        
        # 脈衝效果
        scale = 1.0 + 0.05 * math.sin(self.animation_frame * 0.1)
        size = int(28 * scale)
        
        self.label_title.configure(font=("Helvetica", size, "bold"))
        
        # 繼續動畫
        self.root.after(50, self.animate_title)

    def animate_status(self):
        """狀態指示器動畫"""
        current_text = self.label_status.cget('text')
        
        # 如果狀態包含"Listening"，添加脈衝效果
        if "Listening" in current_text or "Waiting" in current_text:
            # 顏色脈衝
            intensity = int(127 + 128 * math.sin(self.animation_frame * 0.15))
            color = f"#{intensity:02x}ff{intensity:02x}"  # 綠色脈衝
            self.label_status.configure(fg=color)
        
        # 繼續動畫
        self.root.after(100, self.animate_status)

    def quit_game(self):
        """退出遊戲"""
        if messagebox.askyesno("Quit Game", "Are you sure you want to quit?"):
            self.root.quit()

    # 保持原有的更新方法，但增加視覺效果
    def update_status(self, message):
        """更新狀態（增強版）"""
        # 添加emoji和格式化
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
            self.label_status.configure(fg=self.colors['warning'])  # 橘色
        else:
            formatted_message = f"ℹ{message}"
            self.label_status.configure(fg=self.colors['text_light'])
        
        self.label_status.config(text=formatted_message)
        self.root.update_idletasks()
        
        # 狀態更新動畫
        self.flash_status()

    def flash_status(self):
        """狀態更新閃爍效果"""
        original_bg = self.label_status.cget('bg')
        self.label_status.configure(bg=self.colors['text_light'])
        self.root.after(100, lambda: self.label_status.configure(bg=original_bg))

    def update_score(self, score, hit_score, pose_score):
        """更新分數（增強版）"""
        # 更新各個分數顯示
        self.label_total_score.config(text=str(score))
        self.label_hit_score.config(text=str(hit_score))
        self.label_pose_score.config(text=str(pose_score))
        
        # 分數更新動畫
        self.animate_score_update()

    def animate_score_update(self):
        """分數更新動畫"""
        # 總分放大效果
        original_font = self.label_total_score.cget('font')
        self.label_total_score.configure(
            font=("Helvetica", 22, "bold"),
            fg=self.colors['success']
        )
        
        # 恢復原樣
        self.root.after(200, lambda: self.label_total_score.configure(
            font=("Helvetica", 18, "bold"),
            fg=self.colors['text_primary']
        ))

    def update_song(self, song_num):
        """更新歌曲（增強版）"""
        self.song_num = song_num
        self.label_song.config(text=f"Song #{song_num}")
        
        # 歌曲更新動畫
        self.animate_song_update()

    def animate_song_update(self):
        """歌曲更新動畫"""
        self.label_song.configure(fg=self.colors['success'])
        self.root.after(1000, lambda: self.label_song.configure(fg=self.colors['text_primary']))

    def update_pose_image(self, pose_id):
        """更新姿勢圖片（增強版）"""
        try:
            # 載入並處理圖片
            image = Image.open(f"poses/pose{pose_id}.png")
            
            # 創建圓角圖片
            image = self.create_rounded_image(image, (220, 220), 20)
            photo = ImageTk.PhotoImage(image)
            
            self.pose_image.config(image=photo, text="")
            self.pose_image.image = photo
            
            # 姿勢更新動畫
            self.animate_pose_update()
            
        except Exception as e:
            # 如果圖片載入失敗，顯示文字
            self.pose_image.config(
                image="",
                text=f"🎭\nPose #{pose_id}",
                font=("Helvetica", 16, "bold"),
                fg=self.colors['text_primary']
            )

    def create_rounded_image(self, image, size, radius):
        """創建圓角圖片"""
        image = image.resize(size, Image.Resampling.LANCZOS)
        
        # 創建圓角遮罩
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, size[0], size[1]], radius=radius, fill=255)
        
        # 應用遮罩
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(image, (0, 0))
        output.putalpha(mask)
        
        return output

    def animate_pose_update(self):
        """姿勢更新動畫"""
        # 縮放效果
        pose_frame = self.pose_image.master
        original_width = pose_frame.cget('width')
        original_height = pose_frame.cget('height')
        
        # 放大
        pose_frame.configure(width=int(original_width * 1.1), height=int(original_height * 1.1))
        
        # 縮回
        self.root.after(150, lambda: pose_frame.configure(width=original_width, height=original_height))

    # 保持原有的遊戲邏輯方法
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

# 使用新的UI類別
class DanceGameUI(ModernDanceGameUI):
    """保持向後兼容的類別名稱"""
    pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DanceGameUI(root)
    root.mainloop()