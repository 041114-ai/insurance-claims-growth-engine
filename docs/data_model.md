# 数据模型说明

## 核心数据源

### 1. 用户数据 (user_data.csv)

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| user_id | int | 用户唯一标识 |
| age | int | 用户年龄 |
| gender | string | 用户性别 |
| city | string | 用户所在城市 |
| registration_date | date | 注册日期 |
| loyalty_level | string | 忠诚度等级 |
| nps_score | int | NPS评分 |

### 2. 保单数据 (policy_data.csv)

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| policy_id | string | 保单唯一标识 |
| user_id | int | 用户唯一标识 |
| policy_type | string | 保单类型 |
| premium | float | 保费金额 |
| purchase_date | date | 购买日期 |
| expiry_date | date | 到期日期 |
| status | string | 保单状态 |

### 3. 理赔数据 (claims_data.csv)

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| claim_id | string | 理赔唯一标识 |
| user_id | int | 用户唯一标识 |
| claim_date | date | 理赔日期 |
| claim_amount | float | 理赔金额 |
| claim_status | string | 理赔状态 |
| claim_type | string | 理赔类型 |
| processing_time | int | 处理时长(天) |

## 衍生数据

### 1. 处理后用户数据 (processed_user_data.csv)

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| user_id | int | 用户唯一标识 |
| age | int | 用户年龄 |
| gender | string | 用户性别 |
| city | string | 用户所在城市 |
| registration_date | date | 注册日期 |
| loyalty_level | string | 忠诚度等级 |
| nps_score | int | NPS评分 |
| claim_count | int | 理赔次数 |
| total_claim_amount | float | 总理赔金额 |
| avg_claim_amount | float | 平均理赔金额 |
| avg_processing_time | float | 平均处理时长 |
| first_claim_date | date | 首次理赔日期 |
| last_claim_date | date | 最近理赔日期 |
| policy_count | int | 保单数量 |
| total_premium | float | 总保费 |
| avg_premium | float | 平均保费 |
| first_policy_date | date | 首份保单日期 |
| days_since_registration | int | 注册天数 |
| days_since_last_claim | int | 距最近理赔天数 |
| claim_frequency | float | 理赔频率(次/年) |
| claim_severity | float | 理赔严重程度 |

## 数据处理流程

1. **数据加载**：从CSV文件加载原始数据
2. **数据清洗**：处理缺失值、异常值
3. **特征工程**：生成衍生特征
4. **数据集成**：合并多源数据
5. **数据存储**：保存处理后的数据

## 数据质量要求

- 数据完整性：关键字段无缺失
- 数据一致性：用户ID、保单ID等唯一标识一致
- 数据准确性：金额、日期等数值准确
- 数据时效性：定期更新数据

## 数据更新频率

建议每周更新一次数据，确保分析结果的及时性。
