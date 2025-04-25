class OrderItem {
  final String id;
  final String name;
  final double pricePerUnit;
  final double totalPrice;
  final String imgUrl;
  final int quantity;
  final List<String> ingredients;

  OrderItem({
    required this.id,
    required this.name,
    required this.pricePerUnit,
    required this.totalPrice,
    required this.imgUrl,
    required this.quantity,
    required this.ingredients,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      id: json['id'] as String,
      name: json['name'] as String,
      pricePerUnit: (json['price_per_unit'] as num).toDouble(),
      totalPrice: (json['total_price'] as num).toDouble(),
      imgUrl: json['img_url'] as String,
      quantity: json['quantity'] as int,
      ingredients: List<String>.from(json['ingredients'] as List),
    );
  }
}

class Order {
  final List<OrderItem> products;
  final double totalPrice;
  final int totalQuantity;
  final String dateCompleted;
  final String orderId;

  Order({
    required this.products,
    required this.totalPrice,
    required this.totalQuantity,
    required this.dateCompleted,
    required this.orderId,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    // Extract products list and parse each item
    final List<OrderItem> orderItems =
        (json['products'] as List)
            .map((item) => OrderItem.fromJson(item as Map<String, dynamic>))
            .toList();

    // Extract or provide default for orderId which might not be in the response
    String orderId = json['order_id'] ?? '';

    return Order(
      products: orderItems,
      totalPrice: (json['total_price'] as num).toDouble(),
      totalQuantity: json['total_quantity'] as int,
      dateCompleted: json['date_completed'] as String,
      orderId: orderId,
    );
  }
}
