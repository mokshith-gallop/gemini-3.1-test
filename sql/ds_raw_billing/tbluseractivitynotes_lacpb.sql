CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.tbluseractivitynotes_lacpb (
  id INT64,
  account_id INT64,
  subaccount_id INT64,
  statuscodeid INT64,
  actioncodeid INT64,
  notes STRING,
  acct_invtype STRING,
  followupdate DATETIME,
  createdby STRING,
  createddate DATETIME,
  updatedby STRING,
  updateddate DATETIME,
  activeflag BOOL,
  organizationgroupid STRING,
  accountnumber STRING,
  additionalfields STRING,
  issmartnotes STRING,
  poolid INT64,
  notetypeid INT64,
  smartauditfields STRING,
  weightage STRING,
  loaddate DATETIME,
  formattednotes STRING
)
PARTITION BY DATE(createddate)
OPTIONS (
  description='Migrated from shc_incomingphysician.tbluseractivitynotes_lacpb'
);
