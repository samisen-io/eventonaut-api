query_user_by_email_and_archived_status = """
    SELECT 
    u.id,
    u.uuid, 
    u.email, 
    u.first_name, 
    u.last_name, 
    u.hashed_password,
    u.is_active, 
    u.is_verified,
    u.is_archived, 
    u.user_status_id,
    r.name AS role
    FROM users u
    JOIN user_role ur ON ur.user_id = u.id
    JOIN role r ON ur.role_id = r.id
    WHERE u.email = :email and u.is_archived = false;
"""