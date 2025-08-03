# Data Dictionary

## Overview
This document serves as the single source of truth for all database tables, columns, and data structures in the system. It defines data types, constraints, relationships, and the purpose of each field.

**Last Updated:** January 2025  
**Version:** 1.0  
**Status:** Draft - Schema in development

## Database Schema Version
- **Current Version:** Not yet implemented
- **Target Database:** TBD (PostgreSQL/MySQL/SQLite)

## Tables

### [Table Name - To Be Defined]
*Description: Purpose and role of this table in the system*

| Column Name | Data Type | Constraints | Default | Description | Example |
|-------------|-----------|-------------|---------|-------------|---------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | - | Unique identifier | 1, 2, 3 |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | Record creation time | 2025-01-15 10:30:00 |
| updated_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | Last modification time | 2025-01-15 14:22:15 |

**Indexes:**
- PRIMARY KEY (id)

**Relationships:**
- None defined yet

---

## Data Types Reference

### Standard Types
- **INTEGER**: Whole numbers (-2,147,483,648 to 2,147,483,647)
- **BIGINT**: Large integers (-9,223,372,036,854,775,808 to 9,223,372,036,854,775,807)
- **VARCHAR(n)**: Variable-length string up to n characters
- **TEXT**: Large text fields (up to 65,535 characters)
- **TIMESTAMP**: Date and time (YYYY-MM-DD HH:MM:SS)
- **DATE**: Date only (YYYY-MM-DD)
- **BOOLEAN**: True/false values
- **DECIMAL(p,s)**: Fixed-point numbers (p=precision, s=scale)

### Custom Types
*To be defined as schema develops*

## Naming Conventions

### Tables
- Use lowercase with underscores (snake_case)
- Use plural nouns (users, orders, products)
- Avoid abbreviations when possible

### Columns
- Use lowercase with underscores (snake_case)
- Use descriptive names (first_name, not fname)
- Boolean columns should start with is_, has_, or can_
- Foreign keys should end with _id

### Indexes
- Format: idx_[table]_[column(s)]
- Unique indexes: uniq_[table]_[column(s)]

## Common Patterns

### Audit Fields
Standard fields for tracking record lifecycle:
- `id`: Primary key
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp
- `created_by`: User who created the record (optional)
- `updated_by`: User who last modified the record (optional)

### Soft Delete Pattern
For tables requiring soft delete functionality:
- `deleted_at`: Timestamp when record was soft deleted (NULL if active)
- `deleted_by`: User who performed the soft delete (optional)

## Constraints and Validation Rules

### Global Rules
- All tables must have a primary key
- All tables should include created_at and updated_at timestamps
- Foreign key constraints must be explicitly defined
- Check constraints should be used for data validation where appropriate

### Data Integrity
- Email fields must follow valid email format
- Phone numbers should follow consistent formatting
- Monetary values should use appropriate decimal precision

## Migration History
*Track schema changes and migrations here*

| Version | Date | Description | Migration File |
|---------|------|-------------|----------------|
| - | - | Initial schema creation | TBD |

## Notes
- This document will be updated as the database schema is designed and implemented
- All schema changes must be reflected in this document
- Consider adding examples and sample data for each table as they are created
- Review and update naming conventions as the project evolves

## TODO
- [ ] Define initial table structure based on application requirements
- [ ] Establish database platform (PostgreSQL, MySQL, SQLite, etc.)
- [ ] Create entity relationship diagram
- [ ] Define indexes and performance considerations
- [ ] Establish migration strategy
- [ ] Add data validation rules and constraints