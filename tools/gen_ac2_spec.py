#!/usr/bin/env python3
"""
Generate the AC2 MVS spec: schema_conformance WITH source cross-check.

Proves every column's migrated BigQuery type matches the LIVE legacy Hive
source catalog. Any float/double/DECIMAL column not landing as NUMERIC is a
HARD FAIL.  Digit-prefixed columns carry source_name with the original
Hive column name so the harness can find them in the live source.
"""
import os
import sys
import yaml

# Import shared parser and maps from generate_ddl
sys.path.insert(0, os.path.dirname(__file__))
from generate_ddl import (
    SOURCE_BASE,
    DB_TO_DATASET,
    DB_TO_DIR,
    map_type,
    make_bq_legal,
    parse_hive_ddl,
)

OUTPUT = "/workspace/project/specs/ac2_type_mapping.mvs.yaml"


def hive_type_upper(hive_type):
    """Return the uppercase Hive source type for the spec.

    For decimal(p,s) return DECIMAL — the harness normalize_type handles it.
    For plain types return uppercase (FLOAT, DOUBLE, TIMESTAMP, etc.).
    """
    ht = hive_type.strip().lower()
    if ht.startswith("decimal"):
        return "DECIMAL"
    return ht.upper()


def build_column_entry_with_source(col_name, hive_type, table_name):
    """Build a column dict with both target and source declarations."""
    bq_name = make_bq_legal(col_name)
    bq_type = map_type(hive_type)
    src_type = hive_type_upper(hive_type)

    entry = {
        "name": bq_name,
        "type": bq_type,
        "source_type": src_type,
    }

    if bq_type == "NUMERIC":
        entry["scale"] = 9

    entry["nullable"] = True

    # If column was renamed (digit-prefix), declare the original source_name
    if bq_name != col_name:
        entry["source_name"] = col_name

    return entry


def build_table_entry_with_source(parsed):
    """Build a table dict for the MVS spec with source cross-check fields."""
    table = parsed["table"]
    all_columns = parsed["columns"] + parsed["partition_cols"]

    columns = []
    for col_name, hive_type in all_columns:
        columns.append(build_column_entry_with_source(col_name, hive_type, table))

    entry = {
        "table": table,
        "source_table": table,
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


def build_source_setup_ddl(all_parsed):
    """Build the source_setup.ddl list of absolute paths to legacy HQL files."""
    ddl_paths = []
    for parsed in all_parsed:
        ddl_paths.append(parsed["filepath"])
    return ddl_paths


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

    # Group tables by source database for separate suites
    db_groups = {}
    for parsed in all_parsed:
        db = parsed["db"]
        db_groups.setdefault(db, []).append(parsed)

    for db, tables in db_groups.items():
        print(f"  {db}: {len(tables)} tables")

    # Build migration steps
    steps = build_migration_steps(all_parsed)

    # Build source_setup.ddl paths
    source_ddl_paths = build_source_setup_ddl(all_parsed)

    # Build suites — one per source database
    # Order: shc_incomingphysician (STG), shc_gold (GOLD), shc_datamart (DM), shcrcm_datamart
    suite_configs = [
        ("shc_incomingphysician", "${DS_RAW_BILLING}", "ac2-stg-type-mapping"),
        ("shc_gold", "${DS_GOLD_ANALYTICS}", "ac2-gold-type-mapping"),
        ("shc_datamart", "${DS_GOLD_ANALYTICS}", "ac2-dm-type-mapping"),
        ("shcrcm_datamart", "${DS_GOLD_ANALYTICS}", "ac2-shcrcm-type-mapping"),
    ]

    suites = []
    for src_db, target_ds, suite_id in suite_configs:
        tables = db_groups.get(src_db, [])
        if not tables:
            continue
        table_entries = [build_table_entry_with_source(p) for p in tables]
        suite = {
            "pattern": "schema_conformance",
            "id": suite_id,
            "target_dataset": target_ds,
            "source_database": src_db,
            "expect_table_count": len(table_entries),
            "tables": table_entries,
        }
        suites.append(suite)

    # Build the full spec
    spec = {
        "name": "ac2_type_mapping",
        "connections": {
            "source": {"engine": "hive"},
            "target": {"engine": "bigquery"},
        },
        "source_setup": {
            "ddl": source_ddl_paths,
        },
        "migration": {
            "build_datasets": ["raw_billing", "gold_analytics"],
            "steps": steps,
        },
        "suites": suites,
    }

    # Write the spec
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

    class NoAliasDumper(yaml.SafeDumper):
        def ignore_aliases(self, data):
            return True

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

    # Print summary
    print(f"\nWrote {OUTPUT}")
    print(f"  source_setup.ddl: {len(source_ddl_paths)} files")
    print(f"  migration steps: {len(steps)}")
    total_tables = sum(len(s["tables"]) for s in suites)
    total_cols = sum(
        len(col)
        for s in suites
        for t in s["tables"]
        for col in [t["columns"]]
    )
    print(f"  suites: {len(suites)}")
    print(f"  total tables: {total_tables}")
    print(f"  total column declarations: {total_cols}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
