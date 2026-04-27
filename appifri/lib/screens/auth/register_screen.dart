import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/auth_provider.dart';
import '../users/users_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nomCtrl = TextEditingController();
  final _prenomCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _confirmPasswordCtrl = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirm = true;

  @override
  void dispose() {
    _nomCtrl.dispose();
    _prenomCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _confirmPasswordCtrl.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;

    final auth = context.read<AuthProvider>();
    final success = await auth.register(
      nom: _nomCtrl.text.trim(),
      prenom: _prenomCtrl.text.trim(),
      email: _emailCtrl.text.trim(),
      motDePasse: _passwordCtrl.text,
    );

    if (success && mounted) {
      Navigator.pushAndRemoveUntil(
        context,
        MaterialPageRoute(builder: (_) => const UsersScreen()),
        (route) => false,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: const Color(0xFF2D3748),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Créer un compte',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF2D3748),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Remplissez les informations ci-dessous',
                style: TextStyle(color: Colors.grey, fontSize: 14),
              ),
              const SizedBox(height: 32),

              Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      children: [
                        // Prenom + Nom (row)
                        Row(
                          children: [
                            Expanded(
                              child: TextFormField(
                                controller: _prenomCtrl,
                                decoration:
                                    _inputDecoration('Prénom', Icons.person_outline),
                                validator: (v) =>
                                    v == null || v.isEmpty ? 'Requis' : null,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: TextFormField(
                                controller: _nomCtrl,
                                decoration:
                                    _inputDecoration('Nom', Icons.badge_outlined),
                                validator: (v) =>
                                    v == null || v.isEmpty ? 'Requis' : null,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),

                        // Email
                        TextFormField(
                          controller: _emailCtrl,
                          keyboardType: TextInputType.emailAddress,
                          decoration:
                              _inputDecoration('Email', Icons.email_outlined),
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
                          decoration:
                              _inputDecoration('Mot de passe', Icons.lock_outline)
                                  .copyWith(
                            suffixIcon: IconButton(
                              icon: Icon(_obscurePassword
                                  ? Icons.visibility_outlined
                                  : Icons.visibility_off_outlined),
                              onPressed: () => setState(
                                  () => _obscurePassword = !_obscurePassword),
                            ),
                          ),
                          validator: (v) {
                            if (v == null || v.isEmpty) return 'Mot de passe requis';
                            if (v.length < 6) return 'Minimum 6 caractères';
                            return null;
                          },
                        ),
                        const SizedBox(height: 16),

                        // Confirmation
                        TextFormField(
                          controller: _confirmPasswordCtrl,
                          obscureText: _obscureConfirm,
                          decoration: _inputDecoration(
                                  'Confirmer le mot de passe', Icons.lock_outline)
                              .copyWith(
                            suffixIcon: IconButton(
                              icon: Icon(_obscureConfirm
                                  ? Icons.visibility_outlined
                                  : Icons.visibility_off_outlined),
                              onPressed: () => setState(
                                  () => _obscureConfirm = !_obscureConfirm),
                            ),
                          ),
                          validator: (v) {
                            if (v != _passwordCtrl.text) {
                              return 'Les mots de passe ne correspondent pas';
                            }
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
                                  border:
                                      Border.all(color: Colors.red.shade200),
                                ),
                                child: Text(
                                  auth.errorMessage!,
                                  style:
                                      TextStyle(color: Colors.red.shade700),
                                ),
                              );
                            }
                            return const SizedBox.shrink();
                          },
                        ),

                        // Bouton inscription
                        Consumer<AuthProvider>(
                          builder: (_, auth, __) {
                            return SizedBox(
                              width: double.infinity,
                              height: 52,
                              child: ElevatedButton(
                                onPressed: auth.isLoading ? null : _register,
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
                                        'Créer mon compte',
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
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text("Déjà un compte ? ",
                      style: TextStyle(color: Colors.grey)),
                  GestureDetector(
                    onTap: () => Navigator.pop(context),
                    child: const Text(
                      'Se connecter',
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
    );
  }

  InputDecoration _inputDecoration(String label, IconData icon) {
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
