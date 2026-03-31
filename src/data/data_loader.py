import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class DataLoader:
    """数据加载和预处理类"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_claims_data(self, filename='claims_data.csv'):
        """加载理赔数据"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        else:
            # 生成示例数据
            return self.generate_sample_claims_data()
    
    def load_policy_data(self, filename='policy_data.csv'):
        """加载保单数据"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        else:
            # 生成示例数据
            return self.generate_sample_policy_data()
    
    def load_user_data(self, filename='user_data.csv'):
        """加载用户数据"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        else:
            # 生成示例数据
            return self.generate_sample_user_data()
    
    def generate_sample_claims_data(self):
        """生成示例理赔数据"""
        np.random.seed(42)
        
        n_users = 1000
        user_ids = range(1, n_users + 1)
        
        # 生成理赔记录
        claims = []
        for user_id in user_ids:
            # 每个用户1-3次理赔
            n_claims = np.random.randint(1, 4)
            for i in range(n_claims):
                claim_date = datetime.now() - timedelta(days=np.random.randint(1, 365))
                claims.append({
                    'claim_id': f'CL{user_id:04d}{i+1}',
                    'user_id': user_id,
                    'claim_date': claim_date.strftime('%Y-%m-%d'),
                    'claim_amount': np.random.uniform(100, 5000),
                    'claim_status': np.random.choice(['已结案', '处理中', '已拒绝'], p=[0.8, 0.15, 0.05]),
                    'claim_type': np.random.choice(['医疗', '意外', '财产', '其他']),
                    'processing_time': np.random.randint(1, 15)
                })
        
        df = pd.DataFrame(claims)
        df.to_csv(os.path.join(self.data_dir, 'claims_data.csv'), index=False)
        return df
    
    def generate_sample_policy_data(self):
        """生成示例保单数据"""
        np.random.seed(42)
        
        n_users = 1000
        user_ids = range(1, n_users + 1)
        
        policies = []
        for user_id in user_ids:
            # 每个用户1-4份保单
            n_policies = np.random.randint(1, 5)
            for i in range(n_policies):
                purchase_date = datetime.now() - timedelta(days=np.random.randint(1, 730))
                expiry_date = purchase_date + timedelta(days=365)
                policies.append({
                    'policy_id': f'PL{user_id:04d}{i+1}',
                    'user_id': user_id,
                    'policy_type': np.random.choice(['重疾', '医疗', '意外', '寿险', '财产']),
                    'premium': np.random.uniform(500, 5000),
                    'purchase_date': purchase_date.strftime('%Y-%m-%d'),
                    'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                    'status': np.random.choice(['有效', '过期', '退保'], p=[0.7, 0.2, 0.1])
                })
        
        df = pd.DataFrame(policies)
        df.to_csv(os.path.join(self.data_dir, 'policy_data.csv'), index=False)
        return df
    
    def generate_sample_user_data(self):
        """生成示例用户数据"""
        np.random.seed(42)
        
        n_users = 1000
        user_ids = range(1, n_users + 1)
        
        users = []
        for user_id in user_ids:
            users.append({
                'user_id': user_id,
                'age': np.random.randint(18, 70),
                'gender': np.random.choice(['男', '女']),
                'city': np.random.choice(['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉']),
                'registration_date': (datetime.now() - timedelta(days=np.random.randint(1, 1095))).strftime('%Y-%m-%d'),
                'loyalty_level': np.random.choice(['新用户', '普通用户', '银卡', '金卡', '钻石'], p=[0.3, 0.4, 0.15, 0.1, 0.05]),
                'nps_score': np.random.randint(0, 11) if np.random.random() > 0.3 else None
            })
        
        df = pd.DataFrame(users)
        df.to_csv(os.path.join(self.data_dir, 'user_data.csv'), index=False)
        return df
    
    def preprocess_data(self):
        """预处理数据，生成分析所需的特征"""
        # 加载数据
        claims = self.load_claims_data()
        policies = self.load_policy_data()
        users = self.load_user_data()
        
        # 转换日期格式
        claims['claim_date'] = pd.to_datetime(claims['claim_date'])
        policies['purchase_date'] = pd.to_datetime(policies['purchase_date'])
        policies['expiry_date'] = pd.to_datetime(policies['expiry_date'])
        users['registration_date'] = pd.to_datetime(users['registration_date'])
        
        # 计算用户层面的特征
        user_claims = claims.groupby('user_id').agg({
            'claim_id': 'count',
            'claim_amount': ['sum', 'mean'],
            'processing_time': 'mean',
            'claim_date': ['min', 'max']
        }).reset_index()
        user_claims.columns = ['user_id', 'claim_count', 'total_claim_amount', 
                             'avg_claim_amount', 'avg_processing_time', 
                             'first_claim_date', 'last_claim_date']
        
        # 计算保单层面的特征
        user_policies = policies.groupby('user_id').agg({
            'policy_id': 'count',
            'premium': ['sum', 'mean'],
            'purchase_date': 'min'
        }).reset_index()
        user_policies.columns = ['user_id', 'policy_count', 'total_premium', 
                               'avg_premium', 'first_policy_date']
        
        # 合并数据
        merged = users.merge(user_claims, on='user_id', how='left')
        merged = merged.merge(user_policies, on='user_id', how='left')
        
        # 填充缺失值
        merged = merged.fillna({
            'claim_count': 0,
            'total_claim_amount': 0,
            'avg_claim_amount': 0,
            'avg_processing_time': 0,
            'policy_count': 0,
            'total_premium': 0,
            'avg_premium': 0
        })
        
        # 计算衍生特征
        merged['days_since_registration'] = (pd.Timestamp.now() - merged['registration_date']).dt.days
        merged['days_since_last_claim'] = (pd.Timestamp.now() - merged['last_claim_date']).dt.days.fillna(9999)
        merged['claim_frequency'] = merged['claim_count'] / (merged['days_since_registration'] / 365)
        merged['claim_severity'] = merged['total_claim_amount'] / merged['claim_count'].replace(0, 1)
        
        return merged
    
    def create_etl_pipeline(self):
        """创建ETL流水线"""
        # 这里可以实现更复杂的ETL逻辑
        # 包括数据清洗、特征工程、数据集成等
        processed_data = self.preprocess_data()
        
        # 保存处理后的数据
        processed_data.to_csv(os.path.join(self.data_dir, 'processed_user_data.csv'), index=False)
        
        return processed_data

if __name__ == '__main__':
    loader = DataLoader()
    data = loader.create_etl_pipeline()
    print("ETL完成，处理后的数据形状:", data.shape)
    print("数据字段:", list(data.columns))
