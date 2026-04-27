class GraphQLQueries {
  // ===== MUTATIONS =====

  static const String register = r'''
    mutation Register($input: RegisterInput!) {
      register(input: $input) {
        token
        message
        user {
          id
          nom
          prenom
          email
          role
          createdAt
        }
      }
    }
  ''';

  static const String login = r'''
    mutation Login($input: LoginInput!) {
      login(input: $input) {
        token
        message
        user {
          id
          nom
          prenom
          email
          role
          createdAt
        }
      }
    }
  ''';

  // ===== QUERIES =====

  static const String getAllUsers = r'''
    query GetAllUsers {
      getAllUsers {
        id
        nom
        prenom
        email
        role
        createdAt
      }
    }
  ''';

  static const String getUserById = r'''
    query GetUserById($id: ID!) {
      getUserById(id: $id) {
        id
        nom
        prenom
        email
        role
        createdAt
      }
    }
  ''';

  static const String me = r'''
    query Me {
      me {
        id
        nom
        prenom
        email
        role
        createdAt
      }
    }
  ''';
}
