CREATE SCHEMA IF NOT EXISTS `${DS_GOLD_ANALYTICS}`;
CREATE TABLE IF NOT EXISTS `${DS_GOLD_ANALYTICS}`.dmcurrentinventorydaywise (
  day DATETIME,
  placementfinancialclass STRING,
  placementpayor STRING,
  currentpayor STRING,
  currentfinancialclass STRING,
  facilityname STRING,
  department STRING,
  speciality STRING,
  servicearea STRING,
  providername STRING,
  region STRING,
  osarvolume INT64,
  osar NUMERIC,
  sequencenumber INT64,
  specialtygroupnumber STRING,
  placementdate DATETIME,
  invoicecreationperiod DATETIME,
  organizationgroupid STRING,
  batch_id STRING
)
PARTITION BY DATE(placementdate)
CLUSTER BY placementfinancialclass, placementpayor, department
OPTIONS (
  description='Migrated from shc_datamart.dmcurrentinventorydaywise'
);
