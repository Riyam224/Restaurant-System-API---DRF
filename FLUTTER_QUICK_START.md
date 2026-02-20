# Flutter Firebase Auth - Quick Start Guide

## 🚀 Quick Setup (5 Steps)

### 1. Add to `pubspec.yaml`

```yaml
dependencies:
  firebase_core: ^3.3.0
  firebase_auth: ^5.1.4
  google_sign_in: ^6.2.1
  http: ^1.2.0
  shared_preferences: ^2.2.3
```

Run: `flutter pub get`

### 2. Initialize Firebase in `main.dart`

```dart
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}
```

### 3. Create `lib/services/auth_service.dart`

```dart
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();

  // TODO: Change this to your production URL
  static const String baseUrl = 'http://localhost:8000/api';

  /// Sign in with Google
  Future<Map<String, dynamic>?> signInWithGoogle() async {
    try {
      // 1. Google Sign-In
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) return null;

      // 2. Get Google Auth
      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;

      // 3. Create Firebase credential
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // 4. Sign in to Firebase
      final UserCredential userCredential =
          await _auth.signInWithCredential(credential);

      // 5. Get Firebase ID token
      final String? idToken = await userCredential.user?.getIdToken();
      if (idToken == null) throw Exception('Failed to get ID token');

      // 6. Send to Django backend
      final response = await http.post(
        Uri.parse('$baseUrl/accounts/auth/google'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'id_token': idToken}),
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
        throw Exception('Authentication failed');
      }
    } catch (e) {
      print('Error: $e');
      rethrow;
    }
  }

  Future<void> _storeTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', accessToken);
    await prefs.setString('refresh_token', refreshToken);
  }

  Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  Future<void> signOut() async {
    await _auth.signOut();
    await _googleSignIn.signOut();
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
  }

  /// Make authenticated API requests
  Future<http.Response> authenticatedRequest({
    required String url,
    required String method,
    Object? body,
  }) async {
    final token = await getAccessToken();
    if (token == null) throw Exception('Not authenticated');

    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };

    switch (method.toUpperCase()) {
      case 'GET':
        return await http.get(Uri.parse(url), headers: headers);
      case 'POST':
        return await http.post(Uri.parse(url), headers: headers, body: body);
      case 'PUT':
        return await http.put(Uri.parse(url), headers: headers, body: body);
      case 'DELETE':
        return await http.delete(Uri.parse(url), headers: headers);
      default:
        throw Exception('Unsupported method: $method');
    }
  }
}
```

### 4. Create Login Button Widget

```dart
import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class GoogleSignInButton extends StatefulWidget {
  final VoidCallback onSuccess;

  const GoogleSignInButton({Key? key, required this.onSuccess})
      : super(key: key);

  @override
  State<GoogleSignInButton> createState() => _GoogleSignInButtonState();
}

class _GoogleSignInButtonState extends State<GoogleSignInButton> {
  final AuthService _authService = AuthService();
  bool _isLoading = false;

  Future<void> _handleSignIn() async {
    setState(() => _isLoading = true);

    try {
      final result = await _authService.signInWithGoogle();

      if (result != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Welcome ${result['user']['first_name']}!'),
            backgroundColor: Colors.green,
          ),
        );
        widget.onSuccess();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Sign in failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return _isLoading
        ? const CircularProgressIndicator()
        : ElevatedButton.icon(
            onPressed: _handleSignIn,
            icon: const Icon(Icons.login),
            label: const Text('Sign in with Google'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(
                horizontal: 24,
                vertical: 12,
              ),
            ),
          );
  }
}
```

### 5. Use in Your App

```dart
// In your login screen
GoogleSignInButton(
  onSuccess: () {
    // Navigate to home screen
    Navigator.pushReplacementNamed(context, '/home');
  },
)

// Make authenticated API calls
final authService = AuthService();
final response = await authService.authenticatedRequest(
  url: '${AuthService.baseUrl}/accounts/profile',
  method: 'GET',
);

if (response.statusCode == 200) {
  final user = json.decode(response.body);
  print('Email: ${user['email']}');
}
```

## 📡 API Endpoint

**URL**: `POST http://localhost:8000/api/accounts/auth/google`

**Request**:
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response**:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
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

## 🎯 What Happens

1. **Flutter**: User clicks "Sign in with Google"
2. **Google**: User selects Google account
3. **Firebase**: Authenticates with Firebase
4. **Flutter**: Gets Firebase ID token
5. **Django**: Verifies token with Firebase Admin SDK
6. **Django**: Creates/updates user in database
7. **Django**: Returns JWT tokens
8. **Flutter**: Stores JWT tokens for future API calls

## ✅ Testing Checklist

- [ ] Firebase initialized in Flutter
- [ ] Google Sign-In working
- [ ] Firebase ID token received
- [ ] Backend endpoint returns JWT tokens
- [ ] Tokens stored in SharedPreferences
- [ ] Authenticated API calls working
- [ ] Sign out clears tokens

## 🔧 Configuration

**Change base URL for production**:
```dart
// In auth_service.dart
static const String baseUrl = 'https://your-domain.com/api';
```

**Add to CORS (if using Flutter web)**:
```python
# In Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Add your Flutter web URL
]
```

## 📚 Resources

- Full documentation: [FIREBASE_AUTH_INTEGRATION.md](FIREBASE_AUTH_INTEGRATION.md)
- API docs: http://localhost:8000/api/schema/swagger-ui/
- Backend code: [accounts/views.py](accounts/views.py#L408-L457)

## 🆘 Need Help?

**Common errors:**

1. **"Invalid Google token"** → Make sure you're sending Firebase ID token, not Google token
2. **"Token expired"** → Tokens expire after 1 hour, get a new one
3. **CORS errors** → Add your URL to `CORS_ALLOWED_ORIGINS` in Django settings
4. **No ID token** → Check Firebase initialization

**Debug tips:**
```dart
// Print the ID token to verify it's correct
print('Firebase ID Token: $idToken');

// Check response from backend
print('Response status: ${response.statusCode}');
print('Response body: ${response.body}');
```

That's it! You're ready to integrate Firebase Google Sign-In with your Django API. 🎉
