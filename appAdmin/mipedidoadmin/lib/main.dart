import 'package:fluent_ui/fluent_ui.dart';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import 'package:flutter_acrylic/flutter_acrylic.dart';
import 'package:window_manager/window_manager.dart';
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
      //check if not in login screen
      await windowManager.setMaximizable(false);
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
    // You can check if the admin is already logged in
    // For example, by checking if there's a valid token in shared preferences
    // or making an API call to validate an existing token

    // For now, let's just assume the user is not logged in
    setState(() {
      isLoggedIn = false;
    });
  }

  @override
  Widget build(BuildContext context) {

    windowManager.waitUntilReadyToShow().then((_) async {
      await windowManager.setMaximizable(true);
      await windowManager.setResizable(true);
      await windowManager.setMinimumSize(const Size(800, 600));
      await windowManager.center();
      await windowManager.show();
      await windowManager.setSkipTaskbar(false);
    });

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
      body: const WelcomeScreen(),
    ),
    PaneItemExpander(
      icon: const Icon(FluentIcons.people),
      title: const Text('Usuarios'),
      body: const UserScreen(),
      items: [
        PaneItem(
          icon: const Icon(FluentIcons.people),
          title: const Text('Lista de Usuarios'),
          body: const UserScreen(),
        ),
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
          icon: const Icon(FluentIcons.clipboard_list),
          title: const Text('Lista de Restaurantes'),
          body: const RestaurantListScreen(),
        ),
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
          icon: const Icon(FluentIcons.add),
          title: const Text('Agregar Producto'),
          body: const ProductAddScreen(),
        ),
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
                icon: const Icon(FluentIcons.contact),
                onPressed: () {
                  // Show user profile or account settings
                },
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(FluentIcons.sign_out),
                onPressed: () {
                  // Log out functionality
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
