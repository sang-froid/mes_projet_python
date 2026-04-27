package com.app.dto;

public class LoginInput {
    private String email;
    private String motDePasse;

    public LoginInput() {}

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getMotDePasse() { return motDePasse; }
    public void setMotDePasse(String motDePasse) { this.motDePasse = motDePasse; }
}
