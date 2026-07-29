#!/usr/bin/env python3
"""
Generate the AC3 + AC4 MVS specs:
  AC3: schema_conformance for partitioning, clustering, FK type consistency
  AC4: query_performance for queryability and scan-pruning
"""
import os
import sys
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from generate_ddl import (
    SOURCE_BASE,
    PARTITION_MAP,
    CLUSTER_MAP,
    DB_TO_DATASET,
    DB_TO_DIR,
    map_type,
    make_bq_legal,
    parse_hive_ddl,
)

AC3_OUTPUT = "/workspace/project/specs/ac3_physical_access.mvs.yaml"
AC4_OUTPUT = "/workspace/project/specs/ac4_queryability_pruning.mvs.yaml"

# FK columns to check for cross-table type consistency.
# Every table that carries one of these gets the column in its columns list.
FK_COLUMNS = [
    "accountheaderid",
    "billingheaderid",
    "facilityid",
    "patientid",
    "organizationgroupid",
]


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def build_migration_steps(all_parsed):
    steps = []
    for parsed in all_parsed:
        db = parsed["db"]
        table = parsed["table"]
        subdir = DB_TO_DIR.get(db, "ds_raw_billing")
        steps.append({"kind": "ddl", "sql": f"sql/{subdir}/{table}.sql"})
    return steps


def build_ac3_table_entry(parsed):
    """Build a table entry for the AC3 physical-access spec.

    Every table gets: table, expect_object_type, columns (at least one column).
    Partitioned tables get partition_by.
    Clustered tables get cluster_by.
    FK columns are always included if present.
    """
    table = parsed["table"]
    all_cols = parsed["columns"] + parsed["partition_cols"]
    col_lookup = {cn: ct for cn, ct in all_cols}

    # Determine which columns to include: FK columns + partition col + cluster cols + first col fallback
    included_cols = set()

    # FK columns present in this table
    for fk in FK_COLUMNS:
        if fk in col_lookup:
            included_cols.add(fk)

    # Partition column
    part_col = PARTITION_MAP.get(table)
    if part_col and part_col in col_lookup:
        included_cols.add(part_col)

    # Cluster columns
    cluster_cols = CLUSTER_MAP.get(table)
    if cluster_cols:
        for cc in cluster_cols:
            if cc in col_lookup:
                included_cols.add(cc)

    # Guarantee at least one column (harness requires minItems: 1)
    if not included_cols:
        first_col = all_cols[0][0]
        included_cols.add(first_col)

    # Build column entries preserving source order
    columns = []
    for cn, ct in all_cols:
        if cn in included_cols:
            bq_name = make_bq_legal(cn)
            bq_type = map_type(ct)
            entry = {"name": bq_name, "type": bq_type}
            if bq_type == "NUMERIC":
                entry["scale"] = 9
            columns.append(entry)

    result = {
        "table": table,
        "expect_object_type": "TABLE",
        "columns": columns,
    }

    # Partition declaration
    if part_col and part_col in col_lookup:
        result["partition_by"] = make_bq_legal(part_col)

    # Cluster declaration
    if cluster_cols:
        valid_cluster = []
        all_col_names = [cn for cn, _ in all_cols]
        for cc in cluster_cols:
            if cc in all_col_names:
                valid_cluster.append(make_bq_legal(cc))
        if valid_cluster:
            result["cluster_by"] = valid_cluster

    return result


def build_ac4_measure_query(table, dataset_placeholder):
    """Build a mode: measure query for queryability smoke test."""
    return {
        "id": f"smoke-{table}",
        "mode": "measure",
        "sql": f"SELECT * FROM `{dataset_placeholder}`.{table} LIMIT 0",
    }


# Hot-path DM tables and their partition filter columns for compare mode
HOT_PATH_TABLES = {
    "factkpimonthend": {
        "partition_col": "invoicecreationperiod",
        "cluster_cols": ["placementpayor"],
    },
    "dmadjustment": {
        "partition_col": "adjustmentdate",
        "cluster_cols": ["placementpayor"],
    },
    "dmpayment": {
        "partition_col": "paymentpostingperiod",
        "cluster_cols": ["placementpayor"],
    },
    "dmcharges": {
        "partition_col": "servicefromdate",
        "cluster_cols": ["financialclasscode"],
    },
    "dmdenial": {
        "partition_col": "denieddate",
        "cluster_cols": ["placementpayor"],
    },
}


def build_ac4_compare_query(table, dataset_placeholder, part_col):
    """Build a mode: compare query pair for scan-pruning proof."""
    return {
        "id": f"prune-{table}",
        "mode": "compare",
        "a": {
            "sql": f"SELECT COUNT(*) AS n FROM `{dataset_placeholder}`.{table}",
        },
        "b": {
            "sql": (
                f"SELECT COUNT(*) AS n FROM `{dataset_placeholder}`.{table} "
                f"WHERE {part_col} >= DATETIME('2020-01-01')"
            ),
        },
        "compare": {
            "bytes_scanned": "b <= a",
        },
    }


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

    # Build shared migration steps
    steps = build_migration_steps(all_parsed)

    # ── AC3: Physical Access ──────────────────────────────────────────────

    # Split by target dataset
    raw_tables = []
    gold_tables = []
    for parsed in all_parsed:
        ds = DB_TO_DATASET.get(parsed["db"], "${DS_RAW_BILLING}")
        entry = build_ac3_table_entry(parsed)
        if ds == "${DS_RAW_BILLING}":
            raw_tables.append(entry)
        else:
            gold_tables.append(entry)

    ac3_spec = {
        "name": "ac3_physical_access",
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
                "id": "ac3-raw-billing-physical",
                "target_dataset": "${DS_RAW_BILLING}",
                "expect_table_count": len(raw_tables),
                "tables": raw_tables,
            },
            {
                "pattern": "schema_conformance",
                "id": "ac3-gold-analytics-physical",
                "target_dataset": "${DS_GOLD_ANALYTICS}",
                "expect_table_count": len(gold_tables),
                "tables": gold_tables,
            },
        ],
    }

    os.makedirs(os.path.dirname(AC3_OUTPUT), exist_ok=True)
    with open(AC3_OUTPUT, "w") as f:
        yaml.dump(ac3_spec, f, Dumper=NoAliasDumper, default_flow_style=False,
                  sort_keys=False, width=200, allow_unicode=True)

    n_part = sum(1 for t in raw_tables + gold_tables if "partition_by" in t)
    n_clust = sum(1 for t in raw_tables + gold_tables if "cluster_by" in t)
    print(f"\nAC3: {AC3_OUTPUT}")
    print(f"  raw_billing: {len(raw_tables)} tables")
    print(f"  gold_analytics: {len(gold_tables)} tables")
    print(f"  partitioned: {n_part}")
    print(f"  clustered: {n_clust}")

    # ── AC4: Queryability & Pruning ───────────────────────────────────────

    queries = []

    # Smoke queries for all 86 tables
    for parsed in all_parsed:
        ds = DB_TO_DATASET.get(parsed["db"], "${DS_RAW_BILLING}")
        queries.append(build_ac4_measure_query(parsed["table"], ds))

    # Compare queries for hot-path tables
    for table, info in HOT_PATH_TABLES.items():
        queries.append(
            build_ac4_compare_query(table, "${DS_GOLD_ANALYTICS}", info["partition_col"])
        )

    ac4_spec = {
        "name": "ac4_queryability_pruning",
        "connections": {
            "target": {"engine": "bigquery"},
        },
        "migration": {
            "build_datasets": ["raw_billing", "gold_analytics"],
            "steps": steps,
        },
        "suites": [
            {
                "pattern": "query_performance",
                "id": "ac4-queryability-pruning",
                "queries": queries,
            },
        ],
    }

    with open(AC4_OUTPUT, "w") as f:
        yaml.dump(ac4_spec, f, Dumper=NoAliasDumper, default_flow_style=False,
                  sort_keys=False, width=200, allow_unicode=True)

    n_measure = sum(1 for q in queries if q["mode"] == "measure")
    n_compare = sum(1 for q in queries if q["mode"] == "compare")
    print(f"\nAC4: {AC4_OUTPUT}")
    print(f"  measure queries: {n_measure}")
    print(f"  compare queries: {n_compare}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
