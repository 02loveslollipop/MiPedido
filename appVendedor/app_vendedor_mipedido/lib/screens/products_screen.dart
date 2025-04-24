import 'package:flutter/material.dart';
import '../components/nav_bar.dart';
import '../models/product.dart';
import '../api/api_connector.dart';
import 'product_detail_screen.dart';
import 'main_menu.dart';
import 'qr_scanner_screen.dart';

class ProductsScreen extends StatefulWidget {
  final String restaurantId;

  const ProductsScreen({super.key, required this.restaurantId});

  @override
  State<ProductsScreen> createState() => _ProductsScreenState();
}

class _ProductsScreenState extends State<ProductsScreen> {
  final ApiConnector _apiConnector = ApiConnector();
  bool _isLoading = true;
  List<Product> _products = [];
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  void _showLogoutConfirmationDialog() {
    final colorScheme = Theme.of(context).colorScheme;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Cerrar sesión'),
          content: const Text('¿Deseas cerrar sesión?'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(); // Close the dialog
              },
              child: Text('No', style: TextStyle(color: colorScheme.primary)),
            ),
            TextButton(
              onPressed: () async {
                Navigator.of(context).pop(); // Close the dialog

                // Show loading indicator
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Cerrando sesión...'),
                    duration: Duration(seconds: 1),
                  ),
                );

                // Logout and clear user data
                await _apiConnector.logout();

                // Navigate back to main menu screen
                if (mounted) {
                  Navigator.of(context).pushAndRemoveUntil(
                    MaterialPageRoute(builder: (context) => const MainMenu()),
                    (route) => false, // Remove all previous routes
                  );
                }
              },
              style: TextButton.styleFrom(foregroundColor: colorScheme.error),
              child: const Text('Sí'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _loadProducts() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await _apiConnector.getProductsWithStatus(
        widget.restaurantId,
      );

      if (result['success']) {
        setState(() {
          _products = result['products'] as List<Product>;
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = result['error'];
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error al conectar con el servidor: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  Future<void> _toggleProductStatus(Product product) async {
    try {
      Map<String, dynamic> result;
      if (product.isEnabled) {
        result = await _apiConnector.disableProduct(
          widget.restaurantId,
          product.id,
        );
      } else {
        result = await _apiConnector.enableProduct(
          widget.restaurantId,
          product.id,
        );
      }

      if (result['success']) {
        setState(() {
          product.isEnabled = !product.isEnabled;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              product.isEnabled
                  ? '${product.name} habilitado'
                  : '${product.name} deshabilitado',
            ),
            backgroundColor: product.isEnabled ? Colors.green : Colors.orange,
            duration: const Duration(seconds: 2),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${result['error']}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: ${e.toString()}'),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  void _navigateToProductDetails(Product product) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder:
            (context) => ProductDetailScreen(
              restaurantId: widget.restaurantId,
              productId: product.id,
            ),
      ),
    );
  }

  void _navigateToQRScannerScreen() {
    // Navigate to QR scanner screen
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const QRScannerScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: NavBar(
        title: 'Productos',
        isBackButtonAlert: true,
        onBackPressed: _showLogoutConfirmationDialog,
      ),
      body:
          _isLoading
              ? Center(
                child: CircularProgressIndicator(color: colorScheme.primary),
              )
              : _errorMessage != null
              ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Error al cargar productos',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: colorScheme.error,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _errorMessage!,
                      style: TextStyle(color: colorScheme.error),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _loadProducts,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: colorScheme.primary,
                        foregroundColor: colorScheme.onPrimary,
                      ),
                      child: const Text('Reintentar'),
                    ),
                  ],
                ),
              )
              : _products.isEmpty
              ? Center(
                child: Text(
                  'No hay productos disponibles',
                  style: TextStyle(
                    fontSize: 18,
                    color: colorScheme.onSurface.withOpacity(0.7),
                  ),
                ),
              )
              : RefreshIndicator(
                onRefresh: _loadProducts,
                color: colorScheme.primary,
                child: ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: _products.length,
                  separatorBuilder: (context, index) => const Divider(),
                  itemBuilder: (context, index) {
                    final product = _products[index];
                    return ProductListItem(
                      product: product,
                      onToggle: () => _toggleProductStatus(product),
                      onTap: () => _navigateToProductDetails(product),
                    );
                  },
                ),
              ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _navigateToQRScannerScreen,
        backgroundColor: colorScheme.primary,
        foregroundColor: colorScheme.onPrimary,
        icon: const Icon(Icons.qr_code_scanner),
        label: const Text('Leer QR'),
      ),
    );
  }
}

class ProductListItem extends StatelessWidget {
  final Product product;
  final VoidCallback onToggle;
  final VoidCallback onTap;

  const ProductListItem({
    super.key,
    required this.product,
    required this.onToggle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0),
        child: Row(
          children: [
            // Price (now first on left)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
              margin: const EdgeInsets.only(right: 12),
              decoration: BoxDecoration(
                color:
                    product.isEnabled
                        ? colorScheme.primaryContainer
                        : colorScheme.surfaceVariant,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                '\$${product.price.toStringAsFixed(2)}',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                  color:
                      product.isEnabled
                          ? colorScheme.onPrimaryContainer
                          : colorScheme.onSurfaceVariant,
                ),
              ),
            ),
            // Product information
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.name,
                    style: TextStyle(
                      fontWeight:
                          product.isEnabled
                              ? FontWeight.bold
                              : FontWeight.normal,
                      fontSize: 16,
                      color:
                          product.isEnabled
                              ? colorScheme.onSurface
                              : colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    product.description,
                    style: TextStyle(
                      color: colorScheme.onSurfaceVariant,
                      fontSize: 13,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            // Toggle switch
            Switch(
              value: product.isEnabled,
              onChanged: (_) => onToggle(),
              activeColor: colorScheme.primary,
            ),
          ],
        ),
      ),
    );
  }
}
