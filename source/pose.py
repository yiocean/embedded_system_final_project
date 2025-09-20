#!/usr/bin/python3

import sys
import cv2 
import time
import math
import numpy as np
import imutils
import subprocess
import mediapipe as mp
import asyncio
from picamera2 import Picamera2

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)
mp_drawing = mp.solutions.drawing_utils 



def detectPose(image, pose):
    output_image = image.copy()
    
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(imageRGB)
    
    height, width, _ = image.shape
    landmarks = []
    
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
                                  connections=mp_pose.POSE_CONNECTIONS)
        
        for landmark in results.pose_landmarks.landmark:
            
            landmarks.append((int(landmark.x * width), int(landmark.y * height),
                                  (landmark.z * width)))
    
    return output_image, landmarks


def calculateAngle(landmark1, landmark2, landmark3):
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3

    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    
    if angle < 0:
        angle += 360

    angle = min(angle, 360 - angle)
    
    return angle


async def check_pose(correct_pose_num, picam2):
    
    #----------------------------------------------------------------------------------------------------------------
    # Calculate the required angles.
    #----------------------------------------------------------------------------------------------------------------
    
    try:
        # subprocess.run("libcamera-jpeg -n --timeout 1 --output image3.jpg", shell=True,
        #        stdout=subprocess.DEVNULL,
        #        stderr=subprocess.DEVNULL) # blocking call # set timeout to 100ms
        # image = cv2.imread("image.jpg")
        await asyncio.sleep(1)
        image = picam2.capture_array()  # 直接取得 numpy 圖像
        pose_image, landmarks = detectPose(image, pose)

        # Get the angle between the left shoulder, elbow and wrist points. 
        left_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])
    
        # Get the angle between the right shoulder, elbow and wrist points. 
        right_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                           landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
                                           landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])   
    
        # Get the angle between the left elbow, shoulder and hip points. 
        left_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                             landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])

        # Get the angle between the right hip, shoulder and elbow points. 
        right_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                              landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])

        # Get the angle between the left hip, knee and ankle points. 
        left_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value])

        # Get the angle between the right hip, knee and ankle points 
        right_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value])
        if correct_pose_num == 0:
            return check_pose_0(left_elbow_angle,right_elbow_angle,left_shoulder_angle,right_shoulder_angle)
        elif correct_pose_num == 1:
            return check_pose_1(left_elbow_angle,right_elbow_angle,left_shoulder_angle,right_shoulder_angle)
        elif correct_pose_num == 2:
            return check_pose_2(left_elbow_angle,right_elbow_angle,left_shoulder_angle,right_shoulder_angle)
        elif correct_pose_num == 3:
            return check_pose_3(left_elbow_angle,right_elbow_angle,left_shoulder_angle,right_shoulder_angle)
        elif correct_pose_num == 4:
            return check_pose_4(left_elbow_angle,right_elbow_angle,left_shoulder_angle,right_shoulder_angle)
        else:
            print(f'Invalid pose number: {correct_pose_num}')
            return False
    
    except Exception as e:
        print(f'Check pose failed: {e}')
    #     output_image = []

    
    # return output_image, label
elbow_angle_threshold_left = 150
elbow_angle_threshold_right = 210
shoulder_angle_threshold_left = 60
shoulder_angle_threshold_right = 120
ninety_left = 60
ninety_right = 120
hundred_eighty_left = 150
hundred_eighty_right = 210
def check_pose_0(left_elbow_angle, right_elbow_angle, left_shoulder_angle, right_shoulder_angle):
    print(f'left_elbow_angle: {left_elbow_angle}, right_elbow_angle: {right_elbow_angle}, left_shoulder_angle: {left_shoulder_angle}, right_shoulder_angle: {right_shoulder_angle}')
    return hundred_eighty_left < left_elbow_angle < hundred_eighty_right and hundred_eighty_left < right_elbow_angle < hundred_eighty_right and ninety_left < left_shoulder_angle < ninety_right and ninety_left < right_shoulder_angle < ninety_right
def check_pose_1(left_elbow_angle, right_elbow_angle, left_shoulder_angle, right_shoulder_angle):
    print(f'left_elbow_angle: {left_elbow_angle}, right_elbow_angle: {right_elbow_angle}, left_shoulder_angle: {left_shoulder_angle}, right_shoulder_angle: {right_shoulder_angle}')
    return hundred_eighty_left < left_elbow_angle < hundred_eighty_right and ninety_left < right_elbow_angle < ninety_right and ninety_left < left_shoulder_angle < ninety_right and ninety_left < right_shoulder_angle < ninety_right
def check_pose_2(left_elbow_angle, right_elbow_angle, left_shoulder_angle, right_shoulder_angle):
    print(f'left_elbow_angle: {left_elbow_angle}, right_elbow_angle: {right_elbow_angle}, left_shoulder_angle: {left_shoulder_angle}, right_shoulder_angle: {right_shoulder_angle}')
    return ninety_left < left_elbow_angle < ninety_right and hundred_eighty_left < right_elbow_angle < hundred_eighty_right and ninety_left < left_shoulder_angle < ninety_right and ninety_left < right_shoulder_angle < ninety_right
def check_pose_3(left_elbow_angle, right_elbow_angle, left_shoulder_angle, right_shoulder_angle):
    print(f'left_elbow_angle: {left_elbow_angle}, right_elbow_angle: {right_elbow_angle}, left_shoulder_angle: {left_shoulder_angle}, right_shoulder_angle: {right_shoulder_angle}')
    return ninety_left < left_elbow_angle < ninety_right and ninety_left < right_elbow_angle < ninety_right and ninety_left < left_shoulder_angle < ninety_right and ninety_left < right_shoulder_angle < ninety_right
def check_pose_4(left_elbow_angle, right_elbow_angle, left_shoulder_angle, right_shoulder_angle):
    print(f'left_elbow_angle: {left_elbow_angle}, right_elbow_angle: {right_elbow_angle}, left_shoulder_angle: {left_shoulder_angle}, right_shoulder_angle: {right_shoulder_angle}')
    return hundred_eighty_left < left_elbow_angle < hundred_eighty_right and hundred_eighty_left < right_elbow_angle < hundred_eighty_right and hundred_eighty_left < left_shoulder_angle < hundred_eighty_right and hundred_eighty_left < right_shoulder_angle < hundred_eighty_right


def main():
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={"size": (3280, 2464)}))
    picam2.start()
    time.sleep(1)
    poses = [0,1,2,3,4]
    # music = "song0.mp3"
    # subprocess.Popen(["mpg123", music])
    # while True:
    for i in poses:
        try:
            pose_num = i
            print(f'Pose {i}!!')
            time.sleep(2)
            result = check_pose(pose_num, picam2)
            if result:
                print(f'Successfully perform pose {pose_num}')
            else:
                print(f'Failed to perform pose {pose_num}')

        except KeyboardInterrupt:
            print("Receiving Ctrl+C, terminating...")
            break
        except Exception as e:
            print(e)
            break

if __name__ == "__main__":
    main()