CREATE SCHEMA IF NOT EXISTS `${DS_GOLD_ANALYTICS}`;
CREATE TABLE IF NOT EXISTS `${DS_GOLD_ANALYTICS}`.dmoutboundlaccashposting (
  accountnumber STRING,
  arbalance NUMERIC,
  servicearea STRING,
  patientname STRING,
  region STRING,
  payercode STRING,
  primaryplanbalance STRING,
  secondaryplanbalance STRING,
  tertiaryplanbalance STRING,
  organizationgroupid STRING,
  batchid STRING
)
CLUSTER BY payercode, servicearea
OPTIONS (
  description='Migrated from shc_datamart.dmoutboundlaccashposting'
);
