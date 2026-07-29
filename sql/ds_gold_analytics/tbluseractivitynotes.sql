CREATE SCHEMA IF NOT EXISTS `${DS_GOLD_ANALYTICS}`;
CREATE TABLE IF NOT EXISTS `${DS_GOLD_ANALYTICS}`.tbluseractivitynotes (
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
  accountnumber STRING,
  additionalfields STRING,
  issmartnotes STRING,
  poolid INT64,
  notetypeid INT64,
  smartauditfields STRING,
  weightage STRING,
  organizationgroupid STRING
)
PARTITION BY DATE(createddate)
OPTIONS (
  description='Migrated from shc_gold.tbluseractivitynotes'
);
