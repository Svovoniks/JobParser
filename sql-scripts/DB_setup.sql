SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE DATABASE parser_db;

ALTER DATABASE parser_db OWNER TO postgres;

\connect parser_db

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE SCHEMA main;

CREATE TABLE main.vacancy (
    id SERIAL PRIMARY KEY,
    vacancy_id BIGINT NOT NULL UNIQUE,
    name TEXT,
    area TEXT,
    salary_from BIGINT,
    salary_to BIGINT,
    currency TEXT,
    is_open BOOLEAN,
    published_at TIMESTAMP,
    employer_id BIGINT,
    employer TEXT,
    experience TEXT,
    is_remote BOOLEAN
);

CREATE TABLE main.role (
    id SERIAL PRIMARY KEY,
    role TEXT NOT NULL UNIQUE
);

CREATE TABLE main.skill (
    id SERIAL PRIMARY KEY,
    skill TEXT NOT NULL UNIQUE
);

CREATE TABLE main.vacancy_role (
    vacancy_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    FOREIGN KEY (vacancy_id) REFERENCES main.vacancy (id),
    FOREIGN KEY (role_id) REFERENCES main.role (id)
);

CREATE TABLE main.vacancy_skill (
    vacancy_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    FOREIGN KEY (vacancy_id) REFERENCES main.vacancy (id),
    FOREIGN KEY (skill_id) REFERENCES main.skill (id)
);

CREATE TABLE main.resume (
    id SERIAL PRIMARY KEY,
    resume_id TEXT NOT NULL UNIQUE,
    gender TEXT,
    age BIGINT,
    salary BIGINT,
    experience BIGINT,
    search_status TEXT
);

CREATE TABLE main.resume_skill (
    resume_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    FOREIGN KEY (resume_id) REFERENCES main.resume (id),
    FOREIGN KEY (skill_id) REFERENCES main.skill (id)
);

CREATE TABLE main.resume_role (
    resume_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    FOREIGN KEY (resume_id) REFERENCES main.resume (id),
    FOREIGN KEY (role_id) REFERENCES main.role (id)
);

CREATE TABLE main.parsing_requests (
    id SERIAL PRIMARY KEY,
    request_json TEXT NOT NULL,
    status TEXT NOT NULL,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);