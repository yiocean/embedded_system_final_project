import spidev
import time
import json

from rpi_ws281x import PixelStrip, Color
import argparse

# 初始化 SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0 (CE0)
spi.max_speed_hz = 1350000
threshold = 10

LED_COUNT = 64
LED_PIN = 18

LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def colorWipe(strip, color, wait_ms=20):
    """一次擦除顯示像素的顏色。"""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def light_selected_range(strip, segments, color=Color(255, 0, 0), wait_ms=1000):
    """只亮指定範圍內的燈"""

    # start = segment * 7
    # end = start + 6
    # for i in range(strip.numPixels()):
    #     if start <= i < end:
    #         strip.setPixelColor(i, color)
        # else:
        #     strip.setPixelColor(i, 0)
    # segments = 

    expanded = [x for val in segments for x in [val]*7]
    for i in range(56):
        if expanded[i]:
            strip.setPixelColor(i, color)
        else:
            strip.setPixelColor(i, 0)

    strip.show()
    time.sleep(wait_ms / 1000.0)
    for i in range(56):
        strip.setPixelColor(i, 0)

# 讀 MCP3008 資料的函式
def read_channel(channel):
    assert 0 <= channel <= 7, "Channel must be 0-7"
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data
    
def keys_to_binary_list(keys):
    result = [0] * 8
    for key in keys:
        try:
            idx = int(key) - 1  # 把 key 轉成 index (從 0 開始)
            if 0 <= idx < 8:
                result[idx] = 1
        except ValueError:
            pass  # 忽略不是數字的 key
    return result

def detect_press(event):
    pressed_channels = []
    for ch in range(8):
        value = read_channel(ch)
        if value > threshold:
            pressed_channels.append(ch+1)
    if pressed_channels and sorted(pressed_channels) == sorted(event):
        return 1
    else:
        return 0     

def load_game_data(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filename}: {e}")
        return []

def game_loop(game_data):
    score = 0
    start_time = time.time()
    pre_event = []
    pose_flag = 1
    
    try:
        for event in game_data:
            while time.time() - start_time < event['time']:
                if pose_flag and pre_event:
                    result = detect_press(pre_event)
                    if result == 1:
                        score = score + 1
                        pre_event = []
                time.sleep(0.01)
            
            light_num = keys_to_binary_list(event['keys'])
            light_selected_range(strip, light_num, wait_ms = 2000)
            print(f"Current event keys: {event['keys']}")

            if pose_flag:
                result = detect_press(event['keys'])
                if result == 1:
                    score = score + 1
                    pre_event = []
                else:
                    pre_event = event['keys']
                
            # if int(event['time']) % 3 == 0:
                # pose_flag = detect_pose
           
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    
    print(f"Game Over! Your score: {score}")

if __name__ == "__main__":
    # start()
    # song_num = chose_song
    print("start")
    song_num = 0
    game_data = load_game_data(f"{song_num}.json")
    game_loop(game_data)
    colorWipe(strip, Color(0, 0, 0), 100)

