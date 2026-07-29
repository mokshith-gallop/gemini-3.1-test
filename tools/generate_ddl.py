#!/usr/bin/env python3
"""
Parse all 86 legacy Hive DDL files and generate BigQuery CREATE TABLE IF NOT EXISTS scripts.

Type mapping rules (locked decisions):
  - float/double -> NUMERIC (exact decimal for financial AR parity)
  - DECIMAL(p,s) -> NUMERIC (all observed: DECIMAL(18,6), DECIMAL(18,2) => p-s<=29)
  - TIMESTAMP -> DATETIME (wall-clock, timezone-less)
  - INT/TINYINT/SMALLINT -> INT64
  - BIGINT -> INT64
  - STRING -> STRING
  - BOOLEAN -> BOOL

Structural rules:
  - Hive partition columns (organizationgroupid, batch_id) demoted to regular columns
  - Digit-prefixed column names get underscore prefix for BQ legality
  - Time-unit partitioning on primary business date for large tables
  - Multi-column clustering on Tableau filter keys for DM tables
"""
import os
import re
import sys

SOURCE_BASE = "/workspace/source/Clarifications/SHA_GCPMigration_LACPhysician/SHA_GCPMigration_LACPhysician/DDL"
OUTPUT_BASE = "/workspace/project/sql"

# Type mapping: Hive -> BigQuery
TYPE_MAP = {
    "string": "STRING",
    "bigint": "INT64",
    "int": "INT64",
    "tinyint": "INT64",
    "smallint": "INT64",
    "float": "NUMERIC",
    "double": "NUMERIC",
    "boolean": "BOOL",
    "timestamp": "DATETIME",
    "date": "DATE",
}

# Partitioning strategy: table_name -> partition column (DATETIME column to wrap with DATE())
PARTITION_MAP = {
    # STG large transactional tables
    "stg_araccountheader": "recordreceiveddate",
    "stg_aradjustments": "recordreceiveddate",
    "stg_ardenial": "recordreceiveddate",
    "stg_arpayments": "recordreceiveddate",
    "stg_receivedfiles_metadata": "createddate",
    "tbldialeraccountdtl": "createddate",
    "tblsubaccount_lacpb": "createddate",
    "tbluseractivitynotes_lacpb": "createddate",
    # GOLD tables
    "araccountheader": "recordreceiveddate",
    "aradjustments": "recordreceiveddate",
    "arcurrentinventory": "postingperiod",
    "ardenial": "recordreceiveddate",
    "arpayments": "recordreceiveddate",
    "billingheader": "recordreceiveddate",
    "holdbillheader": "holdbillcreateddate",
    "tbluseractivitynotes": "createddate",
    # DM tables
    "dmadjustment": "adjustmentdate",
    "dmbillingheader": "recordreceiveddate",
    "dmcharges": "servicefromdate",
    "dmcurrentinventory": "postingperiod",
    "dmcurrentinventorydaywise": "placementdate",
    "dmdenial": "denieddate",
    "dmdenialdetails": "denieddate",
    "dmholdbillheader": "holdbillcreateddate",
    "dmkpimonthend": "invoicecreationperiod",
    # dmoutboundlaccashposting has no DATETIME column - skip partitioning
    "dmpayment": "paymentpostingperiod",
    "dmreferrals": "placementdate",
    "dmreferrals_spc_analytics": "placementdate",
    "dmtouchevents": "createddate",
    "dmtransaction": "invoicecreationperiod",
    "dmweeklyreport": "weekdate",
    "factkpimonthend": "invoicecreationperiod",
    "tb_factkpimonthend": "invoicecreationperiod",
}

# Clustering strategy: table_name -> list of cluster columns (up to 4)
CLUSTER_MAP = {
    # DM tables - Tableau filter keys
    "factkpimonthend": ["placementpayor", "department", "providername"],
    "tb_factkpimonthend": ["placementpayor", "department", "providername"],
    "dmkpimonthend": ["department", "payer", "fsctype"],
    "dmadjustment": ["placementpayor", "department", "financialclasscode"],
    "dmpayment": ["placementpayor", "department", "financialclasscode"],
    "dmcharges": ["financialclasscode", "placementpayor", "department"],
    "dmdenial": ["placementpayor", "department", "placementfinancialclass"],
    "dmdenialdetails": ["placementpayor", "department", "placementfinancialclass"],
    "dmcurrentinventory": ["financialclasscode", "primarypayor"],
    "dmcurrentinventorydaywise": ["placementfinancialclass", "placementpayor", "department"],
    "dmtransaction": ["placementfinancialclass", "accountnumber"],
    "dmtouchevents": ["accountheaderid"],
    "dmbillingheader": ["primarypayercode"],
    "dmholdbillheader": ["financialclasscode"],
    "dmweeklyreport": ["tag", "community"],
    "dmoutboundlaccashposting": ["payercode", "servicearea"],
    "dmreferrals": ["currentfinancialclass", "currentpayor"],
    "dmreferrals_spc_analytics": ["currentfinancialclass", "currentpayor"],
    # GOLD tables - common filter keys
    "araccountheader": ["organizationgroupid", "facilityid"],
    "aradjustments": ["organizationgroupid"],
    "arpayments": ["organizationgroupid"],
    "ardenial": ["organizationgroupid"],
    "arcurrentinventory": ["organizationgroupid"],
    "billingheader": ["organizationgroupid"],
}

# Dataset mapping: source_db -> target_dataset_placeholder
DB_TO_DATASET = {
    "shc_incomingphysician": "${DS_RAW_BILLING}",
    "shc_gold": "${DS_GOLD_ANALYTICS}",
    "shc_datamart": "${DS_GOLD_ANALYTICS}",
    "shcrcm_datamart": "${DS_GOLD_ANALYTICS}",
}

# Dataset mapping: source_db -> output_dir
DB_TO_DIR = {
    "shc_incomingphysician": "ds_raw_billing",
    "shc_gold": "ds_gold_analytics",
    "shc_datamart": "ds_gold_analytics",
    "shcrcm_datamart": "ds_gold_analytics",
}


def map_type(hive_type):
    """Map a Hive type to BigQuery type."""
    hive_type = hive_type.strip().lower()
    # Handle DECIMAL(p,s)
    m = re.match(r"decimal\((\d+),(\d+)\)", hive_type)
    if m:
        p, s = int(m.group(1)), int(m.group(2))
        # NUMERIC if p<=38, s<=9, p-s<=29; else BIGNUMERIC
        if p <= 38 and s <= 9 and (p - s) <= 29:
            return "NUMERIC"
        else:
            return "BIGNUMERIC"
    if hive_type in TYPE_MAP:
        return TYPE_MAP[hive_type]
    raise ValueError(f"Unknown Hive type: {hive_type}")


def make_bq_legal(col_name):
    """Ensure column name is legal in BigQuery (starts with letter or underscore)."""
    if col_name[0].isdigit():
        return "_" + col_name
    return col_name


def find_balanced_parens(text, start):
    """Find the content inside balanced parentheses starting at position start.
    Returns (content, end_pos) where end_pos is position after closing paren."""
    assert text[start] == "(", f"Expected '(' at position {start}, got '{text[start]}'"
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
        i += 1
    raise ValueError("Unbalanced parentheses")


def parse_hive_ddl(filepath):
    """Parse a Hive DDL file and extract table name, database, columns, and partition columns."""
    with open(filepath, "r") as f:
        content = f.read()

    # Remove \r
    content = content.replace("\r", "")

    # Find the CREATE TABLE statement and extract db.table
    m = re.search(
        r"CREATE\s+EXTERNAL\s+TABLE\s+`(\w+)`\.`(\w+)`\s*\(",
        content,
        re.IGNORECASE,
    )
    if not m:
        m = re.search(
            r"CREATE\s+EXTERNAL\s+TABLE\s+(\w+)\.(\w+)\s*\(",
            content,
            re.IGNORECASE,
        )
    if not m:
        print(f"WARNING: Could not parse {filepath}")
        return None

    db_name = m.group(1)
    table_name = m.group(2)

    # Find the opening paren of the column list and extract balanced content
    paren_start = content.index("(", m.end() - 1)
    cols_str, after_cols = find_balanced_parens(content, paren_start)

    # Check for PARTITIONED BY
    rest = content[after_cols:]
    part_str = ""
    pm = re.search(r"PARTITIONED\s+BY\s*\(", rest, re.IGNORECASE)
    if pm:
        part_paren_start = after_cols + pm.end() - 1
        part_str, _ = find_balanced_parens(content, part_paren_start)

    def parse_columns(col_string):
        """Parse column definitions from a Hive DDL column string."""
        columns = []
        for line in col_string.strip().split("\n"):
            line = line.strip().rstrip(",").strip()
            if not line:
                continue
            # Match `col_name` type_with_optional_params
            cm = re.match(r"`?(\w+)`?\s+(decimal\(\d+,\s*\d+\)|\S+)", line, re.IGNORECASE)
            if cm:
                col_name = cm.group(1).lower()
                col_type = cm.group(2).lower().rstrip(",")
                columns.append((col_name, col_type))
        return columns

    columns = parse_columns(cols_str)
    partition_cols = parse_columns(part_str) if part_str else []

    return {
        "db": db_name,
        "table": table_name,
        "columns": columns,
        "partition_cols": partition_cols,
        "filepath": filepath,
    }


def generate_bq_ddl(parsed):
    """Generate BigQuery CREATE TABLE IF NOT EXISTS DDL from parsed Hive DDL."""
    db = parsed["db"]
    table = parsed["table"]
    columns = parsed["columns"]
    partition_cols = parsed["partition_cols"]

    dataset_placeholder = DB_TO_DATASET.get(db, "${DS_RAW_BILLING}")

    # Merge partition columns into regular columns (demote)
    all_columns = columns + partition_cols

    # Build column definitions
    col_defs = []
    renamed_cols = {}
    for col_name, hive_type in all_columns:
        bq_type = map_type(hive_type)
        bq_name = make_bq_legal(col_name)
        if bq_name != col_name:
            renamed_cols[col_name] = bq_name
        col_defs.append(f"  {bq_name} {bq_type}")

    # Build the DDL
    lines = []
    lines.append(f"CREATE TABLE IF NOT EXISTS `{dataset_placeholder}`.{table} (")
    lines.append(",\n".join(col_defs))
    lines.append(")")

    # Partitioning
    part_col = PARTITION_MAP.get(table)
    if part_col:
        # Check if the partition col exists and map its renamed version
        actual_col = make_bq_legal(part_col)
        # Find the type of this column
        col_type = None
        for cn, ct in all_columns:
            if make_bq_legal(cn) == actual_col:
                col_type = map_type(ct)
                break
        if col_type == "DATETIME":
            lines.append(f"PARTITION BY DATE({actual_col})")
        elif col_type == "DATE":
            lines.append(f"PARTITION BY {actual_col}")
        else:
            # Skip partitioning if no suitable column found
            part_col = None

    # Clustering
    cluster_cols = CLUSTER_MAP.get(table)
    if cluster_cols:
        # Map to BQ-legal names and verify they exist
        valid_cluster_cols = []
        all_col_names = [make_bq_legal(cn) for cn, _ in all_columns]
        for cc in cluster_cols:
            cc_bq = make_bq_legal(cc)
            if cc_bq in all_col_names:
                valid_cluster_cols.append(cc_bq)
        if valid_cluster_cols:
            lines.append(f"CLUSTER BY {', '.join(valid_cluster_cols)}")

    # Options
    lines.append(f"OPTIONS (")
    lines.append(f"  description='Migrated from {db}.{table}'")
    lines.append(f");")

    return "\n".join(lines)


def main():
    # Collect all source DDL files
    source_dirs = {
        "STG": os.path.join(SOURCE_BASE, "STG"),
        "GOLD": os.path.join(SOURCE_BASE, "GOLD"),
        "DM": os.path.join(SOURCE_BASE, "DM"),
    }

    all_parsed = []
    errors = []

    for layer, src_dir in source_dirs.items():
        if not os.path.isdir(src_dir):
            print(f"WARNING: {src_dir} not found")
            continue
        for fname in sorted(os.listdir(src_dir)):
            if not fname.endswith(".sql"):
                continue
            fpath = os.path.join(src_dir, fname)
            parsed = parse_hive_ddl(fpath)
            if parsed:
                parsed["layer"] = layer
                parsed["source_file"] = fname
                all_parsed.append(parsed)
            else:
                errors.append(fpath)

    print(f"Parsed {len(all_parsed)} tables, {len(errors)} errors")

    # Generate BigQuery DDLs
    generated = 0
    for parsed in all_parsed:
        db = parsed["db"]
        table = parsed["table"]
        out_dir = os.path.join(OUTPUT_BASE, DB_TO_DIR.get(db, "ds_raw_billing"))
        os.makedirs(out_dir, exist_ok=True)

        try:
            ddl = generate_bq_ddl(parsed)
            out_path = os.path.join(out_dir, f"{table}.sql")
            with open(out_path, "w") as f:
                f.write(ddl + "\n")
            generated += 1
            print(f"  Generated: {out_path}")
        except Exception as e:
            print(f"  ERROR generating {table}: {e}")
            errors.append(f"{table}: {e}")

    print(f"\nTotal generated: {generated}")
    if errors:
        print(f"Errors: {errors}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
