"""完整 P2P 驗證腳本"""
import socket
import time
from blockchain_types.wallet import Wallet
from blockchain_types.transaction import Transaction
from blockchain_types.network_node import NetworkNode
from tools.converter import Converter

def send_message(host, port, message):
    """發送訊息"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect((host, port))
        client.sendall((message + "\n").encode('utf-8'))
        response = client.recv(4096).decode('utf-8').strip()
        client.close()
        return response
    except Exception as e:
        return f"Error: {e}"

print("=" * 60)
print("P2P 區塊鏈網路驗證")
print("=" * 60)
print()

# 1. 建立節點連接
print("步驟 1: 建立節點網路")
print("-" * 60)

# Node1 加入 Node2
node2 = NetworkNode("127.0.0.1", 8301)
message = f"joinNetwork, {Converter.string_to_base64(node2.to_base64())}"
response = send_message("127.0.0.1", 8300, message)
print(f"✓ Node1 → Node2: {Converter.base64_to_string(response) if response else 'Failed'}")

# Node1 加入 Node3
node3 = NetworkNode("127.0.0.1", 8302)
message = f"joinNetwork, {Converter.string_to_base64(node3.to_base64())}"
response = send_message("127.0.0.1", 8300, message)
print(f"✓ Node1 → Node3: {Converter.base64_to_string(response) if response else 'Failed'}")

# Node2 加入 Node3
message = f"joinNetwork, {Converter.string_to_base64(node3.to_base64())}"
response = send_message("127.0.0.1", 8301, message)
print(f"✓ Node2 → Node3: {Converter.base64_to_string(response) if response else 'Failed'}")
print()

# 2. 查詢餘額
print("步驟 2: 查詢各節點餘額")
print("-" * 60)

wallets = [
    ("Alice", 8300),
    ("Bob", 8301),
    ("Charlie", 8302)
]

for name, port in wallets:
    wallet = Wallet(name)
    account = wallet.get_account()
    message = f"getBalance, {Converter.string_to_base64(account)}"
    response = send_message("127.0.0.1", port, message)
    if response:
        balance = Converter.base64_to_string(response)
        print(f"✓ {name} (Port {port}): {balance} coins")
print()

# 3. 發送交易測試
print("步驟 3: 發送交易測試 (Alice → Bob)")
print("-" * 60)

alice = Wallet("Alice")
bob = Wallet("Bob")

tx = Transaction(
    sender=alice.get_account(),
    receiver=bob.get_account(),
    amount=5.0,
    fee=0.5
)
tx.set_signature(alice.sign(tx.to_base64_with_content_only()))

message = f"doTransact, {Converter.string_to_base64(tx.to_base64())}"
response = send_message("127.0.0.1", 8300, message)
print(f"✓ Transaction sent: {Converter.base64_to_string(response) if response else 'Failed'}")
print()

print("=" * 60)
print("驗證完成!")
print("=" * 60)
print()
print("📝 下一步:")
print("1. 觀察三個終端機的日誌")
print("2. 應該看到 Node1 廣播交易到 Node2 和 Node3")
print("3. 等待挖礦,交易會被打包進區塊")
print("4. 挖到區塊後會廣播,所有節點應該同步")
print()
print("✓ 如果看到 'Broadcasting' 和 'Broadcasted to' 訊息")
print("  表示 P2P 網路運作正常!")