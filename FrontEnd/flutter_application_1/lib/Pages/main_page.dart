import 'package:flutter/material.dart';
import 'package:flutter_application_1/Components/custom_button.dart';
import 'package:flutter_application_1/Pages/login_page.dart';
import 'package:google_fonts/google_fonts.dart';

class MainPage extends StatefulWidget {
  const MainPage({super.key});

  @override
  State<MainPage> createState() => _MainPageState();
}

class _MainPageState extends State<MainPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Container(
          margin: const EdgeInsets.all(100),
          decoration: BoxDecoration(
            border:
                Border.all(width: 1, color: const Color.fromARGB(50, 0, 0, 0)),
            color: const Color.fromARGB(255, 213, 213, 213),
            borderRadius: const BorderRadius.all(Radius.circular(10)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      "Bem-vindo",
                      style: GoogleFonts.jost(
                          color: const Color(0xff494949),
                          fontWeight: FontWeight.normal,
                          fontSize: 64),
                    ),
                    const SizedBox(
                      height: 10,
                    ),
                    Text(
                      "SafeView",
                      style: GoogleFonts.juliusSansOne(
                        fontSize: 82,
                        color: const Color(0xff5B9EB3),
                      ),
                    ),
                    Text(
                      "Visão na proteção, cuidado\nem cada detalhe!",
                      textAlign: TextAlign.center,
                      style: GoogleFonts.jost(
                        fontSize: 24,
                        fontWeight: FontWeight.w400,
                        color: const Color(0xff5B9EB3),
                      ),
                    ),
                    const SizedBox(
                      height: 40,
                    ),
                    CustomButton(
                      text: 'LOGIN',
                      function: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                              builder: (context) => const LoginPage()),
                        );
                      },
                    )
                  ],
                ),
              ),
              Expanded(
                  child: Container(
                margin: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color.fromARGB(50, 0, 0, 0),
                  borderRadius: BorderRadius.circular(40),
                  border: Border.all(
                    color: const Color.fromARGB(50, 0, 0, 0),
                    width: 9.0,
                  ),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(30),
                  child: const Image(
                    fit: BoxFit.contain,
                    image: AssetImage('lib/images/trabalhadores_image.png'),
                  ),
                ),
              ))
            ],
          ),
        ),
      ),
    );
  }
}
