CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.lac_phy_idx_stg_insurance (
  filename STRING,
  filedate STRING,
  grp STRING,
  mrn STRING,
  oth_num STRING,
  pat_nm STRING,
  inv_num STRING,
  tot_chg STRING,
  ser_dt STRING,
  dob STRING,
  sex STRING,
  cert_num STRING,
  ssn STRING,
  fsc STRING,
  prov STRING,
  ins_comp_dict_entry STRING,
  ins_comp_nm STRING,
  ins_comp_addr1 STRING,
  ins_comp_addr2 STRING,
  ins_comp_ctyst STRING,
  ins_comp_zip STRING,
  inv_bal STRING,
  hos STRING,
  u_acsn_num STRING,
  inv_cre_dt STRING
)
OPTIONS (
  description='Migrated from shc_incomingphysician.lac_phy_idx_stg_insurance'
);
