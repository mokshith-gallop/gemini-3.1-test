CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.idx_stg_hosp_dict (
  filename STRING,
  filedate STRING,
  name STRING,
  mnemonic STRING,
  numeric_code STRING,
  valid_organization STRING,
  additional1 STRING,
  additional2 STRING,
  additional3 STRING,
  additional4 STRING,
  additional5 STRING
)
OPTIONS (
  description='Migrated from shc_incomingphysician.idx_stg_hosp_dict'
);
