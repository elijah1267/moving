import cv2
import numpy as np
import time
import subprocess
import pigpio

pi = pigpio.pi()
previous_angle = 1500
pi.set_servo_pulsewidth(18,previous_angle)

start_time = int(time.time())
face_detected = False
state = 0

off_time = 0

prev_frame_size = -1  # 이전 프레임 크기 초기화
sound = 5

# ADB 명령 실행 함수
def run_adb_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing ADB command: {e}")
        
# 볼륨 제어 함수
def remote_volume():
    
    global prev_frame_size
    global sound
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        if w < 100 :
            goal = 10    
            gap = goal - sound
            if gap < 0 :
                gap = gap * (-1)
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_DOWN")
            elif gap > 0 :
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_UP")
            sound = 10
        elif 100 <= w < 200 :
            goal = 9        
            gap = goal - sound
            if gap < 0 :
                gap = gap * (-1)
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_DOWN")
            elif gap > 0 :
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_UP")
            sound = 9
        elif 200 <= w < 300 :
            goal = 8
            gap = goal - sound
            if gap < 0 :
                gap = gap * (-1)
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_DOWN")
                    
            elif gap > 0 :
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_UP")
            sound = 8        
            
        elif 300 <= w < 400 :
            goal = 7
            gap = goal - sound
            if gap < 0 :
                gap = gap * (-1)
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_DOWN")
                    
            elif gap > 0 :
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_UP")
            sound = 7
        elif 400 <= w < 500 :
            goal = 6
            gap = goal - sound
            if gap < 0 :
                gap = gap * (-1)
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_DOWN")
                    
            elif gap > 0 :
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_UP")
            sound = 6
        elif 500 < w :
            goal = 5
            gap = goal - sound
            if gap < 0 :
                gap = gap * (-1)
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_DOWN")
                    
            elif gap > 0 :
                for i in range(gap) :
                    run_adb_command("adb shell input keyevent KEYCODE_VOLUME_UP")
            sound = 5

        
# stap&play 함수 
def stop_play():
    
    global state
    global start_time
    global off_time
    
    current_time = int(time.time())

    if len(faces) > 0:
        # 얼굴이 감지된 경우  
        start_time = current_time 
        if(state == 1 and (current_time - off_time) >= 1):
            print("얼굴이 감지되었습니다. 영상을 재생합니다.")
            run_adb_command("adb shell input keyevent KEYCODE_SPACE")
            state = 0
            
    else:
        # 얼굴이 감지되지 않은 경우
        elapsed_time = current_time - start_time

        # 5초 이상 얼굴이 감지되지 않았을 때 ADB 커맨드 실행
        if elapsed_time >= 5 and state == 0:
            print("얼굴이 5초 이상 감지되지 않았습니다. 영상을 정지합니다.")
            run_adb_command("adb shell input keyevent KEYCODE_SPACE")
            state = 1
            off_time = current_time

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)


# face tracking 함수
def face_tracking():
    
    global previous_angle
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        if x + w//2 < 550 :
            current_angle = previous_angle + 20
            pi.set_servo_pulsewidth(18,previous_angle) 
            previous_angle = current_angle
            time.sleep(0.3)
        elif x + w//2 > 730 :
            current_angle = previous_angle - 20
            pi.set_servo_pulsewidth(18,previous_angle) 
            previous_angle = current_angle
            time.sleep(0.3)

# main code

pipeline = "libcamerasrc ! video/x-raw, width=1280, height=720, framerate=15/1 ! videoconvert ! videoscale ! video/x-raw, width=1280, height=720 ! appsink"
capture = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
face_cascade = cv2.CascadeClassifier('/home/pi/opencv/data/haarcascades/haarcascade_frontalface_default.xml')

while True :
    ret, frame = capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    face_tracking()
    remote_volume()
    stop_play()

    cv2.imshow('Face Detection', frame)
                
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()             
cv2.destroyAllWindows()         
pi.stop()
