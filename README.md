# AS7341 Spectral Sensor Data Monitoring and Similarity Search

This project provides a comprehensive solution for monitoring AS7341 spectral sensor data, capturing and saving it, and performing real-time similarity searches against a dataset of previously captured spectral profiles. It consists of an Arduino sketch for sensor data acquisition and a Python Flask web application for data visualization, control, and analysis.

## Features

*   **Real-time Sensor Data Display:** Visualize AS7341 spectral data (F1-F8, Clear, NIR channels) in real-time on a web interface.
*   **Serial Communication:** Connects to an Arduino board via serial port to receive sensor data.
*   **Data Capture & Saving:** Capture current sensor readings with a user-defined tag and save them to a CSV dataset (`sensor_dataset.csv`).
*   **Real-time Similarity Search:** Continuously compares the current sensor data with the existing dataset to find and display the most similar spectral profiles (tags) based on cosine similarity.
*   **Web-based User Interface:** Intuitive web interface built with Flask and Socket.IO for easy interaction.
*   **Arduino Integration:** Includes an Arduino sketch (`src/main.cpp`) for reading AS7341 sensor data and sending it over serial.

## Setup/Installation

### 1. Arduino (Firmware):

*   Ensure you have [PlatformIO Core](https://platformio.org/install) installed.
*   Navigate to the `AS7341_test` directory (where `platformio.ini` is located).
*   Upload the firmware to your Arduino board:
    ```bash
    pio run -t upload
    ```
*   Make sure the AS7341 sensor is correctly wired to your Arduino board.

### 2. Python (Web Application):

*   **Prerequisites:** Python 3.x
*   Install required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
*   Run the web application:
    ```bash
    python app.py
    ```
    Or use the provided batch file:
    ```bash
    start.bat
    ```
*   The application will open in your default web browser at `http://127.0.0.1:5000`.

## Usage

1.  **Connect Serial Port:** Select your Arduino's serial port from the dropdown menu and click "연결" (Connect).
2.  **Real-time Data:** Observe the real-time spectral sensor values.
3.  **Capture Data:** Enter a tag (e.g., "Red Apple", "Green Leaf") in the input field and click "캡처 및 저장" (Capture and Save) to add the current sensor data to `sensor_dataset.csv`.
4.  **Similarity Search:** Toggle the "실시간 유사 태그 찾기" (Real-time Similarity Search) switch to enable continuous comparison of live sensor data with your dataset. The most similar tags will be displayed.
5.  **Shutdown Server:** Click "서버 종료" (Shutdown Server) to gracefully stop the web application.

## Technologies Used

*   **Arduino:** Firmware for AS7341 sensor data acquisition.
*   **PlatformIO:** For Arduino project management and compilation.
*   **Python:** Backend logic and web server.
*   **Flask:** Web framework for the application.
*   **Flask-SocketIO:** For real-time bidirectional communication between the server and the web client.
*   **PySerial:** Python library for serial communication with Arduino.
*   **Pandas & NumPy:** For data handling and numerical operations (e.g., vector normalization, cosine similarity calculation).
*   **HTML, CSS, JavaScript:** Frontend web interface.
