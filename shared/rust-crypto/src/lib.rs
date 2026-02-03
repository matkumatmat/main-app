use pyo3::prelude::*;
use pyo3::types::PyDict;
// HAPUS import pyo3::PyObject yang bikin error
use aes_gcm::{
    aead::{Aead, KeyInit, Payload},
    Aes256Gcm, Nonce, Key
};
use argon2::{
    password_hash::{
        rand_core::OsRng,
        PasswordHasher // Trait ini WAJIB ada biar hash_password_into jalan
    },
    Argon2
};
use rand::RngCore;
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};

/// Derives a 32-byte key from the master key and a salt using Argon2id.
fn derive_key(master_key: &str, salt: &[u8]) -> Result<[u8; 32], String> {
    let argon2 = Argon2::default();
    let mut output_key_material = [0u8; 32];
    
    // Method ini butuh trait PasswordHasher di-import
    argon2.hash_password_into(
        master_key.as_bytes(),
        salt,
        &mut output_key_material
    ).map_err(|e| format!("Key derivation failed: {}", e))?;

    Ok(output_key_material)
}

#[pyfunction]
fn encrypt_with_context(
    py: Python<'_>,
    plaintext: &str,
    master_key: &str,
    aad_context: &str 
) -> PyResult<Py<PyDict>> { // FIX: Return type spesifik Py<PyDict>, bukan PyObject
    
    // 1. Generate Random Salt
    let mut salt = [0u8; 16];
    OsRng.fill_bytes(&mut salt);

    // 2. Generate Random Nonce
    let mut nonce_bytes = [0u8; 12];
    OsRng.fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    // 3. Derive Session Key
    let key_bytes = derive_key(master_key, &salt).map_err(pyo3::exceptions::PyValueError::new_err)?;
    let key = Key::<Aes256Gcm>::from_slice(&key_bytes);

    // 4. Initialize Cipher
    let cipher = Aes256Gcm::new(key);

    // 5. Encrypt with AAD
    let payload = Payload {
        msg: plaintext.as_bytes(),
        aad: aad_context.as_bytes(),
    };

    let ciphertext = cipher.encrypt(nonce, payload)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Encryption failed: {}", e)))?;

    // 6. Return Dictionary
    // Di PyO3 0.28, PyDict::new(py) returnnya Bound<'py, PyDict>
    let result = PyDict::new(py);
    result.set_item("ciphertext", BASE64.encode(ciphertext))?;
    result.set_item("salt", BASE64.encode(salt))?;
    result.set_item("nonce", BASE64.encode(nonce_bytes))?;

    // .unbind() mengubah Bound<'_, PyDict> menjadi Py<PyDict> (detached object)
    // Ini solusi paling bersih untuk return value di versi baru
    Ok(result.unbind())
}

#[pyfunction]
fn decrypt_with_context(
    ciphertext_b64: &str,
    salt_b64: &str,
    nonce_b64: &str,
    master_key: &str,
    aad_context: &str
) -> PyResult<String> {
    // 1. Decode Base64
    let ciphertext = BASE64.decode(ciphertext_b64)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid base64 ciphertext: {}", e)))?;
    let salt = BASE64.decode(salt_b64)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid base64 salt: {}", e)))?;
    let nonce_bytes = BASE64.decode(nonce_b64)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid base64 nonce: {}", e)))?;

    if nonce_bytes.len() != 12 {
        return Err(pyo3::exceptions::PyValueError::new_err("Invalid nonce length"));
    }
    let nonce = Nonce::from_slice(&nonce_bytes);

    // 2. Derive Key
    let key_bytes = derive_key(master_key, &salt).map_err(pyo3::exceptions::PyValueError::new_err)?;
    let key = Key::<Aes256Gcm>::from_slice(&key_bytes);

    // 3. Decrypt
    let cipher = Aes256Gcm::new(key);
    let payload = Payload {
        msg: &ciphertext,
        aad: aad_context.as_bytes(),
    };

    let plaintext_bytes = cipher.decrypt(nonce, payload)
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Decryption failed: Integrity check failed or context mismatch"))?;

    let plaintext = String::from_utf8(plaintext_bytes)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid UTF-8: {}", e)))?;

    Ok(plaintext)
}

#[pymodule]
fn k_services_crypto(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encrypt_with_context, m)?)?;
    m.add_function(wrap_pyfunction!(decrypt_with_context, m)?)?;
    Ok(())
}