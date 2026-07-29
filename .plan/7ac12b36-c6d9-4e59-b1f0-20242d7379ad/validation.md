# Validation

Validation will leverage the platform's declarative MVS testing harness to verify structural and mathematical parity against the target BigQuery environment:

1. **Schema Exists & Complete**: Assert that all 86 scripts execute with 0 failures on a scratch environment and all 86 tables/views are discoverable in the BigQuery live catalog.
2. **Numeric Enforced**: Compare every live column recursively against the legacy Hive schema, issuing a HARD FAIL if any float/double column failed to map explicitly to `NUMERIC` or `BIGNUMERIC`.
3. **Partition/Cluster Assertions**: Query the `INFORMATION_SCHEMA.COLUMNS` and `TABLES` to strictly assert that `is_partitioning_column = YES` for the designated business dates, and that the specified `clustering_columns` exist exactly as designed to support Tableau pruning.
4. **Coercion Read Test**: Run a baseline `SELECT *` or aggregate test on all 86 tables to verify zero runtime type-coercion errors during data reads.
