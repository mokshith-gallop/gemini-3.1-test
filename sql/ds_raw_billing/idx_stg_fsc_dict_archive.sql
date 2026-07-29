CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.idx_stg_fsc_dict_archive (
  filename STRING,
  filedate STRING,
  name STRING,
  fsc_number STRING,
  mnemonic STRING,
  reporting_category_1 STRING,
  reporting_category_2 STRING,
  reporting_category_3 STRING,
  payerid STRING,
  group_restriction STRING,
  apply_fsc_restrict_inscomp_d120 STRING,
  street_address STRING,
  second_line_address STRING,
  city_state STRING,
  zip_code STRING,
  telephone_number STRING,
  additional1 STRING,
  additional2 STRING,
  additional3 STRING,
  additional4 STRING,
  additional5 STRING
)
OPTIONS (
  description='Migrated from shc_incomingphysician.idx_stg_fsc_dict_archive'
);
