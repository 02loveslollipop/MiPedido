import 'package:fluent_ui/fluent_ui.dart';
import 'screens/user/info.dart';
import 'screens/user/add.dart';
import 'screens/user/assign.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return FluentApp(
      title: 'Flutter Demo',
      theme: FluentThemeData(
        brightness: Brightness.light,
        accentColor: Colors.teal,
      ),
      home: const Home(),
    );
  }
}

List<NavigationPaneItem> items = [
  PaneItemHeader(header: Text('Administración')),
  PaneItemExpander(
    icon: const Icon(FluentIcons.user_clapper),
    title: const Text('Usuario'),
    body: UserScreen(),
    items: [
      PaneItem(
        icon: const Icon(FluentIcons.add),
        title: const Text('Agregar'),
        body: AddUserScreen(),
      ),
      PaneItem(
        icon: const Icon(FluentIcons.edit),
        title: const Text('Asignar'),
        body: AssignUserScreen(),
      ),
    ],
  ),
];

class Home extends StatefulWidget {
  const Home({super.key});

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  int topIndex = 0;

  @override
  Widget build(BuildContext context) {
    return ScaffoldPage(
      content: Center(
        child: NavigationView(
          pane: NavigationPane(
            selected: topIndex,
            displayMode: PaneDisplayMode.auto,
            items: items,
            onChanged: (i) {
              setState(() {
                topIndex = i;
              });
            },
          ),
        ),
      ),
    );
  }
}
