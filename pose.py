#!/usr/bin/python3

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


def check_pose(correct_pose_num):
    
    #----------------------------------------------------------------------------------------------------------------
    # Calculate the required angles.
    #----------------------------------------------------------------------------------------------------------------
    
    try:
        subprocess.run("libcamera-still -n --timeout 100 -o image.jpg", shell=True,
               stdout=subprocess.DEVNULL,
               stderr=subprocess.DEVNULL) # blocking call # set timeout to 100ms
        image = cv2.imread("image.jpg")
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

def check_pose_0(left_elbow_angle, right_elbow_angle, left_shoulder_angle, right_shoulder_angle):
    return 165 < left_elbow_angle < 195 and 165 < right_elbow_angle < 195 and 80 < left_shoulder_angle < 110 and 80 < right_shoulder_angle < 110
def check_pose_1(left_elbow_angle, right_elbow_angle, left_shoulder_angle, right_shoulder_angle):
    print(f'right_elbow_angle: {right_elbow_angle}')
    return 165 < left_elbow_angle < 195 and 60 < right_elbow_angle < 120 and 80 < left_shoulder_angle < 110 and 80 < right_shoulder_angle < 110
def check_pose_2(left_elbow_angle, right_elbow_angle, left_shoulder_angle, right_shoulder_angle):
    print(f'left_elbow_angle: {left_elbow_angle}')
    return 60 < left_elbow_angle < 120 and 165 < right_elbow_angle < 195 and 80 < left_shoulder_angle < 110 and 80 < right_shoulder_angle < 110
def check_pose_3(left_elbow_angle, right_elbow_angle, left_shoulder_angle, right_shoulder_angle):
    print(f'right_elbow_angle: {right_elbow_angle}, left_elbow_angle: {left_elbow_angle}')
    return 60 < left_elbow_angle < 120 and 60 < right_elbow_angle < 120 and 80 < left_shoulder_angle < 110 and 80 < right_shoulder_angle < 110
def check_pose_4(left_elbow_angle, right_elbow_angle, left_shoulder_angle, right_shoulder_angle):
    print(f'right_shoulder_angle: {right_shoulder_angle}, left_shoulder_angle: {left_shoulder_angle}')
    return 165 < left_elbow_angle < 195 and 165 < right_elbow_angle < 195 and 165 < left_shoulder_angle < 195 and 165 < right_shoulder_angle < 195


def main():
    poses = [0,1,2,3,4]
    # music = "song0.mp3"
    # subprocess.Popen(["mpg123", music])
    # while True:
    for i in poses:
        try:
            pose_num = i
            print(f'Pose {i}!!')
            time.sleep(2)
            result = check_pose(pose_num)
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