package com.app.resolver;

import com.app.dto.AuthResponse;
import com.app.dto.LoginInput;
import com.app.dto.RegisterInput;
import com.app.dto.UserDto;
import com.app.service.UserService;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;

import java.util.List;

@Controller
public class UserResolver {

    private final UserService userService;

    public UserResolver(UserService userService) {
        this.userService = userService;
    }

    // ===== MUTATIONS =====

    @MutationMapping
    public AuthResponse register(@Argument RegisterInput input) {
        return userService.register(input);
    }

    @MutationMapping
    public AuthResponse login(@Argument LoginInput input) {
        return userService.login(input);
    }

    // ===== QUERIES =====

    @QueryMapping
    public List<UserDto> getAllUsers() {
        return userService.getAllUsers();
    }

    @QueryMapping
    public UserDto getUserById(@Argument Long id) {
        return userService.getUserById(id)
                .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé avec l'id: " + id));
    }

    @QueryMapping
    public UserDto me() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            throw new RuntimeException("Non authentifié");
        }
        String email = auth.getName();
        return userService.getUserByEmail(email)
                .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));
    }
}
