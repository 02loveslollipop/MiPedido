import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';

class ProductEditScreen extends StatefulWidget {
  const ProductEditScreen({super.key});

  @override
  State<ProductEditScreen> createState() => _ProductEditScreenState();
}

class _ProductEditScreenState extends State<ProductEditScreen> {
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _imageUrlController = TextEditingController();
  final _priceController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  bool _isLoadingRestaurants = true;
  bool _isLoadingProducts = false;
  bool _isUpdatingProduct = false;
  List<dynamic> _restaurants = [];
  List<dynamic> _products = [];
  String? _errorMessage;
  dynamic _selectedRestaurant;
  dynamic _selectedProduct;

  @override
  void initState() {
    super.initState();
    _loadRestaurants();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _imageUrlController.dispose();
    _priceController.dispose();
    super.dispose();
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
      _selectedProduct = null;
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
      _selectedProduct = null;
      _clearForm();
    });
    _loadProducts(restaurant['id']);
  }

  void _selectProduct(dynamic product) {
    setState(() {
      _selectedProduct = product;
      _nameController.text = product['name'] ?? '';
      _descriptionController.text = product['description'] ?? '';
      _imageUrlController.text = product['img_url'] ?? '';
      _priceController.text = product['price']?.toString() ?? '';
      _errorMessage = null;
    });
  }

  void _clearForm() {
    _nameController.clear();
    _descriptionController.clear();
    _imageUrlController.clear();
    _priceController.clear();
    setState(() {
      _errorMessage = null;
    });
  }

  Future<void> _updateProduct() async {
    if (_formKey.currentState?.validate() != true || _selectedProduct == null) {
      return;
    }

    setState(() {
      _isUpdatingProduct = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.updateProduct(
      productId: _selectedProduct['id'],
      name: _nameController.text,
      description: _descriptionController.text,
      price: double.parse(_priceController.text),
      imageUrl: _imageUrlController.text,
    );

    setState(() {
      _isUpdatingProduct = false;
    });

    if (result['success']) {
      // Reload products to get updated data
      _loadProducts(_selectedRestaurant['id']);

      if (!mounted) return;
      showSnackbar(
        context,
        const InfoBar(
          title: Text('Éxito'),
          content: Text('Producto actualizado correctamente'),
          severity: InfoBarSeverity.success,
        ),
      );
    } else {
      setState(() {
        _errorMessage = result['error'] ?? 'Error al actualizar producto';
      });
    }
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
    final bool isLoading = _isLoadingRestaurants || _isLoadingProducts;

    return ScaffoldPage(
      header: const PageHeader(title: Text('Editar Producto')),
      content:
          isLoading
              ? const Center(child: ProgressRing())
              : _errorMessage != null && _restaurants.isEmpty
              ? Center(
                child: InfoBar(
                  title: const Text('Error'),
                  content: Text(_errorMessage!),
                  severity: InfoBarSeverity.error,
                  isLong: true,
                  action: FilledButton(
                    onPressed: _loadRestaurants,
                    child: const Text('Reintentar'),
                  ),
                ),
              )
              : _restaurants.isEmpty
              ? const Center(
                child: Text(
                  'No hay restaurantes disponibles. Debe crear al menos un restaurante.',
                ),
              )
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
                  if (_products.isEmpty && !isLoading) ...[
                    const Center(
                      child: Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Text('No hay productos para este restaurante'),
                      ),
                    ),
                  ] else ...[
                    Expanded(
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Left panel with product list
                          SizedBox(
                            width: 250,
                            child: ListView.builder(
                              padding: const EdgeInsets.all(8),
                              itemCount: _products.length,
                              itemBuilder: (context, index) {
                                final product = _products[index];
                                final isSelected =
                                    _selectedProduct != null &&
                                    product['id'] == _selectedProduct['id'];
                                return Card(
                                  padding: const EdgeInsets.all(8),
                                  margin: const EdgeInsets.symmetric(
                                    vertical: 4,
                                  ),
                                  backgroundColor:
                                      isSelected ? Colors.teal.lightest : null,
                                  child: ListTile(
                                    title: Text(
                                      product['name'] ?? 'Sin nombre',
                                    ),
                                    subtitle: Text(
                                      '\$${product['price']?.toStringAsFixed(2) ?? '0.00'}',
                                      style: const TextStyle(fontSize: 12),
                                    ),
                                    onPressed: () => _selectProduct(product),
                                    trailing:
                                        isSelected
                                            ? Icon(
                                              FluentIcons.check_mark,
                                              color: Colors.teal,
                                            )
                                            : null,
                                  ),
                                );
                              },
                            ),
                          ),
                          // Right panel with edit form
                          Expanded(
                            child:
                                _selectedProduct == null
                                    ? const Center(
                                      child: Text(
                                        'Seleccione un producto para editar',
                                      ),
                                    )
                                    : Form(
                                      key: _formKey,
                                      child: SingleChildScrollView(
                                        padding: const EdgeInsets.all(24),
                                        child: Center(
                                          child: Container(
                                            constraints: const BoxConstraints(
                                              maxWidth: 600,
                                            ),
                                            child: Card(
                                              padding: const EdgeInsets.all(24),
                                              child: Column(
                                                crossAxisAlignment:
                                                    CrossAxisAlignment.start,
                                                children: [
                                                  InfoLabel(
                                                    label:
                                                        'Nombre del Producto',
                                                    child: TextFormBox(
                                                      controller:
                                                          _nameController,
                                                      placeholder:
                                                          'Ingresar nombre del producto',
                                                      validator: (value) {
                                                        if (value == null ||
                                                            value.isEmpty) {
                                                          return 'Por favor ingrese el nombre del producto';
                                                        }
                                                        return null;
                                                      },
                                                      autovalidateMode:
                                                          AutovalidateMode
                                                              .onUserInteraction,
                                                    ),
                                                  ),
                                                  const SizedBox(height: 16),
                                                  InfoLabel(
                                                    label: 'Descripción',
                                                    child: TextFormBox(
                                                      controller:
                                                          _descriptionController,
                                                      placeholder:
                                                          'Ingresar descripción del producto',
                                                      maxLines: 3,
                                                      validator: (value) {
                                                        if (value == null ||
                                                            value.isEmpty) {
                                                          return 'Por favor ingrese una descripción';
                                                        }
                                                        return null;
                                                      },
                                                      autovalidateMode:
                                                          AutovalidateMode
                                                              .onUserInteraction,
                                                    ),
                                                  ),
                                                  const SizedBox(height: 16),
                                                  InfoLabel(
                                                    label: 'Precio (\$)',
                                                    child: TextFormBox(
                                                      controller:
                                                          _priceController,
                                                      placeholder:
                                                          'Ingresar precio (ej. 9.99)',
                                                      validator: (value) {
                                                        if (value == null ||
                                                            value.isEmpty) {
                                                          return 'Por favor ingrese el precio';
                                                        }
                                                        try {
                                                          final price =
                                                              double.parse(
                                                                value,
                                                              );
                                                          if (price <= 0) {
                                                            return 'El precio debe ser mayor a 0';
                                                          }
                                                        } catch (e) {
                                                          return 'Por favor ingrese un precio válido';
                                                        }
                                                        return null;
                                                      },
                                                      autovalidateMode:
                                                          AutovalidateMode
                                                              .onUserInteraction,
                                                    ),
                                                  ),
                                                  const SizedBox(height: 16),
                                                  InfoLabel(
                                                    label: 'URL de la Imagen',
                                                    child: TextFormBox(
                                                      controller:
                                                          _imageUrlController,
                                                      placeholder:
                                                          'Ingresar URL de la imagen',
                                                      validator: (value) {
                                                        if (value == null ||
                                                            value.isEmpty) {
                                                          return 'Por favor ingrese una URL para la imagen';
                                                        }
                                                        // Simple URL validation
                                                        if (!value.startsWith(
                                                              'http://',
                                                            ) &&
                                                            !value.startsWith(
                                                              'https://',
                                                            )) {
                                                          return 'Por favor ingrese una URL válida (debe comenzar con http:// o https://)';
                                                        }
                                                        return null;
                                                      },
                                                      autovalidateMode:
                                                          AutovalidateMode
                                                              .onUserInteraction,
                                                    ),
                                                  ),
                                                  const SizedBox(height: 16),
                                                  if (_imageUrlController
                                                      .text
                                                      .isNotEmpty) ...[
                                                    const Text(
                                                      'Vista previa de la imagen:',
                                                    ),
                                                    const SizedBox(height: 8),
                                                    Container(
                                                      height: 200,
                                                      width: double.infinity,
                                                      decoration: BoxDecoration(
                                                        border: Border.all(
                                                          color:
                                                              Colors.grey[130],
                                                        ),
                                                        borderRadius:
                                                            BorderRadius.circular(
                                                              4,
                                                            ),
                                                      ),
                                                      child: ClipRRect(
                                                        borderRadius:
                                                            BorderRadius.circular(
                                                              4,
                                                            ),
                                                        child: Image.network(
                                                          _imageUrlController
                                                              .text,
                                                          fit: BoxFit.cover,
                                                          errorBuilder: (
                                                            context,
                                                            error,
                                                            stackTrace,
                                                          ) {
                                                            return const Center(
                                                              child: Text(
                                                                'Error al cargar la imagen',
                                                              ),
                                                            );
                                                          },
                                                        ),
                                                      ),
                                                    ),
                                                    const SizedBox(height: 16),
                                                  ],
                                                  if (_errorMessage !=
                                                      null) ...[
                                                    InfoBar(
                                                      title: const Text(
                                                        'Error',
                                                      ),
                                                      content: Text(
                                                        _errorMessage!,
                                                      ),
                                                      severity:
                                                          InfoBarSeverity.error,
                                                      isLong: true,
                                                    ),
                                                    const SizedBox(height: 16),
                                                  ],
                                                  Row(
                                                    mainAxisAlignment:
                                                        MainAxisAlignment.end,
                                                    children: [
                                                      Button(
                                                        child: const Text(
                                                          'Cancelar',
                                                        ),
                                                        onPressed: () {
                                                          // Reset form to original values
                                                          _selectProduct(
                                                            _selectedProduct,
                                                          );
                                                        },
                                                      ),
                                                      const SizedBox(width: 8),
                                                      FilledButton(
                                                        onPressed:
                                                            _isUpdatingProduct
                                                                ? null
                                                                : _updateProduct,
                                                        child:
                                                            _isUpdatingProduct
                                                                ? const Row(
                                                                  mainAxisSize:
                                                                      MainAxisSize
                                                                          .min,
                                                                  children: [
                                                                    ProgressRing(
                                                                      strokeWidth:
                                                                          2,
                                                                    ),
                                                                    SizedBox(
                                                                      width: 8,
                                                                    ),
                                                                    Text(
                                                                      'Actualizando...',
                                                                    ),
                                                                  ],
                                                                )
                                                                : const Text(
                                                                  'Guardar Cambios',
                                                                ),
                                                      ),
                                                    ],
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ),
                                        ),
                                      ),
                                    ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
    );
  }
}
