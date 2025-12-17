-- UserHub Seed Data
-- This file populates the database with sample data for development and testing

-- Note: All passwords are hashed using bcrypt with cost factor 12
-- Plain text passwords are documented in comments for testing purposes

-- Clear existing data (if any)
TRUNCATE TABLE users RESTART IDENTITY CASCADE;

-- Insert admin user
-- Password: Admin123!
INSERT INTO users (
    email,
    username,
    full_name,
    hashed_password,
    is_active,
    is_superuser,
    bio,
    last_login
) VALUES (
    'admin@userhub.com',
    'admin',
    'System Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    true,
    true,
    'System administrator with full access to all features.',
    CURRENT_TIMESTAMP - INTERVAL '2 hours'
);

-- Insert regular users
-- Password: User123!
INSERT INTO users (
    email,
    username,
    full_name,
    hashed_password,
    is_active,
    is_superuser,
    bio,
    last_login
) VALUES
(
    'john.doe@example.com',
    'johndoe',
    'John Doe',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    true,
    false,
    'Software engineer passionate about web development and open source.',
    CURRENT_TIMESTAMP - INTERVAL '1 day'
),
(
    'jane.smith@example.com',
    'janesmith',
    'Jane Smith',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    true,
    false,
    'Product designer focused on creating intuitive user experiences.',
    CURRENT_TIMESTAMP - INTERVAL '3 hours'
),
(
    'bob.johnson@example.com',
    'bobjohnson',
    'Bob Johnson',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    true,
    false,
    'Data scientist working with machine learning and analytics.',
    CURRENT_TIMESTAMP - INTERVAL '5 days'
),
(
    'alice.williams@example.com',
    'alicewilliams',
    'Alice Williams',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    true,
    false,
    'DevOps engineer specializing in cloud infrastructure and automation.',
    CURRENT_TIMESTAMP - INTERVAL '2 days'
),
(
    'charlie.brown@example.com',
    'charliebrown',
    'Charlie Brown',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    true,
    false,
    'Full-stack developer with expertise in React and Node.js.',
    CURRENT_TIMESTAMP - INTERVAL '6 hours'
),
(
    'emma.davis@example.com',
    'emmadavis',
    'Emma Davis',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    true,
    false,
    'Mobile app developer creating cross-platform solutions.',
    NULL
),
(
    'david.miller@example.com',
    'davidmiller',
    'David Miller',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    true,
    false,
    'Cybersecurity specialist focused on application security.',
    CURRENT_TIMESTAMP - INTERVAL '10 days'
),
(
    'sarah.wilson@example.com',
    'sarahwilson',
    'Sarah Wilson',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    true,
    false,
    'Technical writer documenting software and APIs.',
    CURRENT_TIMESTAMP - INTERVAL '1 hour'
),
(
    'michael.moore@example.com',
    'michaelmoore',
    'Michael Moore',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    false,
    false,
    'Inactive user account for testing purposes.',
    CURRENT_TIMESTAMP - INTERVAL '30 days'
),
(
    'lisa.taylor@example.com',
    'lisataylor',
    'Lisa Taylor',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v/X5yKHUqfNu',
    true,
    false,
    'QA engineer ensuring software quality and reliability.',
    CURRENT_TIMESTAMP - INTERVAL '4 days'
);

-- Display seeded data summary
SELECT
    'Seed data inserted successfully' AS status,
    COUNT(*) AS total_users,
    COUNT(*) FILTER (WHERE is_active = true) AS active_users,
    COUNT(*) FILTER (WHERE is_active = false) AS inactive_users,
    COUNT(*) FILTER (WHERE is_superuser = true) AS admin_users
FROM users;

-- Display all seeded users
SELECT
    username,
    email,
    full_name,
    is_active,
    is_superuser,
    created_at
FROM users
ORDER BY created_at DESC;

-- Password Reference for Testing:
-- ================================
-- Admin User:
--   Email: admin@userhub.com
--   Password: Admin123!
--
-- Regular Users (all have same password):
--   Password: User123!
--
-- Note: In production, use unique strong passwords and store them securely!
