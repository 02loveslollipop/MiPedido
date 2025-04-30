import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';
import '../../main.dart';

class AssignUserScreen extends StatefulWidget {
  const AssignUserScreen({super.key});

  @override
  State<AssignUserScreen> createState() => _AssignUserScreenState();
}

class _AssignUserScreenState extends State<AssignUserScreen> {
  bool _isLoadingUsers = true;
  bool _isLoadingRestaurants = true;
  bool _isAssigning = false;
  List<dynamic> _users = [];
  List<dynamic> _restaurants = [];
  String? _errorMessage;
  dynamic _selectedUser;
  dynamic _selectedRestaurant;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    await Future.wait([_loadUsers(), _loadRestaurants()]);
  }

  Future<void> _loadUsers() async {
    setState(() {
      _isLoadingUsers = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.listUsers();

    setState(() {
      _isLoadingUsers = false;
      if (result['success']) {
        _users = result['users'];
      } else {
        _errorMessage = result['error'] ?? 'Failed to load users';
      }
    });
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

  Future<void> _assignRestaurant() async {
    if (_selectedUser == null || _selectedRestaurant == null) {
      setState(() {
        _errorMessage = 'Debe seleccionar un usuario y un restaurante';
      });
      return;
    }

    setState(() {
      _isAssigning = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.assignRestaurantToUser(
      _selectedUser['id'],
      _selectedRestaurant['id'],
    );

    setState(() {
      _isAssigning = false;
    });

    if (result['success']) {
      setState(() {
        _selectedUser = null;
        _selectedRestaurant = null;
      });

      if (!mounted) return;
      showSnackbar(
        context,
        InfoBar(
          title: const Text('Éxito'),
          content: const Text('Restaurante asignado correctamente al usuario'),
          severity: InfoBarSeverity.success,
        ),
      );

      // Reload users to reflect changes
      _loadUsers();
    } else {
      setState(() {
        _errorMessage = result['error'] ?? 'Error al asignar restaurante';
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
    final bool isLoading = _isLoadingUsers || _isLoadingRestaurants;

    return ScaffoldPage(
      header: const PageHeader(title: Text('Asignar Restaurante a Usuario')),
      content:
          isLoading
              ? const Center(child: ProgressRing())
              : _errorMessage != null
              ? Center(
                child: InfoBar(
                  title: const Text('Error'),
                  content: Text(_errorMessage!),
                  severity: InfoBarSeverity.error,
                  isLong: true,
                  action: FilledButton(
                    child: const Text('Reintentar'),
                    onPressed: _loadData,
                  ),
                ),
              )
              : SingleChildScrollView(
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
                            label: 'Seleccionar Usuario',
                            child: ComboBox<dynamic>(
                              placeholder: const Text('Seleccione un usuario'),
                              isExpanded: true,
                              items:
                                  _users.map((user) {
                                    return ComboBoxItem<dynamic>(
                                      value: user,
                                      child: Text(user['username']),
                                    );
                                  }).toList(),
                              value: _selectedUser,
                              onChanged: (value) {
                                setState(() {
                                  _selectedUser = value;
                                  _errorMessage = null;
                                });
                              },
                            ),
                          ),
                          const SizedBox(height: 16),
                          InfoLabel(
                            label: 'Seleccionar Restaurante',
                            child: ComboBox<dynamic>(
                              placeholder: const Text(
                                'Seleccione un restaurante',
                              ),
                              isExpanded: true,
                              items:
                                  _restaurants.map((restaurant) {
                                    return ComboBoxItem<dynamic>(
                                      value: restaurant,
                                      child: Text(restaurant['name']),
                                    );
                                  }).toList(),
                              value: _selectedRestaurant,
                              onChanged: (value) {
                                setState(() {
                                  _selectedRestaurant = value;
                                  _errorMessage = null;
                                });
                              },
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
                                  setState(() {
                                    _selectedUser = null;
                                    _selectedRestaurant = null;
                                    _errorMessage = null;
                                  });
                                },
                              ),
                              const SizedBox(width: 8),
                              FilledButton(
                                onPressed:
                                    _isAssigning ? null : _assignRestaurant,
                                child:
                                    _isAssigning
                                        ? const Row(
                                          mainAxisSize: MainAxisSize.min,
                                          children: [
                                            ProgressRing(strokeWidth: 2),
                                            SizedBox(width: 8),
                                            Text('Asignando...'),
                                          ],
                                        )
                                        : const Text('Asignar Restaurante'),
                              ),
                            ],
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
