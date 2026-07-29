CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.idx_stg_lac_mh_paycode_dict (
  filename STRING,
  filedate STRING,
  name STRING,
  code STRING,
  payment_category STRING,
  type STRING,
  security_restriction STRING,
  additional1 STRING,
  additional2 STRING,
  additional3 STRING,
  additional4 STRING,
  additional5 STRING
)
OPTIONS (
  description='Migrated from shc_incomingphysician.idx_stg_lac_mh_paycode_dict'
);
