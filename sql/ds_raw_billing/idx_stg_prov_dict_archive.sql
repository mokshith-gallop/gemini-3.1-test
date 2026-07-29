CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.idx_stg_prov_dict_archive (
  filename STRING,
  filedate STRING,
  name STRING,
  numeric_code STRING,
  mnemonic STRING,
  division STRING,
  billing_area STRING,
  loc STRING,
  reporting_category_1 STRING,
  reporting_category_2 STRING,
  reporting_category_3 STRING,
  valid_organization STRING,
  npi_number STRING,
  additional1 STRING,
  additional2 STRING,
  additional3 STRING,
  additional4 STRING,
  additional5 STRING
)
OPTIONS (
  description='Migrated from shc_incomingphysician.idx_stg_prov_dict_archive'
);
