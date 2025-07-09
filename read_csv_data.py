import pandas as pd
import os

# CSV 파일 경로 (현재 스크립트와 같은 디렉토리에 있다고 가정)
# 필요하다면 절대 경로로 변경하세요.
csv_file_path = 'C:/Users/sky27/OneDrive/바탕 화면/Arduino/AS7341_test/AS7341_test/sensor_dataset.csv'

if not os.path.exists(csv_file_path):
    print(f"오류: '{csv_file_path}' 파일을 찾을 수 없습니다.")
else:
    try:
        # cp949 인코딩으로 CSV 파일 읽기
        df = pd.read_csv(csv_file_path, encoding='cp949')
        
        print(f"--- '{csv_file_path}' 파일 내용 ---")
        print(df.to_string()) # 전체 내용을 출력하기 위해 to_string() 사용
        print("------------------------------------")
        
    except Exception as e:
        print(f"파일을 읽는 중 오류 발생: {e}")
