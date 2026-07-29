# Implementation Approach

We will manage the BigQuery Schema DDLs as **Raw GoogleSQL Scripts**.

- **File Structure**: All 86 `CREATE TABLE` and `CREATE VIEW` statements will be authored as standalone `.sql` files placed in `/workspace/project/sql/`.
- **Dataset Targets**:
  - `ds_raw_billing` (Bronze): Raw transactional mirrors (e.g., `stg_araccountheader`).
  - `ds_gold_analytics` (Silver/Gold): Conformed facts and dimension aggregations (e.g., `factkpimonthend`).
- **Idempotency**: Scripts will use `CREATE TABLE IF NOT EXISTS` or `CREATE OR REPLACE TABLE` constructs, ensuring they can be rerun cleanly by the CI/CD pipeline or Airflow runner without failure.
- **Table Options**: All configuration (like `partition_expiration_days` or `description`) will be defined intrinsically within the `OPTIONS(...)` block of each `CREATE TABLE` script, centralizing the schema definition.
