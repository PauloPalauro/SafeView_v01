import 'package:flutter/material.dart';
import 'package:flutter_application_1/Components/web_cam_streaming.dart';
import 'package:flutter_application_1/Pages/register_page.dart';
import 'package:flutter_application_1/Pages/test_page.dart';
import 'package:google_fonts/google_fonts.dart';

class MenuPage extends StatefulWidget {
  const MenuPage({super.key});

  @override
  State<MenuPage> createState() => _MenuPageState();
}

class _MenuPageState extends State<MenuPage> {
  int _selectedIndex = 0;
  static final List<Widget> _widgetOptions = <Widget>[
    const RegisterPage(),
    const WebcamStreamScreen(),
    const StorageListPage(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        iconTheme: const IconThemeData(color: Colors.white, size: 32),
        backgroundColor: const Color.fromRGBO(72, 105, 110, 1),
        title: Text(
          "SafeView",
          style: GoogleFonts.juliusSansOne(
            fontSize: 48,
            color: Colors.white,
          ),
        ),
        actions: [
          IconButton(
            onPressed: () {},
            icon: const Icon(
              Icons.person,
              size: 48,
              color: Colors.white,
            ),
          )
        ],
      ),
      body: _widgetOptions[_selectedIndex],
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(
                color: Color.fromRGBO(72, 105, 110, 1),
              ),
              child: Center(
                child: Text(
                  "SafeView",
                  style: GoogleFonts.juliusSansOne(
                    fontSize: 56,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            ListTile(
              title: const Text('Registrar'),
              onTap: () {
                _onItemTapped(0);
                Navigator.pop(context);
              },
            ),
            ListTile(
              title: const Text('Visualizar Camera'),
              onTap: () {
                _onItemTapped(1);
                Navigator.pop(context);
              },
            ),
            ListTile(
              title: const Text('Testes'),
              onTap: () {
                _onItemTapped(2);
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }
}
