CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.tblsubaccount_lacpb (
  subaccountid INT64,
  account_id INT64,
  program_id INT64,
  invoicenumber STRING,
  srcclientaccountnumber STRING,
  invoicecreationdate DATETIME,
  lkpaccounttype_id INT64,
  placementdate DATETIME,
  claimrundate DATETIME,
  followupdate DATETIME,
  unitnumber STRING,
  islocked INT64,
  activeflag STRING,
  createdby STRING,
  createddate DATETIME,
  updatedby STRING,
  updateddate DATETIME,
  indicatorstatus STRING,
  groupnumber INT64,
  originalinvoicenumber STRING,
  invoicecreationperiod STRING,
  untagtypeid INT64,
  invoicetype INT64,
  tfltype STRING,
  tfldate DATETIME,
  organizationgroupid STRING
)
PARTITION BY DATE(createddate)
OPTIONS (
  description='Migrated from shc_incomingphysician.tblsubaccount_lacpb'
);
