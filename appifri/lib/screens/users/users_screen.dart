import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/user_model.dart';
import '../../services/auth_provider.dart';
import '../../services/user_service.dart';
import '../auth/login_screen.dart';

class UsersScreen extends StatefulWidget {
  const UsersScreen({super.key});

  @override
  State<UsersScreen> createState() => _UsersScreenState();
}

class _UsersScreenState extends State<UsersScreen> {
  final UserService _userService = UserService();
  List<UserModel> _users = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadUsers();
  }

  Future<void> _loadUsers() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final users = await _userService.getAllUsers();
      setState(() {
        _users = users;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  Future<void> _logout() async {
    await context.read<AuthProvider>().logout();
    if (mounted) {
      Navigator.pushAndRemoveUntil(
        context,
        MaterialPageRoute(builder: (_) => const LoginScreen()),
        (route) => false,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        backgroundColor: const Color(0xFF6C63FF),
        elevation: 0,
        title: const Text(
          'Utilisateurs',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _loadUsers,
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.white),
            onPressed: _logout,
          ),
        ],
      ),
      body: Column(
        children: [
          // Carte profil connecté
          if (authProvider.currentUser != null)
            Container(
              color: const Color(0xFF6C63FF),
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 20),
              child: Card(
                elevation: 4,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 28,
                        backgroundColor: const Color(0xFF6C63FF),
                        child: Text(
                          authProvider.currentUser!.prenom[0].toUpperCase(),
                          style: const TextStyle(
                              color: Colors.white,
                              fontSize: 22,
                              fontWeight: FontWeight.bold),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              authProvider.currentUser!.nomComplet,
                              style: const TextStyle(
                                  fontWeight: FontWeight.bold, fontSize: 16),
                            ),
                            Text(
                              authProvider.currentUser!.email,
                              style: TextStyle(
                                  color: Colors.grey.shade600, fontSize: 13),
                            ),
                          ],
                        ),
                      ),
                      _RoleBadge(role: authProvider.currentUser!.role),
                    ],
                  ),
                ),
              ),
            ),

          // Liste
          Expanded(
            child: _isLoading
                ? const Center(
                    child: CircularProgressIndicator(
                        color: Color(0xFF6C63FF)))
                : _error != null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.error_outline,
                                color: Colors.red.shade400, size: 48),
                            const SizedBox(height: 12),
                            Text(_error!,
                                style:
                                    TextStyle(color: Colors.red.shade600),
                                textAlign: TextAlign.center),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: _loadUsers,
                              style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF6C63FF)),
                              child: const Text('Réessayer',
                                  style: TextStyle(color: Colors.white)),
                            ),
                          ],
                        ),
                      )
                    : _users.isEmpty
                        ? const Center(
                            child: Text('Aucun utilisateur trouvé',
                                style: TextStyle(color: Colors.grey)))
                        : RefreshIndicator(
                            onRefresh: _loadUsers,
                            color: const Color(0xFF6C63FF),
                            child: ListView.separated(
                              padding: const EdgeInsets.all(16),
                              itemCount: _users.length,
                              separatorBuilder: (_, __) =>
                                  const SizedBox(height: 10),
                              itemBuilder: (context, index) {
                                return _UserCard(user: _users[index]);
                              },
                            ),
                          ),
          ),
        ],
      ),
    );
  }
}

class _UserCard extends StatelessWidget {
  final UserModel user;
  const _UserCard({required this.user});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: ListTile(
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: CircleAvatar(
          backgroundColor: const Color(0xFF6C63FF).withOpacity(0.12),
          child: Text(
            user.prenom[0].toUpperCase(),
            style: const TextStyle(
                color: Color(0xFF6C63FF), fontWeight: FontWeight.bold),
          ),
        ),
        title: Text(
          user.nomComplet,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
        ),
        subtitle: Text(
          user.email,
          style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
        ),
        trailing: _RoleBadge(role: user.role),
      ),
    );
  }
}

class _RoleBadge extends StatelessWidget {
  final String role;
  const _RoleBadge({required this.role});

  @override
  Widget build(BuildContext context) {
    final isAdmin = role == 'ADMIN';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: isAdmin
            ? const Color(0xFF6C63FF).withOpacity(0.12)
            : Colors.green.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        role,
        style: TextStyle(
          color: isAdmin ? const Color(0xFF6C63FF) : Colors.green.shade700,
          fontWeight: FontWeight.w600,
          fontSize: 12,
        ),
      ),
    );
  }
}
