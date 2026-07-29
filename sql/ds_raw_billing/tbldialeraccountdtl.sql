CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.tbldialeraccountdtl (
  dialeraccountrecordid INT64,
  poolid INT64,
  programcode STRING,
  account_id INT64,
  subaccount_id INT64,
  customerfirstname STRING,
  customerlastname STRING,
  clientaccountnumber STRING,
  statuscode INT64,
  agencyaccountnumber INT64,
  stateid INT64,
  agencycurrentbalance NUMERIC,
  timezoneid INT64,
  dateofdeliquency DATETIME,
  callbackdate DATETIME,
  daysoflastactivity DATETIME,
  createdby STRING,
  createddate DATETIME,
  updatedby STRING,
  updateddate DATETIME,
  customerprofileid INT64,
  priorityid INT64,
  colorid INT64,
  identifiertype INT64,
  identifier STRING,
  istxpush STRING
)
PARTITION BY DATE(createddate)
OPTIONS (
  description='Migrated from shc_incomingphysician.tbldialeraccountdtl'
);
