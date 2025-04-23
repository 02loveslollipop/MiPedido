class Product {
  final String id;
  final String name;
  final String description;
  final double price;
  final String imgUrl;
  final List<String> ingredients;
  bool isEnabled;

  Product({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.imgUrl,
    required this.ingredients,
    this.isEnabled = true,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      price: (json['price'] as num).toDouble(),
      imgUrl: json['img_url'] as String,
      ingredients: List<String>.from(json['ingredients'] as List),
      isEnabled: json['enabled'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'price': price,
      'img_url': imgUrl,
      'ingredients': ingredients,
      'enabled': isEnabled,
    };
  }
}
