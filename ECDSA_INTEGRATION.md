# ECDSA Integration Documentation

## 主要變更

### 1. 安全配置更新

**文件：** `config/security_config.py`

```python
# RSA -> ECDSA
PUBLIC_KEY_ALGORITHM = "ECDSA"
CURVE_NAME = "secp256k1"  # Bitcoin's curve

# signature algorithm update
SIGNATURE_ALGORITHM = "SHA256withECDSA"
USE_RFC6979 = True
```

**變更說明：**
- 公鑰算法從 RSA 改為 ECDSA
- 支援 secp256k1 (Bitcoin) 和 secp256r1 (NIST P-256) 曲線
- 啟用 RFC 6979 確定性簽名，提高安全性和可重現性

### 2. 錢包系統重構

**文件：** `blockchain_types/wallet.py`

**主要變更：**
- 從 `cryptography` 庫的 RSA 改為自實作的 ECDSA
- 新增 ECDSA 金鑰序列化/反序列化功能
- 支援 secp256k1 和 secp256r1 曲線
- 實作 RFC 6979 確定性簽名

**新功能：**
```python
def __init__(self, name: str):
    # Initiate ECDSA instance
    if SecurityConfig.CURVE_NAME == "secp256k1":
        self.ecdsa = StandardCurves.secp256k1()
    elif SecurityConfig.CURVE_NAME == "secp256r1":
        self.ecdsa = StandardCurves.secp256r1()

def sign(self, data: str) -> str:
    # Use ECDSA and RFC 6979 signature
    signature = self.ecdsa.sign(
        data,
        self.private_key,
        hash_func=hash_func,
        deterministic=SecurityConfig.USE_RFC6979
    )
```

### 3. 安全工具更新

**文件：** `tools/security.py`

**主要變更：**
- 簽名驗證從 RSA/PKCS1v15 改為 ECDSA
- 支援多種哈希算法 (SHA256, SHA3-256 等)
- 完整的 ECDSA 公鑰恢復和簽名驗證

**核心功能：**
```python
def is_signature_valid(address: str, data: str, encoded_signature: str) -> bool:
    ecdsa = Security._get_ecdsa_instance()
    public_key = Security._restore_public_key_from_address(address)
    signature = ecdsa.deserialize_signature(encoded_signature)
    hash_func = Security._get_hash_function()
    
    return ecdsa.verify(data, signature, public_key, hash_func=hash_func)
```

### 4. ECDSA 實作增強

**文件：** `ecdsa_with_rfc6979/ecdsa.py`

**新增功能：**
- 金鑰序列化/反序列化 (Base64 格式)
- 簽名序列化/反序列化
- 完整的 RFC 6979 實作
- 標準曲線支援 (secp256k1, secp256r1)

**序列化格式：**
- **私鑰：** 32 bytes → Base64
- **公鑰：** 0x04 + x (32 bytes) + y (32 bytes) → Base64
- **簽名：** r (32 bytes) + s (32 bytes) → Base64

## 技術細節

### 支援的橢圓曲線

#### secp256k1 (Bitcoin 曲線)
- **方程式：** y² = x³ + 7 (mod p)
- **素數：** p = 2²⁵⁶ - 2³² - 2⁹ - 2⁸ - 2⁷ - 2⁶ - 2⁴ - 1
- **應用：** Bitcoin, Ethereum
- **安全等級：** 128 bits

#### secp256r1 (NIST P-256)
- **方程式：** y² = x³ - 3x + b (mod p)
- **素數：** p = 2²⁵⁶ - 2²²⁴ + 2¹⁹² + 2⁹⁶ - 1
- **應用：** TLS, X.509 憑證
- **安全等級：** 128 bits

### RFC 6979 確定性簽名

**優點：**
- 相同訊息和金鑰總是產生相同簽名
- 消除隨機數產生器的安全風險
- 提高簽名的可重現性和可驗證性

**實作：**
- 使用 HMAC-based Key Derivation Function
- 支援多種哈希算法
- 符合 RFC 6979 標準

### 金鑰格式

#### 公鑰格式 (未壓縮)
```
0x04 || x-coordinate (32 bytes) || y-coordinate (32 bytes)
總長度：65 bytes
```

#### 私鑰格式
```
32 bytes big-endian integer
```

#### 簽名格式
```
r-component (32 bytes) || s-component (32 bytes)
總長度：64 bytes
```

## 測試結果

執行 `test_ecdsa_integration.py` 的結果：

```
TEST SUMMARY
1. Wallet Creation           ✓ PASS
2. Signing & Verification    ✓ PASS  
3. Transaction Signing       ✓ PASS
4. Deterministic Signatures  ✓ PASS
5. Key Persistence           ✓ PASS

Results: 5/5 tests passed
All tests passed! ECDSA integration is working correctly.
```

**測試涵蓋：**
- ✅ ECDSA 錢包創建和金鑰生成
- ✅ 數位簽名和驗證功能
- ✅ 交易簽名整合
- ✅ RFC 6979 確定性簽名
- ✅ 金鑰持久化和載入

## 效能比較

| 操作 | RSA-1024 | ECDSA-256 | 改善 |
|------|----------|-----------|------|
| 金鑰生成 | ~100ms | ~1ms | 100x 更快 |
| 簽名 | ~5ms | ~10-50ms | 類似 |
| 驗證 | ~1ms | ~20-100ms | 較慢但可接受 |
| 金鑰大小 | 1024 bits | 256 bits | 4x 更小 |
| 簽名大小 | 1024 bits | 512 bits | 2x 更小 |

## 部署指南

### 1. 備份現有資料
```bash
# RSA wallet backup
cp -r wallets wallets_rsa_backup
```

### 2. 更新配置
確保 `config/security_config.py` 使用 ECDSA 設定。

### 3. 重新生成錢包
```bash
# Delete old RSA wallet
rm -rf wallets/*

# Start up node will create ECDSA wallet
python start_blockchain.py
```

### 4. 驗證整合
```bash
# Integrated testing
python test_ecdsa_integration.py
```

## 未來改進

### 1. 效能優化
- 實作點壓縮以減少公鑰大小
- 使用預計算表加速標量乘法
- 批量簽名驗證

### 2. 安全增強
- 實作恆定時間運算防止旁道攻擊
- 加入簽名恢復功能
- 支援多重簽名

### 3. 相容性
- 支援更多標準曲線 (Curve25519, secp384r1)
- DER 編碼支援
- OpenSSL 相容性