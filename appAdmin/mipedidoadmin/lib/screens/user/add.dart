import 'package:fluent_ui/fluent_ui.dart';

class AddUserScreen extends StatelessWidget {
  const AddUserScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ScaffoldPage(
      header: const PageHeader(title: Text('Agregar Usuario')),
      content: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Ingrese la información del nuevo usuario:',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 20),
            // Form fields
            InfoLabel(
              label: 'Nombre completo',
              child: TextFormBox(
                placeholder: 'Ingrese el nombre completo',
                expands: false,
              ),
            ),
            const SizedBox(height: 10),
            InfoLabel(
              label: 'Correo electrónico',
              child: TextFormBox(
                placeholder: 'ejemplo@correo.com',
                expands: false,
              ),
            ),
            const SizedBox(height: 10),
            InfoLabel(
              label: 'Teléfono',
              child: TextFormBox(
                placeholder: 'Ingrese el número de teléfono',
                expands: false,
              ),
            ),
            const SizedBox(height: 20),
            Button(
              child: const Text('Guardar Usuario'),
              onPressed: () {
                showDialog(
                  context: context,
                  builder:
                      (context) => ContentDialog(
                        title: const Text('Éxito'),
                        content: const Text('Usuario agregado correctamente.'),
                        actions: [
                          Button(
                            child: const Text('Aceptar'),
                            onPressed: () => Navigator.pop(context),
                          ),
                        ],
                      ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
