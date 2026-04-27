class UserModel {
  final String id;
  final String nom;
  final String prenom;
  final String email;
  final String role;
  final String createdAt;

  UserModel({
    required this.id,
    required this.nom,
    required this.prenom,
    required this.email,
    required this.role,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id']?.toString() ?? '',
      nom: json['nom'] ?? '',
      prenom: json['prenom'] ?? '',
      email: json['email'] ?? '',
      role: json['role'] ?? 'USER',
      createdAt: json['createdAt'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nom': nom,
      'prenom': prenom,
      'email': email,
      'role': role,
      'createdAt': createdAt,
    };
  }

  String get nomComplet => '$prenom $nom';
}
