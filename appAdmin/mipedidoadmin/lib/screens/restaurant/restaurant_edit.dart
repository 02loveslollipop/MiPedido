import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';
import 'restaurant_list.dart';
import '../../main.dart';
import '../../components/image_upload_field.dart';
import '../../components/position_pick_component.dart';

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

    if (!mounted) return;
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
    if (!mounted) return;
    setState(() {
      _selectedRestaurant = restaurant;
      _nameController.text = restaurant['name'] ?? '';
      _descriptionController.text = restaurant['description'] ?? '';
      _imageUrlController.text = restaurant['img_url'] ?? '';
      _previousImageUrl = restaurant['img_url'] ?? '';
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
      if (!mounted) return;
      setState(() {
        _isUpdating = false;
        _errorMessage = 'Invalid latitude or longitude format';
      });
      return;
    }

    final apiConnector = ApiConnector();

    // If the image URL changed and the previous one is a blob, delete it
    if (_previousImageUrl != null &&
        _previousImageUrl!.isNotEmpty &&
        _previousImageUrl != _imageUrlController.text &&
        _previousImageUrl!.contains('/blob/')) {
      await apiConnector.deleteFileFromBlobStorage(_previousImageUrl!);
    }

    final result = await apiConnector.updateRestaurant(
      _selectedRestaurant['id'],
      name: _nameController.text,
      description: _descriptionController.text,
      imageUrl: _imageUrlController.text,
      type: _typeController.text,
      position: {'lat': latitude, 'lng': longitude},
    );

    if (!mounted) return;
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
      if (!mounted) return;
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
                    onPressed: _loadRestaurants,
                    child: const Text('Reintentar'),
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
                          onPressed: _loadRestaurants,
                          child: const Text('Refrescar'),
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
                                            label: 'Imagen',
                                            child: ImageUploadField(
                                              initialUrl:
                                                  _imageUrlController.text,
                                              onImageUploaded: (url) {
                                                setState(() {
                                                  _imageUrlController.text =
                                                      url;
                                                });
                                              },
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
                                            label: 'Ubicación en el mapa',
                                            child: PositionPickComponent(
                                              onPositionSelected: (lat, lon) {
                                                setState(() {
                                                  _latitudeController.text =
                                                      lat.toString();
                                                  _longitudeController.text =
                                                      lon.toString();
                                                });
                                              },
                                            ),
                                          ),
                                          const SizedBox(height: 16),
                                          // InfoLabel(
                                          //   label: 'Latitud',
                                          //   child: TextFormBox(
                                          //     controller: _latitudeController,
                                          //     placeholder: 'Ingresar latitud',
                                          //     validator: (value) {
                                          //       if (value == null || value.isEmpty) {
                                          //         return 'Por favor ingrese la latitud';
                                          //       }
                                          //       return null;
                                          //     },
                                          //     autovalidateMode: AutovalidateMode.onUserInteraction,
                                          //   ),
                                          // ),
                                          // const SizedBox(height: 16),
                                          // InfoLabel(
                                          //   label: 'Longitud',
                                          //   child: TextFormBox(
                                          //     controller: _longitudeController,
                                          //     placeholder: 'Ingresar longitud',
                                          //     validator: (value) {
                                          //       if (value == null || value.isEmpty) {
                                          //         return 'Por favor ingrese la longitud';
                                          //       }
                                          //       return null;
                                          //     },
                                          //     autovalidateMode: AutovalidateMode.onUserInteraction,
                                          //   ),
                                          // ),
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
