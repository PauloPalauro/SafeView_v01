// ignore_for_file: library_private_types_in_public_api

import 'package:flutter/material.dart';
import 'package:flutter_mjpeg/flutter_mjpeg.dart';
import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'dart:async';

class WebcamStreamScreen extends StatefulWidget {
  const WebcamStreamScreen({super.key});

  @override
  _WebcamStreamScreenState createState() => _WebcamStreamScreenState();
}

class _WebcamStreamScreenState extends State<WebcamStreamScreen> {
  String streamUrl = 'http://localhost:8001/video_feed';
  late WebSocketChannel channel;
  String statusMessage = 'Nenhuma mensagem recebida';
  String securityMessage = "";
  String? base64Image;
  Color securityMessageColor = Colors.red;

  int? countdown; // Variável para a contagem regressiva

  @override
  void initState() {
    super.initState();
    channel = IOWebSocketChannel.connect('ws://localhost:8001/ws');

    // Escuta as mensagens recebidas do WebSocket
    channel.stream.listen((message) {
      if (message.trim().toLowerCase().startsWith("img:")) {
        setState(() {
          base64Image = message.substring(4).trim();
        });
      } else if (message.trim().toLowerCase().startsWith("msg:")) {
        String msg = message.substring(4).trim();
        setState(() {
          statusMessage = msg;
        });

        // Iniciar contagem regressiva dependendo do conteúdo da mensagem
        if (msg.contains("Analise volta em 10") ||
            msg.contains("Pessoa Detectada. Tirando foto em 10 segundos")) {
          setState(() {
            countdown = 10;
          });
        }
      } else if (message.trim().toLowerCase().startsWith("sec:")) {
        String secMessage = message.substring(4).trim();
        setState(() {
          securityMessage = secMessage;
          securityMessageColor =
              secMessage.contains("Todos os itens de segurança presentes para ")
                  ? Colors.green
                  : Colors.red;
        });
      } else {
        setState(() {
          statusMessage = message.trim();
        });
      }
    });
  }

  @override
  void dispose() {
    channel.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Webcam Streaming'),
      ),
      body: Column(
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                flex: 1,
                child: Container(
                  padding: const EdgeInsets.all(20),
                  margin: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.3),
                        blurRadius: 15,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Mjpeg(
                    stream: streamUrl,
                    isLive: true,
                    error: (context, error, stack) {
                      return const Center(
                          child: Text('Erro ao carregar o stream'));
                    },
                  ),
                ),
              ),
              Expanded(
                flex: 1,
                child: Container(
                  padding: const EdgeInsets.all(20),
                  margin: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.3),
                        blurRadius: 15,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: base64Image != null
                      ? Image.memory(
                          const Base64Decoder().convert(base64Image!),
                          fit: BoxFit.cover,
                        )
                      : const Center(
                          child: Text(
                            'Nenhuma imagem recebida',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 5),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20.0),
            child: Text(
              statusMessage,
              style: const TextStyle(
                fontSize: 18,
                color: Colors.white,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          // Exibe o widget da contagem regressiva se `countdown` não for nulo
          if (countdown != null)
            CountdownWidget(
              initialCountdown: countdown!,
              onCountdownComplete: () {
                setState(() {
                  countdown = null;
                });
              },
            ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 80.0),
            child: Text(
              securityMessage,
              style: TextStyle(fontSize: 20, color: securityMessageColor),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }
}

class CountdownWidget extends StatefulWidget {
  final int initialCountdown;
  final VoidCallback onCountdownComplete;

  const CountdownWidget({
    super.key,
    required this.initialCountdown,
    required this.onCountdownComplete,
  });

  @override
  _CountdownWidgetState createState() => _CountdownWidgetState();
}

class _CountdownWidgetState extends State<CountdownWidget> {
  late int countdown;
  Timer? timer;

  @override
  void initState() {
    super.initState();
    countdown = widget.initialCountdown;
    timer = Timer.periodic(const Duration(seconds: 1), (Timer t) {
      setState(() {
        if (countdown > 0) {
          countdown -= 1;
        } else {
          t.cancel();
          widget
              .onCountdownComplete(); // Chama o callback quando a contagem termina
        }
      });
    });
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Text(
      'Contagem regressiva: $countdown segundos',
      style: const TextStyle(
        fontSize: 18,
        color: Colors.orange,
      ),
    );
  }
}
