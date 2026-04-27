import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';

enum AuthStatus { unknown, authenticated, unauthenticated }

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();

  AuthStatus _status = AuthStatus.unknown;
  UserModel? _currentUser;
  String? _errorMessage;
  bool _isLoading = false;

  AuthStatus get status => _status;
  UserModel? get currentUser => _currentUser;
  String? get errorMessage => _errorMessage;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _status == AuthStatus.authenticated;

  // ===== INIT =====
  Future<void> checkAuthStatus() async {
    final isLoggedIn = await _authService.isLoggedIn();
    _status = isLoggedIn ? AuthStatus.authenticated : AuthStatus.unauthenticated;
    notifyListeners();
  }

  // ===== INSCRIPTION =====
  Future<bool> register({
    required String nom,
    required String prenom,
    required String email,
    required String motDePasse,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _authService.register(
        nom: nom,
        prenom: prenom,
        email: email,
        motDePasse: motDePasse,
      );
      _currentUser = response.user;
      _status = AuthStatus.authenticated;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // ===== CONNEXION =====
  Future<bool> login({
    required String email,
    required String motDePasse,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _authService.login(
        email: email,
        motDePasse: motDePasse,
      );
      _currentUser = response.user;
      _status = AuthStatus.authenticated;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // ===== DÉCONNEXION =====
  Future<void> logout() async {
    await _authService.logout();
    _currentUser = null;
    _status = AuthStatus.unauthenticated;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
