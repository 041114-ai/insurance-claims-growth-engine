import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class UserSegmentation:
    """用户分群类"""
    
    def __init__(self, data):
        self.data = data
    
    def segment_by_claim_value(self):
        """基于理赔价值分群"""
        # 选择理赔相关特征
        claim_features = self.data[[
            'claim_count', 'total_claim_amount', 
            'claim_frequency', 'claim_severity'
        ]].fillna(0)
        
        # 标准化
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(claim_features)
        
        # K-means聚类
        kmeans = KMeans(n_clusters=2, random_state=42)
        clusters = kmeans.fit_predict(scaled_features)
        
        # 分析聚类结果
        cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
        
        # 确定高低价值
        high_value_cluster = np.argmax(cluster_centers[:, 1])  # 总理赔金额
        
        # 标记用户群
        self.data['claim_value_segment'] = np.where(
            clusters == high_value_cluster, '高频高额', '低频低额'
        )
        
        return self.data
    
    def segment_by_user_status(self):
        """基于用户状态分群"""
        # 选择用户状态相关特征
        status_features = self.data[[
            'days_since_last_claim', 'policy_count', 
            'total_premium', 'days_since_registration'
        ]].fillna(0)
        
        # 标准化
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(status_features)
        
        # K-means聚类
        kmeans = KMeans(n_clusters=2, random_state=42)
        clusters = kmeans.fit_predict(scaled_features)
        
        # 分析聚类结果
        cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
        
        # 确定深度忠诚和流失风险
        # 深度忠诚：保单数多、保费高、注册时间长、最近有理赔
        loyalty_score = (cluster_centers[:, 1] * 0.3 +  # policy_count
                         cluster_centers[:, 2] * 0.3 +  # total_premium
                         cluster_centers[:, 3] * 0.2 -  # days_since_registration
                         cluster_centers[:, 0] * 0.2)  # days_since_last_claim
        
        loyal_cluster = np.argmax(loyalty_score)
        
        # 标记用户群
        self.data['user_status_segment'] = np.where(
            clusters == loyal_cluster, '深度忠诚', '流失风险'
        )
        
        return self.data
    
    def create_combined_segment(self):
        """创建组合分群"""
        # 先进行两个维度的分群
        self.segment_by_claim_value()
        self.segment_by_user_status()
        
        # 创建组合分群
        segment_mapping = {
            ('高频高额', '深度忠诚'): '高价值忠诚用户',
            ('高频高额', '流失风险'): '高价值流失风险',
            ('低频低额', '深度忠诚'): '低价值忠诚用户',
            ('低频低额', '流失风险'): '低价值流失风险'
        }
        
        self.data['combined_segment'] = list(map(
            lambda x: segment_mapping.get(x, '其他'),
            zip(self.data['claim_value_segment'], self.data['user_status_segment'])
        ))
        
        return self.data
    
    def analyze_segments(self):
        """分析各分群特征"""
        if 'combined_segment' not in self.data.columns:
            self.create_combined_segment()
        
        # 分析各分群的关键指标
        segment_analysis = self.data.groupby('combined_segment').agg({
            'user_id': 'count',
            'claim_count': 'mean',
            'total_claim_amount': 'mean',
            'total_premium': 'mean',
            'policy_count': 'mean',
            'days_since_last_claim': 'mean',
            'claim_frequency': 'mean',
            'claim_severity': 'mean'
        }).round(2)
        
        # 计算占比
        segment_analysis['percentage'] = (
            segment_analysis['user_id'] / segment_analysis['user_id'].sum() * 100
        ).round(2)
        
        return segment_analysis
    
    def identify_high_potential_segments(self):
        """识别高潜力分群"""
        segment_analysis = self.analyze_segments()
        
        # 定义高潜力分群的标准
        # 1. 理赔频率适中
        # 2. 保费水平较高
        # 3. 有一定的忠诚度
        
        high_potential = segment_analysis[
            (segment_analysis['claim_frequency'] > 0.1) &
            (segment_analysis['total_premium'] > segment_analysis['total_premium'].median())
        ]
        
        return high_potential
    
    def generate_segment_report(self):
        """生成分群报告"""
        # 基础分群分析
        segment_analysis = self.analyze_segments()
        
        # 高潜力分群
        high_potential = self.identify_high_potential_segments()
        
        # 生成报告
        report = {
            'segment_analysis': segment_analysis,
            'high_potential_segments': high_potential,
            'total_users': len(self.data),
            'segment_distribution': self.data['combined_segment'].value_counts(normalize=True)
        }
        
        return report

if __name__ == '__main__':
    from src.data.data_loader import DataLoader
    
    # 加载数据
    loader = DataLoader()
    data = loader.create_etl_pipeline()
    
    # 分群分析
    segmenter = UserSegmentation(data)
    report = segmenter.generate_segment_report()
    
    print("=== 分群分析报告 ===")
    print("\n各分群统计:")
    print(report['segment_analysis'])
    
    print("\n高潜力分群:")
    print(report['high_potential_segments'])
    
    print("\n分群分布:")
    print(report['segment_distribution'])
