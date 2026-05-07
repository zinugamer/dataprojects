DROP TABLE IF EXISTS himaxx_bi.store_monthly_summary;

CREATE TABLE himaxx_bi.store_monthly_summary (
  store_number INT,
  store_type VARCHAR(20), -- 门店类型
  store_level VARCHAR(20), -- 门店层级
  store_name VARCHAR(50) PRIMARY KEY, -- 门店名称
  open_date DATE, -- 门店开业时间
  annual_bep DECIMAL(10,2), -- 年盈亏平衡点
  strategic_brand VARCHAR(20), -- 主推品牌
  annual_target_sales DECIMAL(15,2), -- 年目标销售额
  annual_actual_sales DECIMAL(15,2),  -- 年实际销售额
  yoy_annual_sales DECIMAL(15,2), -- 同期年销售额
  monthly_target_sales DECIMAL(15,2), -- 月目标销售额
  monthly_target_traffic INT, -- 月目标流量
  monthly_target_trans_num_ppl DECIMAL(15,2), -- 月目标交易人数
  monthly_target_cr DECIMAL(15,10), -- 月目标转化率
  monthly_target_atv DECIMAL(15,10), -- 月目标客单价
  monthly_actual_sales DECIMAL(15,2), -- 月实际销售额
  monthly_actual_traffic INT, -- 月实际流量
  monthly_actual_new_traffic INT, -- 月实际新客流量
  monthly_actual_cr DECIMAL(15,10), -- 月实际转化率
  monthly_actual_trans_num_ppl DECIMAL(15,2), -- 月实际交易人数
  monthly_actual_atv DECIMAL(15,10), -- 月实际客单价
  yoy_monthly_sales DECIMAL(15,4), -- 同期月销售额
  yoy_monthly_traffic INT, -- 同期月流量
  yoy_monthly_new_traffic INT, -- 同期月新客流量
  yoy_monthly_cr DECIMAL(15,10), -- 同期月转化率
  yoy_monthly_trans_num_ppl DECIMAL(15,2), -- 同期月交易人数
  yoy_monthly_atv DECIMAL(15,10), -- 同期月客单价
  yoy_monthly_sales_pct DECIMAL(15,10), -- 月销售额同比
  yoy_monthly_traffic_pct DECIMAL(15,10), -- 月流量同比
  yoy_monthly_cr_pct DECIMAL(15,10), -- 月转化率同比
  yoy_monthly_atv_pct DECIMAL(15,10) -- 月客单价同比

);

SELECT COUNT(store_name)
FROM himaxx_bi.store_monthly_summary
WHERE strategic_brand IS NOT NULL
ORDER BY store_number ASC
;
