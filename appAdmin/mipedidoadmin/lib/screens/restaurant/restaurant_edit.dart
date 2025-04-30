import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';
import 'restaurant_list.dart';
import '../../main.dart';

class RestaurantEditScreen extends StatefulWidget {
  const RestaurantEditScreen({super.key});

  @override
  State<RestaurantEditScreen> createState() => _RestaurantEditScreenState();
}

class _RestaurantEditScreenState extends State<RestaurantEditScreen> {
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _imageUrlController = TextEditingController();
  final _typeController = TextEditingController();
  final _latitudeController = TextEditingController();
  final _longitudeController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  bool _isLoadingRestaurants = true;
  bool _isUpdating = false;
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
    _typeController.dispose();
    _latitudeController.dispose();
    _longitudeController.dispose();
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
      } else {
        _errorMessage = result['error'] ?? 'Failed to load restaurants';
      }
    });
  }

  void _selectRestaurant(dynamic restaurant) {
    setState(() {
      _selectedRestaurant = restaurant;
      _nameController.text = restaurant['name'] ?? '';
      _descriptionController.text = restaurant['description'] ?? '';
      _imageUrlController.text = restaurant['img_url'] ?? '';
      _typeController.text = restaurant['type'] ?? '';

      // Handle position data
      if (restaurant['position'] != null) {
        _latitudeController.text =
            restaurant['position']['lat']?.toString() ?? '';
        _longitudeController.text =
            restaurant['position']['lng']?.toString() ?? '';
      } else {
        _latitudeController.text = '';
        _longitudeController.text = '';
      }

      _errorMessage = null;
    });
  }

  Future<void> _updateRestaurant() async {
    if (_formKey.currentState?.validate() != true ||
        _selectedRestaurant == null) {
      return;
    }

    setState(() {
      _isUpdating = true;
      _errorMessage = null;
    });

    // Parse latitude and longitude from text controllers
    double? latitude;
    double? longitude;
    try {
      if (_latitudeController.text.isNotEmpty) {
        latitude = double.parse(_latitudeController.text);
      }
      if (_longitudeController.text.isNotEmpty) {
        longitude = double.parse(_longitudeController.text);
      }
    } catch (e) {
      setState(() {
        _isUpdating = false;
        _errorMessage = 'Invalid latitude or longitude format';
      });
      return;
    }

    final apiConnector = ApiConnector();
    final result = await apiConnector.updateRestaurant(
      _selectedRestaurant['id'],
      name: _nameController.text,
      description: _descriptionController.text,
      imageUrl: _imageUrlController.text,
      type: _typeController.text,
      position: {'lat': latitude, 'lng': longitude},
    );

    setState(() {
      _isUpdating = false;
    });

    if (result['success']) {
      // Update was successful, reload restaurants
      await _loadRestaurants();

      if (!mounted) return;
      showSnackbar(
        context,
        const InfoBar(
          title: Text('Éxito'),
          content: Text('Restaurante actualizado correctamente'),
          severity: InfoBarSeverity.success,
        ),
      );

      // Navigate to RestaurantListScreen after successful update
      if (!mounted) return;
      Navigator.push(
        context,
        FluentPageRoute(builder: (context) => const MiPedidoAdminApp()),
      );
    } else {
      setState(() {
        _errorMessage = result['error'] ?? 'Error al actualizar el restaurante';
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
    return ScaffoldPage(
      header: const PageHeader(title: Text('Editar Restaurante')),
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
                child: Text('No hay restaurantes disponibles para editar'),
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
                                      child: Text(
                                        restaurant['name'] ?? 'Sin nombre',
                                      ),
                                    );
                                  }).toList(),
                              onChanged: (value) {
                                if (value != null) {
                                  _selectRestaurant(value);
                                }
                              },
                            ),
                          ),
                        ),
                        const Spacer(),
                        Button(
                          child: const Text('Refrescar'),
                          onPressed: _loadRestaurants,
                        ),
                      ],
                    ),
                  ),
                  // Main content area with restaurant edit form
                  Expanded(
                    child:
                        _selectedRestaurant == null
                            ? const Center(
                              child: Text(
                                'Seleccione un restaurante para editar',
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
                                            label: 'Nombre del Restaurante',
                                            child: TextFormBox(
                                              controller: _nameController,
                                              placeholder:
                                                  'Ingresar nombre del restaurante',
                                              validator: (value) {
                                                if (value == null ||
                                                    value.isEmpty) {
                                                  return 'Por favor ingrese el nombre del restaurante';
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
                                                  'Ingresar descripción del restaurante',
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
                                            label: 'URL de la Imagen',
                                            child: TextFormBox(
                                              controller: _imageUrlController,
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
                                          InfoLabel(
                                            label: 'Tipo de Restaurante',
                                            child: TextFormBox(
                                              controller: _typeController,
                                              placeholder:
                                                  'Ingresar tipo de restaurante',
                                              validator: (value) {
                                                if (value == null ||
                                                    value.isEmpty) {
                                                  return 'Por favor ingrese el tipo de restaurante';
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
                                            label: 'Latitud',
                                            child: TextFormBox(
                                              controller: _latitudeController,
                                              placeholder: 'Ingresar latitud',
                                              validator: (value) {
                                                if (value == null ||
                                                    value.isEmpty) {
                                                  return 'Por favor ingrese la latitud';
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
                                            label: 'Longitud',
                                            child: TextFormBox(
                                              controller: _longitudeController,
                                              placeholder: 'Ingresar longitud',
                                              validator: (value) {
                                                if (value == null ||
                                                    value.isEmpty) {
                                                  return 'Por favor ingrese la longitud';
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
                                                  color: Colors.grey[130],
                                                ),
                                                borderRadius:
                                                    BorderRadius.circular(4),
                                              ),
                                              child: ClipRRect(
                                                borderRadius:
                                                    BorderRadius.circular(4),
                                                child: Image.network(
                                                  _imageUrlController.text,
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
                                            mainAxisAlignment:
                                                MainAxisAlignment.end,
                                            children: [
                                              Button(
                                                child: const Text('Cancelar'),
                                                onPressed: () {
                                                  // Reset form to original values
                                                  _selectRestaurant(
                                                    _selectedRestaurant,
                                                  );
                                                },
                                              ),
                                              const SizedBox(width: 8),
                                              FilledButton(
                                                onPressed:
                                                    _isUpdating
                                                        ? null
                                                        : _updateRestaurant,
                                                child:
                                                    _isUpdating
                                                        ? const Row(
                                                          mainAxisSize:
                                                              MainAxisSize.min,
                                                          children: [
                                                            ProgressRing(
                                                              strokeWidth: 2,
                                                            ),
                                                            SizedBox(width: 8),
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
    );
  }
}
