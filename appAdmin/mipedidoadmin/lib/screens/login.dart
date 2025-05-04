import 'package:fluent_ui/fluent_ui.dart';
import '../api/api_connector.dart';
import 'package:window_manager/window_manager.dart';
import 'package:flutter/foundation.dart';
import '../main.dart';

bool get isDesktop {
  if (kIsWeb) return false;
  return [
    TargetPlatform.windows,
    TargetPlatform.linux,
    TargetPlatform.macOS,
  ].contains(defaultTargetPlatform);
}

class LoginScreen extends StatefulWidget {
  final void Function(BuildContext context)? onLoginSuccess;

  const LoginScreen({super.key, this.onLoginSuccess});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  bool _isLoading = false;
  bool _isPasswordVisible = false;
  String? _errorMessage;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
    if (!kIsWeb) {
    windowManager.waitUntilReadyToShow().then((_) async {
        await windowManager.setMaximizable(true);
        await windowManager.setResizable(true);
        await windowManager.setMinimumSize(const Size(800, 600));
        await windowManager.setMaximumSize(const Size(10000, 10000));
        await windowManager.setSize(const Size(800, 600));
        await windowManager.center();
        await windowManager.show();
        await windowManager.setSkipTaskbar(false);
      });
    }
  }

  Future<void> _login() async {
    if (_formKey.currentState?.validate() != true) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.login(
      _usernameController.text,
      _passwordController.text,
    );

    setState(() {
      _isLoading = false;
    });

    if (result['success']) {
      if (!mounted) return;

      Navigator.of(context).pushReplacement(
        FluentPageRoute(builder: (context) => const AppShell()),
      );
    } else {
      setState(() {
        _errorMessage = result['error'] ?? 'Error de autenticación';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    windowManager.waitUntilReadyToShow().then((_) async {
      await windowManager.setMaximizable(false);
      //await windowManager.setResizable(false);
      await windowManager.setMinimumSize(const Size(600, 600));
      await windowManager.setMaximumSize(const Size(600, 600));
      await windowManager.setSize(const Size(600, 600));
      await windowManager.center();
      await windowManager.show();
      await windowManager.setSkipTaskbar(false);
    });

    return ScaffoldPage(
      content: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Color(0xFF006A60), // Dark blue
              Color(0xFF004C44), // Light blue
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: Form(
            key: _formKey,
            child: Container(
              constraints: const BoxConstraints(maxWidth: 400),
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Color.fromARGB(96, 0, 0, 0),
                borderRadius: BorderRadius.circular(8),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.2),
                    blurRadius: 10,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Logo or app name
                  Column(
                    children: [
                      SizedBox(
                        height: 72,
                        //rounded corners
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(16),
                          child: Image(
                            image: AssetImage('assets/icon.png'),
                            fit: BoxFit.contain,
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'MiPedido - Admin',
                        style: FluentTheme.of(context).typography.title,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Panel de Administración',
                        style: TextStyle(
                          color: Color.fromARGB(255, 184, 184, 184),
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),

                  // Error message
                  if (_errorMessage != null) ...[
                    InfoBar(
                      title: const Text('Error'),
                      content: Text(_errorMessage!),
                      severity: InfoBarSeverity.error,
                      isLong: true,
                    ),
                    const SizedBox(height: 16),
                  ],

                  // Username field
                  InfoLabel(
                    label: 'Nombre de Usuario',
                    child: TextFormBox(
                      controller: _usernameController,
                      placeholder: 'Ingrese su nombre de usuario',
                      prefix: const Padding(
                        padding: EdgeInsets.only(left: 8),
                        child: Icon(FluentIcons.contact),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Por favor ingrese su nombre de usuario';
                        }
                        return null;
                      },
                      autovalidateMode: AutovalidateMode.onUserInteraction,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Password field
                  InfoLabel(
                    label: 'Contraseña',
                    child: TextFormBox(
                      controller: _passwordController,
                      placeholder: 'Ingrese su contraseña',
                      obscureText: !_isPasswordVisible,
                      prefix: const Padding(
                        padding: EdgeInsets.only(left: 8),
                        child: Icon(FluentIcons.lock),
                      ),
                      suffix: IconButton(
                        icon: Icon(
                          _isPasswordVisible
                              ? FluentIcons.hide3
                              : FluentIcons.view,
                        ),
                        onPressed: () {
                          setState(() {
                            _isPasswordVisible = !_isPasswordVisible;
                          });
                        },
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Por favor ingrese su contraseña';
                        }
                        return null;
                      },
                      autovalidateMode: AutovalidateMode.onUserInteraction,
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Login button
                  FilledButton(
                    onPressed: _isLoading ? null : _login,
                    child:
                        _isLoading
                            ? const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: ProgressRing(strokeWidth: 2),
                                ),
                                SizedBox(width: 12),
                                Text('Iniciando sesión...'),
                              ],
                            )
                            : const Text('Iniciar Sesión'),
                  ),

                  const SizedBox(height: 8),
                  const Text(
                    '© 2025 02loveslollipop. Todos los derechos reservados.',
                    style: TextStyle(
                      color: Color.fromARGB(255, 184, 184, 184),
                      fontSize: 12,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
