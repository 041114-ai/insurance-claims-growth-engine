# 数据模型文档

## 1. 用户维度表 (dim_user)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| user_id | STRING | 用户ID |
| user_name | STRING | 用户姓名 |
| phone | STRING | 手机号 |
| id_card | STRING | 身份证号 |
| gender | STRING | 性别 |
| age | INT | 年龄 |
| city | STRING | 城市 |
| register_date | STRING | 注册日期 |
| channel | STRING | 注册渠道 |
| user_level | STRING | 用户等级 |

## 2. 理赔事实表 (fact_claim)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| claim_id | STRING | 理赔ID |
| claim_no | STRING | 理赔号 |
| user_id | STRING | 用户ID |
| policy_id | STRING | 保单ID |
| claim_type | STRING | 理赔类型 |
| claim_amount | DECIMAL | 理赔金额 |
| claim_date | STRING | 理赔日期 |
| report_date | STRING | 报案日期 |
| finish_date | STRING | 结案日期 |
| status | STRING | 理赔状态 |
| satisfaction_score | INT | 满意度评分 |
| is_fraud | INT | 是否欺诈 |
| is_complaint | INT | 是否投诉 |

## 3. 保单事实表 (fact_policy)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| policy_id | STRING | 保单ID |
| policy_no | STRING | 保单号 |
| user_id | STRING | 用户ID |
| product_id | STRING | 产品ID |
| product_name | STRING | 产品名称 |
| coverage_amount | DECIMAL | 保额 |
| premium | DECIMAL | 保费 |
| start_date | STRING | 生效日期 |
| end_date | STRING | 到期日期 |
| status | STRING | 保单状态 |

## 4. 用户分群结果表 (dws_user_segment)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| user_id | STRING | 用户ID |
| claim_amount_pct_rank | DECIMAL | 理赔金额分位 |
| premium_pct_rank | DECIMAL | 保费分位 |
| renewal_pct_rank | DECIMAL | 续保率分位 |
| segment | STRING | 用户分群 |
| segment_name | STRING | 分群名称 |
| strategy_type | STRING | 策略类型 |
| priority | INT | 优先级 |
| is_target | INT | 是否目标用户 |