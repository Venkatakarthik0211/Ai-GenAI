"""
JWT Token Creation and Verification Demo using PyJWT
=====================================================

This demo shows how to:
1. Generate JWT access and refresh tokens
2. Verify and decode tokens
3. Handle token expiration
4. Implement token refresh logic
5. Blacklist tokens (logout simulation)

Requirements:
    pip install pyjwt cryptography python-dotenv

Run: python jwt_demo.py
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import secrets
import json


# ============================================================================
# CONFIGURATION - In production, load from environment variables
# ============================================================================

SECRET_KEY = secrets.token_urlsafe(32)  # Generate random secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Simulate token blacklist (In production: use Redis)
TOKEN_BLACKLIST = set()


# ============================================================================
# TOKEN GENERATION FUNCTIONS
# ============================================================================

def create_access_token(user_data: dict) -> str:
    """
    Create a short-lived JWT access token

    Args:
        user_data: Dictionary containing user information
                  Example: {"user_id": "123", "username": "john", "role": "DEVOPS_ENGINEER"}

    Returns:
        Encoded JWT token string
    """
    # Copy data to avoid modifying original
    payload = user_data.copy()

    # Add standard JWT claims
    now = datetime.utcnow()
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload.update({
        "exp": expire,          # Expiration time
        "iat": now,             # Issued at
        "nbf": now,             # Not before
        "type": "access",       # Token type
        "jti": secrets.token_urlsafe(16)  # JWT ID (unique identifier)
    })

    # Encode and sign token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    print(f"\n✅ Access Token Created:")
    print(f"   User ID: {user_data.get('user_id')}")
    print(f"   Username: {user_data.get('username')}")
    print(f"   Role: {user_data.get('role')}")
    print(f"   Expires: {expire.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"   Token: {token[:50]}...")

    return token


def create_refresh_token(user_id: str) -> str:
    """
    Create a long-lived JWT refresh token

    Args:
        user_id: User identifier

    Returns:
        Encoded JWT refresh token string
    """
    now = datetime.utcnow()
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user_id,         # Subject (user ID)
        "exp": expire,
        "iat": now,
        "type": "refresh",
        "jti": secrets.token_urlsafe(16)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    print(f"\n✅ Refresh Token Created:")
    print(f"   User ID: {user_id}")
    print(f"   Expires: {expire.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"   Token: {token[:50]}...")

    return token


# ============================================================================
# TOKEN VERIFICATION FUNCTIONS
# ============================================================================

def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded payload dictionary if valid, None if invalid
    """
    try:
        # Check if token is blacklisted
        if token in TOKEN_BLACKLIST:
            print(f"\n❌ Token Verification Failed: Token has been revoked (logged out)")
            return None

        # Decode and verify token
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "verify_exp": True,  # Verify expiration
                "verify_iat": True,  # Verify issued at
                "verify_nbf": True,  # Verify not before
            }
        )

        # Verify token type
        if payload.get("type") != token_type:
            print(f"\n❌ Token Verification Failed: Expected {token_type} token, got {payload.get('type')}")
            return None

        print(f"\n✅ Token Verified Successfully:")
        print(f"   Type: {payload.get('type')}")
        print(f"   User ID: {payload.get('user_id') or payload.get('sub')}")
        print(f"   Issued At: {datetime.fromtimestamp(payload['iat']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Expires At: {datetime.fromtimestamp(payload['exp']).strftime('%Y-%m-%d %H:%M:%S')}")

        return payload

    except jwt.ExpiredSignatureError:
        print(f"\n❌ Token Verification Failed: Token has expired")
        return None

    except jwt.InvalidTokenError as e:
        print(f"\n❌ Token Verification Failed: {str(e)}")
        return None


def decode_token_without_verification(token: str) -> Dict:
    """
    Decode token WITHOUT verification (for debugging only)

    Args:
        token: JWT token string

    Returns:
        Decoded payload dictionary
    """
    try:
        # Decode without verifying signature or expiration
        payload = jwt.decode(
            token,
            options={"verify_signature": False, "verify_exp": False}
        )
        return payload
    except Exception as e:
        print(f"\n❌ Failed to decode token: {str(e)}")
        return {}


# ============================================================================
# TOKEN MANAGEMENT FUNCTIONS
# ============================================================================

def refresh_access_token(refresh_token: str, user_data: dict) -> Optional[str]:
    """
    Generate new access token using refresh token

    Args:
        refresh_token: Valid refresh token
        user_data: User information for new access token

    Returns:
        New access token if refresh token is valid, None otherwise
    """
    # Verify refresh token
    payload = verify_token(refresh_token, token_type="refresh")

    if payload is None:
        print("\n❌ Cannot refresh: Invalid refresh token")
        return None

    # Generate new access token
    print("\n🔄 Generating new access token...")
    new_access_token = create_access_token(user_data)

    return new_access_token


def revoke_token(token: str) -> bool:
    """
    Revoke token (logout) - Add to blacklist

    Args:
        token: JWT token to revoke

    Returns:
        True if successfully revoked
    """
    TOKEN_BLACKLIST.add(token)
    print(f"\n🚫 Token Revoked (Logged Out)")
    print(f"   Token added to blacklist")
    print(f"   Total blacklisted tokens: {len(TOKEN_BLACKLIST)}")
    return True


# ============================================================================
# DEMO SCENARIOS
# ============================================================================

def demo_login_flow():
    """Demonstrate complete login flow with token generation"""
    print("\n" + "="*70)
    print("DEMO 1: Login Flow - Generate Tokens")
    print("="*70)

    # Simulate user login
    user_data = {
        "user_id": "usr_123456",
        "username": "john.doe",
        "email": "john.doe@example.com",
        "role": "DEVOPS_ENGINEER",
        "department": "Infrastructure"
    }

    # Generate tokens
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data["user_id"])

    print(f"\n📦 Login Response:")
    print(json.dumps({
        "access_token": access_token[:50] + "...",
        "refresh_token": refresh_token[:50] + "...",
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }, indent=2))

    return access_token, refresh_token


def demo_token_verification(access_token: str):
    """Demonstrate token verification"""
    print("\n" + "="*70)
    print("DEMO 2: Token Verification - Authenticated Request")
    print("="*70)

    # Simulate authenticated API request
    print("\n📨 Incoming API Request:")
    print(f"   Authorization: Bearer {access_token[:50]}...")

    # Verify token
    payload = verify_token(access_token, token_type="access")

    if payload:
        print(f"\n✅ Request Authorized!")
        print(f"   Authenticated as: {payload.get('username')}")
        print(f"   Role: {payload.get('role')}")


def demo_token_inspection(token: str):
    """Demonstrate token structure inspection"""
    print("\n" + "="*70)
    print("DEMO 3: Token Structure Inspection")
    print("="*70)

    # Split token into parts
    parts = token.split('.')
    print(f"\n🔍 Token Structure:")
    print(f"   Total Parts: {len(parts)}")
    print(f"   Part 1 (Header):    {parts[0][:40]}...")
    print(f"   Part 2 (Payload):   {parts[1][:40]}...")
    print(f"   Part 3 (Signature): {parts[2][:40]}...")

    # Decode without verification (for inspection only)
    payload = decode_token_without_verification(token)
    print(f"\n📋 Decoded Payload (Unverified):")
    print(json.dumps(payload, indent=2, default=str))


def demo_token_refresh(refresh_token: str):
    """Demonstrate token refresh flow"""
    print("\n" + "="*70)
    print("DEMO 4: Token Refresh - Access Token Expired")
    print("="*70)

    print("\n⏰ Scenario: Access token expired, need new one")

    user_data = {
        "user_id": "usr_123456",
        "username": "john.doe",
        "role": "DEVOPS_ENGINEER"
    }

    # Use refresh token to get new access token
    new_access_token = refresh_access_token(refresh_token, user_data)

    if new_access_token:
        print(f"\n✅ New access token issued successfully")
        return new_access_token


def demo_token_expiration():
    """Demonstrate token expiration handling"""
    print("\n" + "="*70)
    print("DEMO 5: Token Expiration - Expired Token Handling")
    print("="*70)

    # Create token with very short expiration (1 second)
    print("\n⏱️  Creating token with 1-second expiration...")

    payload = {"user_id": "usr_test", "username": "test_user"}
    now = datetime.utcnow()
    expire = now + timedelta(seconds=1)

    payload.update({
        "exp": expire,
        "iat": now,
        "type": "access"
    })

    expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"   Token created: {expired_token[:50]}...")

    # Wait for expiration
    import time
    print(f"\n⏳ Waiting 2 seconds for token to expire...")
    time.sleep(2)

    # Try to verify expired token
    print(f"\n🔍 Attempting to verify expired token...")
    verify_token(expired_token)


def demo_token_logout(access_token: str, refresh_token: str):
    """Demonstrate logout (token revocation)"""
    print("\n" + "="*70)
    print("DEMO 6: Logout - Token Revocation")
    print("="*70)

    # Revoke tokens
    print("\n🚪 User logging out...")
    revoke_token(access_token)
    revoke_token(refresh_token)

    # Try to use revoked token
    print(f"\n🔍 Attempting to use revoked access token...")
    verify_token(access_token)


def demo_invalid_signature():
    """Demonstrate invalid signature detection"""
    print("\n" + "="*70)
    print("DEMO 7: Security - Invalid Signature Detection")
    print("="*70)

    # Create valid token
    user_data = {"user_id": "usr_456", "username": "jane.doe"}
    valid_token = create_access_token(user_data)

    # Tamper with token (modify payload)
    print(f"\n⚠️  Attempting to tamper with token...")
    parts = valid_token.split('.')

    # Decode payload and modify it
    import base64
    payload_bytes = base64.urlsafe_b64decode(parts[1] + '==')  # Add padding
    payload_dict = json.loads(payload_bytes)

    # Change user_id
    print(f"   Original user_id: {payload_dict['user_id']}")
    payload_dict['user_id'] = "usr_hacker"
    print(f"   Tampered user_id: {payload_dict['user_id']}")

    # Encode modified payload
    tampered_payload = base64.urlsafe_b64encode(
        json.dumps(payload_dict).encode()
    ).decode().rstrip('=')

    # Create tampered token (same signature, different payload)
    tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

    print(f"\n🔍 Verifying tampered token...")
    verify_token(tampered_token)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all JWT demonstrations"""
    print("\n" + "🔐"*35)
    print("JWT TOKEN DEMONSTRATION - PyJWT Library")
    print("🔐"*35)

    print(f"\n⚙️  Configuration:")
    print(f"   Secret Key: {SECRET_KEY[:20]}... (randomly generated)")
    print(f"   Algorithm: {ALGORITHM}")
    print(f"   Access Token Expiry: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"   Refresh Token Expiry: {REFRESH_TOKEN_EXPIRE_DAYS} days")

    # Run demonstrations
    access_token, refresh_token = demo_login_flow()
    demo_token_verification(access_token)
    demo_token_inspection(access_token)
    new_access_token = demo_token_refresh(refresh_token)
    demo_token_expiration()
    demo_token_logout(access_token, refresh_token)
    demo_invalid_signature()

    print("\n" + "="*70)
    print("✅ All Demonstrations Completed!")
    print("="*70)
    print("\nKey Takeaways:")
    print("1. JWT tokens are self-contained (no database lookup needed)")
    print("2. Tokens are cryptographically signed (tamper-proof)")
    print("3. Expiration is enforced automatically")
    print("4. Refresh tokens enable seamless token renewal")
    print("5. Token blacklist enables logout functionality")
    print("6. Invalid signatures are detected immediately")
    print("\n💡 In production:")
    print("   - Load SECRET_KEY from environment variables")
    print("   - Use Redis for token blacklist")
    print("   - Implement HTTPS for all communications")
    print("   - Store refresh tokens in HttpOnly cookies")
    print("   - Use shorter access token expiration (5-15 min)")


if __name__ == "__main__":
    main()
