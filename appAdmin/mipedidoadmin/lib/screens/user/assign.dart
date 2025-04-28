import 'package:fluent_ui/fluent_ui.dart';

class AssignUserScreen extends StatefulWidget {
  const AssignUserScreen({Key? key}) : super(key: key);

  @override
  State<AssignUserScreen> createState() => _AssignUserScreenState();
}

class _AssignUserScreenState extends State<AssignUserScreen> {
  final List<String> users = ['Juan Pérez', 'María López', 'Carlos Rodríguez'];
  final List<String> roles = ['Administrador', 'Vendedor', 'Cliente'];

  String? selectedUser;
  String? selectedRole;

  @override
  Widget build(BuildContext context) {
    return ScaffoldPage(
      header: const PageHeader(title: Text('Asignar Roles')),
      content: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Asignar rol a usuario:',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 20),
            InfoLabel(
              label: 'Usuario',
              child: ComboBox<String>(
                placeholder: const Text('Seleccione un usuario'),
                isExpanded: true,
                items:
                    users.map((user) {
                      return ComboBoxItem<String>(
                        value: user,
                        child: Text(user),
                      );
                    }).toList(),
                value: selectedUser,
                onChanged: (value) {
                  setState(() => selectedUser = value);
                },
              ),
            ),
            const SizedBox(height: 15),
            InfoLabel(
              label: 'Rol a asignar',
              child: ComboBox<String>(
                placeholder: const Text('Seleccione un rol'),
                isExpanded: true,
                items:
                    roles.map((role) {
                      return ComboBoxItem<String>(
                        value: role,
                        child: Text(role),
                      );
                    }).toList(),
                value: selectedRole,
                onChanged: (value) {
                  setState(() => selectedRole = value);
                },
              ),
            ),
            const SizedBox(height: 20),
            Button(
              child: const Text('Asignar Rol'),
              onPressed:
                  (selectedUser != null && selectedRole != null)
                      ? () {
                        showDialog(
                          context: context,
                          builder:
                              (context) => ContentDialog(
                                title: const Text('Éxito'),
                                content: Text(
                                  'Se ha asignado el rol de $selectedRole a $selectedUser.',
                                ),
                                actions: [
                                  Button(
                                    child: const Text('Aceptar'),
                                    onPressed: () => Navigator.pop(context),
                                  ),
                                ],
                              ),
                        );
                      }
                      : null,
            ),
          ],
        ),
      ),
    );
  }
}
