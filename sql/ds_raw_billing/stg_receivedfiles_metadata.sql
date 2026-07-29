CREATE SCHEMA IF NOT EXISTS `${DS_RAW_BILLING}`;
CREATE TABLE IF NOT EXISTS `${DS_RAW_BILLING}`.stg_receivedfiles_metadata (
  filename STRING,
  filesize STRING,
  createddate DATETIME,
  createdby STRING,
  organizationgroupid STRING
)
PARTITION BY DATE(createddate)
OPTIONS (
  description='Migrated from shc_incomingphysician.stg_receivedfiles_metadata'
);
