CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD '123';
SELECT pg_create_physical_replication_slot('replication_slot');

-- Создание базы данных
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'mydb') THEN
        CREATE DATABASE mydb;
    END IF;
END $$;

-- Подключение к базе данных
\connect mydb;

-- Создание таблицы emails
CREATE TABLE emails (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE
);

-- Создание таблицы phone_numbers
CREATE TABLE phone_numbers (
  id SERIAL PRIMARY KEY,
  phone TEXT UNIQUE
);
