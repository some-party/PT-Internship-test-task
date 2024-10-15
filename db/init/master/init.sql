DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'repl_user') THEN
        CREATE ROLE repl_user WITH REPLICATION LOGIN ENCRYPTED PASSWORD '123';
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'replication_slot') THEN
        PERFORM pg_create_physical_replication_slot('replication_slot');
    END IF;
END $$;

CREATE DATABASE mydb;


\connect mydb;

CREATE TABLE IF NOT EXISTS emails (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS phone_numbers (
  id SERIAL PRIMARY KEY,
  phone TEXT UNIQUE
);
