import serial
import csv
import os
import sys
import threading
import time
import webbrowser
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from serial.tools import list_ports
import pandas as pd
import numpy as np

# --- 설정 ---
SERIAL_PORT = None
BAUD_RATE = 9600
CSV_FILE = 'sensor_dataset.csv'

# Flask 및 SocketIO 초기화
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# 전역 변수
ser = None
serial_thread = None
thread_stop_event = threading.Event()
latest_sensor_data = {}  # 실시간 센서 데이터를 저장할 변수
similarity_thread = None
similarity_thread_stop_event = threading.Event()

# --- 실시간 유사 태그 찾기 스레드 ---
def find_similar_tags_continuously():
    print("실시간 유사 태그 찾기 스레드 시작...")
    while not similarity_thread_stop_event.is_set():
        if latest_sensor_data:
            try:
                new_sensor_data = [float(x) for x in latest_sensor_data.values()]
                normalized_new_sensor = normalize_vector(np.array(new_sensor_data))
                # print(f"[DEBUG] 실시간 정규화된 센서: {normalized_new_sensor}") # 실시간 정규화 데이터 로그

                similar_tags, msg = find_similar_tag_from_csv(new_sensor_data, CSV_FILE)
                
                # 유사 태그 결과 로그 (정밀한 거리 값 포함)
                # print("[DEBUG] 유사 태그 결과:")
                # for tag, dist in similar_tags:
                #     print(f"  - 태그: {tag}, 거리: {dist:.8f}") # 거리 정밀도 높여서 출력
                socketio.emit('similar_tags_update', {'tags': [{'tag': t, 'distance': f'{d:.8f}'} for t, d in similar_tags]})
            except Exception as e:
                print(f"[ERROR] 실시간 유사 태그 찾기 중 오류: {e}")

# --- 시리얼 통신 및 데이터 읽기 스레드 ---
def read_from_serial():
    global ser, latest_sensor_data
    print(f"시리얼 포트 {SERIAL_PORT}에서 데이터 읽기 시작...")
    while not thread_stop_event.is_set():
        if ser and ser.is_open:
            try:
                line = ser.readline().decode('utf-8').strip()
                
                if not line:
                    time.sleep(0.01)
                    continue

                # print(f"[DEBUG] 수신 라인: '{line}'")

                if line.startswith("Name,"):
                    # print("[DEBUG] 헤더 라인 건너뜁니다.")
                    time.sleep(0.01)
                    continue

                data_values = line.split(',')
                # print(f"[DEBUG] {len(data_values)}개 값으로 분리됨: {data_values}")

                if len(data_values) == 10:
                    sensor_data = {
                        'F1': data_values[0], 'F2': data_values[1], 'F3': data_values[2],
                        'F4': data_values[3], 'F5': data_values[4], 'F6': data_values[5],
                        'F7': data_values[6], 'F8': data_values[7], 'Clear': data_values[8],
                        'NIR': data_values[9]
                    }
                    # print(f"[DEBUG] 원본 센서 데이터: {sensor_data}") # 원본 데이터 로그
                    latest_sensor_data = sensor_data
                    socketio.emit('sensor_update', sensor_data)
                    # print("[DEBUG] 'sensor_update' 이벤트 발생시킴.")
                else:
                    print(f"[경고] 예상치 못한 길이의 데이터 수신: {len(data_values)}")
                
                time.sleep(0.01)
            except serial.SerialException as e:
                print(f"시리얼 통신 오류: {e}")
                socketio.emit('serial_error', {'message': f'시리얼 통신 오류: {e}'})
                ser = None
                thread_stop_event.set()
                time.sleep(1)
            except Exception as e:
                print(f"데이터 처리 중 오류: {e}")
                socketio.emit('serial_error', {'message': f'데이터 처리 중 오류: {e}'})
                time.sleep(1)
        else:
            time.sleep(1)

# --- 유사 태그 찾기 함수 ---


def normalize_vector(v):
    """벡터를 정규화하여 크기(밝기) 영향을 줄이고 패턴(색상)을 강조합니다.
    신호가 너무 약하면 (norm이 임계값 이하) 0 벡터로 간주합니다.
    """
    norm = np.linalg.norm(v)
    # 신호가 너무 약하면 (모든 채널 값이 0이거나 매우 작은 경우) 0 벡터로 처리
    if norm < 1e-6: # 임계값 설정 (매우 작은 값)
        return np.zeros_like(v) # 모든 요소가 0인 벡터 반환
    return v / norm

def find_similar_tag_from_csv(new_sensor_data, csv_file=CSV_FILE):
    try:
        df = pd.read_csv(csv_file, encoding='cp949')
    except FileNotFoundError:
        return [], "데이터셋 파일이 없습니다."

    if 'Name' not in df.columns:
        return [], "데이터셋 파일에 'Name' 컬럼이 없습니다."

    sensor_feature_columns = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'Clear', 'NIR']
    if not all(col in df.columns for col in sensor_feature_columns):
        missing_cols = [col for col in sensor_feature_columns if col not in df.columns]
        return [], f"데이터셋 파일에 다음 센서 특징 컬럼이 없습니다: {', '.join(missing_cols)}"

    # 'Name'으로 그룹화하여 평균값 계산
    df_agg = df.groupby('Name')[sensor_feature_columns].mean().reset_index()

    sensor_features = df_agg[sensor_feature_columns].apply(pd.to_numeric, errors='coerce').dropna()
    tags = df_agg['Name'][sensor_features.index]

    if sensor_features.empty:
        return [], "유효한 센서 데이터가 데이터셋에 없습니다."

    # 실시간 센서 데이터를 정규화
    new_sensor_array = np.array(new_sensor_data)
    normalized_new_sensor = normalize_vector(new_sensor_array)
    
    distances = []
    for index, row in sensor_features.iterrows():
        # 데이터셋의 각 태그 대표값도 정규화
        normalized_row = normalize_vector(row.values)
        # print(f"[DEBUG] 데이터셋 '{tags[index]}' 정규화된 값: {normalized_row}") # 데이터셋 정규화 데이터 로그
        
        # 두 벡터 중 하나라도 0 벡터이면 거리를 최댓값(1)으로 설정
        if np.all(normalized_row == 0) or np.all(normalized_new_sensor == 0):
            distance = 1.0 # 0 벡터와의 유사도는 0, 거리는 1
        else:
            # 정규화된 벡터들 사이의 코사인 거리를 계산 (1 - 코사인 유사도).
            # 코사인 유사도는 np.dot(a, b)로 계산 가능 (정규화된 벡터의 경우)
            cosine_similarity = np.dot(normalized_row, normalized_new_sensor)
            distance = 1 - cosine_similarity

        distances.append((tags[index], distance))

    # 거리를 기준으로 정렬
    distances.sort(key=lambda x: x[1])

    # 상위 8개 반환
    return distances[:8], "성공"

# --- Flask 라우트 ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    global ser, thread_stop_event, serial_thread
    thread_stop_event.set()
    if serial_thread and serial_thread.is_alive():
        serial_thread.join(timeout=1)
    if ser and ser.is_open:
        ser.close()
    
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        sys.exit(0)
    else:
        func()
    return "Server shutting down..."

# --- SocketIO 이벤트 핸들러 ---
@socketio.on('connect')
def handle_connect():
    print('클라이언트 연결됨')
    ports = [{'port': port, 'desc': desc, 'hwid': hwid} for port, desc, hwid in sorted(list_ports.comports())]
    emit('available_ports', {'ports': ports})

@socketio.on('disconnect')
def handle_disconnect():
    print('클라이언트 연결 해제됨')

@socketio.on('request_ports')
def request_ports():
    ports = [{'port': port, 'desc': desc, 'hwid': hwid} for port, desc, hwid in sorted(list_ports.comports())]
    emit('available_ports', {'ports': ports})

@socketio.on('connect_serial_port')
def connect_serial_port(data):
    global ser, serial_thread, SERIAL_PORT
    selected_port = data.get('port')
    if not selected_port:
        emit('serial_error', {'message': '시리얼 포트가 선택되지 않았습니다.'})
        return

    if ser and ser.is_open:
        ser.close()
        print(f"기존 시리얼 포트 {SERIAL_PORT} 연결 닫음.")
        thread_stop_event.set()
        if serial_thread and serial_thread.is_alive():
            serial_thread.join(timeout=1)

    SERIAL_PORT = selected_port

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        ser.dtr = False
        print(f"시리얼 포트 {SERIAL_PORT} 연결 시도...")
        time.sleep(2)
        print(f"시리얼 포트 {SERIAL_PORT} 연결 성공.")
        emit('serial_connected', {'port': SERIAL_PORT, 'message': f'{SERIAL_PORT}에 연결되었습니다.'})

        thread_stop_event.clear()
        serial_thread = threading.Thread(target=read_from_serial)
        serial_thread.daemon = True
        serial_thread.start()

    except serial.SerialException as e:
        print(f"시리얼 포트 {SERIAL_PORT} 연결 실패: {e}")
        emit('serial_error', {'message': f'시리얼 포트 연결 실패: {e}'})
        ser = None
    except Exception as e:
        print(f"connect_serial_port에서 예상치 못한 오류 발생: {e}")
        emit('serial_error', {'message': f'예상치 못한 오류 발생: {e}'})
        ser = None

@socketio.on('capture_data')
def handle_capture_data(data):
    tag = data.get('tag', 'No Tag')
    print(f"'{tag}' 태그로 데이터 캡처 요청 수신.")

    if latest_sensor_data:
        try:
            data_values = list(latest_sensor_data.values())
            row = [tag] + data_values
            file_exists = os.path.isfile(CSV_FILE)
            with open(CSV_FILE, 'a', newline='', encoding='cp949') as f: # 인코딩을 cp949로 변경
                writer = csv.writer(f)
                if not file_exists or os.stat(CSV_FILE).st_size == 0:
                    writer.writerow(['Name', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'Clear', 'NIR'])
                writer.writerow(row)
            print(f"데이터 캡처 및 저장 완료: {row}")
            emit('capture_success', {'message': '데이터 캡처 및 저장 완료', 'data': row})
        except Exception as e:
            print(f"데이터 캡처 중 오류: {e}")
            emit('capture_error', {'message': f'데이터 캡처 중 오류: {e}'})
    else:
        emit('capture_error', {'message': '캡처할 센서 데이터가 없습니다. 잠시 후 다시 시도해주세요.'})

@socketio.on('start_similarity_search')
def start_similarity_search():
    global similarity_thread
    if not similarity_thread or not similarity_thread.is_alive():
        similarity_thread_stop_event.clear()
        similarity_thread = threading.Thread(target=find_similar_tags_continuously)
        similarity_thread.daemon = True
        similarity_thread.start()

@socketio.on('stop_similarity_search')
def stop_similarity_search():
    similarity_thread_stop_event.set()

if __name__ == '__main__':
    print(f"웹 서버 시작 중... http://127.0.0.1:5000")
    if not ('WERKZEUG_RUN_MAIN' in os.environ):
        webbrowser.open("http://127.0.0.1:5000/")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)