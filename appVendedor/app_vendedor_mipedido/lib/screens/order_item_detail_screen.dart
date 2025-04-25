import 'package:flutter/material.dart';
import '../models/order_item.dart';
import '../components/nav_bar.dart';

class OrderItemDetailScreen extends StatelessWidget {
  final OrderItem orderItem;

  const OrderItemDetailScreen({Key? key, required this.orderItem})
    : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: NavBar(
        title: orderItem.name,
        onBackPressed: () => Navigator.pop(context),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Product image
            Center(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child:
                    orderItem.imgUrl.isNotEmpty
                        ? Image.network(
                          orderItem.imgUrl,
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
            const SizedBox(height: 24),

            // Quantity
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Cantidad:',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    '${orderItem.quantity}',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: colorScheme.onPrimaryContainer,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(),

            // Price per unit
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Precio por unidad:',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Text(
                  '\$${orderItem.pricePerUnit.toStringAsFixed(2)}',
                  style: TextStyle(fontSize: 16, color: colorScheme.onSurface),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Total price
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Precio total:',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  '\$${orderItem.totalPrice.toStringAsFixed(2)}',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: colorScheme.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(),

            // Selected ingredients
            const Text(
              'Ingredientes seleccionados:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            if (orderItem.ingredients.isEmpty)
              const Text(
                'Sin ingredientes',
                style: TextStyle(fontStyle: FontStyle.italic),
              )
            else
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children:
                    orderItem.ingredients
                        .map(
                          (ingredient) => Chip(
                            label: Text(ingredient),
                            backgroundColor: colorScheme.surfaceVariant,
                            labelStyle: TextStyle(
                              color: colorScheme.onSurfaceVariant,
                            ),
                          ),
                        )
                        .toList(),
              ),
          ],
        ),
      ),
    );
  }
}
