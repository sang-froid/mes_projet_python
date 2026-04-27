import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/auth_provider.dart';
import 'register_screen.dart';
import '../users/users_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;

    final auth = context.read<AuthProvider>();
    final success = await auth.login(
      email: _emailCtrl.text.trim(),
      motDePasse: _passwordCtrl.text,
    );

    if (success && mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const UsersScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                // Logo / Titre
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: const Color(0xFF6C63FF),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Icon(Icons.hub_rounded, color: Colors.white, size: 40),
                ),
                const SizedBox(height: 24),
                const Text(
                  'Connexion',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF2D3748),
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Bienvenue ! Connectez-vous à votre compte',
                  style: TextStyle(color: Colors.grey, fontSize: 14),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 40),

                // Formulaire
                Card(
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        children: [
                          // Email
                          TextFormField(
                            controller: _emailCtrl,
                            keyboardType: TextInputType.emailAddress,
                            decoration: _inputDecoration(
                              label: 'Email',
                              icon: Icons.email_outlined,
                            ),
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Email requis';
                              if (!v.contains('@')) return 'Email invalide';
                              return null;
                            },
                          ),
                          const SizedBox(height: 16),

                          // Mot de passe
                          TextFormField(
                            controller: _passwordCtrl,
                            obscureText: _obscurePassword,
                            decoration: _inputDecoration(
                              label: 'Mot de passe',
                              icon: Icons.lock_outline,
                            ).copyWith(
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscurePassword
                                      ? Icons.visibility_outlined
                                      : Icons.visibility_off_outlined,
                                ),
                                onPressed: () => setState(
                                    () => _obscurePassword = !_obscurePassword),
                              ),
                            ),
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Mot de passe requis';
                              return null;
                            },
                          ),
                          const SizedBox(height: 24),

                          // Erreur
                          Consumer<AuthProvider>(
                            builder: (_, auth, __) {
                              if (auth.errorMessage != null) {
                                return Container(
                                  width: double.infinity,
                                  padding: const EdgeInsets.all(12),
                                  margin: const EdgeInsets.only(bottom: 16),
                                  decoration: BoxDecoration(
                                    color: Colors.red.shade50,
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(color: Colors.red.shade200),
                                  ),
                                  child: Text(
                                    auth.errorMessage!,
                                    style: TextStyle(color: Colors.red.shade700),
                                  ),
                                );
                              }
                              return const SizedBox.shrink();
                            },
                          ),

                          // Bouton connexion
                          Consumer<AuthProvider>(
                            builder: (_, auth, __) {
                              return SizedBox(
                                width: double.infinity,
                                height: 52,
                                child: ElevatedButton(
                                  onPressed: auth.isLoading ? null : _login,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFF6C63FF),
                                    foregroundColor: Colors.white,
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    elevation: 0,
                                  ),
                                  child: auth.isLoading
                                      ? const CircularProgressIndicator(
                                          color: Colors.white, strokeWidth: 2)
                                      : const Text(
                                          'Se connecter',
                                          style: TextStyle(
                                              fontSize: 16,
                                              fontWeight: FontWeight.w600),
                                        ),
                                ),
                              );
                            },
                          ),
                        ],
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 20),

                // Lien inscription
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text("Pas encore de compte ? ",
                        style: TextStyle(color: Colors.grey)),
                    GestureDetector(
                      onTap: () {
                        context.read<AuthProvider>().clearError();
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                              builder: (_) => const RegisterScreen()),
                        );
                      },
                      child: const Text(
                        "S'inscrire",
                        style: TextStyle(
                          color: Color(0xFF6C63FF),
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(
      {required String label, required IconData icon}) {
    return InputDecoration(
      labelText: label,
      prefixIcon: Icon(icon, color: const Color(0xFF6C63FF)),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: Colors.grey.shade300),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: Colors.grey.shade300),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Color(0xFF6C63FF), width: 2),
      ),
      filled: true,
      fillColor: Colors.grey.shade50,
    );
  }
}
