import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';

class AdminAddScreen extends StatefulWidget {
  const AdminAddScreen({super.key});

  @override
  State<AdminAddScreen> createState() => _AdminAddScreenState();
}

class _AdminAddScreenState extends State<AdminAddScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  String? _errorMessage;
  bool _showPassword = false;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _addAdmin() async {
    if (_formKey.currentState?.validate() != true) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.createAdmin(
      _usernameController.text,
      _passwordController.text,
    );

    setState(() {
      _isLoading = false;
    });

    if (result['success']) {
      _usernameController.clear();
      _passwordController.clear();

      if (!mounted) return;
      showSnackbar(
        context,
        const InfoBar(
          title: Text('Éxito'),
          content: Text('Administrador creado correctamente'),
          severity: InfoBarSeverity.success,
        ),
      );
    } else {
      setState(() {
        _errorMessage = result['error'] ?? 'Error al crear administrador';
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
      header: const PageHeader(title: Text('Agregar Nuevo Administrador')),
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
                      label: 'Nombre de Usuario',
                      child: TextFormBox(
                        controller: _usernameController,
                        placeholder: 'Ingresar nombre de usuario',
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Por favor ingrese un nombre de usuario';
                          }
                          return null;
                        },
                        autovalidateMode: AutovalidateMode.onUserInteraction,
                      ),
                    ),
                    const SizedBox(height: 16),
                    InfoLabel(
                      label: 'Contraseña',
                      child: TextFormBox(
                        controller: _passwordController,
                        placeholder: 'Ingresar contraseña',
                        obscureText: !_showPassword,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Por favor ingrese una contraseña';
                          }
                          if (value.length < 8) {
                            return 'La contraseña debe tener al menos 8 caracteres';
                          }
                          return null;
                        },
                        autovalidateMode: AutovalidateMode.onUserInteraction,
                        suffix: IconButton(
                          icon: Icon(
                            _showPassword ? FluentIcons.hide : FluentIcons.view,
                          ),
                          onPressed: () {
                            setState(() {
                              _showPassword = !_showPassword;
                            });
                          },
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
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
                            _usernameController.clear();
                            _passwordController.clear();
                            setState(() {
                              _errorMessage = null;
                            });
                          },
                        ),
                        const SizedBox(width: 8),
                        FilledButton(
                          onPressed: _isLoading ? null : _addAdmin,
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
                                  : const Text('Crear Administrador'),
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
