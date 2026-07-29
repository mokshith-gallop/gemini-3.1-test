#!/usr/bin/env python3
"""
Generate the AC1 MVS spec: schema_conformance (TARGET-ONLY).

Proves all 86 DDL scripts execute with 0 BigQuery engine errors, landing
exactly the expected object count per dataset with correct column types.

NO source_setup / source_database / source_type — this is a 'DDL applies' criterion.
"""
import os
import sys
import yaml

# Import shared parser and maps from generate_ddl
sys.path.insert(0, os.path.dirname(__file__))
from generate_ddl import (
    SOURCE_BASE,
    TYPE_MAP,
    PARTITION_MAP,
    CLUSTER_MAP,
    DB_TO_DATASET,
    DB_TO_DIR,
    map_type,
    make_bq_legal,
    parse_hive_ddl,
)

OUTPUT = "/workspace/project/specs/ac1_schema_applies.mvs.yaml"


def build_column_entry(col_name, hive_type):
    """Build a column dict for the MVS spec."""
    bq_name = make_bq_legal(col_name)
    bq_type = map_type(hive_type)
    entry = {"name": bq_name, "type": bq_type}
    if bq_type == "NUMERIC":
        entry["scale"] = 9
    # All columns nullable (Hive EXTERNAL imposes no NOT NULL)
    entry["nullable"] = True
    return entry


def build_table_entry(parsed):
    """Build a table dict for the MVS spec."""
    table = parsed["table"]
    all_columns = parsed["columns"] + parsed["partition_cols"]

    columns = []
    for col_name, hive_type in all_columns:
        columns.append(build_column_entry(col_name, hive_type))

    entry = {
        "table": table,
        "expect_object_type": "TABLE",
        "columns": columns,
    }
    return entry


def build_migration_steps(all_parsed):
    """Build the migration steps listing all 86 DDL files."""
    steps = []
    for parsed in all_parsed:
        db = parsed["db"]
        table = parsed["table"]
        subdir = DB_TO_DIR.get(db, "ds_raw_billing")
        sql_path = f"sql/{subdir}/{table}.sql"
        steps.append({
            "kind": "ddl",
            "sql": sql_path,
        })
    return steps


def main():
    # Parse all source DDL files
    source_dirs = [
        ("STG", os.path.join(SOURCE_BASE, "STG")),
        ("GOLD", os.path.join(SOURCE_BASE, "GOLD")),
        ("DM", os.path.join(SOURCE_BASE, "DM")),
    ]

    all_parsed = []
    for layer, src_dir in source_dirs:
        for fname in sorted(os.listdir(src_dir)):
            if not fname.endswith(".sql"):
                continue
            fpath = os.path.join(src_dir, fname)
            parsed = parse_hive_ddl(fpath)
            if parsed:
                parsed["layer"] = layer
                all_parsed.append(parsed)

    print(f"Parsed {len(all_parsed)} tables")

    # Split by target dataset
    raw_billing_tables = []
    gold_analytics_tables = []

    for parsed in all_parsed:
        db = parsed["db"]
        ds = DB_TO_DATASET.get(db, "${DS_RAW_BILLING}")
        if ds == "${DS_RAW_BILLING}":
            raw_billing_tables.append(parsed)
        else:
            gold_analytics_tables.append(parsed)

    print(f"  ds_raw_billing: {len(raw_billing_tables)} tables")
    print(f"  ds_gold_analytics: {len(gold_analytics_tables)} tables")

    # Build migration steps
    steps = build_migration_steps(all_parsed)

    # Build table entries for each suite
    raw_tables = [build_table_entry(p) for p in raw_billing_tables]
    gold_tables = [build_table_entry(p) for p in gold_analytics_tables]

    # Build the full spec
    spec = {
        "name": "ac1_schema_applies",
        "connections": {
            "target": {"engine": "bigquery"},
        },
        "migration": {
            "build_datasets": ["raw_billing", "gold_analytics"],
            "steps": steps,
        },
        "suites": [
            {
                "pattern": "schema_conformance",
                "id": "ac1-raw-billing",
                "target_dataset": "${DS_RAW_BILLING}",
                "expect_table_count": len(raw_billing_tables),
                "tables": raw_tables,
            },
            {
                "pattern": "schema_conformance",
                "id": "ac1-gold-analytics",
                "target_dataset": "${DS_GOLD_ANALYTICS}",
                "expect_table_count": len(gold_analytics_tables),
                "tables": gold_tables,
            },
        ],
    }

    # Write the spec
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

    # Custom YAML representer to avoid anchors/aliases and handle formatting
    class NoAliasDumper(yaml.SafeDumper):
        def ignore_aliases(self, data):
            return True

    # Represent True/False as true/false (YAML native)
    def bool_representer(dumper, data):
        return dumper.represent_bool(data)

    with open(OUTPUT, "w") as f:
        yaml.dump(
            spec,
            f,
            Dumper=NoAliasDumper,
            default_flow_style=False,
            sort_keys=False,
            width=200,
            allow_unicode=True,
        )

    print(f"\nWrote {OUTPUT}")
    print(f"  Total migration steps: {len(steps)}")
    print(f"  Suite 1 (raw_billing): {len(raw_tables)} tables")
    print(f"  Suite 2 (gold_analytics): {len(gold_tables)} tables")

    return 0


if __name__ == "__main__":
    sys.exit(main())
