import 'package:flutter/material.dart';
import '../components/nav_bar.dart';
import '../api/api_connector.dart';
import '../models/product.dart';

class ProductDetailScreen extends StatefulWidget {
  final String restaurantId;
  final String productId;

  const ProductDetailScreen({
    super.key,
    required this.restaurantId,
    required this.productId,
  });

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  final ApiConnector _apiConnector = ApiConnector();
  bool _isLoading = true;
  Product? _product;
  String? _errorMessage;
  bool _isTogglingStatus = false; // Keep this to track toggle state

  @override
  void initState() {
    super.initState();
    _loadProductDetails();
  }

  Future<void> _loadProductDetails() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await _apiConnector.getProductDetails(
        widget.restaurantId,
        widget.productId,
      );

      if (result['success']) {
        setState(() {
          _product = result['product'] as Product;
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

  Future<void> _toggleProductStatus() async {
    // Prevent multiple rapid clicks
    if (_isTogglingStatus || _product == null) {
      return;
    }

    setState(() {
      _isTogglingStatus = true;
    });

    try {
      Map<String, dynamic> result;
      if (_product!.isEnabled) {
        result = await _apiConnector.disableProduct(
          widget.restaurantId,
          widget.productId,
        );
      } else {
        result = await _apiConnector.enableProduct(
          widget.restaurantId,
          widget.productId,
        );
      }

      if (result['success']) {
        setState(() {
          _product!.isEnabled = !_product!.isEnabled;
        });
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
    } finally {
      // Always reset the toggling state when done
      if (mounted) {
        setState(() {
          _isTogglingStatus = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: NavBar(
        title:
            _isLoading ? 'Detalle de producto' : _product?.name ?? 'Producto',
        onBackPressed: () => Navigator.pop(context),
      ),
      body: Stack(
        children: [
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
                      'Error al cargar el producto',
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
                      onPressed: _loadProductDetails,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: colorScheme.primary,
                        foregroundColor: colorScheme.onPrimary,
                      ),
                      child: const Text('Reintentar'),
                    ),
                  ],
                ),
              )
              : _product == null
              ? Center(
                child: Text(
                  'Producto no encontrado',
                  style: TextStyle(
                    fontSize: 18,
                    color: colorScheme.onSurface.withOpacity(0.7),
                  ),
                ),
              )
              : SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Product image
                    Center(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child:
                            _product!.imgUrl.isNotEmpty
                                ? Image.network(
                                  _product!.imgUrl,
                                  height: 200,
                                  width: double.infinity,
                                  fit: BoxFit.cover,
                                  errorBuilder: (context, error, stackTrace) {
                                    return Container(
                                      height: 200,
                                      width: double.infinity,
                                      color: colorScheme.surfaceVariant,
                                      child: Icon(
                                        Icons.image_not_supported,
                                        size: 50,
                                        color: colorScheme.onSurfaceVariant,
                                      ),
                                    );
                                  },
                                )
                                : Container(
                                  height: 200,
                                  width: double.infinity,
                                  color: colorScheme.surfaceVariant,
                                  child: Icon(
                                    Icons.restaurant_menu,
                                    size: 50,
                                    color: colorScheme.onSurfaceVariant,
                                  ),
                                ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Product status
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Estado',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: colorScheme.onSurface,
                          ),
                        ),
                        Row(
                          children: [
                            Text(
                              _product!.isEnabled
                                  ? 'Habilitado'
                                  : 'Deshabilitado',
                              style: TextStyle(
                                color:
                                    _product!.isEnabled
                                        ? Colors.green
                                        : Colors.orange,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(width: 8),
                            // Keep switch enabled all the time
                            Switch(
                              value: _product!.isEnabled,
                              onChanged: (_) => _toggleProductStatus(),
                              activeColor: colorScheme.primary,
                            ),
                          ],
                        ),
                      ],
                    ),
                    const Divider(),

                    // Price
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Precio',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: colorScheme.onSurface,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            vertical: 6,
                            horizontal: 12,
                          ),
                          decoration: BoxDecoration(
                            color:
                                _product!.isEnabled
                                    ? colorScheme.primaryContainer
                                    : colorScheme.surfaceVariant,
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Text(
                            '\$${_product!.price.toStringAsFixed(2)}',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color:
                                  _product!.isEnabled
                                      ? colorScheme.onPrimaryContainer
                                      : colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Description
                    Text(
                      'Descripción',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: colorScheme.onSurface,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _product!.description,
                      style: TextStyle(
                        fontSize: 14,
                        color: colorScheme.onSurface,
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Ingredients
                    Text(
                      'Ingredientes',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: colorScheme.onSurface,
                      ),
                    ),
                    const SizedBox(height: 8),
                    if (_product!.ingredients.isEmpty)
                      Text(
                        'No hay ingredientes disponibles',
                        style: TextStyle(
                          fontSize: 14,
                          fontStyle: FontStyle.italic,
                          color: colorScheme.onSurfaceVariant,
                        ),
                      )
                    else
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children:
                            _product!.ingredients.map((ingredient) {
                              return Chip(
                                label: Text(ingredient),
                                backgroundColor: colorScheme.surfaceVariant,
                                labelStyle: TextStyle(
                                  color: colorScheme.onSurfaceVariant,
                                ),
                              );
                            }).toList(),
                      ),
                  ],
                ),
              ),

          // Loading overlay during toggle operation
          if (_isTogglingStatus && _product != null)
            Positioned.fill(
              child: Container(
                color: Colors.black.withOpacity(0.3),
                child: Center(
                  child: Card(
                    elevation: 8,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                        vertical: 20,
                        horizontal: 24,
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          CircularProgressIndicator(color: colorScheme.primary),
                          const SizedBox(height: 16),
                          Text(
                            'Actualizando ${_product!.name}',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
