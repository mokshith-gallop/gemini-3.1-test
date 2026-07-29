CREATE SCHEMA IF NOT EXISTS `${DS_GOLD_ANALYTICS}`;
CREATE TABLE IF NOT EXISTS `${DS_GOLD_ANALYTICS}`.dmcurrentinventory (
  accountnumber STRING,
  accountar NUMERIC,
  postingperiod DATETIME,
  currentpayor STRING,
  miscategory1 STRING,
  miscategory2 STRING,
  miscategory3 STRING,
  miscategory4 STRING,
  miscategory5 STRING,
  category STRING,
  financialclasscode STRING,
  placementfinancialclass STRING,
  primarypayor STRING,
  placementpayor STRING,
  facilityname STRING,
  department STRING,
  speciality STRING,
  servicearea STRING,
  providername STRING,
  region STRING,
  specialtygroupnumber STRING,
  placementdate DATETIME,
  invoicecreationperiod DATETIME,
  sequencenumber INT64,
  specialtygroupdescription STRING,
  provision STRING,
  tag STRING,
  organizationgroupid STRING,
  batch_id STRING
)
PARTITION BY DATE(postingperiod)
CLUSTER BY financialclasscode, primarypayor
OPTIONS (
  description='Migrated from shc_datamart.dmcurrentinventory'
);
