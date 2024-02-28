query = """SELECT 
    u.email,
    u.first_name,
    u.last_name,
    a.title,
    u.company,
    a.bio,
    a.share_my_profile,
    a.share_my_agenda,
    a.profile_image_url,
    a.uuid,
    u.is_active,
    (SELECT UPPER(status) FROM organizer_status os WHERE id = u.user_status_id) status
FROM 
    attendees a 
JOIN 
    attendee_conferences ac ON ac.attendee_id = a.id 
JOIN 
    users u ON u.id = a.user_id 
JOIN 
    conferences c ON c.id = ac.conference_id
WHERE 
    c.uuid = :conference_uuid 
    AND a.share_my_profile = true 
    AND u.is_archived = false"""