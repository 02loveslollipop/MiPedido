import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'dart:developer';

class ApiConnector {
  // Singleton pattern
  static final ApiConnector _instance = ApiConnector._internal();
  factory ApiConnector() => _instance;
  ApiConnector._internal();

  // Base API URL
  final String _baseUrl =
      'https://valkyrie.02loveslollipop.uk'; // Change to your actual API URL

  // Token storage keys
  final String _accessTokenKey = 'admin_access_token';
  final String _adminIdKey = 'admin_id';
  final String _adminUsernameKey = 'admin_username';

  // HTTP client
  final http.Client _client = http.Client();

  // Get stored tokens
  Future<String?> get accessToken async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_accessTokenKey);
  }

  Future<String?> get adminId async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_adminIdKey);
  }

  Future<String?> get adminUsername async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_adminUsernameKey);
  }

  // Store access token and admin info
  Future<void> _saveAuthInfo(
    String accessToken,
    String adminId,
    String username,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessTokenKey, accessToken);
    await prefs.setString(_adminIdKey, adminId);
    await prefs.setString(_adminUsernameKey, username);
  }

  // Clear auth info on logout
  Future<void> clearAuthInfo() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_accessTokenKey);
    await prefs.remove(_adminIdKey);
    await prefs.remove(_adminUsernameKey);
  }

  // Check if user is logged in
  Future<bool> isLoggedIn() async {
    final token = await accessToken;
    return token != null && token.isNotEmpty;
  }

  // Admin login
  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/v1/admin/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'username': username, 'password': password}),
      );

      final responseData = json.decode(response.body);

      if (response.statusCode == 200) {
        // Extract token and admin info
        log('Login successful: $responseData');
        final accessToken = responseData['access_token'];
        final adminId = responseData['admin_id'];
        final adminUsername =
            "admin"; //TODO: fix this to get the username from the response

        // Save token and admin info
        await _saveAuthInfo(accessToken, adminId, adminUsername);

        return {'success': true};
      } else {
        return {
          'success': false,
          'error': responseData['detail'] ?? 'Authentication failed',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }

  // Admin logout
  Future<bool> logout() async {
    try {
      await clearAuthInfo();
      return true;
    } catch (e) {
      return false;
    }
  }

  // Generic GET request with authentication
  Future<Map<String, dynamic>> get(String endpoint) async {
    try {
      final token = await accessToken;
      if (token == null) {
        return {'success': false, 'error': 'Not authenticated'};
      }

      final response = await _client.get(
        Uri.parse('$_baseUrl$endpoint'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return {'success': true, 'data': json.decode(response.body)};
      } else if (response.statusCode == 401) {
        // Token expired
        await clearAuthInfo();
        return {'success': false, 'error': 'Authentication expired'};
      } else {
        return {
          'success': false,
          'error': 'Request failed: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }

  // Generic POST request with authentication
  Future<Map<String, dynamic>> post(
    String endpoint, {
    Map<String, dynamic>? body,
  }) async {
    try {
      final token = await accessToken;
      if (token == null) {
        return {'success': false, 'error': 'Not authenticated'};
      }

      final response = await _client.post(
        Uri.parse('$_baseUrl$endpoint'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: body != null ? json.encode(body) : null,
      );

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return {'success': true, 'data': json.decode(response.body)};
      } else if (response.statusCode == 401) {
        // Token expired
        await clearAuthInfo();
        return {'success': false, 'error': 'Authentication expired'};
      } else {
        return {
          'success': false,
          'error': 'Request failed: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }

  // Generic PUT request with authentication
  Future<Map<String, dynamic>> put(
    String endpoint, {
    Map<String, dynamic>? body,
  }) async {
    try {
      final token = await accessToken;
      if (token == null) {
        return {'success': false, 'error': 'Not authenticated'};
      }

      final response = await _client.put(
        Uri.parse('$_baseUrl$endpoint'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: body != null ? json.encode(body) : null,
      );

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return {'success': true, 'data': json.decode(response.body)};
      } else if (response.statusCode == 401) {
        // Token expired
        await clearAuthInfo();
        return {'success': false, 'error': 'Authentication expired'};
      } else {
        return {
          'success': false,
          'error': 'Request failed: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }

  // Generic DELETE request with authentication
  Future<Map<String, dynamic>> delete(String endpoint) async {
    try {
      final token = await accessToken;
      if (token == null) {
        return {'success': false, 'error': 'Not authenticated'};
      }

      final response = await _client.delete(
        Uri.parse('$_baseUrl$endpoint'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return {'success': true};
      } else if (response.statusCode == 401) {
        // Token expired
        await clearAuthInfo();
        return {'success': false, 'error': 'Authentication expired'};
      } else {
        return {
          'success': false,
          'error': 'Request failed: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }

  // ========= ADMIN ENDPOINTS =========

  // Get current admin info
  Future<Map<String, dynamic>> getCurrentAdmin() async {
    return await get('/v1/admin/me');
  }

  // List all admins
  Future<Map<String, dynamic>> listAdmins() async {
    final result = await get('/v1/admin/');
    if (result['success']) {
      return {'success': true, 'admins': result['data']};
    }
    return result;
  }

  // Create a new admin
  Future<Map<String, dynamic>> createAdmin(
    String username,
    String password,
  ) async {
    return await post(
      '/v1/admin/',
      body: {'username': username, 'password': password},
    );
  }

  // Update an admin
  Future<Map<String, dynamic>> updateAdmin(
    String adminId, {
    String? username,
    String? password,
  }) async {
    Map<String, dynamic> body = {};
    if (username != null) body['username'] = username;
    if (password != null) body['password'] = password;

    return await put('/v1/admin/$adminId', body: body);
  }

  // Delete an admin
  Future<Map<String, dynamic>> deleteAdmin(String adminId) async {
    return await delete('/v1/admin/$adminId');
  }

  // ========= RESTAURANT ENDPOINTS =========

  // List all restaurants
  Future<Map<String, dynamic>> listRestaurants() async {
    final result = await get('/v1/admin/restaurants/');
    if (result['success']) {
      return {'success': true, 'restaurants': result['data']};
    }
    return result;
  }

  // Get restaurant details
  Future<Map<String, dynamic>> getRestaurant(String restaurantId) async {
    return await get('/v1/admin/restaurants/$restaurantId');
  }

  // Create a new restaurant
  Future<Map<String, dynamic>> createRestaurant(
    String name,
    String description,
    String imageUrl, {
    String? type,
    Map<String, double>? position,
  }) async {
    Map<String, dynamic> body = {
      'name': name,
      'description': description,
      'img_url': imageUrl,
      'rating': 0,
    };

    if (type != null) body['type'] = type;
    if (position != null) body['position'] = position;

    log('Create restaurant body: $body');

    Map<String, dynamic> response = await post(
      '/v1/admin/restaurants/',
      body: body,
    );

    log('Create restaurant response: $response');

    return response;
  }

  // Update a restaurant
  Future<Map<String, dynamic>> updateRestaurant(
    String restaurantId, {
    String? name,
    String? description,
    String? imageUrl,
    String? type,
    Map<String, double?>? position,
  }) async {
    Map<String, dynamic> body = {};
    if (name != null) body['name'] = name;
    if (description != null) body['description'] = description;
    if (imageUrl != null) body['img_url'] = imageUrl;
    if (type != null) body['type'] = type;
    if (position != null) body['position'] = position;

    Map<String, dynamic> response = await put('/v1/admin/restaurants/$restaurantId', body: body);

    log('Update restaurant response: $response');
    log ('Update restaurant body: $body');

    return response;
  }

  // Delete a restaurant
  Future<Map<String, dynamic>> deleteRestaurant(String restaurantId) async {
    return await delete('/v1/admin/restaurants/$restaurantId');
  }

  // Update restaurant rating
  Future<Map<String, dynamic>> updateRestaurantRating(
    String restaurantId,
    double rating,
  ) async {
    return await put(
      '/v1/admin/restaurants/$restaurantId/update-rating',
      body: {'rating': rating},
    );
  }

  // ========= PRODUCT ENDPOINTS =========

  // List products by restaurant
  Future<Map<String, dynamic>> listProductsByRestaurant(
    String restaurantId,
  ) async {
    final result = await get('/v1/admin/products/restaurant/$restaurantId');
    if (result['success']) {
      return {'success': true, 'products': result['data']};
    }
    return result;
  }

  // Get product details
  Future<Map<String, dynamic>> getProduct(String productId) async {
    return await get('/v1/admin/products/$productId');
  }

  // Create a new product
  Future<Map<String, dynamic>> createProduct({
    required String restaurantId,
    required String name,
    required String description,
    required double price,
    required String imageUrl,
    required List<String> ingredients,
  }) async {
    return await post(
      '/v1/admin/products/',
      body: {
        'restaurant_id': restaurantId,
        'name': name,
        'description': description,
        'price': price,
        'img_url': imageUrl,
        'ingredients': ingredients,
      },
    );
  }

  // Update a product
  Future<Map<String, dynamic>> updateProduct({
    required String productId,
    String? name,
    String? description,
    double? price,
    String? imageUrl,
    List<String>? ingredients,
  }) async {
    Map<String, dynamic> body = {};
    if (name != null) body['name'] = name;
    if (description != null) body['description'] = description;
    if (price != null) body['price'] = price;
    if (imageUrl != null) body['img_url'] = imageUrl;
    if (ingredients != null) body['ingredients'] = ingredients;

    return await put('/v1/admin/products/$productId', body: body);
  }

  // Delete a product
  Future<Map<String, dynamic>> deleteProduct(String productId) async {
    return await delete('/v1/admin/products/$productId');
  }

  // Enable a product
  Future<Map<String, dynamic>> enableProduct(String productId) async {
    return await put('/v1/admin/products/$productId/enable');
  }

  // Disable a product
  Future<Map<String, dynamic>> disableProduct(String productId) async {
    return await put('/v1/admin/products/$productId/disable');
  }

  // ========= USER ENDPOINTS =========

  // List all users
  Future<Map<String, dynamic>> listUsers() async {
    final result = await get('/v1/admin/users/');
    if (result['success']) {
      return {'success': true, 'users': result['data']};
    }
    return result;
  }

  // Get user details
  Future<Map<String, dynamic>> getUser(String userId) async {
    return await get('/v1/admin/users/$userId');
  }

  // Create a new user
  Future<Map<String, dynamic>> createUser(
    String username,
    String password,
  ) async {
    return await post(
      '/v1/admin/users/',
      body: {'username': username, 'password': password},
    );
  }

  // Update a user
  Future<Map<String, dynamic>> updateUser(
    String userId, {
    String? username,
    String? password,
  }) async {
    Map<String, dynamic> body = {};
    if (username != null) body['username'] = username;
    if (password != null) body['password'] = password;

    return await put('/v1/admin/users/$userId', body: body);
  }

  // Delete a user
  Future<Map<String, dynamic>> deleteUser(String userId) async {
    return await delete('/v1/admin/users/$userId');
  }

  // Assign restaurant to user
  Future<Map<String, dynamic>> assignRestaurantToUser(
    String userId,
    String restaurantId,
  ) async {
    return await put(
      '/v1/admin/users/$userId/assign-restaurant',
      body: {'restaurant_id': restaurantId},
    );
  }

  // Revoke restaurant from user
  Future<Map<String, dynamic>> revokeRestaurantFromUser(
    String userId,
    String restaurantId,
  ) async {
    return await put(
      '/v1/admin/users/$userId/revoke-restaurant',
      body: {'restaurant_id': restaurantId},
    );
  }

  // ========= ADMIN ACTIVITY LOGS =========

  // List admin logs with optional filtering
  Future<Map<String, dynamic>> getAdminLogs({
    String? adminId,
    String? adminUsername,
    String? operation,
    String? targetType,
    String? targetId,
    String? fromDate,
    String? toDate,
    int skip = 0,
    int limit = 20,
  }) async {
    Map<String, dynamic> queryParams = {
      'skip': skip.toString(),
      'limit': limit.toString(),
    };

    if (adminId != null) queryParams['admin_id'] = adminId;
    if (adminUsername != null) queryParams['admin_username'] = adminUsername;
    if (operation != null) queryParams['operation'] = operation;
    if (targetType != null) queryParams['target_type'] = targetType;
    if (targetId != null) queryParams['target_id'] = targetId;
    if (fromDate != null) queryParams['from_date'] = fromDate;
    if (toDate != null) queryParams['to_date'] = toDate;

    final queryString = Uri(queryParameters: queryParams).query;
    final result = await get('/v1/admin/logs/?$queryString');

    if (result['success']) {
      return {
        'success': true,
        'logs': result['data']['logs'],
        'total': result['data']['total'],
        'skip': result['data']['skip'],
        'limit': result['data']['limit'],
      };
    }
    return result;
  }

  // Get specific log entry
  Future<Map<String, dynamic>> getAdminLogEntry(String logId) async {
    return await get('/v1/admin/logs/$logId');
  }

  // ========= ORDER MANAGEMENT =========

  // Get all orders (with optional filters)
  Future<Map<String, dynamic>> getOrders({
    String? restaurantId,
    String? status,
    String? fromDate,
    String? toDate,
    int skip = 0,
    int limit = 20,
  }) async {
    Map<String, dynamic> queryParams = {
      'skip': skip.toString(),
      'limit': limit.toString(),
    };

    if (restaurantId != null) queryParams['restaurant_id'] = restaurantId;
    if (status != null) queryParams['status'] = status;
    if (fromDate != null) queryParams['from_date'] = fromDate;
    if (toDate != null) queryParams['to_date'] = toDate;

    final queryString = Uri(queryParameters: queryParams).query;
    final result = await get('/v1/admin/orders/?$queryString');

    if (result['success']) {
      return {
        'success': true,
        'orders': result['data']['orders'],
        'total': result['data']['total'],
      };
    }
    return result;
  }

  // Get order details
  Future<Map<String, dynamic>> getOrderDetails(String orderId) async {
    return await get('/v1/admin/orders/$orderId');
  }
}
