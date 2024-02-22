query_user_by_email_and_archived_status = """
    SELECT u.id, u."uuid", u.created_on, u.updated_on, 
    u.email, u.first_name, u.last_name, 
    u.company, u.business_type, u.hashed_password,
    u.is_active, u.timezone, u.is_verified,
    u.is_archived, u.profile_image_url, u.user_status_id,
    r.name AS role
    FROM users u
    JOIN user_role ur ON ur.user_id = u.id
    JOIN role r ON ur.role_id = r.id
    WHERE u.email = :email and u.is_archived = false;
"""