package id.ycmlg.absensisiswa.data;

public class User {
    private String username = null;
    private String email = null;
    private String mode = null;

    public User() {}

    public User(String username, String email, String mode) {
        this.username = username;
        this.email = email;
        this.mode = mode;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getMode() {
        return mode;
    }

    public void setMode(String mode) {
        this.mode = mode;
    }
}
