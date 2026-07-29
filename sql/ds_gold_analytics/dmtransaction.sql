CREATE SCHEMA IF NOT EXISTS `${DS_GOLD_ANALYTICS}`;
CREATE TABLE IF NOT EXISTS `${DS_GOLD_ANALYTICS}`.dmtransaction (
  accountnumber STRING,
  invoicecreationperiod DATETIME,
  postingperiod DATETIME,
  insurancepaymentamount NUMERIC,
  selfpaymentamount NUMERIC,
  debitamount NUMERIC,
  refundamount NUMERIC,
  insuranceadjustmentamount NUMERIC,
  selfadjustmentamount NUMERIC,
  writeoffamount NUMERIC,
  credits NUMERIC,
  placementdate DATETIME,
  placementfinancialclass STRING,
  placementfacility STRING,
  specialtygroupnumber STRING,
  sequencenumber INT64,
  division STRING,
  organizationgroupid STRING,
  batch_id STRING
)
PARTITION BY DATE(invoicecreationperiod)
CLUSTER BY placementfinancialclass, accountnumber
OPTIONS (
  description='Migrated from shc_datamart.dmtransaction'
);
