import 'package:flutter/material.dart';
import 'screens/main_menu.dart';
import 'theme.dart';
import 'api/api_connector.dart';
import 'screens/products_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mi Pedido - Vendedor',
      theme: MaterialTheme(Typography.englishLike2021).light(),
      darkTheme: MaterialTheme(Typography.englishLike2021).dark(),
      themeMode: ThemeMode.system,
      home: const AuthCheckScreen(),
    );
  }
}

class AuthCheckScreen extends StatefulWidget {
  const AuthCheckScreen({super.key});

  @override
  State<AuthCheckScreen> createState() => _AuthCheckScreenState();
}

class _AuthCheckScreenState extends State<AuthCheckScreen> {
  final ApiConnector _apiConnector = ApiConnector();
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    bool isLoggedIn = await _apiConnector.initialize();

    if (mounted) {
      setState(() {
        _isLoading = false;
      });

      if (isLoggedIn) {
        // Navigate to products screen if user is already logged in
        String? restaurantId = _apiConnector.restaurantId;

        if (restaurantId != null) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(
              builder: (context) => ProductsScreen(restaurantId: restaurantId),
            ),
          );
        } else {
          // If restaurant ID is not available, try to get it
          final result = await _apiConnector.getUserRestaurant();
          if (result['success'] && result['restaurant_id'] != null) {
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(
                builder:
                    (context) =>
                        ProductsScreen(restaurantId: result['restaurant_id']),
              ),
            );
          } else {
            // If we can't get restaurant ID, log out and show login screen
            await _apiConnector.logout();
          }
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        body: Center(
          child: CircularProgressIndicator(
            color: Theme.of(context).colorScheme.primary,
          ),
        ),
      );
    }

    // Show login screen if not logged in
    return const MainMenu();
  }
}
