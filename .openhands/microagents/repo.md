---
name: repo
type: repo
agent: CodeActAgent
---

# Clean Code Guidelines

## Constants Over Magic Numbers
- Replace hard-coded values with named constants
- Use descriptive constant names that explain the value's purpose
- Keep constants at the top of the file or in a dedicated constants file

## Meaningful Names
- Variables, functions, and classes should reveal their purpose
- Names should explain why something exists and how it's used
- Avoid abbreviations unless they're universally understood

## Smart Comments
- Don't comment on what the code does - make the code self-documenting
- Use comments to explain why something is done a certain way
- Document APIs, complex algorithms, and non-obvious side effects

## Single Responsibility
- Each function should do exactly one thing
- Functions should be small and focused
- If a function needs a comment to explain what it does, it should be split

## DRY (Don't Repeat Yourself)
- Extract repeated code into reusable functions
- Share common logic through proper abstraction
- Maintain single sources of truth

## Clean Structure
- Keep related code together
- Organize code in a logical hierarchy
- Use consistent file and folder naming conventions

## Encapsulation
- Hide implementation details
- Expose clear interfaces
- Move nested conditionals into well-named functions

## Code Quality Maintenance
- Refactor continuously
- Fix technical debt early
- Leave code cleaner than you found it

## Testing
- Write tests before fixing bugs
- Keep tests readable and maintainable
- Test edge cases and error conditions

## Version Control
- Write clear commit messages
- Make small, focused commits
- Use meaningful branch names 

# Code Quality Guidelines

## Verify Information
Always verify information before presenting it. Do not make assumptions or speculate without clear evidence.

## File-by-File Changes
Make changes file by file and give me a chance to spot mistakes.

## No Apologies
Never use apologies.

## No Understanding Feedback
Avoid giving feedback about understanding in comments or documentation.

## No Whitespace Suggestions
Don't suggest whitespace changes.

## No Summaries
Don't summarize changes made.

## No Inventions
Don't invent changes other than what's explicitly requested.

## No Unnecessary Confirmations
Don't ask for confirmation of information already provided in the context.

## Preserve Existing Code
Don't remove unrelated code or functionalities. Pay attention to preserving existing structures.

## Single Chunk Edits
Provide all edits in a single chunk instead of multiple-step instructions or explanations for the same file.

## No Implementation Checks
Don't ask the user to verify implementations that are visible in the provided context.

## No Unnecessary Updates
Don't suggest updates or changes to files when there are no actual modifications needed.

## Provide Real File Links
Always provide links to the real files, not x.md.

## No Current Implementation
Don't show or discuss the current implementation unless specifically requested.


# FastAPI Best Practices

## Project Structure
- Use proper directory structure
- Implement proper module organization
- Use proper dependency injection
- Keep routes organized by domain
- Implement proper middleware
- Use proper configuration management

## API Design
- Use proper HTTP methods
- Implement proper status codes
- Use proper request/response models
- Implement proper validation
- Use proper error handling
- Document APIs with OpenAPI

## Models
- Use Pydantic models
- Implement proper validation
- Use proper type hints
- Keep models organized
- Use proper inheritance
- Implement proper serialization

## Database
- Use proper ORM (SQLAlchemy)
- Implement proper migrations
- Use proper connection pooling
- Implement proper transactions
- Use proper query optimization
- Handle database errors properly

## Authentication
- Implement proper JWT authentication
- Use proper password hashing
- Implement proper role-based access
- Use proper session management
- Implement proper OAuth2
- Handle authentication errors properly

## Security
- Implement proper CORS
- Use proper rate limiting
- Implement proper input validation
- Use proper security headers
- Handle security errors properly
- Implement proper logging

## Performance
- Use proper caching
- Implement proper async operations
- Use proper background tasks
- Implement proper connection pooling
- Use proper query optimization
- Monitor performance metrics

## Testing
- Write proper unit tests
- Implement proper integration tests
- Use proper test fixtures
- Implement proper mocking
- Test error scenarios
- Use proper test coverage

## Deployment
- Use proper Docker configuration
- Implement proper CI/CD
- Use proper environment variables
- Implement proper logging
- Use proper monitoring
- Handle deployment errors properly

## Documentation
- Use proper docstrings
- Implement proper API documentation
- Use proper type hints
- Keep documentation updated
- Document error scenarios
- Use proper versioning 


# Postgres SQL Style Guide

## General

- Use lowercase for SQL reserved words to maintain consistency and readability.
- Employ consistent, descriptive identifiers for tables, columns, and other database objects.
- Use white space and indentation to enhance the readability of your code.
- Store dates in ISO 8601 format (`yyyy-mm-ddThh:mm:ss.sssss`).
- Include comments for complex logic, using '/* ... */' for block comments and '--' for line comments.

## Naming Conventions

- Avoid SQL reserved words and ensure names are unique and under 63 characters.
- Use snake_case for tables and columns.
- Prefer plurals for table names
- Prefer singular names for columns.

## Tables

- Avoid prefixes like 'tbl_' and ensure no table name matches any of its column names.
- Always add an `id` column of type `identity generated always` unless otherwise specified.
- Create all tables in the `public` schema unless otherwise specified.
- Always add the schema to SQL queries for clarity.
- Always add a comment to describe what the table does. The comment can be up to 1024 characters.

## Columns

- Use singular names and avoid generic names like 'id'.
- For references to foreign tables, use the singular of the table name with the `_id` suffix. For example `user_id` to reference the `users` table
- Always use lowercase except in cases involving acronyms or when readability would be enhanced by an exception.

#### Examples:

```sql
create table books (
  id bigint generated always as identity primary key,
  title text not null,
  author_id bigint references authors (id)
);
comment on table books is 'A list of all the books in the library.';
```


## Queries

- When the query is shorter keep it on just a few lines. As it gets larger start adding newlines for readability
- Add spaces for readability.

Smaller queries:


```sql
select *
from employees
where end_date is null;

update employees
set end_date = '2023-12-31'
where employee_id = 1001;
```

Larger queries:

```sql
select
  first_name,
  last_name
from
  employees
where
  start_date between '2021-01-01' and '2021-12-31'
and
  status = 'employed';
```


### Joins and Subqueries

- Format joins and subqueries for clarity, aligning them with related SQL clauses.
- Prefer full table names when referencing tables. This helps for readability.

```sql
select
  employees.employee_name,
  departments.department_name
from
  employees
join
  departments on employees.department_id = departments.department_id
where
  employees.start_date > '2022-01-01';
```

## Aliases

- Use meaningful aliases that reflect the data or transformation applied, and always include the 'as' keyword for clarity.

```sql
select count(*) as total_employees
from employees
where end_date is null;
```


## Complex queries and CTEs

- If a query is extremely complex, prefer a CTE.
- Make sure the CTE is clear and linear. Prefer readability over performance.
- Add comments to each block.

```sql
with department_employees as (
  -- Get all employees and their departments
  select
    employees.department_id,
    employees.first_name,
    employees.last_name,
    departments.department_name
  from
    employees
  join
    departments on employees.department_id = departments.department_id
),
employee_counts as (
  -- Count how many employees in each department
  select
    department_name,
    count(*) as num_employees
  from
    department_employees
  group by
    department_name
)
select
  department_name,
  num_employees
from
  employee_counts
order by
  department_name;
```


# PostgreSQL Best Practices

## Schema Design
- **Choose appropriate data types** to optimize storage and performance:
  - Use `INT` or `BIGINT` for integers, `VARCHAR(n)` or `TEXT` for strings, and `TIMESTAMP WITH TIME ZONE` for dates.
  - Example: `CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(50), created_at TIMESTAMP WITH TIME ZONE);`
- **Normalize tables** to eliminate redundancy, but denormalize strategically for read-heavy workloads.
- **Enforce data integrity** with constraints:
  - `PRIMARY KEY` for unique row identification.
  - `FOREIGN KEY` for referential integrity (e.g., `user_id INT REFERENCES users(id)`).
  - `UNIQUE` and `CHECK` for additional rules (e.g., `CHECK (age >= 0)`).
- **Use PostgreSQL-specific types** like `JSONB` for semi-structured data or `UUID` for unique identifiers.

## Query Writing
- **Specify explicit columns** in `SELECT` instead of `SELECT *` for clarity and performance.
  - Example: `SELECT id, name FROM users WHERE active = true;`
- **Write efficient JOINs** with indexed columns and appropriate types (`INNER JOIN`, `LEFT JOIN`, etc.).
- **Use parameterized queries** to prevent SQL injection and improve performance:
  - Example: `SELECT * FROM users WHERE id = $1 AND status = $2;`
- **Limit result sets** with `LIMIT` and `OFFSET` for pagination, or use keyset pagination for large datasets:
  - Example: `SELECT * FROM orders WHERE id > $1 ORDER BY id LIMIT 10;`

## Indexing Strategies
- **Create indexes** on columns in `WHERE`, `JOIN`, and `ORDER BY` clauses:
  - Example: `CREATE INDEX idx_users_name ON users (name);`
- **Select the right index type**:
  - **B-tree**: For equality and range queries (default).
  - **GIN**: For `JSONB`, arrays, or full-text search.
  - **GiST**: For spatial or geometric data.
- **Use composite indexes** for multi-column filters:
  - Example: `CREATE INDEX idx_orders_date_customer ON orders (order_date, customer_id);`
- **Avoid over-indexing** to maintain write performance; remove unused indexes using `pg_stat_user_indexes`.

## PostgreSQL-Specific Features
- **Window functions**: Perform calculations across rows:
  - Example: `SELECT name, salary, RANK() OVER (PARTITION BY dept ORDER BY salary DESC) FROM employees;`
- **Common Table Expressions (CTEs)**: Simplify complex queries:
  - Example: `WITH active_users AS (SELECT * FROM users WHERE active = true) SELECT * FROM active_users;`
- **Full-text search**: Use `tsvector` and `tsquery`:
  - Example: `SELECT title FROM articles WHERE to_tsvector(content) @@ to_tsquery('database & performance');`
- **JSONB**: Query semi-structured data:
  - Example: `SELECT data->>'email' FROM profiles WHERE data->>'age'::int > 25;`

## Code Organization
- **Use schemas** to group related tables and views (e.g., `auth`, `reporting`).
- **Encapsulate logic** in views or functions for reuse:
  - Example: `CREATE VIEW active_users AS SELECT * FROM users WHERE active = true;`
- **Keep SQL files modular** by separating schema creation, indexes, and queries into distinct files.

## Functions and Methods
- **Use stored procedures or functions** for reusable logic:
  - Example: `CREATE FUNCTION get_user_count() RETURNS INT AS $$ SELECT COUNT(*) FROM users; $$ LANGUAGE SQL;`
- **Keep functions focused** on a single task and use parameters for flexibility.

## Best Practices
- **Optimize queries** by leveraging indexes and avoiding unnecessary data retrieval.
- **Maintain data integrity** with constraints and transactions.
- **Write secure SQL** with parameterized queries and minimal permissions.
- **Use EXPLAIN** to analyze query performance:
  - Example: `EXPLAIN SELECT * FROM orders WHERE customer_id = 123;`
- **Update statistics** with `ANALYZE` to ensure the query planner works effectively.

## Error Handling
- **Handle exceptions** in functions or transactions:
  - Example:
    ```sql
    DO $$
    BEGIN
        INSERT INTO users (name) VALUES ('Test');
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'Duplicate entry detected';
    END;
    $$;
    ```
- **Use transactions** to rollback on errors (see Transaction Management).

## Transaction Management
- **Wrap multi-statement operations** in transactions:
  - Example:
    ```sql
    BEGIN;
    UPDATE accounts SET balance = balance - 50 WHERE id = 1;
    UPDATE accounts SET balance = balance + 50 WHERE id = 2;
    COMMIT;
    ```
- **Use savepoints** for partial rollbacks:
  - Example: `SAVEPOINT sp1; ROLLBACK TO sp1;`

## Performance Tuning
- **Analyze query plans** with `EXPLAIN ANALYZE` to identify bottlenecks.
- **Monitor slow queries** using `pg_stat_statements` or log settings.
- **Tune configurations** like `work_mem` and `shared_buffers` for your workload.

## Documentation
- **Add comments** to explain intent:
  - Example: `-- Retrieve all active users ordered by registration date`
- **Document views and functions** with purpose and usage:
  - Example: `COMMENT ON FUNCTION get_user_count IS 'Returns total number of users';`

## Security Practices
- **Prevent SQL injection** with parameterized queries.
- **Restrict access** using roles and privileges:
  - Example: `GRANT SELECT ON users TO read_only_role;`
- **Encrypt sensitive data** with `pgcrypto` or application-level encryption.


# Python Best Practices

## Project Structure
- Use src-layout with `src/your_package_name/`
- Place tests in `tests/` directory parallel to `src/`
- Keep configuration in `config/` or as environment variables
- Store requirements in `requirements.txt` or `pyproject.toml`
- Place static files in `static/` directory
- Use `templates/` for Jinja2 templates

## Code Style
- Follow Black code formatting
- Use isort for import sorting
- Follow PEP 8 naming conventions:
  - snake_case for functions and variables
  - PascalCase for classes
  - UPPER_CASE for constants
- Maximum line length of 88 characters (Black default)
- Use absolute imports over relative imports

## Type Hints
- Use type hints for all function parameters and returns
- Import types from `typing` module
- Use `Optional[Type]` instead of `Type | None`
- Use `TypeVar` for generic types
- Define custom types in `types.py`
- Use `Protocol` for duck typing

## Flask Structure
- Use Flask factory pattern
- Organize routes using Blueprints
- Use Flask-SQLAlchemy for database
- Implement proper error handlers
- Use Flask-Login for authentication
- Structure views with proper separation of concerns

## Database
- Use SQLAlchemy ORM
- Implement database migrations with Alembic
- Use proper connection pooling
- Define models in separate modules
- Implement proper relationships
- Use proper indexing strategies

## Authentication
- Use Flask-Login for session management
- Implement Google OAuth using Flask-OAuth
- Hash passwords with bcrypt
- Use proper session security
- Implement CSRF protection
- Use proper role-based access control

## API Design
- Use Flask-RESTful for REST APIs
- Implement proper request validation
- Use proper HTTP status codes
- Handle errors consistently
- Use proper response formats
- Implement proper rate limiting

## Testing
- Use pytest for testing
- Write tests for all routes
- Use pytest-cov for coverage
- Implement proper fixtures
- Use proper mocking with pytest-mock
- Test all error scenarios

## Security
- Use HTTPS in production
- Implement proper CORS
- Sanitize all user inputs
- Use proper session configuration
- Implement proper logging
- Follow OWASP guidelines

## Performance
- Use proper caching with Flask-Caching
- Implement database query optimization
- Use proper connection pooling
- Implement proper pagination
- Use background tasks for heavy operations
- Monitor application performance

## Error Handling
- Create custom exception classes
- Use proper try-except blocks
- Implement proper logging
- Return proper error responses
- Handle edge cases properly
- Use proper error messages

## Documentation
- Use Google-style docstrings
- Document all public APIs
- Keep README.md updated
- Use proper inline comments
- Generate API documentation
- Document environment setup

## Development Workflow
- Use virtual environments (venv)
- Implement pre-commit hooks
- Use proper Git workflow
- Follow semantic versioning
- Use proper CI/CD practices
- Implement proper logging

## Dependencies
- Pin dependency versions
- Use requirements.txt for production
- Separate dev dependencies
- Use proper package versions
- Regularly update dependencies
- Check for security vulnerabilities

# GitHub README Best Practices for Open-Source Projects

## Introduction
A GitHub README is the gateway to an open-source project, serving as the primary resource for users and contributors. It should clearly explain what the project does, how to use it, and how to get involved, all while being well-organized and engaging. This guide provides best practices for an LLM to write a README, leveraging its ability to generate clear text and code snippets, while noting where visuals could be added by others.

## General Writing Principles
- Use **clear and concise language** to ensure accessibility for all readers, including beginners and non-native speakers.
- Adopt an **inclusive and welcoming tone** to encourage participation from diverse contributors.
- Maintain a **professional yet friendly style** to reflect the project's quality and foster community.
- Ensure **proper grammar and spelling** using tools like spell checkers to polish the text.
- Format **code snippets** with Markdown's triple backticks and specify the language (e.g., ```bash) for readability.

## README Structure
- Include standard sections: **Project Overview**, **Installation**, **Usage**, **Contributing**, **License**, etc.
- Use **Markdown headers** (`#` for main sections, `##` for subsections) to create a logical flow.
- Order sections intuitively, starting with an introduction and progressing to detailed instructions.

## Project Overview
- **Describe the project**: Start with a brief, compelling summary of what the project does. Example: "A lightweight Rust web framework for building fast, scalable APIs."
- **Highlight purpose and value**: Explain why the project exists and its unique features (e.g., "Designed for simplicity and performance, unlike heavier alternatives").
- **Target the audience**: Specify who the project is for if not obvious (e.g., "Ideal for Rust developers new to web programming").
- **Keep it short**: Limit this to 2-3 paragraphs to retain reader interest.

## Installation Instructions
- **List prerequisites**: Detail required software or libraries (e.g., "Requires Rust 1.50+ and Cargo").
- **Provide step-by-step commands**: Use code blocks for clarity. Example:
  ```bash
  git clone https://github.com/user/project.git
  cd project
  cargo build --release
  ```
- **Address multiple platforms**: Include variations for different OSes if applicable (e.g., "On Windows, use `cargo build` without sudo").
- **Test instructions**: Ensure commands are accurate and reproducible.

## Usage Examples
- **Demonstrate functionality**: Provide practical examples of how to use the project. Example:
  ```rust
  use project::App;

  fn main() {
      let app = App::new();
      app.route("/hello", |req| "Hello, world!");
      app.run(8080);
  }
  ```
- **Explain the code**: Follow snippets with plain-language descriptions (e.g., "This sets up a server responding with 'Hello, world!' on port 8080").
- **Show outputs**: Describe expected results (e.g., "Visiting `localhost:8080/hello` displays 'Hello, world!'").
- **Suggest visuals**: Note where images could help (e.g., "A screenshot of the server output would clarify this step").

## Contributing Guidelines
- **Welcome contributions**: State that all skill levels are encouraged to participate.
- **Link to details**: Reference a `CONTRIBUTING.md` file if available (e.g., "See [Contributing](./CONTRIBUTING.md) for more").
- **Outline processes**: Briefly explain how to submit issues or pull requests (e.g., "File bugs on GitHub Issues; PRs should include tests").
- **Set expectations**: Mention coding standards or requirements (e.g., "Follow Rustfmt and pass Clippy checks").

## License
- **Specify the license**: Clearly state the terms (e.g., "Licensed under MIT").
- **Include or link**: Add the full text or link to a `LICENSE` file (e.g., "[MIT License](./LICENSE)").
- **Guide selection**: Suggest using [choosealicense.com](https://choosealicense.com/) if undecided.

## Badges
- **Display status**: Use badges for build status, version, etc. Example:
  ```markdown
  ![Build](https://img.shields.io/badge/build-passing-green)
  ![License](https://img.shields.io/badge/license-MIT-blue)
  ```
- **Source badges**: Recommend services like [shields.io](https://shields.io/) and link them to relevant pages.
- **Place strategically**: Position badges at the top for immediate visibility.

## Dependencies
- **List clearly**: Include all runtime and dev dependencies. Example:
  ```markdown
  - `serde` (v1.0) - Serialization framework
  - `tokio` (v0.2) - Async runtime
  ```
- **Use tables for complexity**: For many dependencies, format as:
  | Dependency | Version | Purpose          |
  |------------|---------|------------------|
  | `serde`    | 1.0     | Serialization    |
  | `tokio`    | 0.2     | Async processing |
- **Keep updated**: Reflect the latest `Cargo.toml` or equivalent.

## Support
- **Offer help channels**: List contact options (e.g., "Join our [Discord](https://discord.gg/xyz) or email support@project.com").
- **Encourage issues**: Point to GitHub Issues (e.g., "Report bugs at [Issues](https://github.com/user/project/issues)").
- **Set response tone**: Assure timely replies (e.g., "We aim to respond within 48 hours").

## Credits
- **Recognize contributors**: Name key individuals or teams (e.g., "Thanks to @alice and @bob").
- **Link profiles**: Use GitHub handles or URLs (e.g., "[@alice](https://github.com/alice)").
- **Reference GitHub**: Suggest viewing all contributors via the repository’s contributor graph.

## Visual Suggestions
- **Recommend types**: Suggest screenshots, diagrams, or GIFs (e.g., "A GIF of the app running would show its speed").
- **Describe placement**: Advise proximity to relevant text (e.g., "Place a terminal screenshot after installation steps").
- **Acknowledge limits**: Note that LLMs can’t create visuals but can describe them (e.g., "Diagram the request flow here").
- **Mention tools**: Suggest [Asciinema](https://asciinema.org/) or [ttygif](https://github.com/icholy/ttygif) for terminal demos.

## Formatting and Style
- **Leverage Markdown**: Use headers, lists, tables, and emphasis (e.g., **bold**, *italics*).
- **Organize content**: Break long sections into subsections for skimmability.
- **Highlight key points**: Use bold or code blocks to draw attention (e.g., **Run `cargo test`**).

## Maintenance
- **Update regularly**: Revise the README with project changes to avoid outdated info.
- **Use relative links**: Link to repo files with `./` (e.g., `./docs/setup.md`) for branch compatibility.
- **Test usability**: Follow the README steps to confirm they work as written.
- **Seek feedback**: Encourage community input to refine the document.

## Conclusion
A stellar README enhances a project's accessibility and appeal, driving adoption and collaboration. By following these guidelines, an LLM can craft a README that’s informative, structured, and community-friendly, even without visuals. Keep it current and open to improvement for lasting impact.

Repository: MyProject
Description: A web application for task management

Directory Structure:
- src/: Main application code
- tests/: Test files
- docs/: Documentation

Setup:
- Run `npm install` to install dependencies
- Use `npm run dev` for development
- Run `npm test` for testing

Guidelines:
- Follow ESLint configuration
- Write tests for all new features
- Use TypeScript for new code

If adding a new component in src/components, always add appropriate unit tests in tests/components/.

