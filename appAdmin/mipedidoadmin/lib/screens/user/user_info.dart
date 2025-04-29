import 'package:fluent_ui/fluent_ui.dart';
import 'package:fluent_ui/src/controls/surfaces/card.dart';
import 'package:flutter/material.dart' as material;
import '../../api/api_connector.dart';

class UserScreen extends StatefulWidget {
  const UserScreen({super.key});

  @override
  State<UserScreen> createState() => _UserScreenState();
}

class _UserScreenState extends State<UserScreen> {
  bool _isLoading = true;
  List<dynamic> _users = [];
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadUsers();
  }

  Future<void> _loadUsers() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.listUsers();

    setState(() {
      _isLoading = false;
      if (result['success']) {
        _users = result['users'];
      } else {
        _errorMessage = result['error'] ?? 'Failed to load users';
      }
    });
  }

  Future<void> _deleteUser(String userId) async {
    setState(() {
      _isLoading = true;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.deleteUser(userId);

    setState(() {
      _isLoading = false;
    });

    if (result['success']) {
      _loadUsers(); // Reload the user list
      showSnackbar(
        context,
        const InfoBar(
          title: Text('Éxito'),
          content: Text('Usuario eliminado con éxito'),
          severity: InfoBarSeverity.success,
        ),
      );
    } else {
      showSnackbar(
        context,
        InfoBar(
          title: const Text('Error'),
          content: Text(result['error'] ?? 'Failed to delete user'),
          severity: InfoBarSeverity.error,
        ),
      );
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
      header: const PageHeader(title: Text('Gestión de Usuarios')),
      content:
          _isLoading
              ? const Center(child: ProgressRing())
              : _errorMessage != null
              ? Center(
                child: InfoBar(
                  title: const Text('Error'),
                  content: Text(_errorMessage!),
                  severity: InfoBarSeverity.error,
                  isLong: true,
                ),
              )
              : _users.isEmpty
              ? const Center(child: Text('No hay usuarios registrados'))
              : ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  const SizedBox(height: 12),
                  CommandBar(
                    mainAxisAlignment: MainAxisAlignment.end,
                    primaryItems: [
                      CommandBarButton(
                        icon: const Icon(FluentIcons.refresh),
                        label: const Text('Refrescar'),
                        onPressed: _loadUsers,
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Card(
                    child: SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: material.DataTable(
                        columns: const [
                          material.DataColumn(label: Text('ID')),
                          material.DataColumn(label: Text('Username')),
                          material.DataColumn(label: Text('Restaurant ID')),
                          material.DataColumn(label: Text('Acciones')),
                        ],
                        rows:
                            _users.map<material.DataRow>((user) {
                              return material.DataRow(
                                cells: [
                                  material.DataCell(Text(user['id'] ?? 'N/A')),
                                  material.DataCell(Text(user['username'] ?? 'N/A')),
                                  material.DataCell(
                                    Text(
                                      user['restaurant_id'] ?? 'No asignado',
                                    ),
                                  ),
                                  material.DataCell(
                                    Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        IconButton(
                                          icon: const Icon(FluentIcons.edit),
                                          onPressed: () {
                                            // Edit user action (implement later)
                                          },
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              );
                            }).toList(),
                      ),
                    ),
                  ),
                ],
              ),
    );
  }
}
