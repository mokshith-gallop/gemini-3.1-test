CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.idx_stg_insurance_dict (
  filename STRING,
  filedate STRING,
  name STRING,
  street_address STRING,
  second_line_of_address STRING,
  city_state STRING,
  zip_code STRING,
  tel_no STRING,
  mnemonic STRING,
  payer_id STRING,
  valid_fsc_for_this_insurance_company STRING,
  grp STRING,
  additional1 STRING,
  additional2 STRING,
  additional3 STRING,
  additional4 STRING,
  additional5 STRING
)
OPTIONS (
  description='Migrated from shc_incomingphysician.idx_stg_insurance_dict'
);
