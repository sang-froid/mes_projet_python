package com.app.dto;

import com.app.entity.User;

public class AuthResponse {
    private String token;
    private UserDto user;
    private String message;

    public AuthResponse() {}

    public AuthResponse(String token, User user, String message) {
        this.token = token;
        this.user = new UserDto(user);
        this.message = message;
    }

    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }

    public UserDto getUser() { return user; }
    public void setUser(UserDto user) { this.user = user; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}
