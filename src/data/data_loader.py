import pandas as pd
import numpy as np
from pathlib import Path

class DataLoader:
    """数据加载和ETL管道"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.claims_data = None
        self.policies_data = None
        self.users_data = None
        self.processed_data = None
    
    def load_raw_data(self):
        """加载原始数据"""
        # 加载理赔数据
        claims_path = self.data_dir / 'claims_data.csv'
        if claims_path.exists():
            self.claims_data = pd.read_csv(claims_path)
        else:
            self.claims_data = self._generate_claims_data()
        
        # 加载保单数据
        policies_path = self.data_dir / 'policy_data.csv'
        if policies_path.exists():
            self.policies_data = pd.read_csv(policies_path)
        else:
            self.policies_data = self._generate_policies_data()
        
        # 加载用户数据
        users_path = self.data_dir / 'user_data.csv'
        if users_path.exists():
            self.users_data = pd.read_csv(users_path)
        else:
            self.users_data = self._generate_user_data()
    
    def _generate_claims_data(self):
        """生成模拟理赔数据"""
        np.random.seed(42)
        n_claims = 2700
        
        claims_data = pd.DataFrame({
            'claim_id': [f'CLM{i:06d}' for i in range(n_claims)],
            'user_id': np.random.randint(1, 1001, n_claims),
            'claim_date': pd.date_range('2024-01-01', periods=n_claims, freq='H'),
            'claim_amount': np.random.exponential(scale=5000, size=n_claims),
            'claim_type': np.random.choice(['医疗', '财产', '意外', '其他'], n_claims),
            'status': np.random.choice(['已结案', '处理中', '待审核'], n_claims, p=[0.7, 0.2, 0.1]),
            'processing_time': np.random.normal(7, 3, n_claims).clip(1, 30)
        })
        
        claims_path = self.data_dir / 'claims_data.csv'
        claims_data.to_csv(claims_path, index=False)
        
        return claims_data
    
    def _generate_policies_data(self):
        """生成模拟保单数据"""
        np.random.seed(42)
        n_policies = 3500
        
        policies_data = pd.DataFrame({
            'policy_id': [f'POL{i:06d}' for i in range(n_policies)],
            'user_id': np.random.randint(1, 1001, n_policies),
            'purchase_date': pd.date_range('2023-01-01', periods=n_policies, freq='D'),
            'expiry_date': pd.date_range('2024-01-01', periods=n_policies, freq='D'),
            'premium': np.random.exponential(scale=3500, size=n_policies),
            'coverage_amount': np.random.exponential(scale=100000, size=n_policies),
            'status': np.random.choice(['有效', '已失效', '已取消'], n_policies, p=[0.6, 0.3, 0.1])
        })
        
        policies_path = self.data_dir / 'policy_data.csv'
        policies_data.to_csv(policies_path, index=False)
        
        return policies_data
    
    def _generate_user_data(self):
        """生成模拟用户数据"""
        np.random.seed(42)
        n_users = 1000
        
        users_data = pd.DataFrame({
            'user_id': range(1, n_users + 1),
            'age': np.random.randint(18, 70, n_users),
            'gender': np.random.choice(['男', '女'], n_users),
            'city': np.random.choice(['北京', '上海', '广州', '深圳', '杭州'], n_users),
            'registration_date': pd.date_range('2022-01-01', periods=n_users, freq='D'),
            'membership_level': np.random.choice(['普通', '银卡', '金卡', '白金'], n_users, p=[0.4, 0.3, 0.2, 0.1])
        })
        
        users_path = self.data_dir / 'user_data.csv'
        users_data.to_csv(users_path, index=False)
        
        return users_data
    
    def create_etl_pipeline(self):
        """创建ETL管道"""
        # 加载原始数据
        self.load_raw_data()
        
        # 聚合理赔数据
        claims_agg = self.claims_data.groupby('user_id').agg({
            'claim_id': 'count',
            'claim_amount': 'sum',
            'processing_time': 'mean'
        }).reset_index()
        claims_agg.columns = ['user_id', 'claim_count', 'total_claim_amount', 'avg_processing_time']
        
        # 聚合保单数据
        policies_agg = self.policies_data.groupby('user_id').agg({
            'policy_id': 'count',
            'premium': 'sum',
            'coverage_amount': 'sum',
            'status': lambda x: (x == '有效').sum()
        }).reset_index()
        policies_agg.columns = ['user_id', 'policy_count', 'total_premium', 'total_coverage', 'active_policies']
        
        # 合并数据
        processed_data = self.users_data.merge(claims_agg, on='user_id', how='left')
        processed_data = processed_data.merge(policies_agg, on='user_id', how='left')
        
        # 填充缺失值
        processed_data = processed_data.fillna({
            'claim_count': 0,
            'total_claim_amount': 0,
            'avg_processing_time': 0,
            'policy_count': 0,
            'total_premium': 0,
            'total_coverage': 0,
            'active_policies': 0
        })
        
        # 计算衍生指标
        processed_data['avg_claim_amount'] = np.where(
            processed_data['claim_count'] > 0,
            processed_data['total_claim_amount'] / processed_data['claim_count'],
            0
        )
        
        processed_data['renewal_rate'] = np.where(
            processed_data['policy_count'] > 0,
            processed_data['active_policies'] / processed_data['policy_count'],
            0
        )
        
        processed_data['premium_per_policy'] = np.where(
            processed_data['policy_count'] > 0,
            processed_data['total_premium'] / processed_data['policy_count'],
            0
        )
        
        self.processed_data = processed_data
        
        # 保存处理后的数据
        output_path = self.data_dir / 'processed_user_data.csv'
        processed_data.to_csv(output_path, index=False)
        
        return processed_data