CREATE DATABASE hospital_appointment_db;
SHOW DATABASES;
USE hospital_appointment_db;

SHOW COLUMNS FROM patients LIKE 'phone';
SHOW COLUMNS FROM users LIKE 'phone';
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    COLUMN_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'hospital_appointment_db'
  AND COLUMN_NAME = 'phone'
  AND TABLE_NAME IN ('patients', 'users');
USE hospital_appointment_db;

SELECT
    id,
    doctor_id,
    appointment_date,
    slot_time,
    status,
    appointment_number
FROM appointments
WHERE doctor_id = 1
  AND appointment_date = '2026-10-27'
ORDER BY slot_time;
SHOW CREATE TABLE appointments;
SHOW INDEX FROM appointments
WHERE Non_unique = 0;
SELECT
    CONSTRAINT_NAME,
    COLUMN_NAME,
    ORDINAL_POSITION
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'hospital_appointment_db'
  AND TABLE_NAME = 'appointments'
  AND CONSTRAINT_NAME = 'uq_doctor_appointment_slot'
ORDER BY ORDINAL_POSITION;

SELECT id, doctor_id, appointment_date, slot_time, status
FROM appointments
WHERE doctor_id = 1
  AND appointment_date = '2026-10-27'
ORDER BY slot_time;
SHOW INDEX FROM appointments WHERE Key_name = 'uq_doctor
_appointment_slot';
SHOW CREATE TABLE appointments;
SHOW INDEX FROM appointments;
SELECT leave_date, reason
FROM doctor_leaves
WHERE doctor_id = 1;
SELECT day_of_week, start_time, end_time
FROM doctor_schedules
WHERE doctor_id = 1;