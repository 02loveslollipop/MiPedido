import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';
import '../../main.dart';
import '../../components/image_upload_field.dart';
import '../../components/position_pick_component.dart';

class RestaurantAddScreen extends StatefulWidget {
  const RestaurantAddScreen({super.key});

  @override
  State<RestaurantAddScreen> createState() => _RestaurantAddScreenState();
}

class _RestaurantAddScreenState extends State<RestaurantAddScreen> {
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _imageUrlController = TextEditingController();
  final _typeController = TextEditingController();
  final _latitudeController = TextEditingController();
  final _longitudeController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  String? _errorMessage;

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

  Future<void> _addRestaurant() async {
    if (_formKey.currentState?.validate() != true) {
      return;
    }

    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();

    // Parse latitude and longitude from text controllers
    double? latitudeNull;
    double? longitudeNull;
    double latitude;
    double longitude;
    try {
      latitudeNull = double.tryParse(_latitudeController.text);
      longitudeNull = double.tryParse(_longitudeController.text);
      latitude = latitudeNull ?? 0.0;
      longitude = longitudeNull ?? 0.0;
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = 'Invalid latitude or longitude format';
      });
      return;
    }

    final result = await apiConnector.createRestaurant(
      _nameController.text,
      _descriptionController.text,
      _imageUrlController.text,
      type: _typeController.text,
      position: {'lat': latitude, 'lng': longitude},
    );

    if (!mounted) return;
    setState(() {
      _isLoading = false;
    });

    if (result['success']) {
      _nameController.clear();
      _descriptionController.clear();
      _imageUrlController.clear();
      _typeController.clear();
      _latitudeController.clear();
      _longitudeController.clear();

      if (!mounted) return;
      showSnackbar(
        context,
        const InfoBar(
          title: Text('Éxito'),
          content: Text('Restaurante creado correctamente'),
          severity: InfoBarSeverity.success,
        ),
      );
    } else {
      if (!mounted) return;
      setState(() {
        _errorMessage = result['error'] ?? 'Error al crear restaurante';
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
      header: const PageHeader(title: Text('Agregar Nuevo Restaurante')),
      content: Form(
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
                      label: 'Nombre del Restaurante',
                      child: TextFormBox(
                        controller: _nameController,
                        placeholder: 'Ingresar nombre del restaurante',
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Por favor ingrese el nombre del restaurante';
                          }
                          return null;
                        },
                        autovalidateMode: AutovalidateMode.onUserInteraction,
                      ),
                    ),
                    const SizedBox(height: 16),
                    InfoLabel(
                      label: 'Descripción',
                      child: TextFormBox(
                        controller: _descriptionController,
                        placeholder: 'Ingresar descripción del restaurante',
                        maxLines: 3,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Por favor ingrese una descripción';
                          }
                          return null;
                        },
                        autovalidateMode: AutovalidateMode.onUserInteraction,
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
                    InfoLabel(
                      label: 'Tipo de Restaurante',
                      child: TextFormBox(
                        controller: _typeController,
                        placeholder: 'Ingresar tipo de restaurante',
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Por favor ingrese el tipo de restaurante';
                          }
                          return null;
                        },
                        autovalidateMode: AutovalidateMode.onUserInteraction,
                      ),
                    ),
                    const SizedBox(height: 16),
                    InfoLabel(
                      label: 'Ubicación en el mapa',
                      child: PositionPickComponent(
                        onPositionSelected: (lat, lon) {
                          setState(() {
                            _latitudeController.text = lat.toString();
                            _longitudeController.text = lon.toString();
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
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Button(
                          child: const Text('Cancelar'),
                          onPressed: () {
                            _nameController.clear();
                            _descriptionController.clear();
                            _imageUrlController.clear();
                            _typeController.clear();
                            _latitudeController.clear();
                            _longitudeController.clear();
                            setState(() {
                              _errorMessage = null;
                            });
                          },
                        ),
                        const SizedBox(width: 8),
                        FilledButton(
                          onPressed: _isLoading ? null : _addRestaurant,
                          child:
                              _isLoading
                                  ? const Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      ProgressRing(strokeWidth: 2),
                                      SizedBox(width: 8),
                                      Text('Creando...'),
                                    ],
                                  )
                                  : const Text('Crear Restaurante'),
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
