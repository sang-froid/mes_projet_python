package com.app.service;

import com.app.dto.AuthResponse;
import com.app.dto.LoginInput;
import com.app.dto.RegisterInput;
import com.app.dto.UserDto;
import com.app.entity.User;
import com.app.repository.UserRepository;
import com.app.security.JwtService;
import org.springframework.context.annotation.Lazy;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class UserService implements UserDetailsService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    public UserService(UserRepository userRepository,
                       PasswordEncoder passwordEncoder,
                       JwtService jwtService,
                       @Lazy AuthenticationManager authenticationManager) { // 👈 @Lazy ici
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
        this.authenticationManager = authenticationManager;
    }

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("Utilisateur non trouvé: " + email));
    }

    public AuthResponse register(RegisterInput input) {
        if (userRepository.existsByEmail(input.getEmail())) {
            throw new RuntimeException("Cet email est déjà utilisé");
        }
        User user = new User();
        user.setNom(input.getNom());
        user.setPrenom(input.getPrenom());
        user.setEmail(input.getEmail());
        user.setMotDePasse(passwordEncoder.encode(input.getMotDePasse()));
        user.setRole(input.getRole() != null ? input.getRole().toUpperCase() : "USER");
        User savedUser = userRepository.save(user);
        String token = jwtService.generateToken(savedUser);
        return new AuthResponse(token, savedUser, "Inscription réussie !");
    }

    public AuthResponse login(LoginInput input) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(input.getEmail(), input.getMotDePasse())
        );
        User user = userRepository.findByEmail(input.getEmail())
                .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));
        String token = jwtService.generateToken(user);
        return new AuthResponse(token, user, "Connexion réussie !");
    }

    public List<UserDto> getAllUsers() {
        return userRepository.findAll()
                .stream()
                .map(UserDto::new)
                .collect(Collectors.toList());
    }

    public Optional<UserDto> getUserById(Long id) {
        return userRepository.findById(id).map(UserDto::new);
    }

    public Optional<UserDto> getUserByEmail(String email) {
        return userRepository.findByEmail(email).map(UserDto::new);
    }
}