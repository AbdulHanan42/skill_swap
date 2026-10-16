from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_roundtrip():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong-password", hashed)


def test_jwt_roundtrip():
    token = create_access_token(42)
    assert decode_access_token(token) == "42"
