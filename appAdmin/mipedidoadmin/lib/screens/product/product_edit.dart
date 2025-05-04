import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';
import '../../main.dart';
import '../../components/image_upload_field.dart';

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
  final List<TextEditingController> _ingredientControllers = [
    TextEditingController(),
  ];
  final _formKey = GlobalKey<FormState>();

  bool _isLoadingRestaurants = true;
  bool _isLoadingProducts = false;
  bool _isUpdatingProduct = false;
  List<dynamic> _restaurants = [];
  List<dynamic> _products = [];
  String? _errorMessage;
  dynamic _selectedRestaurant;
  dynamic _selectedProduct;
  String? _previousImageUrl;

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

    // Dispose all ingredient controllers
    for (var controller in _ingredientControllers) {
      controller.dispose();
    }

    super.dispose();
  }

  Future<void> _loadRestaurants() async {
    setState(() {
      _isLoadingRestaurants = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.listRestaurants();

    if (!mounted) return;
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

    if (!mounted) return;
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

  // Add a new empty ingredient field
  void _addIngredientField() {
    setState(() {
      _ingredientControllers.add(TextEditingController());
    });
  }

  // Delete an ingredient field
  void _deleteIngredientField(int index) {
    setState(() {
      if (_ingredientControllers.length > 1) {
        // If we have more than one field, remove the controller
        _ingredientControllers[index].dispose();
        _ingredientControllers.removeAt(index);
      } else {
        // If it's the only field, just clear it
        _ingredientControllers[index].clear();
      }
    });
  }

  // Get all non-empty ingredients
  List<String> _getIngredients() {
    return _ingredientControllers
        .map((controller) => controller.text.trim())
        .where((text) => text.isNotEmpty)
        .toList();
  }

  void _selectProduct(dynamic product) {
    // Clear existing ingredient controllers except the first one
    for (int i = 1; i < _ingredientControllers.length; i++) {
      _ingredientControllers[i].dispose();
    }
    _ingredientControllers.clear();

    // Set basic product details
    setState(() {
      _selectedProduct = product;
      _nameController.text = product['name'] ?? '';
      _descriptionController.text = product['description'] ?? '';
      _imageUrlController.text = product['img_url'] ?? '';
      _previousImageUrl = product['img_url'] ?? '';
      _priceController.text = product['price']?.toString() ?? '';

      // Load ingredients
      final ingredients = product['ingredients'] as List<dynamic>? ?? [];

      if (ingredients.isNotEmpty) {
        // Create controllers for each ingredient
        for (int i = 0; i < ingredients.length; i++) {
          if (i == 0) {
            // Use the first controller
            _ingredientControllers.add(
              TextEditingController(text: ingredients[i].toString()),
            );
          } else {
            _ingredientControllers.add(
              TextEditingController(text: ingredients[i].toString()),
            );
          }
        }
      } else {
        // Just add one empty controller
        _ingredientControllers.add(TextEditingController());
      }

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

    // If the image URL changed and the previous one is a blob, delete it
    if (_previousImageUrl != null &&
        _previousImageUrl!.isNotEmpty &&
        _previousImageUrl != _imageUrlController.text &&
        _previousImageUrl!.contains('/blob/')) {
      await apiConnector.deleteFileFromBlobStorage(_previousImageUrl!);
    }

    final result = await apiConnector.updateProduct(
      productId: _selectedProduct['id'],
      name: _nameController.text,
      description: _descriptionController.text,
      price: double.parse(_priceController.text),
      imageUrl: _imageUrlController.text,
      ingredients: _getIngredients(),
    );

    if (!mounted) return;
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

    if (!mounted) return;
    Navigator.push(
      context,
      FluentPageRoute(builder: (context) => const MiPedidoAdminApp()),
    );
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
                                                    label: 'Imagen',
                                                    child: ImageUploadField(
                                                      initialUrl:
                                                          _imageUrlController
                                                              .text,
                                                      onImageUploaded: (url) {
                                                        setState(() {
                                                          _imageUrlController
                                                              .text = url;
                                                        });
                                                      },
                                                    ),
                                                  ),
                                                  const SizedBox(height: 16),
                                                  // Ingredients section
                                                  InfoLabel(
                                                    label: 'Ingredientes',
                                                    child: Column(
                                                      crossAxisAlignment:
                                                          CrossAxisAlignment
                                                              .start,
                                                      children: [
                                                        for (
                                                          int i = 0;
                                                          i <
                                                              _ingredientControllers
                                                                  .length;
                                                          i++
                                                        )
                                                          Padding(
                                                            padding:
                                                                const EdgeInsets.only(
                                                                  bottom: 8.0,
                                                                ),
                                                            child: Row(
                                                              children: [
                                                                Expanded(
                                                                  child: TextFormBox(
                                                                    controller:
                                                                        _ingredientControllers[i],
                                                                    placeholder:
                                                                        'Ingrediente ${i + 1}',
                                                                    onChanged: (
                                                                      value,
                                                                    ) {
                                                                      // If this is the last textbox and it has text,
                                                                      // add a new empty textbox
                                                                      if (i ==
                                                                              _ingredientControllers.length -
                                                                                  1 &&
                                                                          value
                                                                              .isNotEmpty) {
                                                                        _addIngredientField();
                                                                      }
                                                                    },
                                                                  ),
                                                                ),
                                                                const SizedBox(
                                                                  width: 8,
                                                                ),
                                                                IconButton(
                                                                  icon: const Icon(
                                                                    FluentIcons
                                                                        .delete,
                                                                  ),
                                                                  onPressed:
                                                                      () =>
                                                                          _deleteIngredientField(
                                                                            i,
                                                                          ),
                                                                ),
                                                              ],
                                                            ),
                                                          ),
                                                      ],
                                                    ),
                                                  ),
                                                  const SizedBox(height: 16),
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
