CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.idx_stg_lac_mh_rejection_archive (
  filename STRING,
  filedate STRING,
  mrn STRING,
  inv_num STRING,
  orig_inv_num STRING,
  orig_fsc__2 STRING,
  fsc_at_payment__2 STRING,
  txn_num STRING,
  proc__2 STRING,
  tot_chg NUMERIC,
  inv_bal NUMERIC,
  chg_amt NUMERIC,
  ser_dt STRING,
  post_dt STRING,
  rej_check_dt STRING,
  post_pd STRING,
  pay_code__2 STRING,
  mod_1 STRING,
  mod_2 STRING,
  mod_3 STRING,
  units STRING,
  rvu STRING,
  rvu_work_comp STRING,
  rej_4__1 STRING,
  rej_1__1 STRING,
  rej_2__1 STRING,
  rej_3__1 STRING,
  grp__2 STRING,
  rej_remark STRING,
  rej_mess STRING
)
OPTIONS (
  description='Migrated from shc_incomingphysician.idx_stg_lac_mh_rejection_archive'
);
