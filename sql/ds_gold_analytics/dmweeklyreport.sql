CREATE SCHEMA IF NOT EXISTS `${DS_GOLD_ANALYTICS}`;
CREATE TABLE IF NOT EXISTS `${DS_GOLD_ANALYTICS}`.dmweeklyreport (
  weekdate DATETIME,
  totalopenarvolume INT64,
  totalopenaramount INT64,
  touchedarvolume INT64,
  touchedosaramount INT64,
  untouchedarvolume INT64,
  untouchedosaramount INT64,
  weeklyrecallsvolume INT64,
  weeklyrecallsamount INT64,
  totalrecallsvolume INT64,
  totalrecallsamount INT64,
  newplacementvolume INT64,
  newplacementamount INT64,
  totalplacementvolume INT64,
  totalplacementamount INT64,
  adjustmentvolume INT64,
  adjustmentamount INT64,
  mtdadjustmentvolume INT64,
  mtdadjustmentamount INT64,
  weeklycollectionvolume INT64,
  weeklycollectionamount INT64,
  mtdcollectionvolume INT64,
  mtdcollectionamount INT64,
  totalcollectionvolume INT64,
  totalcollectionamount INT64,
  adjcollectionvolume INT64,
  adjcollectionamount INT64,
  iboproductivity STRING,
  cliftonproductivity STRING,
  iboavgdailyproductivity STRING,
  cliftonavgdailyproductivity STRING,
  ibofte NUMERIC,
  cliftonfte NUMERIC,
  cashtrending INT64,
  tag STRING,
  community STRING,
  organizationgroupid STRING,
  batch_id STRING
)
PARTITION BY DATE(weekdate)
CLUSTER BY tag, community
OPTIONS (
  description='Migrated from shc_datamart.dmweeklyreport'
);
