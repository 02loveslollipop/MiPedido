import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';
import '../../main.dart';
import '../../components/image_upload_field.dart';

class ProductAddScreen extends StatefulWidget {
  const ProductAddScreen({super.key});

  @override
  State<ProductAddScreen> createState() => _ProductAddScreenState();
}

class _ProductAddScreenState extends State<ProductAddScreen> {
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _imageUrlController = TextEditingController();
  final _priceController = TextEditingController();
  final List<TextEditingController> _ingredientControllers = [
    TextEditingController(),
  ];
  final _formKey = GlobalKey<FormState>();

  bool _isLoadingRestaurants = true;
  bool _isAddingProduct = false;
  List<dynamic> _restaurants = [];
  String? _errorMessage;
  dynamic _selectedRestaurant;

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

    setState(() {
      _isLoadingRestaurants = false;
      if (result['success']) {
        _restaurants = result['restaurants'];
        if (_restaurants.isNotEmpty) {
          _selectedRestaurant = _restaurants.first;
        }
      } else {
        _errorMessage = result['error'] ?? 'Failed to load restaurants';
      }
    });
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

  Future<void> _addProduct() async {
    if (_formKey.currentState?.validate() != true ||
        _selectedRestaurant == null) {
      return;
    }

    setState(() {
      _isAddingProduct = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.createProduct(
      restaurantId: _selectedRestaurant['id'],
      name: _nameController.text,
      description: _descriptionController.text,
      price: double.parse(_priceController.text),
      imageUrl: _imageUrlController.text,
      ingredients: _getIngredients(),
    );

    setState(() {
      _isAddingProduct = false;
    });

    if (result['success']) {
      _nameController.clear();
      _descriptionController.clear();
      _imageUrlController.clear();
      _priceController.clear();

      if (!mounted) return;
      showSnackbar(
        context,
        const InfoBar(
          title: Text('Éxito'),
          content: Text('Producto creado correctamente'),
          severity: InfoBarSeverity.success,
        ),
      );
    } else {
      setState(() {
        _errorMessage = result['error'] ?? 'Error al crear producto';
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
    return ScaffoldPage(
      header: const PageHeader(title: Text('Agregar Nuevo Producto')),
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
              ? const Center(
                child: Text(
                  'No hay restaurantes disponibles. Debe crear al menos un restaurante.',
                ),
              )
              : Form(
                key: _formKey,
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: Center(
                    child: Container(
                      constraints: const BoxConstraints(maxWidth: 600),
                      child: Card(
                        padding: const EdgeInsets.all(24),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            InfoLabel(
                              label: 'Restaurante',
                              child: ComboBox<dynamic>(
                                value: _selectedRestaurant,
                                items:
                                    _restaurants.map((restaurant) {
                                      return ComboBoxItem<dynamic>(
                                        value: restaurant,
                                        child: Text(restaurant['name']),
                                      );
                                    }).toList(),
                                onChanged: (value) {
                                  setState(() {
                                    _selectedRestaurant = value;
                                  });
                                },
                              ),
                            ),
                            const SizedBox(height: 16),
                            InfoLabel(
                              label: 'Nombre del Producto',
                              child: TextFormBox(
                                controller: _nameController,
                                placeholder: 'Ingresar nombre del producto',
                                validator: (value) {
                                  if (value == null || value.isEmpty) {
                                    return 'Por favor ingrese el nombre del producto';
                                  }
                                  return null;
                                },
                                autovalidateMode:
                                    AutovalidateMode.onUserInteraction,
                              ),
                            ),
                            const SizedBox(height: 16),
                            InfoLabel(
                              label: 'Descripción',
                              child: TextFormBox(
                                controller: _descriptionController,
                                placeholder:
                                    'Ingresar descripción del producto',
                                maxLines: 3,
                                validator: (value) {
                                  if (value == null || value.isEmpty) {
                                    return 'Por favor ingrese una descripción';
                                  }
                                  return null;
                                },
                                autovalidateMode:
                                    AutovalidateMode.onUserInteraction,
                              ),
                            ),
                            const SizedBox(height: 16),
                            InfoLabel(
                              label: 'Precio (\$)',
                              child: TextFormBox(
                                controller: _priceController,
                                placeholder: 'Ingresar precio (ej. 9.99)',
                                validator: (value) {
                                  if (value == null || value.isEmpty) {
                                    return 'Por favor ingrese el precio';
                                  }
                                  try {
                                    final price = double.parse(value);
                                    if (price <= 0) {
                                      return 'El precio debe ser mayor a 0';
                                    }
                                  } catch (e) {
                                    return 'Por favor ingrese un precio válido';
                                  }
                                  return null;
                                },
                                autovalidateMode:
                                    AutovalidateMode.onUserInteraction,
                              ),
                            ),
                            const SizedBox(height: 16),
                            InfoLabel(
                              label: 'Imagen',
                              child: ImageUploadField(
                                initialUrl: _imageUrlController.text,
                                onImageUploaded: (url) {
                                  setState(() {
                                    _imageUrlController.text = url;
                                  });
                                },
                              ),
                            ),
                            const SizedBox(height: 16),
                            // Ingredients section
                            InfoLabel(
                              label: 'Ingredientes',
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  for (
                                    int i = 0;
                                    i < _ingredientControllers.length;
                                    i++
                                  )
                                    Padding(
                                      padding: const EdgeInsets.only(
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
                                              onChanged: (value) {
                                                // If this is the last textbox and it has text,
                                                // add a new empty textbox
                                                if (i ==
                                                        _ingredientControllers
                                                                .length -
                                                            1 &&
                                                    value.isNotEmpty) {
                                                  _addIngredientField();
                                                }
                                              },
                                            ),
                                          ),
                                          const SizedBox(width: 8),
                                          IconButton(
                                            icon: const Icon(
                                              FluentIcons.delete,
                                            ),
                                            onPressed:
                                                () => _deleteIngredientField(i),
                                          ),
                                        ],
                                      ),
                                    ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 16),
                            if (_errorMessage != null) ...[
                              InfoBar(
                                title: const Text('Error'),
                                content: Text(_errorMessage!),
                                severity: InfoBarSeverity.error,
                                isLong: true,
                              ),
                              const SizedBox(height: 16),
                            ],
                            Row(
                              mainAxisAlignment: MainAxisAlignment.end,
                              children: [
                                Button(
                                  child: const Text('Cancelar'),
                                  onPressed: () {
                                    _nameController.clear();
                                    _descriptionController.clear();
                                    _imageUrlController.clear();
                                    _priceController.clear();
                                    setState(() {
                                      _errorMessage = null;
                                    });
                                  },
                                ),
                                const SizedBox(width: 8),
                                FilledButton(
                                  onPressed:
                                      _isAddingProduct ? null : _addProduct,
                                  child:
                                      _isAddingProduct
                                          ? const Row(
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                              ProgressRing(strokeWidth: 2),
                                              SizedBox(width: 8),
                                              Text('Creando...'),
                                            ],
                                          )
                                          : const Text('Crear Producto'),
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
    );
  }
}
