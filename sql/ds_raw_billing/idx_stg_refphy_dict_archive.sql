CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.idx_stg_refphy_dict_archive (
  filename STRING,
  filedate STRING,
  name STRING,
  mnemonic STRING,
  number STRING,
  valid_organization STRING,
  npi_number STRING,
  address_line1 STRING,
  address_line2 STRING,
  city_state STRING,
  zip_code STRING,
  additional1 STRING,
  additional2 STRING,
  additional3 STRING,
  additional4 STRING,
  additional5 STRING
)
OPTIONS (
  description='Migrated from shc_incomingphysician.idx_stg_refphy_dict_archive'
);
