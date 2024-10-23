import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = "http://127.0.0.1:8000"; // URL base da API

  Future<Map<String, dynamic>> loginUser(
      final String nome, String senha) async {
    final url = Uri.parse('$baseUrl/login');

    final Map<String, dynamic> requestBody = {
      'nome': nome,
      'senha': senha,
    };

    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode(requestBody),
      );

      if (response.statusCode == 200) {
        // Registro bem-sucedido
        return json.decode(response.body);
      } else {
        // Algo deu errado, trate o erro aqui
        return {
          'error': true,
          'message': json.decode(response.body)['detail'] ?? 'Erro desconhecido'
        };
      }
    } catch (e) {
      // Exceção ao fazer a requisição
      return {'error': true, 'message': e.toString()};
    }
  }

  Future<Map<String, dynamic>> registerUser(
      String email, String nome, String senha) async {
    final url = Uri.parse(
        '$baseUrl/registra_usuario_padrao'); // Apenas o endpoint necessário

    // Montando o body da requisição
    final Map<String, dynamic> requestBody = {
      'email': email,
      'nome': nome,
      'senha': senha,
    };

    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode(requestBody),
      );

      if (response.statusCode == 201) {
        // Registro bem-sucedido
        return json.decode(response.body);
      } else {
        // Algo deu errado, trate o erro aqui
        return {
          'error': true,
          'message': json.decode(response.body)['detail'] ?? 'Erro desconhecido'
        };
      }
    } catch (e) {
      // Exceção ao fazer a requisição
      return {'error': true, 'message': e.toString()};
    }
  }
}
