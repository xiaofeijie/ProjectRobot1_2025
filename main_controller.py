# main_controller.py
import face_recognition
import cv2
import serial
import time
import os
import hashlib # 引入哈希库，用于保护数据 

# --- 1. 初始化 ---
# 连接到Micro:bit（请根据你的设备管理器中的端口号修改 'COM3'）
# Windows上可能是 'COM3', 'COM4'等
# Mac上可能是 '/dev/tty.usbmodemXXXX'
try:
    ser = serial.Serial('COM3', 9600)
    print("Micro:bit connected.")
except:
    print("Micro:bit not found. Please check the port.")
    exit()

# 加载已知人脸并进行编码
known_face_encodings = []
known_face_names = []
faces_dir = "known_faces"

print("Loading known faces...")
for filename in os.listdir(faces_dir):
    if filename.endswith((".jpg", ".png")):
        # 加载图片
        image_path = os.path.join(faces_dir, filename)
        image = face_recognition.load_image_file(image_path)
        
        # 获取人脸编码
        # 假设每张照片里只有一张脸
        encoding = face_recognition.face_encodings(image)[0]
        
        # 添加编码和名字（去掉文件扩展名）
        known_face_encodings.append(encoding)
        known_face_names.append(os.path.splitext(filename)[0])

print(f"Loaded {len(known_face_names)} faces: {known_face_names}")

# --- 2. 实现人脸数据保护（哈希）---
# 这是一个演示，展示如何对人脸图片文件进行哈希处理 
def hash_face_image(image_path):
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
            sha256_hash = hashlib.sha256(image_data).hexdigest()
            return sha256_hash
    except:
        return None

print("\n--- Hashing Face Data Demo ---")
for filename in os.listdir(faces_dir):
    if filename.endswith((".jpg", ".png")):
        image_path = os.path.join(faces_dir, filename)
        hashed_value = hash_face_image(image_path)
        print(f"Hash for {filename}: {hashed_value}")
print("--- End of Hashing Demo ---\n")


# --- 3. 主循环：识别人脸并发送指令 ---
# 打开电脑的默认摄像头
video_capture = cv2.VideoCapture(0)

while True:
    # 从摄像头捕获一帧视频
    ret, frame = video_capture.read()
    if not ret:
        break

    # 查找当前帧中的所有人脸
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # 默认为未知
    found_known_face = False

    # 遍历找到的每张脸
    for face_encoding in face_encodings:
        # 与已知人脸进行匹配
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            found_known_face = True
            
            # 根据识别到的名字发送指令 
            if name == "zhang_san":
                ser.write(b'FACE1\n') # 发送指令 'FACE1'
            elif name == "li_si":
                ser.write(b'FACE2\n') # 发送指令 'FACE2'
            
            print(f"Found {name}, sending command.")
            break # 找到一个匹配的就够了
            
    if not found_known_face and len(face_encodings) > 0:
        ser.write(b'UNKNOWN\n') # 发送指令 'UNKNOWN'
        print("Found unknown face, sending command.")

    # 在电脑屏幕上显示结果（可选，但有助于调试）
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
    cv2.imshow('Video', frame)

    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    time.sleep(1) # 每隔1秒识别一次，避免指令发送过于频繁

# --- 4. 清理 ---
video_capture.release()
cv2.destroyAllWindows()
ser.close()
print("Program finished.")

