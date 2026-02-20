# Firebase Google Sign-In Integration Guide

## 🎯 Overview

Your Django API is fully configured with Firebase Google Sign-In authentication. This guide explains how to integrate it with your Flutter app.

## ✅ What's Already Implemented (Backend)

### 1. Firebase Admin SDK Setup
- **Location**: [config/settings.py](config/settings.py#L15-L31)
- Firebase Admin SDK is initialized and ready to verify tokens
- Supports both development (file-based) and production (environment variable) credentials

### 2. Google OAuth Service
- **Location**: [accounts/services.py](accounts/services.py#L19-L99)
- Verifies Firebase ID tokens using Firebase Admin SDK
- Extracts user information (email, name, avatar, etc.)
- Handles token validation errors (expired, revoked, invalid)

### 3. User Service
- **Location**: [accounts/services.py](accounts/services.py#L101-L185)
- Creates new users or updates existing ones from Google data
- Auto-generates unique usernames from email
- Marks users as verified when Google confirms email
- Updates user profile (name, avatar) on each login

### 4. Authentication Endpoint
- **Location**: [accounts/views.py](accounts/views.py#L408-L457)
- **URL**: `POST /api/accounts/auth/google`
- Returns JWT tokens for authenticated sessions

## 📡 API Endpoint Details

### Endpoint: Google Authentication
```
POST /api/accounts/auth/google
```

#### Request Body
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE4MmU0M2NkZGY2N..."
}
```

#### Success Response (200 OK)
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar": "https://lh3.googleusercontent.com/...",
    "phone": null,
    "role": "customer",
    "is_verified": true
  },
  "created": false
}
```

#### Error Response (400 Bad Request)
```json
{
  "id_token": ["Invalid Google token: Token expired"]
}
```

## 📱 Flutter Integration Guide

### Step 1: Add Dependencies

Add these packages to your `pubspec.yaml`:

```yaml
dependencies:
  firebase_core: ^3.3.0
  firebase_auth: ^5.1.4
  google_sign_in: ^6.2.1
  http: ^1.2.0
  shared_preferences: ^2.2.3  # For storing JWT tokens
```

### Step 2: Configure Firebase in Flutter

1. Add your `google-services.json` (Android) and `GoogleService-Info.plist` (iOS) to your Flutter project
2. Initialize Firebase in your `main.dart`:

```dart
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(MyApp());
}
```

### Step 3: Create Authentication Service

Create `lib/services/auth_service.dart`:

```dart
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();

  // Your Django API base URL
  static const String baseUrl = 'http://localhost:8000/api'; // Change for production

  /// Sign in with Google and authenticate with Django backend
  Future<Map<String, dynamic>?> signInWithGoogle() async {
    try {
      // 1. Trigger Google Sign-In flow
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();

      if (googleUser == null) {
        // User canceled the sign-in
        return null;
      }

      // 2. Obtain Google Sign-In authentication details
      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;

      // 3. Create Firebase credential
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // 4. Sign in to Firebase (to get the Firebase ID token)
      final UserCredential userCredential =
          await _auth.signInWithCredential(credential);

      // 5. Get Firebase ID token
      final String? idToken = await userCredential.user?.getIdToken();

      if (idToken == null) {
        throw Exception('Failed to get ID token');
      }

      // 6. Send Firebase ID token to Django backend
      final response = await http.post(
        Uri.parse('$baseUrl/accounts/auth/google'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'id_token': idToken,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // 7. Store JWT tokens
        await _storeTokens(
          accessToken: data['access'],
          refreshToken: data['refresh'],
        );

        return data;
      } else {
        final error = json.decode(response.body);
        throw Exception(error['id_token']?[0] ?? 'Authentication failed');
      }
    } catch (e) {
      print('Error signing in with Google: $e');
      rethrow;
    }
  }

  /// Store JWT tokens in SharedPreferences
  Future<void> _storeTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', accessToken);
    await prefs.setString('refresh_token', refreshToken);
  }

  /// Get stored access token
  Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  /// Get stored refresh token
  Future<String?> getRefreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('refresh_token');
  }

  /// Refresh access token
  Future<String?> refreshAccessToken() async {
    final refreshToken = await getRefreshToken();

    if (refreshToken == null) {
      return null;
    }

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/accounts/auth/refresh'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'refresh': refreshToken,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final newAccessToken = data['access'];

        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('access_token', newAccessToken);

        return newAccessToken;
      }
    } catch (e) {
      print('Error refreshing token: $e');
    }

    return null;
  }

  /// Sign out
  Future<void> signOut() async {
    await _auth.signOut();
    await _googleSignIn.signOut();

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
  }

  /// Check if user is authenticated
  Future<bool> isAuthenticated() async {
    final token = await getAccessToken();
    return token != null;
  }

  /// Make authenticated API request
  Future<http.Response> authenticatedRequest({
    required String url,
    required String method,
    Map<String, String>? headers,
    Object? body,
  }) async {
    String? accessToken = await getAccessToken();

    if (accessToken == null) {
      throw Exception('No access token available');
    }

    final requestHeaders = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
      ...?headers,
    };

    http.Response response;

    switch (method.toUpperCase()) {
      case 'GET':
        response = await http.get(
          Uri.parse(url),
          headers: requestHeaders,
        );
        break;
      case 'POST':
        response = await http.post(
          Uri.parse(url),
          headers: requestHeaders,
          body: body,
        );
        break;
      case 'PUT':
        response = await http.put(
          Uri.parse(url),
          headers: requestHeaders,
          body: body,
        );
        break;
      case 'DELETE':
        response = await http.delete(
          Uri.parse(url),
          headers: requestHeaders,
        );
        break;
      default:
        throw Exception('Unsupported HTTP method: $method');
    }

    // If token expired, try to refresh
    if (response.statusCode == 401) {
      final newToken = await refreshAccessToken();

      if (newToken != null) {
        // Retry request with new token
        requestHeaders['Authorization'] = 'Bearer $newToken';

        switch (method.toUpperCase()) {
          case 'GET':
            response = await http.get(
              Uri.parse(url),
              headers: requestHeaders,
            );
            break;
          case 'POST':
            response = await http.post(
              Uri.parse(url),
              headers: requestHeaders,
              body: body,
            );
            break;
          case 'PUT':
            response = await http.put(
              Uri.parse(url),
              headers: requestHeaders,
              body: body,
            );
            break;
          case 'DELETE':
            response = await http.delete(
              Uri.parse(url),
              headers: requestHeaders,
            );
            break;
        }
      }
    }

    return response;
  }
}
```

### Step 4: Create Login Screen Widget

Create `lib/screens/login_screen.dart`:

```dart
import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final AuthService _authService = AuthService();
  bool _isLoading = false;

  Future<void> _handleGoogleSignIn() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final result = await _authService.signInWithGoogle();

      if (result != null) {
        // Successfully signed in
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Welcome ${result['user']['first_name'] ?? result['user']['email']}!',
              ),
              backgroundColor: Colors.green,
            ),
          );

          // Navigate to home screen
          Navigator.pushReplacementNamed(context, '/home');
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to sign in: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sign In'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                'Welcome to Restaurant App',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              _isLoading
                  ? const CircularProgressIndicator()
                  : ElevatedButton.icon(
                      onPressed: _handleGoogleSignIn,
                      icon: Image.asset(
                        'assets/google_logo.png', // Add Google logo
                        height: 24,
                      ),
                      label: const Text('Sign in with Google'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 24,
                          vertical: 12,
                        ),
                        backgroundColor: Colors.white,
                        foregroundColor: Colors.black87,
                      ),
                    ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### Step 5: Example API Call with Authentication

```dart
// Fetch user profile
Future<void> fetchUserProfile() async {
  final authService = AuthService();

  try {
    final response = await authService.authenticatedRequest(
      url: '${AuthService.baseUrl}/accounts/profile',
      method: 'GET',
    );

    if (response.statusCode == 200) {
      final userData = json.decode(response.body);
      print('User: ${userData['email']}');
    } else {
      print('Failed to fetch profile: ${response.statusCode}');
    }
  } catch (e) {
    print('Error: $e');
  }
}
```

## 🔐 Security Best Practices

1. **HTTPS Only in Production**: Always use HTTPS for API calls in production
2. **Token Storage**: JWT tokens are stored in SharedPreferences (encrypted on iOS by default)
3. **Token Refresh**: The service automatically refreshes expired access tokens
4. **Logout**: Always call `signOut()` to clear tokens and Firebase session

## 🧪 Testing

### Test the Backend Endpoint

You can test the endpoint using curl:

```bash
# First, get a Firebase ID token from your Flutter app (print it in debug mode)
curl -X POST http://localhost:8000/api/accounts/auth/google \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "YOUR_FIREBASE_ID_TOKEN_HERE"
  }'
```

### Test in Flutter

1. Run your Flutter app
2. Click "Sign in with Google"
3. Select your Google account
4. Check the response in debug console
5. Verify JWT tokens are stored
6. Try making an authenticated API call

## 📝 Configuration Checklist

### Backend (Already Done ✅)
- [x] Firebase Admin SDK initialized
- [x] Google OAuth service implemented
- [x] User creation/update logic
- [x] JWT token generation
- [x] API endpoint configured

### Flutter (To Do)
- [ ] Add Firebase dependencies
- [ ] Configure Firebase in Flutter project
- [ ] Add `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)
- [ ] Implement AuthService
- [ ] Create login screen
- [ ] Handle authenticated requests
- [ ] Test the flow

## 🌐 Environment Variables

### Development
Your `.env` file should have:
```env
GOOGLE_OAUTH_CLIENT_ID=757978088939-e08jfccvbfn2kocnsvglgpfqgsj010m2.apps.googleusercontent.com
```

### Production
Set these environment variables:
```env
GOOGLE_OAUTH_CLIENT_ID=your_production_client_id
FIREBASE_CREDENTIALS={"type":"service_account","project_id":"..."}
```

## 🔄 Authentication Flow

```
┌─────────┐         ┌──────────┐         ┌──────────┐         ┌─────────┐
│ Flutter │         │  Google  │         │ Firebase │         │ Django  │
│   App   │         │   Auth   │         │   Auth   │         │   API   │
└────┬────┘         └─────┬────┘         └─────┬────┘         └────┬────┘
     │                    │                    │                   │
     │  1. Sign In        │                    │                   │
     ├───────────────────>│                    │                   │
     │                    │                    │                   │
     │  2. Google Token   │                    │                   │
     │<───────────────────┤                    │                   │
     │                    │                    │                   │
     │  3. Firebase Auth  │                    │                   │
     ├────────────────────┴───────────────────>│                   │
     │                                         │                   │
     │  4. Firebase ID Token                   │                   │
     │<────────────────────────────────────────┤                   │
     │                                         │                   │
     │  5. Send ID Token                       │                   │
     ├─────────────────────────────────────────┴──────────────────>│
     │                                                             │
     │  6. Verify Token with Firebase Admin SDK                   │
     │                                                             │
     │  7. Create/Update User & Generate JWT                       │
     │                                                             │
     │  8. Return JWT Tokens                                       │
     │<────────────────────────────────────────────────────────────┤
     │                                                             │
     │  9. Use JWT for API Requests                                │
     ├────────────────────────────────────────────────────────────>│
     │                                                             │
```

## 📚 API Documentation

Your API documentation is available at:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`

Look for the "Authentication" section to see the Google Auth endpoint documentation.

## 🆘 Troubleshooting

### Common Issues

1. **"Invalid Google token"**
   - Make sure you're sending the Firebase ID token, not the Google access token
   - Verify Firebase Admin SDK is properly initialized
   - Check that the token hasn't expired (tokens expire after 1 hour)

2. **"Token has expired"**
   - Implement token refresh in your Flutter app
   - Get a new ID token from Firebase

3. **"Email already exists"**
   - This is expected behavior - the user will be updated instead of created
   - Check the `created` field in response (false = existing user)

4. **CORS errors**
   - Add your Flutter web URL to `CORS_ALLOWED_ORIGINS` in settings.py
   - For mobile apps, CORS doesn't apply

## 🎉 Summary

Your backend is fully ready for Firebase Google Sign-In! Just follow the Flutter integration guide above to connect your mobile app to the API.

The integration provides:
- ✅ Secure token verification via Firebase Admin SDK
- ✅ Automatic user creation/update
- ✅ JWT token-based session management
- ✅ Profile data synchronization
- ✅ Email verification status tracking
