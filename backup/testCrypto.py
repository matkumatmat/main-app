from shared.backend.cryptoFactory import crypto

# 1. Test Data & Context
data = "MEMEK GEMING"
context_correct = "uservice:iphone15"
context_wrong = "user:123|devd_kw"

print(f"Original: {data}")

# 2. Encrypt
try:
    encrypted = crypto.encryptSensitive(data, context_correct)
    print(f"\n[OK] Encrypted:")
    print(f" - Ciphertext: {encrypted.ciphertext}")
    print(f" - Salt: {encrypted.salt}")
    print(f" - Nonce: {encrypted.nonce}")
except Exception as e:
    print(f"\n[FAIL] Encryption Error: {e}")
    exit()

# 3. Decrypt (Success Case)
try:
    decrypted = crypto.decryptSensitive(encrypted, context_correct)
    print(f"\n[OK] Decrypt Correct Context: {decrypted}")
    assert decrypted == data
except Exception as e:
    print(f"\n[FAIL] Decrypt Correct Context Error: {e}")

# 4. Decrypt (Fail Case - Context Mismatch)
print(f"\n[TEST] Decrypt Wrong Context (Expect Failure)...")
try:
    crypto.decryptSensitive(encrypted, context_wrong)
    print(f"[FAIL] BAHAYA! Berhasil decrypt dengan context salah!")
except ValueError as e:
    print(f"[OK] Aman. Gagal decrypt sesuai prediksi: {e}")