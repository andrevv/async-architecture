CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS tasks;

INSERT INTO auth.users (username, password, role) VALUES ('admin', '$2b$12$dd5VrC2N19dbNhkTQakt9.3/I1Q6wwdP4UihPiytg5XFl/s/tssfu', 'admin');
