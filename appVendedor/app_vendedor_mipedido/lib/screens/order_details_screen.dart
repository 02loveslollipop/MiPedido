import 'package:flutter/material.dart';
import '../models/order_item.dart';
import '../components/nav_bar.dart';
import '../api/api_connector.dart';
import 'qr_scanner_screen.dart';
import 'order_item_detail_screen.dart';

class OrderDetailsScreen extends StatefulWidget {
  final Map<String, dynamic> orderData;

  const OrderDetailsScreen({Key? key, required this.orderData})
    : super(key: key);

  @override
  State<OrderDetailsScreen> createState() => _OrderDetailsScreenState();
}

class _OrderDetailsScreenState extends State<OrderDetailsScreen> {
  late Order order;
  final ApiConnector _apiConnector = ApiConnector();
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    // Parse the order data
    try {
      order = Order.fromJson(widget.orderData);
    } catch (e) {
      // In case of parsing error, create an empty order
      order = Order(
        products: [],
        totalPrice: 0.0,
        totalQuantity: 0,
        dateCompleted: DateTime.now().toString(),
        orderId: 'Error',
      );
    }
  }

  void _showFulfillDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Completar Pedido'),
          content: const Text(
            '¿Estás seguro de que deseas marcar este pedido como completado?',
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(); // Close dialog
              },
              child: const Text('Cancelar'),
            ),
            TextButton(
              onPressed: () async {
                Navigator.of(context).pop(); // Close dialog
                await _fulfillOrder();
              },
              child: const Text('Confirmar'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _fulfillOrder() async {
    setState(() {
      _isProcessing = true;
    });

    try {
      final result = await _apiConnector.fulfillOrder(order.orderId);

      if (result['success']) {
        // Order fulfilled successfully, navigate back to QR scanner
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Pedido completado con éxito'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 2),
            ),
          );

          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const QRScannerScreen()),
          );
        }
      } else {
        // Show error message
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: ${result['error']}'),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 3),
            ),
          );
          setState(() {
            _isProcessing = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
        setState(() {
          _isProcessing = false;
        });
      }
    }
  }

  void _showCancelDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Cancelar Pedido'),
          content: const Text(
            'Si sales, el pedido no se marcará como completado. ¿Deseas continuar?',
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(); // Close dialog
              },
              child: const Text('Volver al Pedido'),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(); // Close dialog
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(
                    builder: (context) => const QRScannerScreen(),
                  ),
                );
              },
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: const Text('Salir sin Completar'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return WillPopScope(
      onWillPop: () async {
        _showCancelDialog();
        return false; // Prevent default back button behavior
      },
      child: Scaffold(
        appBar: NavBar(
          title: 'Detalles del Pedido',
          onBackPressed: _showCancelDialog,
        ),
        body: Stack(
          children: [
            // Main content
            Column(
              children: [
                // Order items list
                Expanded(
                  child:
                      order.products.isEmpty
                          ? Center(
                            child: Text(
                              'No hay productos en este pedido',
                              style: TextStyle(
                                fontSize: 18,
                                color: colorScheme.onSurface.withOpacity(0.7),
                              ),
                            ),
                          )
                          : ListView.separated(
                            padding: const EdgeInsets.all(16),
                            itemCount: order.products.length,
                            separatorBuilder:
                                (context, index) => const Divider(),
                            itemBuilder: (context, index) {
                              final orderItem = order.products[index];
                              return OrderItemListTile(
                                orderItem: orderItem,
                                onTap: () {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder:
                                          (context) => OrderItemDetailScreen(
                                            orderItem: orderItem,
                                          ),
                                    ),
                                  );
                                },
                              );
                            },
                          ),
                ),

                // Order summary card at bottom
                Container(
                  padding: const EdgeInsets.all(16),
                  child: Card(
                    elevation: 4,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'Total a Cobrar:',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                '\$${order.totalPrice.toStringAsFixed(2)}',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: colorScheme.primary,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'Cantidad de Productos:',
                                style: TextStyle(fontSize: 14),
                              ),
                              Text(
                                '${order.totalQuantity}',
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed:
                                  _isProcessing ? null : _showFulfillDialog,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: colorScheme.primary,
                                foregroundColor: colorScheme.onPrimary,
                                padding: const EdgeInsets.symmetric(
                                  vertical: 12,
                                ),
                              ),
                              child: const Text(
                                'Completar Pedido',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),

            // Processing overlay
            if (_isProcessing)
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
                            CircularProgressIndicator(
                              color: colorScheme.primary,
                            ),
                            const SizedBox(height: 16),
                            const Text(
                              'Completando pedido...',
                              style: TextStyle(
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
      ),
    );
  }
}

class OrderItemListTile extends StatelessWidget {
  final OrderItem orderItem;
  final VoidCallback onTap;

  const OrderItemListTile({
    super.key,
    required this.orderItem,
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
            // Quantity indicator (left side)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 12),
              margin: const EdgeInsets.only(right: 12),
              decoration: BoxDecoration(
                color: colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'x${orderItem.quantity}',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: colorScheme.onPrimaryContainer,
                ),
              ),
            ),
            // Product information
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    orderItem.name,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  // Show selected ingredients (or "Sin ingredientes" if none)
                  Text(
                    orderItem.ingredients.isEmpty
                        ? 'Sin ingredientes'
                        : orderItem.ingredients.join(', '),
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
            // Price
            Text(
              '\$${orderItem.totalPrice.toStringAsFixed(2)}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: colorScheme.primary,
              ),
            ),
            // Arrow icon
            Icon(Icons.chevron_right, color: colorScheme.onSurfaceVariant),
          ],
        ),
      ),
    );
  }
}
