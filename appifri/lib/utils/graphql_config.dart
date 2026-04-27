import 'package:graphql_flutter/graphql_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';
class GraphQLConfig {
  static const String apiUrl = 'http://192.168.100.19:8082/graphql'; 
  // static const String apiUrl = 'http://localhost:8080/graphql'; 

  static Future<GraphQLClient> getClient() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('jwt_token');

    final authLink = AuthLink(
      getToken: () async => token != null ? 'Bearer $token' : null,
    );

    final httpLink = HttpLink(apiUrl);
    final link = authLink.concat(httpLink);

    return GraphQLClient(
      link: link,
      cache: GraphQLCache(store: InMemoryStore()),
    );
  }

  static ValueNotifier<GraphQLClient> clientNotifier(String? token) {
    final authLink = AuthLink(
      getToken: () async => token != null ? 'Bearer $token' : null,
    );

    final httpLink = HttpLink(apiUrl);
    final link = authLink.concat(httpLink);

    return ValueNotifier(
      GraphQLClient(
        link: link,
        cache: GraphQLCache(store: InMemoryStore()),
      ),
    );
  }
}
