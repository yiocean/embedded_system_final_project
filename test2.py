import spidev
import time
import json
import asyncio
from rpi_ws281x import PixelStrip, Color
import argparse
# from microphone import check_start, choose_song
import subprocess
from pose import check_pose
from picamera2 import Picamera2

#pose
import sys
import cv2 
import time
import math
import numpy as np
import imutils
import subprocess
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)
mp_drawing = mp.solutions.drawing_utils 

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

import speech_recognition as sr
import subprocess
from ctypes import *
from contextlib import contextmanager
import os
import sys

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

# to hide stderr caused by pyaudio
def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

# to hide stderr caused by pyaudio
@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

# to hide stderr caused by pyaudio
@contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

#obtain audio from the microphone
r=sr.Recognizer() 

def check_start():
    with suppress_stderr(), noalsaerr():
        with sr.Microphone() as source:
            print("Please wait. Calibrating microphone...") 
            #listen for 1 seconds and create the ambient noise energy level 
            r.adjust_for_ambient_noise(source, duration=1) 
            print('Say "Start" to start!')
            audio=r.listen(source)
            try:
                text = r.recognize_google(audio)
                text = text.lower()
                if 'start' or 'hi' in text:
                    print(f'You say "{text}"!')
                    return True
                else:
                    return False
            except:
                print("Failed to check start.")

def choose_song():
    with suppress_stderr(), noalsaerr():
        with sr.Microphone() as source:
            print("Please wait. Calibrating microphone...") 
            #listen for 1 seconds and create the ambient noise energy level 
            r.adjust_for_ambient_noise(source, duration=1) 
            print('Please choose a song (say "I want number 1/2/3"):')
            audio=r.listen(source)

            # recognize speech using Google Speech Recognition 
            try:
                text = r.recognize_google(audio)
                text = text.lower()
                if 'one' in text:
                    print(f'You say "{text}"!')
                    return 1
                elif 'two' in text:
                    print(f'You say "{text}"!')
                    return 2
                elif 'three' in text:
                    print(f'You say "{text}"!')
                    return 3
                else:
                    print(f'You say "{text}", please try again.')
                    return -1
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                return -2
            except sr.RequestError as e:
                print("No response from Google Speech Recognition service: {0}".format(e))
                return -3

def colorWipe(strip, color, wait_ms=20):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

async def light_selected_range(strip, segments, color=Color(255, 0, 0), wait_ms=1000):
    expanded = [x for val in segments for x in [val]*7]
    for i in range(56):
        if expanded[i]:
            strip.setPixelColor(i, color)
        else:
            strip.setPixelColor(i, 0)

    strip.show()
    await asyncio.sleep(wait_ms / 1000)
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
            print(f"channel {ch+1} hit!!, event:{event}")
    if pressed_channels and all(channel in pressed_channels for channel in event):
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

def detect_pose(pose_num):
    result = check_pose(pose_num)
    if result:
        print(f'Successfully perform pose {pose_num}')
    else:
        print(f'Failed to perform pose {pose_num}')
    return result

async def game_loop(game_data, song_num):
    score = 0
    pre_event = []
    pose_flag = 1
    poses = [0,1,2,3,4]
    pose_idx = 0
    hit_score = 0
    pose_score = 0

    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))
    picam2.start()
    time.sleep(1)  # 等相機 warm up（可選）
    subprocess.Popen(f"sudo aplay -D hw:3,0 song{song_num}.wav", shell=True)
    
    start_time = time.time()
    
    try:
        for event in game_data:
            # Check if the pose is correct
            print(f"Current pose index: {pose_idx}")
            # time.sleep(1)  # Wait for 2 seconds before checking the pose
            pose_task = asyncio.create_task(check_pose(poses[pose_idx], picam2))
            # pose_flag = check_pose(poses[pose_idx])
            
            while time.time() - start_time < event['time']:
                if pre_event:
                    result = detect_press(pre_event)
                    if result == 1:
                        print("hit result!!!!!")
                        hit_score += 1
                        pre_event = []
                        if pose_flag == 1:
                            score += 1
                time.sleep(0.1)
            
            light_num = keys_to_binary_list(event['keys'])
            light_task = asyncio.create_task(light_selected_range(strip, light_num, wait_ms = 1500))
            print(f"Current event keys: {event['keys']}")

            result = detect_press(event['keys'])
            if result == 1:
                print("hit result!")
                hit_score += 1
                pre_event = []
                if pose_flag == 1:
                    score += 1
            else:
                pre_event = event['keys']

            await light_task
            pose_flag = await pose_task  # Wait for the pose check to complete
            if pose_flag:
                print(f"Pose {poses[pose_idx]} detected successfully!")
                pose_score += 1
            else:
                print(f"Pose {poses[pose_idx]} failed, try again.")
            pose_idx = (pose_idx + 1) % len(poses)  # Cycle through poses     
            if int(event['time']) % 3 == 0:
                pose_flag = detect_pose
           
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    
    print(f"Game Over! Your score: {score}")
    print(f"hit_score: {hit_score}")
    print(f"pose_score: {pose_score}")

if __name__ == "__main__":
    start_flag = False
    while not start_flag:
        start_flag = check_start()
    
    song_num = 0
    while song_num <= 0:
        song_num = choose_song()
    if song_num > 0: # choose song successfully
        # subprocess.Popen(f"sudo aplay -D hw:3,0 song{song_num}.wav", shell=True)
    # start()
    # song_num = chose_song
        print("start")
        game_data = load_game_data(f"0.json") # modified
        asyncio.run(game_loop(game_data, song_num))
        colorWipe(strip, Color(0, 0, 0), 100)
