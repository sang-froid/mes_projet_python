import 'package:graphql_flutter/graphql_flutter.dart';
import '../models/user_model.dart';
import '../utils/graphql_queries.dart';
import '../utils/graphql_config.dart';

class UserService {
  // ===== LISTE DES UTILISATEURS =====
  Future<List<UserModel>> getAllUsers() async {
    final client = await GraphQLConfig.getClient();

    final result = await client.query(
      QueryOptions(
        document: gql(GraphQLQueries.getAllUsers),
        fetchPolicy: FetchPolicy.networkOnly,
      ),
    );

    if (result.hasException) {
      final msg = result.exception?.graphqlErrors.isNotEmpty == true
          ? result.exception!.graphqlErrors.first.message
          : 'Erreur lors du chargement des utilisateurs';
      throw Exception(msg);
    }

    final List<dynamic> usersJson = result.data!['getAllUsers'] as List<dynamic>;
    return usersJson
        .map((json) => UserModel.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  // ===== UTILISATEUR PAR ID =====
  Future<UserModel> getUserById(String id) async {
    final client = await GraphQLConfig.getClient();

    final result = await client.query(
      QueryOptions(
        document: gql(GraphQLQueries.getUserById),
        variables: {'id': id},
      ),
    );

    if (result.hasException) {
      throw Exception('Utilisateur introuvable');
    }

    return UserModel.fromJson(
        result.data!['getUserById'] as Map<String, dynamic>);
  }

  // ===== MON PROFIL =====
  Future<UserModel> getMe() async {
    final client = await GraphQLConfig.getClient();

    final result = await client.query(
      QueryOptions(
        document: gql(GraphQLQueries.me),
        fetchPolicy: FetchPolicy.networkOnly,
      ),
    );

    if (result.hasException) {
      throw Exception('Erreur lors du chargement du profil');
    }

    return UserModel.fromJson(result.data!['me'] as Map<String, dynamic>);
  }
}
