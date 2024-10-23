import 'package:flutter/material.dart';
import 'package:flutter_application_1/Pages/menu_page.dart';
import 'package:window_manager/window_manager.dart';

void main() async {
  // Inicializar o Flutter antes de rodar código assíncrono
  WidgetsFlutterBinding.ensureInitialized();

  // Inicializar o window_manager
  await windowManager.ensureInitialized();

  // Definir as opções da janela
  WindowOptions windowOptions = const WindowOptions(
    windowButtonVisibility: false,
    size: Size(1200, 700), // Tamanho inicial da janela
    minimumSize: Size(1200, 700), // Tamanho mínimo
    center: true, // Centralizar a janela
    title: 'Meu Aplicativo Flutter',
  );

  // Aplicar as opções e mostrar a janela
  windowManager.waitUntilReadyToShow(windowOptions, () async {
    await windowManager.show();
    await windowManager.focus();
  });

  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: MenuPage(),
    );
  }
}
