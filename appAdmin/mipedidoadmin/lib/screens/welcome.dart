import 'package:fluent_ui/fluent_ui.dart';
import 'package:flutter/foundation.dart';
import 'package:window_manager/window_manager.dart';

import 'dart:developer';

class WelcomeScreen extends StatelessWidget {
  WelcomeScreen({super.key});

  bool isFirstTime = true;

  @override
  Widget build(BuildContext context) {

    if(!kIsWeb && isFirstTime) {
      windowManager.waitUntilReadyToShow().then((_) async {
        await windowManager.setMaximizable(true);
        await windowManager.setResizable(true);
        await windowManager.setMinimumSize(const Size(800, 600));
        await windowManager.setMaximumSize(const Size(10000, 10000));
        await windowManager.setSize(const Size(800, 600));
        await windowManager.center();
        await windowManager.show();
        await windowManager.setSkipTaskbar(false);
        Size result = await windowManager.getSize();
        log('Window size: $result');
        bool isResizable = await windowManager.isResizable();
        log('Window is resizable: $isResizable');
        isFirstTime = false;
      });
    }

    return ScaffoldPage(
      header: const PageHeader(
        title: Text('Bienvenido a MiPedido Admin Panel'),
      ),
      content: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(FluentIcons.home, size: 72, color: Colors.blue),
            const SizedBox(height: 24),
            const Text(
              'Bienvenido al Panel de Administración',
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Text(
              'Seleccione una opción del menú para comenzar',
              style: TextStyle(
                fontSize: 16,
                color:
                    FluentTheme.of(context).brightness == Brightness.light
                        ? Colors.grey[100]
                        : Colors.grey[80],
              ),
            ),
            const SizedBox(height: 48),
            InfoLabel(
              label: 'Versión del Sistema',
              child: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue.lightest,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Text(
                  'MiPedido Admin v1.0',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
