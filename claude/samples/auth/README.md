# JWT Authentication Demo

This sample demonstrates JWT token creation, verification, and management using PyJWT.

## 📋 What This Demo Covers

1. **Token Generation**
   - Creating access tokens (short-lived)
   - Creating refresh tokens (long-lived)
   - Adding custom claims (user_id, role, etc.)

2. **Token Verification**
   - Verifying token signature
   - Checking expiration
   - Validating token type

3. **Token Management**
   - Refreshing expired access tokens
   - Token revocation (logout)
   - Token blacklist simulation

4. **Security Features**
   - Detecting tampered tokens
   - Handling expired tokens
   - Signature validation

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd samples/auth
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
python jwt_demo.py
```

## 📖 Expected Output

The demo will run through 7 scenarios:

### Demo 1: Login Flow
```
✅ Access Token Created:
   User ID: usr_123456
   Username: john.doe
   Role: DEVOPS_ENGINEER
   Expires: 2024-01-15 14:30:00 UTC
```

### Demo 2: Token Verification
```
✅ Token Verified Successfully:
   Type: access
   User ID: usr_123456
   Issued At: 2024-01-15 14:15:00
```

### Demo 3: Token Structure
```
🔍 Token Structure:
   Total Parts: 3
   Part 1 (Header):    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   Part 2 (Payload):   eyJ1c2VyX2lkIjoidXNyXzEyMzQ1NiIsInVz...
   Part 3 (Signature): SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_...
```

### Demo 4: Token Refresh
```
🔄 Generating new access token...
✅ New access token issued successfully
```

### Demo 5: Token Expiration
```
⏱️  Creating token with 1-second expiration...
⏳ Waiting 2 seconds for token to expire...
❌ Token Verification Failed: Token has expired
```

### Demo 6: Logout (Token Revocation)
```
🚫 Token Revoked (Logged Out)
   Token added to blacklist
❌ Token Verification Failed: Token has been revoked
```

### Demo 7: Invalid Signature Detection
```
⚠️  Attempting to tamper with token...
   Original user_id: usr_456
   Tampered user_id: usr_hacker
❌ Token Verification Failed: Signature verification failed
```

## 🔍 Understanding the Code

### Token Structure

A JWT has 3 parts separated by dots:
```
header.payload.signature
```

**Header** (Base64 encoded):
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload** (Base64 encoded):
```json
{
  "user_id": "usr_123456",
  "username": "john.doe",
  "role": "DEVOPS_ENGINEER",
  "exp": 1705329000,  // Expiration timestamp
  "iat": 1705328100,  // Issued at timestamp
  "type": "access"
}
```

**Signature** (HMAC-SHA256):
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

### Key Functions

#### `create_access_token(user_data)`
Generates a short-lived JWT token for API authentication.

```python
access_token = create_access_token({
    "user_id": "123",
    "username": "john",
    "role": "DEVOPS_ENGINEER"
})
```

#### `create_refresh_token(user_id)`
Generates a long-lived token for refreshing access tokens.

```python
refresh_token = create_refresh_token("usr_123456")
```

#### `verify_token(token, token_type)`
Verifies and decodes a JWT token.

```python
payload = verify_token(access_token, token_type="access")
if payload:
    user_id = payload["user_id"]
    # Token is valid, proceed with request
```

#### `refresh_access_token(refresh_token, user_data)`
Uses a refresh token to generate a new access token.

```python
new_token = refresh_access_token(refresh_token, user_data)
```

#### `revoke_token(token)`
Adds token to blacklist (logout functionality).

```python
revoke_token(access_token)  # User logged out
```

## 🔒 Security Considerations

### ✅ Good Practices Shown

1. **Random Secret Key**: Generated using `secrets.token_urlsafe(32)`
2. **Short Access Token Expiry**: 15 minutes (configurable)
3. **Token Type Validation**: Ensures access/refresh tokens aren't mixed
4. **Unique Token IDs (jti)**: Each token has unique identifier
5. **Blacklist Support**: Tokens can be revoked (logout)
6. **Signature Verification**: Tampered tokens are rejected

### ⚠️ Production Enhancements Needed

1. **Environment Variables**: Load SECRET_KEY from `.env` file
   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()
   SECRET_KEY = os.getenv("JWT_SECRET_KEY")
   ```

2. **Redis for Blacklist**: Use Redis instead of in-memory set
   ```python
   import redis

   redis_client = redis.Redis(host='localhost', port=6379)

   def revoke_token(token: str):
       # Store with TTL = token expiry
       redis_client.setex(f"blacklist:{token}", 3600, "revoked")
   ```

3. **HTTPS Only**: Never send JWT over HTTP in production

4. **HttpOnly Cookies**: Store refresh tokens in HttpOnly cookies
   ```python
   response.set_cookie(
       "refresh_token",
       value=refresh_token,
       httponly=True,
       secure=True,  # HTTPS only
       samesite="strict"
   )
   ```

5. **Stronger Algorithm**: Consider RS256 (RSA) for production
   ```python
   # Generate RSA keys
   from cryptography.hazmat.primitives.asymmetric import rsa

   private_key = rsa.generate_private_key(
       public_exponent=65537,
       key_size=2048
   )
   ```

## 🎯 Use Cases in Ticket Management System

### Login Endpoint
```python
@app.post("/auth/login")
async def login(credentials: LoginRequest):
    # Validate credentials...
    access_token = create_access_token({
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    })
    refresh_token = create_refresh_token(user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}
```

### Protected Endpoint
```python
@app.get("/tickets")
async def get_tickets(token: str = Depends(get_bearer_token)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_role = payload["role"]
    # Role-based filtering...
    return tickets
```

### Token Refresh
```python
@app.post("/auth/refresh")
async def refresh(refresh_token: str):
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Generate new access token
    new_access_token = create_access_token({
        "user_id": payload["sub"],
        # Fetch latest user data from DB...
    })
    return {"access_token": new_access_token}
```

### Logout
```python
@app.post("/auth/logout")
async def logout(token: str = Depends(get_bearer_token)):
    revoke_token(token)
    return {"message": "Logged out successfully"}
```

## 📚 Additional Resources

- **PyJWT Documentation**: https://pyjwt.readthedocs.io/
- **JWT.io**: https://jwt.io/ (Token decoder and debugger)
- **RFC 7519**: https://tools.ietf.org/html/rfc7519 (JWT Standard)

## 🤔 Common Questions

**Q: Why not store tokens in localStorage?**
A: localStorage is vulnerable to XSS attacks. Use memory or HttpOnly cookies.

**Q: How to handle token expiration in frontend?**
A: Intercept 401 responses, use refresh token to get new access token, retry request.

**Q: Can I revoke a JWT immediately?**
A: Not by default (stateless), but you can use a blacklist (requires state).

**Q: What if SECRET_KEY is compromised?**
A: All tokens become invalid. Rotate key and force all users to re-login.

**Q: Should I store user data in JWT?**
A: Only non-sensitive, minimal data. Don't store passwords or sensitive info.

## 🎓 Next Steps

After understanding this demo:

1. Integrate with **FastAPI** authentication
2. Implement **Redis** token blacklist
3. Add **password hashing** (bcrypt)
4. Create **middleware** for automatic token verification
5. Implement **role-based access control (RBAC)**

Check the ticket-management system's full authentication implementation in the main backend code!
