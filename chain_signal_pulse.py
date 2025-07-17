import requests
import time
import statistics
import smtplib
from email.mime.text import MIMEText

ETHERSCAN_API_KEY = "YourApiKeyHere"
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

# Порог аномальной активности (изменяем по ситуации)
ANOMALY_THRESHOLD_MULTIPLIER = 3.5

def get_latest_blocks(n=20):
    latest_blocks = []
    for i in range(n):
        block_number = get_block_number() - i
        tx_count = get_tx_count(block_number)
        latest_blocks.append(tx_count)
        time.sleep(0.2)
    return list(reversed(latest_blocks))

def get_block_number():
    url = f"{ETHERSCAN_API_URL}?module=proxy&action=eth_blockNumber&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    return int(response['result'], 16)

def get_tx_count(block_number):
    url = f"{ETHERSCAN_API_URL}?module=proxy&action=eth_getBlockTransactionCountByNumber&tag={hex(block_number)}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    return int(response['result'], 16)

def detect_anomaly(data):
    if len(data) < 5:
        return False
    mean = statistics.mean(data[:-1])
    stdev = statistics.stdev(data[:-1])
    current = data[-1]
    return current > mean + ANOMALY_THRESHOLD_MULTIPLIER * stdev

def notify(message):
    print("[ALERT]:", message)
    # Дополнительно можно отправлять в Telegram/email

def main():
    print("🌀 Monitoring Ethereum blocks for unusual activity...")
    history = get_latest_blocks()
    while True:
        current_block = get_block_number()
        current_tx_count = get_tx_count(current_block)
        history.append(current_tx_count)
        if len(history) > 20:
            history.pop(0)

        if detect_anomaly(history):
            notify(f"Anomaly detected in block {current_block} with {current_tx_count} txs")

        time.sleep(15)

if __name__ == "__main__":
    main()
