import serial
import csv
import os
import sys

# 시리얼 포트 설정 (환경에 맞게 변경하세요)
# Windows: 'COMx' (예: 'COM3')
# macOS/Linux: '/dev/ttyUSBx' 또는 '/dev/ttyACMx' (예: '/dev/ttyACM0')
SERIAL_PORT = 'COM6'  # <-- 이 부분을 아두이노가 연결된 시리얼 포트로 변경하세요
BAUD_RATE = 9600
CSV_FILE = 'sensor_dataset.csv'

def get_serial_port():
    """사용자에게 시리얼 포트 입력을 요청합니다."""
    if sys.platform.startswith('win'):
        default_port = 'COM3'
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        default_port = '/dev/ttyACM0'
    elif sys.platform.startswith('darwin'):
        default_port = '/dev/tty.usbmodem'
    else:
        default_port = '/dev/ttyUSB0' # Fallback for other OS

    port = input(f"아두이노 시리얼 포트를 입력하세요 (기본값: {default_port}): ")
    return port if port else default_port

def main():
    global SERIAL_PORT
    SERIAL_PORT = get_serial_port()

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"시리얼 포트 {SERIAL_PORT}에 연결되었습니다.")
    except serial.SerialException as e:
        print(f"오류: 시리얼 포트 {SERIAL_PORT}에 연결할 수 없습니다. {e}")
        print("올바른 포트가 선택되었는지, 아두이노가 연결되어 있는지 확인하세요.")
        return

    # CSV 파일이 없으면 헤더를 작성합니다.
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Name', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'Clear', 'NIR'])
            print(f"'{CSV_FILE}' 파일을 생성하고 헤더를 작성했습니다.")

    print("\n'q'를 입력하여 종료하거나, 'p'를 입력하여 포트 변경, 'l'을 입력하여 포트 목록을 확인하세요.")
    print("데이터를 캡처하려면 아무 키나 누르고 Enter를 누르세요.")

    while True:
        try:
            user_input = input("태그를 입력하거나 명령을 입력하세요: ").strip()

            if user_input.lower() == 'q':
                print("프로그램을 종료합니다.")
                break
            elif user_input.lower() == 'p':
                ser.close()
                SERIAL_PORT = get_serial_port()
                try:
                    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                    print(f"시리얼 포트 {SERIAL_PORT}로 변경되었습니다.")
                except serial.SerialException as e:
                    print(f"오류: 시리얼 포트 {SERIAL_PORT}에 연결할 수 없습니다. {e}")
                    print("올바른 포트가 선택되었는지, 아두이노가 연결되어 있는지 확인하세요.")
                    continue
            elif user_input.lower() == 'l':
                print("사용 가능한 시리얼 포트:")
                ports = serial.tools.list_ports.comports()
                if ports:
                    for port, desc, hwid in sorted(ports):
                        print(f"  {port}: {desc}")
                else:
                    print("  사용 가능한 시리얼 포트가 없습니다.")
                continue
            
            tag = user_input

            # 아두이노로 트리거 신호 전송
            ser.write(b'capture\n') # 어떤 문자열이든 상관없습니다. 아두이노가 Serial.available()을 감지하도록 합니다.
            print(f"'{tag}' 태그로 데이터 캡처를 요청했습니다...")

            # 아두이노로부터 데이터 한 줄 읽기
            line = ser.readline().decode('utf-8').strip()
            if line:
                data_values = line.split(',')
                if len(data_values) == 9: # F1-F8, Clear, NIR (총 9개)
                    row = [tag] + data_values
                    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(row)
                    print(f"데이터 캡처 및 저장 완료: {row}")
                else:
                    print(f"경고: 예상치 못한 데이터 형식: {line}")
            else:
                print("경고: 아두이노로부터 데이터를 받지 못했습니다. 아두이노가 실행 중인지 확인하세요.")

        except KeyboardInterrupt:
            print("\n사용자가 프로그램을 종료했습니다.")
            break
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")
            print("시리얼 연결을 확인하거나 프로그램을 다시 시작해보세요.")

    if ser.is_open:
        ser.close()
        print("시리얼 포트 연결을 닫았습니다.")

if __name__ == "__main__":
    main()
