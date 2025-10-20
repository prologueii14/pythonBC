"""測試 P2P 網路連接"""
import socket
import time
from tools.converter import Converter
from blockchain_types.network_node import NetworkNode

def send_message(host, port, message):
    """發送訊息到節點"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect((host, port))
        client.sendall((message + "\n").encode('utf-8'))
        response = client.recv(4096).decode('utf-8').strip()
        client.close()
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

# 讓 Node1 (8300) 加入 Node2 (8301) 到網路
print("=== 測試 1: Node1 加入 Node2 ===")
node2 = NetworkNode("127.0.0.1", 8301)
node2_b64 = node2.to_base64()
message = f"joinNetwork, {Converter.string_to_base64(node2_b64)}"
response = send_message("127.0.0.1", 8300, message)
print(f"Response: {response}")
print()

# 讓 Node1 (8300) 加入 Node3 (8302) 到網路
print("=== 測試 2: Node1 加入 Node3 ===")
node3 = NetworkNode("127.0.0.1", 8302)
node3_b64 = node3.to_base64()
message = f"joinNetwork, {Converter.string_to_base64(node3_b64)}"
response = send_message("127.0.0.1", 8300, message)
print(f"Response: {response}")
print()

# 查詢 Node1 的餘額
print("=== 測試 3: 查詢 Node1 餘額 ===")
# 這裡需要 Node1 的帳戶地址,你可以從啟動訊息中看到
# 或者先建立 Wallet 來取得
from blockchain_types.wallet import Wallet
wallet = Wallet("Alice")
account = wallet.get_account()
message = f"getBalance, {Converter.string_to_base64(account)}"
response = send_message("127.0.0.1", 8300, message)
balance = Converter.base64_to_string(response)
print(f"Node1 Balance: {balance}")
print()

print("=== 測試完成 ===")
print("現在 Node1 應該已經連接到 Node2 和 Node3")
print("當 Node1 挖到新區塊時,會自動廣播給 Node2 和 Node3")
print("觀察三個終端機的輸出,應該會看到 'Broadcasting' 和 'Broadcasted to' 訊息")