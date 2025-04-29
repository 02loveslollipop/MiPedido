import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';

class ProductListScreen extends StatefulWidget {
  const ProductListScreen({super.key});

  @override
  State<ProductListScreen> createState() => _ProductListScreenState();
}

class _ProductListScreenState extends State<ProductListScreen> {
  bool _isLoadingRestaurants = true;
  bool _isLoadingProducts = false;
  List<dynamic> _restaurants = [];
  List<dynamic> _products = [];
  String? _errorMessage;
  dynamic _selectedRestaurant;

  @override
  void initState() {
    super.initState();
    _loadRestaurants();
  }

  Future<void> _loadRestaurants() async {
    setState(() {
      _isLoadingRestaurants = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.listRestaurants();

    setState(() {
      _isLoadingRestaurants = false;
      if (result['success']) {
        _restaurants = result['restaurants'];
        if (_restaurants.isNotEmpty) {
          _selectedRestaurant = _restaurants.first;
          _loadProducts(_selectedRestaurant['id']);
        }
      } else {
        _errorMessage = result['error'] ?? 'Failed to load restaurants';
      }
    });
  }

  Future<void> _loadProducts(String restaurantId) async {
    setState(() {
      _isLoadingProducts = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.listProductsByRestaurant(restaurantId);

    setState(() {
      _isLoadingProducts = false;
      if (result['success']) {
        _products = result['products'];
      } else {
        _errorMessage = result['error'] ?? 'Failed to load products';
      }
    });
  }

  void _onRestaurantChanged(dynamic restaurant) {
    setState(() {
      _selectedRestaurant = restaurant;
    });
    _loadProducts(restaurant['id']);
  }

  void showSnackbar(BuildContext context, InfoBar infoBar) {
    displayInfoBar(
      context,
      builder: (context, close) {
        return infoBar;
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return ScaffoldPage(
      header: const PageHeader(title: Text('Listado de Productos')),
      content:
          _isLoadingRestaurants
              ? const Center(child: ProgressRing())
              : _errorMessage != null && _restaurants.isEmpty
              ? Center(
                child: InfoBar(
                  title: const Text('Error'),
                  content: Text(_errorMessage!),
                  severity: InfoBarSeverity.error,
                  isLong: true,
                  action: FilledButton(
                    child: const Text('Reintentar'),
                    onPressed: _loadRestaurants,
                  ),
                ),
              )
              : _restaurants.isEmpty
              ? const Center(child: Text('No hay restaurantes registrados'))
              : Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      children: [
                        SizedBox(
                          width: 300,
                          child: InfoLabel(
                            label: 'Seleccionar Restaurante',
                            child: ComboBox<dynamic>(
                              value: _selectedRestaurant,
                              items:
                                  _restaurants.map((restaurant) {
                                    return ComboBoxItem<dynamic>(
                                      value: restaurant,
                                      child: Text(restaurant['name']),
                                    );
                                  }).toList(),
                              onChanged: _onRestaurantChanged,
                            ),
                          ),
                        ),
                        const Spacer(),
                        Button(
                          child: const Text('Refrescar'),
                          onPressed: () {
                            if (_selectedRestaurant != null) {
                              _loadProducts(_selectedRestaurant['id']);
                            }
                          },
                        ),
                      ],
                    ),
                  ),
                  if (_errorMessage != null && _products.isEmpty) ...[
                    Center(
                      child: InfoBar(
                        title: const Text('Error'),
                        content: Text(_errorMessage!),
                        severity: InfoBarSeverity.error,
                        isLong: true,
                      ),
                    ),
                  ],
                  Expanded(
                    child:
                        _isLoadingProducts
                            ? const Center(child: ProgressRing())
                            : _products.isEmpty
                            ? const Center(
                              child: Text(
                                'No hay productos para este restaurante',
                              ),
                            )
                            : GridView.builder(
                              padding: const EdgeInsets.all(16),
                              gridDelegate:
                                  const SliverGridDelegateWithMaxCrossAxisExtent(
                                    maxCrossAxisExtent: 300,
                                    childAspectRatio: 0.75,
                                    crossAxisSpacing: 16,
                                    mainAxisSpacing: 16,
                                  ),
                              itemCount: _products.length,
                              itemBuilder: (context, index) {
                                final product = _products[index];
                                return Card(
                                  padding: EdgeInsets.zero,
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      ClipRRect(
                                        borderRadius: const BorderRadius.only(
                                          topLeft: Radius.circular(4),
                                          topRight: Radius.circular(4),
                                        ),
                                        child: SizedBox(
                                          height: 150,
                                          width: double.infinity,
                                          child:
                                              product['img_url'] != null &&
                                                      product['img_url']
                                                          .toString()
                                                          .isNotEmpty
                                                  ? Image.network(
                                                    product['img_url'],
                                                    fit: BoxFit.cover,
                                                    errorBuilder: (
                                                      context,
                                                      error,
                                                      stackTrace,
                                                    ) {
                                                      return const Center(
                                                        child: Icon(
                                                          FluentIcons
                                                              .picture_center,
                                                          size: 48,
                                                          color: Colors.grey,
                                                        ),
                                                      );
                                                    },
                                                  )
                                                  : const Center(
                                                    child: Icon(
                                                      FluentIcons
                                                          .picture_center,
                                                      size: 48,
                                                      color: Colors.grey,
                                                    ),
                                                  ),
                                        ),
                                      ),
                                      Padding(
                                        padding: const EdgeInsets.all(12),
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              product['name'] ?? 'Sin nombre',
                                              style: const TextStyle(
                                                fontSize: 16,
                                                fontWeight: FontWeight.bold,
                                              ),
                                              maxLines: 1,
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                            const SizedBox(height: 4),
                                            Text(
                                              product['description'] ??
                                                  'Sin descripción',
                                              style: const TextStyle(
                                                fontSize: 12,
                                                color: Colors.grey,
                                              ),
                                              maxLines: 2,
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                            const SizedBox(height: 4),
                                            Text(
                                              '\$${product['price']?.toStringAsFixed(2) ?? '0.00'}',
                                              style: const TextStyle(
                                                fontSize: 14,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                            const SizedBox(height: 8),
                                            Row(
                                              mainAxisAlignment:
                                                  MainAxisAlignment.end,
                                              children: [
                                                Button(
                                                  child: const Text('Editar'),
                                                  onPressed: () {
                                                    // Navigate to edit screen (implement later)
                                                  },
                                                ),
                                              ],
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                );
                              },
                            ),
                  ),
                ],
              ),
    );
  }
}
