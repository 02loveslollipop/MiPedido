import 'package:fluent_ui/fluent_ui.dart';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import 'package:flutter_acrylic/flutter_acrylic.dart';
import 'package:window_manager/window_manager.dart';
import 'api/api_connector.dart';
import 'screens/login.dart';
import 'screens/welcome.dart';
import 'screens/user/user_info.dart';
import 'screens/user/user_add.dart';
import 'screens/user/user_assign.dart';
import 'screens/admin/admin_add.dart';
import 'screens/restaurant/restaurant_list.dart';
import 'screens/restaurant/restaurant_add.dart';
import 'screens/restaurant/restaurant_edit.dart';
import 'screens/product/product_add.dart';
import 'screens/product/product_edit.dart';
import 'screens/logs/admin_logs.dart';

const String appTitle = 'MiPedido Admin';

/// Checks if the current environment is a desktop environment.
bool get isDesktop {
  if (kIsWeb) return false;
  return [
    TargetPlatform.windows,
    TargetPlatform.linux,
    TargetPlatform.macOS,
  ].contains(defaultTargetPlatform);
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  if (isDesktop) {
    await Window.initialize();
    await WindowManager.instance.ensureInitialized();

    windowManager.waitUntilReadyToShow().then((_) async {
      await windowManager.setTitle(appTitle);
      await windowManager.setTitleBarStyle(TitleBarStyle.normal);
      await windowManager.setBackgroundColor(Colors.transparent);
      await windowManager.setMaximizable(false);
      await windowManager.setResizable(true);
      await windowManager.center();
      await windowManager.show();
      await windowManager.setSkipTaskbar(false);
    });
  }

  runApp(const MiPedidoAdminApp());
}

class MiPedidoAdminApp extends StatefulWidget {
  const MiPedidoAdminApp({super.key});

  @override
  State<MiPedidoAdminApp> createState() => _MiPedidoAdminAppState();
}

class _MiPedidoAdminAppState extends State<MiPedidoAdminApp> {
  ThemeMode themeMode = ThemeMode.system;
  AccentColor accentColor = Colors.blue;
  bool isLoggedIn = false;

  @override
  void initState() {
    super.initState();
    _checkIfLoggedIn();
  }

  Future<void> _checkIfLoggedIn() async {
    // Check if there's a valid token in shared preferences
    final apiConnector = ApiConnector();
    final bool isAuthenticated = await apiConnector.isLoggedIn();

    // If the user has a token, let's verify it with the server to make sure it's still valid
    if (isAuthenticated) {
      try {
        final result = await apiConnector.getCurrentAdmin();
        isLoggedIn = result['success'] == true;
      } catch (e) {
        // If there's an error (like expired token), consider the user not logged in
        isLoggedIn = false;
        // Clear any invalid tokens
        await apiConnector.clearAuthInfo();
      }
    } else {
      isLoggedIn = false;
    }

    setState(() {
      // Update UI based on authentication status
    });
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AppTheme(themeMode, accentColor),
      builder: (context, _) {
        final appTheme = context.watch<AppTheme>();
        return FluentApp(
          title: appTitle,
          themeMode: appTheme.mode,
          theme: FluentThemeData(
            accentColor: appTheme.color,
            brightness: Brightness.light,
            visualDensity: VisualDensity.standard,
          ),
          darkTheme: FluentThemeData(
            accentColor: appTheme.color,
            brightness: Brightness.dark,
            visualDensity: VisualDensity.standard,
          ),
          home: isLoggedIn ? const AppShell() : const LoginScreen(),
          routes: {
            '/login': (context) => const LoginScreen(),
            '/dashboard': (context) => const AppShell(initialIndex: 0),
            '/users': (context) => const AppShell(initialIndex: 1),
            '/admins': (context) => const AppShell(initialIndex: 2),
            '/restaurants': (context) => const AppShell(initialIndex: 3),
            '/products': (context) => const AppShell(initialIndex: 4),
            '/orders': (context) => const AppShell(initialIndex: 5),
            '/logs': (context) => const AppShell(initialIndex: 6),
          },
        );
      },
    );
  }
}

class AppTheme extends ChangeNotifier {
  ThemeMode mode;
  AccentColor color;

  AppTheme(this.mode, this.color);

  void setMode(ThemeMode mode) {
    this.mode = mode;
    notifyListeners();
  }

  void setColor(AccentColor color) {
    this.color = color;
    notifyListeners();
  }
}

class AppShell extends StatefulWidget {
  final int initialIndex;

  const AppShell({super.key, this.initialIndex = 0});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _selectedIndex = 0;
  final List<NavigationPaneItem> _items = [
    PaneItem(
      icon: const Icon(FluentIcons.home),
      title: const Text('Inicio'),
      body: WelcomeScreen(),
    ),
    PaneItemExpander(
      icon: const Icon(FluentIcons.people),
      title: const Text('Usuarios'),
      body: const UserScreen(),
      items: [
        PaneItem(
          icon: const Icon(FluentIcons.add_friend),
          title: const Text('Agregar Usuario'),
          body: const AddUserScreen(),
        ),
        PaneItem(
          icon: const Icon(FluentIcons.link),
          title: const Text('Asignar Restaurantes'),
          body: const AssignUserScreen(),
        ),
      ],
    ),
    PaneItem(
      icon: const Icon(FluentIcons.add_friend),
      title: const Text('Agregar Administrador'),
      body: const AdminAddScreen(),
    ),
    PaneItemExpander(
      icon: const Icon(FluentIcons.city_next),
      title: const Text('Restaurantes'),
      body: const RestaurantListScreen(),
      items: [
        PaneItem(
          icon: const Icon(FluentIcons.add),
          title: const Text('Agregar Restaurante'),
          body: const RestaurantAddScreen(),
        ),
        PaneItem(
          icon: const Icon(FluentIcons.edit),
          title: const Text('Editar Restaurante'),
          body: const RestaurantEditScreen(),
        ),
      ],
    ),
    PaneItemExpander(
      icon: const Icon(FluentIcons.product_catalog),
      title: const Text('Productos'),
      body: const ProductAddScreen(),
      items: [
        PaneItem(
          icon: const Icon(FluentIcons.edit),
          title: const Text('Editar Productos'),
          body: const ProductEditScreen(),
        ),
      ],
    ),
    PaneItem(
      icon: const Icon(FluentIcons.history),
      title: const Text('Logs del Sistema'),
      body: const AdminLogsScreen(),
    ),
  ];

  @override
  void initState() {
    super.initState();
    _selectedIndex = widget.initialIndex;
  }

  @override
  Widget build(BuildContext context) {
    final appTheme = context.watch<AppTheme>();

    return NavigationView(
      appBar: NavigationAppBar(
        title: const Text(appTitle),
        actions: Padding(
          padding: const EdgeInsetsDirectional.only(end: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8.0),
                child: ToggleSwitch(
                  checked: appTheme.mode == ThemeMode.dark,
                  onChanged: (value) {
                    appTheme.setMode(value ? ThemeMode.dark : ThemeMode.light);
                  },
                  content: Icon(
                    appTheme.mode == ThemeMode.dark
                        ? FluentIcons.clear_night
                        : FluentIcons.sunny,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(FluentIcons.sign_out),
                onPressed: () async {
                  // Show loading indicator
                  showDialog(
                    context: context,
                    builder:
                        (context) => ContentDialog(
                          title: const Text('Cerrando sesión'),
                          content: const Center(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                ProgressRing(),
                                SizedBox(height: 16),
                                Text('Cerrando sesión...'),
                              ],
                            ),
                          ),
                        ),
                  );

                  // Log out by clearing the token
                  final apiConnector = ApiConnector();
                  await apiConnector.logout();

                  if (!mounted) return;

                  // Close the dialog and navigate to login
                  Navigator.of(context).pop();
                  Navigator.of(context).pushReplacementNamed('/login');
                },
              ),
            ],
          ),
        ),
      ),
      pane: NavigationPane(
        selected: _selectedIndex,
        onChanged: (index) => setState(() => _selectedIndex = index),
        displayMode: PaneDisplayMode.auto,
        items: _items,
        footerItems: [
          PaneItem(
            icon: const Icon(FluentIcons.settings),
            title: const Text('Configuración'),
            body: const Center(child: Text('Configuración (No implementado)')),
          ),
        ],
      ),
    );
  }
}
