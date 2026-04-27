import 'user_model.dart';

class AuthResponseModel {
  final String token;
  final UserModel user;
  final String message;

  AuthResponseModel({
    required this.token,
    required this.user,
    required this.message,
  });

  factory AuthResponseModel.fromJson(Map<String, dynamic> json) {
    return AuthResponseModel(
      token: json['token'] ?? '',
      user: UserModel.fromJson(json['user'] as Map<String, dynamic>),
      message: json['message'] ?? '',
    );
  }
}
