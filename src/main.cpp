/*
    DFRobot AS7341 분광 센서의 모든 채널 데이터를 읽어
    시리얼 모니터에 출력하는 예제 코드
*/

#include "DFRobot_AS7341.h"

// I2C 통신을 위한 센서 객체 생성
DFRobot_AS7341 as7341;

void setup()
{
  // 시리얼 통신 시작 (속도: 9600)
  Serial.begin(9600);
  // 시리얼 포트가 열릴 때까지 잠시 대기
  while (!Serial)
  {
    ;
  }
  Serial.println("Serial communication started!");

  // 센서 초기화
  Serial.println("Initializing AS7341 sensor...");
  if (as7341.begin() != 0)
  {
    Serial.println("Sensor communication error, please check wiring. Halting.");
    while (1)
      ; // 오류 발생 시 여기서 멈춤
  }
  Serial.println("AS7341 Sensor Initialized!");

  // 측정 모드 설정
  as7341.startMeasure(DFRobot_AS7341::eF1F4ClearNIR);
  as7341.startMeasure(DFRobot_AS7341::eF5F8ClearNIR);
  Serial.println("Measurement mode set. Starting data transmission.");

  // CSV Header 전송
  Serial.println("Name,F1,F2,F3,F4,F5,F6,F7,F8,Clear,NIR");
}

void loop()
{
  // 실시간 스트리밍을 위해 주기적으로 데이터를 보내기
  DFRobot_AS7341::sModeOneData_t dataOne = as7341.readSpectralDataOne();
  DFRobot_AS7341::sModeTwoData_t dataTwo = as7341.readSpectralDataTwo();

  Serial.print(dataOne.ADF1);
  Serial.print(",");
  Serial.print(dataOne.ADF2);
  Serial.print(",");
  Serial.print(dataOne.ADF3);
  Serial.print(",");
  Serial.print(dataOne.ADF4);
  Serial.print(",");
  Serial.print(dataTwo.ADF5);
  Serial.print(",");
  Serial.print(dataTwo.ADF6);
  Serial.print(",");
  Serial.print(dataTwo.ADF7);
  Serial.print(",");
  Serial.print(dataTwo.ADF8);
  Serial.print(",");
  Serial.print(dataOne.ADCLEAR);
  Serial.print(",");
  Serial.println(dataTwo.ADNIR);

  delay(10); // 0.01초마다 데이터 전송
}
