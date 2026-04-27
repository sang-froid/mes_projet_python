import 'package:graphql_flutter/graphql_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/auth_response_model.dart';
import '../models/user_model.dart';
import '../utils/graphql_queries.dart';
import '../utils/graphql_config.dart';

class AuthService {
  // ===== INSCRIPTION =====
  Future<AuthResponseModel> register({
    required String nom,
    required String prenom,
    required String email,
    required String motDePasse,
    String role = 'USER',
  }) async {
    final client = await GraphQLConfig.getClient();

    final result = await client.mutate(
      MutationOptions(
        document: gql(GraphQLQueries.register),
        variables: {
          'input': {
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'motDePasse': motDePasse,
            'role': role,
          },
        },
      ),
    );

    if (result.hasException) {
      final msg = result.exception?.graphqlErrors.isNotEmpty == true
          ? result.exception!.graphqlErrors.first.message
          : 'Erreur lors de l\'inscription';
      throw Exception(msg);
    }

    final data = result.data!['register'] as Map<String, dynamic>;
    final response = AuthResponseModel.fromJson(data);

    // Sauvegarder le token
    await _saveToken(response.token);
    return response;
  }

  // ===== CONNEXION =====
  Future<AuthResponseModel> login({
    required String email,
    required String motDePasse,
  }) async {
    final client = await GraphQLConfig.getClient();

    final result = await client.mutate(
      MutationOptions(
        document: gql(GraphQLQueries.login),
        variables: {
          'input': {
            'email': email,
            'motDePasse': motDePasse,
          },
        },
      ),
    );

    if (result.hasException) {
      final msg = result.exception?.graphqlErrors.isNotEmpty == true
          ? result.exception!.graphqlErrors.first.message
          : 'Email ou mot de passe incorrect';
      throw Exception(msg);
    }

    final data = result.data!['login'] as Map<String, dynamic>;
    final response = AuthResponseModel.fromJson(data);

    await _saveToken(response.token);
    return response;
  }

  // ===== DÉCONNEXION =====
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
    await prefs.remove('user_email');
  }

  // ===== TOKEN =====
  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('jwt_token', token);
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('jwt_token');
  }

  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }
}
