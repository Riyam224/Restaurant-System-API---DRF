#!/usr/bin/env python3
"""
Test script for Firebase Google Authentication endpoint.

This script helps you verify that the Google Auth endpoint is working correctly.

IMPORTANT: You need a real Firebase ID token to test this.
To get one, follow these steps:

1. Run your Flutter app in debug mode
2. Add this line after getting the ID token in signInWithGoogle():
   print('Firebase ID Token: $idToken');
3. Copy the token from the console
4. Run this script: python test_google_auth.py YOUR_TOKEN_HERE
"""

import requests
import json
import sys


def test_google_auth(id_token):
    """Test the Google Auth endpoint with a Firebase ID token."""

    # API endpoint
    url = "http://localhost:8000/api/accounts/auth/google"

    # Request payload
    payload = {"id_token": id_token}

    # Headers
    headers = {"Content-Type": "application/json"}

    print("=" * 80)
    print("Testing Google Authentication Endpoint")
    print("=" * 80)
    print(f"\nEndpoint: {url}")
    print(f"\nPayload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")

    try:
        # Make the request
        response = requests.post(url, json=payload, headers=headers)

        print(f"\nStatus Code: {response.status_code}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        print(f"\nResponse Body:")
        try:
            data = response.json()
            print(json.dumps(data, indent=2))

            if response.status_code == 200:
                print("\n" + "=" * 80)
                print("✅ SUCCESS! Google Authentication is working correctly.")
                print("=" * 80)
                print(f"\n✅ Access Token: {data.get('access', 'N/A')[:50]}...")
                print(f"✅ Refresh Token: {data.get('refresh', 'N/A')[:50]}...")
                print(f"\n✅ User Information:")
                user = data.get("user", {})
                print(f"   - ID: {user.get('id')}")
                print(f"   - Email: {user.get('email')}")
                print(f"   - Name: {user.get('first_name')} {user.get('last_name')}")
                print(f"   - Username: {user.get('username')}")
                print(f"   - Avatar: {user.get('avatar', 'N/A')[:50]}...")
                print(f"   - Role: {user.get('role')}")
                print(f"   - Verified: {user.get('is_verified')}")
                print(f"\n✅ User Created: {data.get('created')}")

                # Test the access token
                print("\n" + "=" * 80)
                print("Testing Access Token - Fetching User Profile")
                print("=" * 80)
                test_access_token(data.get("access"))

            else:
                print("\n" + "=" * 80)
                print("❌ FAILED! Authentication endpoint returned an error.")
                print("=" * 80)
                print("\nError Details:")
                for key, value in data.items():
                    print(f"  {key}: {value}")

        except json.JSONDecodeError:
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 80)
        print("❌ CONNECTION ERROR!")
        print("=" * 80)
        print("\nMake sure your Django server is running:")
        print("  python manage.py runserver")

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR!")
        print("=" * 80)
        print(f"\nError: {str(e)}")


def test_access_token(access_token):
    """Test the JWT access token by fetching user profile."""

    url = "http://localhost:8000/api/accounts/profile"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    print(f"\nEndpoint: {url}")
    print(f"Authorization: Bearer {access_token[:30]}...")

    try:
        response = requests.get(url, headers=headers)

        print(f"\nStatus Code: {response.status_code}")
        print(f"\nResponse Body:")
        data = response.json()
        print(json.dumps(data, indent=2))

        if response.status_code == 200:
            print("\n✅ Access token is valid! Successfully fetched user profile.")
        else:
            print("\n❌ Access token validation failed!")

    except Exception as e:
        print(f"\n❌ Error testing access token: {str(e)}")


def check_backend_status():
    """Check if the Django backend is running."""

    try:
        response = requests.get("http://localhost:8000/api/schema/swagger-ui/")
        if response.status_code == 200:
            print("✅ Django backend is running")
            return True
    except:
        pass

    print("❌ Django backend is not running")
    print("\nPlease start the server:")
    print("  python manage.py runserver")
    return False


def main():
    """Main function."""

    print("\n" + "=" * 80)
    print("Firebase Google Auth - Backend Test Script")
    print("=" * 80)

    # Check backend status
    print("\nChecking backend status...")
    if not check_backend_status():
        return

    # Get token from command line or prompt user
    if len(sys.argv) > 1:
        id_token = sys.argv[1]
    else:
        print("\n" + "=" * 80)
        print("How to get a Firebase ID Token:")
        print("=" * 80)
        print("""
1. In your Flutter app's auth_service.dart, add this debug print:

   final String? idToken = await userCredential.user?.getIdToken();
   print('DEBUG - Firebase ID Token: $idToken');  // ADD THIS LINE

2. Run your Flutter app and sign in with Google

3. Copy the token from the debug console

4. Run this script again:
   python test_google_auth.py YOUR_TOKEN_HERE
        """)

        print("\nOr paste the token now:")
        id_token = input("Firebase ID Token: ").strip()

        if not id_token:
            print("\n❌ No token provided. Exiting.")
            return

    # Test the endpoint
    test_google_auth(id_token)

    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
