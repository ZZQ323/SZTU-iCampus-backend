persons
classes
colleges
majors
departments
books
locations
courses
research_projects
borrow_records
campus_cards
network_permissions
system_access
platform_configs
audit_logs
workflow_instances
course_instances
research_applications
paper_library
assets
transactions
device_registrations
room_occupations
grades
grade_statistics

sqlite3 sztu_campus.db "SELECT 'persons' AS table_name, COUNT(*) AS record_count FROM persons UNION ALL SELECT 'classes', COUNT(*) FROM classes UNION ALL SELECT 'colleges', COUNT(*) FROM colleges UNION ALL SELECT 'majors', COUNT(*) FROM majors UNION ALL SELECT 'departments', COUNT(*) FROM departments UNION ALL SELECT 'books', COUNT(*) FROM books UNION ALL SELECT 'locations', COUNT(*) FROM locations UNION ALL SELECT 'courses', COUNT(*) FROM courses UNION ALL SELECT 'research_projects', COUNT(*) FROM research_projects UNION ALL SELECT 'borrow_records', COUNT(*) FROM borrow_records UNION ALL SELECT 'campus_cards', COUNT(*) FROM campus_cards UNION ALL SELECT 'network_permissions', COUNT(*) FROM network_permissions UNION ALL SELECT 'system_access', COUNT(*) FROM system_access UNION ALL SELECT 'platform_configs', COUNT(*) FROM platform_configs UNION ALL SELECT 'audit_logs', COUNT(*) FROM audit_logs UNION ALL SELECT 'workflow_instances', COUNT(*) FROM workflow_instances UNION ALL SELECT 'course_instances', COUNT(*) FROM course_instances UNION ALL SELECT 'research_applications', COUNT(*) FROM research_applications UNION ALL SELECT 'paper_library', COUNT(*) FROM paper_library UNION ALL SELECT 'assets', COUNT(*) FROM assets UNION ALL SELECT 'transactions', COUNT(*) FROM transactions UNION ALL SELECT 'device_registrations', COUNT(*) FROM device_registrations UNION ALL SELECT 'room_occupations', COUNT(*) FROM room_occupations UNION ALL SELECT 'grades', COUNT(*) FROM grades UNION ALL SELECT 'grade_statistics', COUNT(*) FROM grade_statistics;"