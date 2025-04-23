import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/product.dart';

class ApiConnector {
  static final ApiConnector _instance = ApiConnector._internal();
  static const String _baseUrl =
      'https://valkyrie.02loveslollipop.uk/v1'; // Replace with your actual API URL
  static const String _tokenKey = 'mipedido_access_token';
  static const String _userIdKey = 'mipedido_user_id';
  static const String _restaurantIdKey = 'mipedido_restaurant_id';

  String? _accessToken;
  String? _userId;
  String? _restaurantId;
  bool _isInitialized = false;

  // Private constructor
  ApiConnector._internal();

  // Factory constructor to return the same instance
  factory ApiConnector() {
    return _instance;
  }

  // Initialize the connector (load saved token)
  Future<bool> initialize() async {
    if (_isInitialized) return true;

    final prefs = await SharedPreferences.getInstance();
    _accessToken = prefs.getString(_tokenKey);
    _userId = prefs.getString(_userIdKey);
    _restaurantId = prefs.getString(_restaurantIdKey);
    _isInitialized = true;

    return isLoggedIn();
  }

  // Check if user is logged in
  bool isLoggedIn() {
    return _accessToken != null && _userId != null;
  }

  // Get the current user ID
  String? get userId => _userId;

  // Get the current restaurant ID
  String? get restaurantId => _restaurantId;

  // Login endpoint
  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/user/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      // Save token and user ID
      _accessToken = responseData['access_token'];
      _userId = responseData['user_id'];

      // Save to persistent storage
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_tokenKey, _accessToken!);
      await prefs.setString(_userIdKey, _userId!);

      // Get the user's restaurant after successful login
      final restaurantResult = await getUserRestaurant();
      if (restaurantResult['success'] &&
          restaurantResult['restaurant_id'] != null) {
        _restaurantId = restaurantResult['restaurant_id'];
        await prefs.setString(_restaurantIdKey, _restaurantId!);
      }

      return {
        'success': true,
        'user_id': _userId,
        'restaurant_id': _restaurantId,
      };
    } else if (response.statusCode == 404) {
      return {'success': false, 'error': 'User not found'};
    } else if (response.statusCode == 401) {
      return {'success': false, 'error': 'Invalid credentials'};
    } else if (response.statusCode == 500) {
      return {'success': false, 'error': 'Server error'};
    } else {
      return {
        'success': false,
        'error': responseData['error'] ?? 'Unknown error occurred',
      };
    }
  }

  // Logout function
  Future<void> logout() async {
    _accessToken = null;
    _userId = null;
    _restaurantId = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userIdKey);
    await prefs.remove(_restaurantIdKey);
  }

  // Get User Restaurant endpoint
  Future<Map<String, dynamic>> getUserRestaurant() async {
    if (_accessToken == null) {
      return {'success': false, 'error': 'Not authenticated'};
    }

    final response = await http.get(
      Uri.parse('$_baseUrl/user/restaurant'),
      headers: {
        'Authorization': 'Bearer $_accessToken',
        'Content-Type': 'application/json',
      },
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return {'success': true, 'restaurant_id': responseData['restaurant_id']};
    } else if (response.statusCode == 404) {
      return {'success': false, 'error': 'No restaurant found for this user'};
    } else if (response.statusCode == 401) {
      return {'success': false, 'error': 'Invalid authentication credentials'};
    } else {
      return {
        'success': false,
        'error': responseData['detail'] ?? 'Unknown error occurred',
      };
    }
  }

  // Get products by restaurant
  Future<Map<String, dynamic>> getProductsByRestaurant(
    String restaurantId,
  ) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/products/$restaurantId'),
      headers: {'Content-Type': 'application/json'},
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return {'success': true, 'products': responseData};
    } else {
      return {
        'success': false,
        'error': responseData['error'] ?? 'Unknown error occurred',
      };
    }
  }

  // Close order and get final order details
  Future<Map<String, dynamic>> closeOrder(String orderId) async {
    if (_accessToken == null) {
      return {'success': false, 'error': 'Not authenticated'};
    }

    final response = await http.put(
      Uri.parse('$_baseUrl/order/$orderId'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $_accessToken',
      },
      body: jsonEncode({'access_token': _accessToken}),
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return {'success': true, 'orderData': responseData};
    } else {
      return {
        'success': false,
        'error': responseData['error'] ?? 'Unknown error occurred',
      };
    }
  }

  // Disable product
  Future<Map<String, dynamic>> disableProduct(
    String restaurantId,
    String productId,
  ) async {
    if (_accessToken == null) {
      return {'success': false, 'error': 'Not authenticated'};
    }

    final response = await http.delete(
      Uri.parse('$_baseUrl/products/$restaurantId/$productId'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $_accessToken',
      },
      body: jsonEncode({'access_token': _accessToken}),
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return {'success': true, 'status': responseData['status']};
    } else {
      return {
        'success': false,
        'error': responseData['error'] ?? 'Unknown error occurred',
      };
    }
  }

  // Enable product
  Future<Map<String, dynamic>> enableProduct(
    String restaurantId,
    String productId,
  ) async {
    if (_accessToken == null) {
      return {'success': false, 'error': 'Not authenticated'};
    }

    final response = await http.put(
      Uri.parse('$_baseUrl/products/$restaurantId/$productId/enable'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $_accessToken',
      },
      body: jsonEncode({'access_token': _accessToken}),
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return {'success': true, 'status': responseData['status'] ?? 'Enabled'};
    } else {
      return {
        'success': false,
        'error': responseData['error'] ?? 'Unknown error occurred',
      };
    }
  }

  // Get product details
  Future<Map<String, dynamic>> getProductDetails(
    String restaurantId,
    String productId,
  ) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/products/$restaurantId/$productId'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': _accessToken != null ? 'Bearer $_accessToken' : '',
      },
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return {'success': true, 'product': Product.fromJson(responseData)};
    } else {
      return {
        'success': false,
        'error': responseData['error'] ?? 'Unknown error occurred',
      };
    }
  }

  // Get products by restaurant with disabled status
  Future<Map<String, dynamic>> getProductsWithStatus(
    String restaurantId,
  ) async {
    if (_accessToken == null) {
      return {'success': false, 'error': 'Not authenticated'};
    }

    final response = await http.get(
      Uri.parse('$_baseUrl/products/$restaurantId'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $_accessToken',
      },
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      final List<Product> products =
          (responseData as List).map((item) => Product.fromJson(item)).toList();

      return {'success': true, 'products': products};
    } else {
      return {
        'success': false,
        'error':
            responseData['detail'] ??
            responseData['error'] ??
            'Unknown error occurred',
      };
    }
  }
}
