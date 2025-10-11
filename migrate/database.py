# migrate/database.py
import uuid
from database.connection import db

def migrate_database():
    # Roles
    create_roles = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='roles' AND xtype='U')
    BEGIN
        CREATE TABLE roles (
            id INT IDENTITY(1,1) PRIMARY KEY,
            name NVARCHAR(100) NOT NULL,
            id_user_create UNIQUEIDENTIFIER NOT NULL,
            id_user_modify UNIQUEIDENTIFIER NULL,
            create_date DATETIME2 DEFAULT GETDATE(),
            modify_date DATETIME2 NULL,
            is_active BIT DEFAULT 1
        )
    END
    """

    # Users
    create_users = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
    BEGIN
        CREATE TABLE users (
            id_user UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
            name NVARCHAR(50) NOT NULL,
            last_name NVARCHAR(50) NOT NULL,
            id_role INT NOT NULL,
            birthdate DATE NOT NULL,
            id_user_create UNIQUEIDENTIFIER NOT NULL,
            id_user_modify UNIQUEIDENTIFIER NULL,
            create_date DATETIME2 DEFAULT GETDATE(),
            modify_date DATETIME2 NULL,
            is_active BIT DEFAULT 1,
            CONSTRAINT FK_users_roles FOREIGN KEY (id_role) REFERENCES roles(id)
        )
    END
    """

    # Login
    create_login = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='login' AND xtype='U')
    BEGIN
        CREATE TABLE login (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username NVARCHAR(100) NOT NULL UNIQUE,
            password_hash NVARCHAR(300) NOT NULL,
            id_user UNIQUEIDENTIFIER NOT NULL,
            id_user_create UNIQUEIDENTIFIER NOT NULL,
            id_user_modify UNIQUEIDENTIFIER NULL,
            create_date DATETIME2 DEFAULT GETDATE(),
            modify_date DATETIME2 NULL,
            is_active BIT DEFAULT 1,
            CONSTRAINT FK_login_users FOREIGN KEY (id_user) REFERENCES users(id_user)
        )
    END
    """

    # Area
    create_area = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='area' AND xtype='U')
    BEGIN
        CREATE TABLE area (
            id_area INT IDENTITY(1,1) PRIMARY KEY,
            name NVARCHAR(100) NOT NULL,
            id_user_create UNIQUEIDENTIFIER NOT NULL,
            id_user_modify UNIQUEIDENTIFIER NULL,
            create_date DATETIME2 DEFAULT GETDATE(),
            modify_date DATETIME2 NULL,
            is_active BIT DEFAULT 1
        )
    END
    """

    # Subjects
    create_subjects = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='subjects' AND xtype='U')
    BEGIN
        CREATE TABLE subjects (
            id_subj UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
            name NVARCHAR(100) NOT NULL,
            credits INT NOT NULL,
            id_area INT NULL,
            id_user_create UNIQUEIDENTIFIER NOT NULL,
            id_user_modify UNIQUEIDENTIFIER NULL,
            create_date DATETIME2 DEFAULT GETDATE(),
            modify_date DATETIME2 NULL,
            is_active BIT DEFAULT 1,
            CONSTRAINT FK_subjects_area FOREIGN KEY (id_area) REFERENCES area(id_area)
        )
    END
    """

    # Notes
    create_notes = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='notes' AND xtype='U')
    BEGIN
        CREATE TABLE notes (
            id INT IDENTITY(1,1) PRIMARY KEY,
            id_user UNIQUEIDENTIFIER NOT NULL,
            id_subj UNIQUEIDENTIFIER NOT NULL,
            id_user_create UNIQUEIDENTIFIER NOT NULL,
            id_user_modify UNIQUEIDENTIFIER NULL,
            grade DECIMAL(4,2) NOT NULL,
            create_date DATETIME2 DEFAULT GETDATE(),
            modify_date DATETIME2 NULL,
            is_active BIT DEFAULT 1,
            CONSTRAINT FK_notes_users FOREIGN KEY (id_user) REFERENCES users(id_user),
            CONSTRAINT FK_notes_subjects FOREIGN KEY (id_subj) REFERENCES subjects(id_subj)
        )
    END
    """

    scripts = [
        create_roles,
        create_users,
        create_login,
        create_area,
        create_subjects,
        create_notes
    ]

    for s in scripts:
        db.execute_non_query(s)

    print("Migración completada ✅")
    insert_initial_data()


def insert_initial_data():
    # Roles
    db.execute_non_query("""
        IF NOT EXISTS (SELECT 1 FROM roles WHERE name = 'Administrador')
        BEGIN
            INSERT INTO roles (name, id_user_create) VALUES ('Administrador', NEWID())
        END
    """)

    db.execute_non_query("""
        IF NOT EXISTS (SELECT 1 FROM roles WHERE name = 'Estudiante')
        BEGIN
            INSERT INTO roles (name, id_user_create) VALUES ('Estudiante', NEWID())
        END
    """)

    # Usuario admin
    db.execute_non_query("""
        IF NOT EXISTS (SELECT 1 FROM users WHERE name = 'Admin')
        BEGIN
            INSERT INTO users (id_user, name, last_name, id_role, birthdate, id_user_create)
            VALUES (NEWID(), 'Admin', 'Root', 1, '1990-01-01', NEWID())
        END
    """)

    db.execute_non_query("""
        IF NOT EXISTS (SELECT 1 FROM login WHERE username = 'admin')
        BEGIN
            INSERT INTO login (username, password_hash, id_user, id_user_create)
            SELECT 
                'admin',
                CONVERT(VARCHAR(64), HASHBYTES('SHA2_256', '123456'), 2), -- HEX
                id_user,
                NEWID()
            FROM users WHERE name = 'Admin'
        END
    """)

    # Área inicial
    db.execute_non_query("""
        IF NOT EXISTS (SELECT 1 FROM area WHERE name = 'Ciencias Básicas')
        BEGIN
            INSERT INTO area (name, id_user_create)
            VALUES ('Ciencias Básicas', NEWID())
        END
    """)

    # Materia inicial
    db.execute_non_query("""
        IF NOT EXISTS (SELECT 1 FROM subjects WHERE name = 'Matemáticas I')
        BEGIN
            INSERT INTO subjects (id_subj, name, credits, id_area, id_user_create)
            SELECT NEWID(), 'Matemáticas I', 4, id_area, NEWID() FROM area WHERE name = 'Ciencias Básicas'
        END
    """)

    print("Datos de prueba insertados ✅")


if __name__ == "__main__":
    migrate_database()
