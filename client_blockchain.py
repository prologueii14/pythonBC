import os
import sys
import socket
import threading
import time
from typing import Optional, Tuple

# 保險處理：若直接以相對路徑執行，確保可匯入本專案套件
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(__file__))

from blockchain_types.blockchain import Blockchain
from blockchain_types.wallet import Wallet
from blockchain_types.transaction import Transaction
from blockchain_types.network_node import NetworkNode
from tools.converter import Converter
from tools.io import IO
from config.network_config import NetworkConfig
from start_blockchain import network_server  # 重用現有的伺服器函式


def send_message(host: str, port: int, message: str) -> Optional[str]:
    """
    參考 verify_p2p.py：送一行字串訊息，等待一行回覆（皆結尾 \n）
    """
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect((host, port))
        client.sendall((message + "\n").encode("utf-8"))
        response = client.recv(65536).decode("utf-8").strip()
        client.close()
        return response
    except Exception as e:
        IO.errln(f"send_message error: {e}")
        return None


def mining_worker(blockchain: Blockchain, stop_evt: threading.Event):
    """
    可控的挖礦執行緒：
    - 當 blockchain.mining 為 True 時，呼叫 mine_block() 與 adjust_difficulty()
    - 當 mining 為 False 時，sleep 避免忙等
    """
    while not stop_evt.is_set():
        if getattr(blockchain, "mining", False):
            blockchain.mine_block()
            blockchain.adjust_difficulty()
        else:
            time.sleep(0.5)


def run_local_node(wallet_name: str, port: int) -> Tuple[Blockchain, threading.Event]:
    """
    啟動本地節點伺服器與礦工執行緒（初始先關閉挖礦）。
    回傳 (blockchain, miner_stop_event)
    """
    IO.outln(f"Starting local node as wallet '{wallet_name}' on port {port}")
    blockchain = Blockchain(wallet_name)

    # 先關掉挖礦，避免一啟動就滿載 CPU（之後由選單控制開始/停止）
    blockchain.stop_mine()

    # 啟動網路伺服器（重用 start_blockchain.network_server）
    server_thread = threading.Thread(target=network_server, args=(blockchain, port), daemon=True)
    server_thread.start()

    # 啟動可控的礦工執行緒
    miner_stop = threading.Event()
    miner_thread = threading.Thread(target=mining_worker, args=(blockchain, miner_stop), daemon=True)
    miner_thread.start()

    return blockchain, miner_stop


def menu_loop(wallet: Wallet, listen_port: int):
    """
    簡易的命令列介面：
    1. 查餘額
    2. 發送交易
    3. 加入節點
    4. 從節點克隆區塊鏈
    5. 開始挖礦
    6. 停止挖礦
    7. 離開
    """
    host = "127.0.0.1"

    while True:
        print("\n=== Blockchain Client Menu ===")
        print("1) Check Balance")
        print("2) Send Transaction")
        print("3) Join Network Node")
        print("4) Clone Chain From Node")
        print("5) Start Mining")
        print("6) Stop Mining")
        print("7) Exit")
        print("==============================")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            # 查餘額：getBalance, b64(account)
            message = f"getBalance, {Converter.string_to_base64(wallet.get_account())}"
            resp = send_message(host, listen_port, message)
            if resp:
                try:
                    bal = float(Converter.base64_to_string(resp))
                    IO.outln(f"Balance = {bal}")
                except Exception:
                    IO.errln(f"Invalid response: {resp}")
            else:
                IO.errln("No response from local node.")

        elif choice == "2":
            # 送交易（參照 verify_p2p）：
            # doTransact, b64(transaction.toBase64())
            try:
                receiver_name = input("Enter receiver wallet name: ").strip()
                amount = float(input("Enter amount: ").strip())
                fee = float(input("Enter fee: ").strip())
                message_text = input("Enter message: ").strip()

                receiver_wallet = Wallet(receiver_name)
                tx = Transaction(
                    sender=wallet.get_account(),
                    receiver=receiver_wallet.get_account(),
                    amount=amount,
                    fee=fee
                )
                tx.set_message(message_text)
                # 簽章：用 sender 的錢包對「不含 signature」的內容簽名
                tx.set_signature(wallet.sign(tx.to_base64_with_content_only()))

                payload = Converter.string_to_base64(tx.to_base64())
                resp = send_message(host, listen_port, f"doTransact, {payload}")
                if resp:
                    res_str = Converter.base64_to_string(resp)
                    if res_str == "Ok":
                        IO.outln("Transaction accepted by Server.")
                    else:
                        IO.errln(f"Transaction rejected: {res_str}")
                else:
                    IO.errln("No response from local node.")
            except ValueError:
                IO.errln("Invalid amount/fee. Please enter numeric values.")
            except Exception as e:
                IO.errln(f"Send transaction failed: {e}")

        elif choice == "3":
            # 加入節點：joinNetwork, b64(networkNode.toBase64())
            try:
                peer_host = input("Peer host (e.g., 127.0.0.1): ").strip() or "127.0.0.1"
                peer_port = int(input("Peer port (e.g., 8301): ").strip())
                node = NetworkNode(peer_host, peer_port)
                payload = Converter.string_to_base64(node.to_base64())
                resp = send_message(host, listen_port, f"joinNetwork, {payload}")
                if resp:
                    IO.outln(f"joinNetwork → {Converter.base64_to_string(resp)}")
                else:
                    IO.errln("No response from local node.")
            except Exception as e:
                IO.errln(f"Join network failed: {e}")

        elif choice == "4":
            # 克隆區塊鏈：getCloneChainFrom, b64(networkNode.toBase64())
            try:
                src_host = input("Source host (e.g., 127.0.0.1): ").strip() or "127.0.0.1"
                src_port = int(input("Source port (e.g., 8301): ").strip())
                src_node = NetworkNode(src_host, src_port)
                payload = Converter.string_to_base64(src_node.to_base64())
                resp = send_message(host, listen_port, f"getCloneChainFrom, {payload}")
                if resp:
                    IO.outln(f"clone result → {Converter.base64_to_string(resp)}")
                else:
                    IO.errln("No response from local node.")
            except Exception as e:
                IO.errln(f"Clone chain failed: {e}")

        elif choice == "5":
            # 開始挖礦：startMining（無 payload）
            resp = send_message(host, listen_port, "startMining")
            if resp:
                IO.outln(f"startMining → {Converter.base64_to_string(resp)}")
            else:
                IO.errln("No response from local node.")

        elif choice == "6":
            # 停止挖礦：stopMining（無 payload）
            resp = send_message(host, listen_port, "stopMining")
            if resp:
                IO.outln(f"stopMining → {Converter.base64_to_string(resp)}")
            else:
                IO.errln("No response from local node.")

        elif choice == "7":
            IO.outln("Goodbye!")
            break
        else:
            IO.errln("Invalid choice! Please try again.")


def main():
    """
    啟動本地節點 + 互動式 CLI
    用法（互動式）：直接執行後依序輸入 wallet 與 port
    """
    IO.outln("")
    IO.outln("=== Local Node Bootstrap ===")
    wallet_name = input("Input your wallet name: ").strip() or "DefaultNode"
    try:
        default_port = NetworkConfig.SOCKET_PORT
    except Exception:
        default_port = 8300
    port_text = input(f"Listen port (default {default_port}): ").strip()
    listen_port = int(port_text) if port_text else default_port

    # 啟本地節點（伺服器 + 礦工）
    blockchain, miner_stop = run_local_node(wallet_name, listen_port)

    # 準備本地錢包（用於發交易 / 查餘額）
    wallet = blockchain.wallet  # 與節點同一把錢包，亦可改成分離
    IO.outln(f"Wallet loaded. Account: {wallet.get_account()}")

    # 進入互動式選單
    try:
        menu_loop(wallet, listen_port)
    finally:
        # 結束時終止礦工執行緒
        miner_stop.set()
        IO.outln("Node shutdown requested. Bye.")


if __name__ == "__main__":
    main()
