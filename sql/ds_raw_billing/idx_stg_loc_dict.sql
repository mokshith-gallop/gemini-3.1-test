CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.idx_stg_loc_dict (
  filename STRING,
  filedate STRING,
  name STRING,
  mnemonic STRING,
  numeric_code STRING,
  hipaa_facility_type STRING,
  reporting_category_1 STRING,
  reporting_category_2 STRING,
  reporting_category_3 STRING,
  valid_organization STRING,
  corresponding_loc_medicare_form STRING,
  additional1 STRING,
  additional2 STRING,
  additional3 STRING,
  additional4 STRING,
  additional5 STRING
)
OPTIONS (
  description='Migrated from shc_incomingphysician.idx_stg_loc_dict'
);
