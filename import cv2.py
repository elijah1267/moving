import cv2
import subprocess
import time

# ADB 명령 실행 함수
def run_adb_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing ADB command: {e}")


# OpenCV 카메라 초기화
cap = cv2.VideoCapture(0) 

# 얼굴 감지기 초기화 (OpenCV의 얼굴 감지기 사용)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 타이머 초기화
start_time = int(time.time())
face_detected = False

state = 0

while True:
    # 현재 시간 계산
    current_time = int(time.time())
    # 카메라에서 프레임 읽기
    ret, frame = cap.read()

    # 얼굴 감지
    faces = face_cascade.detectMultiScale(frame, scaleFactor=1.3, minNeighbors=5)

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

    # 화면에 얼굴 박스 그리기 
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # 화면에 프레임 표시
    cv2.imshow("Face Detection", frame)

    if cv2.waitKey(2) & 0xFF == ord('q'):
        break

# 카메라 해제 및 OpenCV 윈도우 닫기
cap.release()
cv2.destroyAllWindows()