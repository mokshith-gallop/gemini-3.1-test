CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.idx_stg_patients (
  filename STRING,
  filedate STRING,
  pat_nm STRING,
  dob STRING,
  sex STRING,
  ssn STRING,
  street_addr_l1 STRING,
  street_addr_l2 STRING,
  ctyst STRING,
  zip STRING,
  tel STRING,
  u_cell_tel STRING,
  secondary_pt_tel STRING,
  bus_tel STRING,
  oth_num STRING,
  grp_2 STRING,
  additional1 STRING,
  additional2 STRING,
  additional3 STRING,
  additional4 STRING,
  additional5 STRING
)
OPTIONS (
  description='Migrated from shc_incomingphysician.idx_stg_patients'
);
