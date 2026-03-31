import pandas as pd
import numpy as np

# 1. 数据加载
claims = pd.read_csv('data/claims_data.csv', parse_dates=['claim_date'])
policies = pd.read_csv('data/policy_data.csv', parse_dates=['purchase_date', 'expiry_date'])
users = pd.read_csv('data/user_data.csv', parse_dates=['registration_date'])

# 2. 数据预处理
# 计算用户理赔频率和金额
user_claims = claims.groupby('user_id').agg({
    'claim_id': 'count',
    'claim_amount': 'sum',
    'processing_time': 'mean'
}).reset_index()
user_claims.columns = ['user_id', 'claim_count', 'total_claim_amount', 'avg_processing_time']

# 计算用户保费和保单情况
user_policies = policies.groupby('user_id').agg({
    'policy_id': 'count',
    'premium': 'sum',
    'status': lambda x: (x == '有效').sum()
}).reset_index()
user_policies.columns = ['user_id', 'policy_count', 'total_premium', 'active_policies']

# 合并数据
user_data = users.merge(user_claims, on='user_id', how='left')
user_data = user_data.merge(user_policies, on='user_id', how='left')

# 填充缺失值
user_data = user_data.fillna({
    'claim_count': 0,
    'total_claim_amount': 0,
    'avg_processing_time': 0,
    'policy_count': 0,
    'total_premium': 0,
    'active_policies': 0
})

# 3. 计算关键指标
# 续保率（假设为活跃保单数/总保单数）
user_data['renewal_rate'] = user_data['active_policies'] / user_data['policy_count'].replace(0, 1)

# 二次开发成功率（假设为有理赔且有多个保单的用户比例）
user_data['second_development_rate'] = np.where(
    (user_data['claim_count'] > 0) & (user_data['policy_count'] > 1),
    1, 0
)

# 4. 用户分群
# 计算分位值
user_data['claim_amount_pct_rank'] = user_data['total_claim_amount'].rank(pct=True)
user_data['premium_pct_rank'] = user_data['total_premium'].rank(pct=True)
user_data['claim_frequency_pct_rank'] = user_data['claim_count'].rank(pct=True)
user_data['renewal_pct_rank'] = user_data['renewal_rate'].rank(pct=True)

# 分层
user_data['segment'] = np.select([
    (user_data['claim_amount_pct_rank'] >= 0.6) & (user_data['premium_pct_rank'] >= 0.6),
    (user_data['claim_amount_pct_rank'] >= 0.6) & (user_data['premium_pct_rank'] < 0.6),
    (user_data['claim_amount_pct_rank'] < 0.6) & (user_data['renewal_pct_rank'] >= 0.6),
    (user_data['claim_amount_pct_rank'] < 0.6) & (user_data['renewal_pct_rank'] < 0.6)
], ['高价值忠诚用户', '高价值流失风险', '低价值忠诚用户', '低价值流失风险'], default='一般用户')

# 5. 策略效果分析
# 模拟策略效果
user_data['strategy_applied'] = np.where(
    user_data['segment'].isin(['高价值忠诚用户', '高价值流失风险']),
    1, 0
)

# 模拟策略效果（假设策略提高了续保率和二开率）
user_data['simulated_renewal_rate'] = user_data['renewal_rate'] + \
    np.where(user_data['strategy_applied'] == 1, 0.02, 0)

user_data['simulated_second_development_rate'] = user_data['second_development_rate'] + \
    np.where(user_data['strategy_applied'] == 1, 0.015, 0)

# 6. 结果分析
segment_analysis = user_data.groupby('segment').agg({
    'user_id': 'count',
    'total_premium': 'mean',
    'renewal_rate': 'mean',
    'second_development_rate': 'mean',
    'simulated_renewal_rate': 'mean',
    'simulated_second_development_rate': 'mean'
}).round(4)

# 计算策略效果
segment_analysis['renewal_improvement'] = segment_analysis['simulated_renewal_rate'] - segment_analysis['renewal_rate']
segment_analysis['second_development_improvement'] = segment_analysis['simulated_second_development_rate'] - segment_analysis['second_development_rate']

# 7. 输出结果
print("=== 分群分析结果 ===")
print(segment_analysis)

# 8. 保存结果
segment_analysis.to_csv('outputs/segment_analysis.csv')
user_data.to_csv('outputs/user_analysis.csv', index=False)

print("\n分析完成，结果已保存到outputs目录")
