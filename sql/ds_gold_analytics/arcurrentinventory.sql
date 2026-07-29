CREATE SCHEMA IF NOT EXISTS `${DS_GOLD_ANALYTICS}`;
CREATE TABLE IF NOT EXISTS `${DS_GOLD_ANALYTICS}`.arcurrentinventory (
  accountnumber STRING,
  accountar NUMERIC,
  currentpayor STRING,
  miscategory1 STRING,
  miscategory2 STRING,
  miscategory3 STRING,
  miscategory4 STRING,
  miscategory5 STRING,
  category STRING,
  postingperiod DATETIME,
  outsourcedate DATETIME,
  organizationgroupid STRING,
  batch_id STRING
)
PARTITION BY DATE(postingperiod)
CLUSTER BY organizationgroupid
OPTIONS (
  description='Migrated from shc_gold.arcurrentinventory'
);
