import pandas as pd
import numpy as np
from scipy import stats

class UserSegmentation:
    """用户分群模型"""
    
    def __init__(self, data):
        self.data = data.copy()
        self.segmented_data = None
    
    def create_value_segment(self):
        """基于价值维度进行分群"""
        # 计算分位数
        self.data['premium_pct_rank'] = self.data['total_premium'].rank(pct=True)
        self.data['claim_pct_rank'] = self.data['total_claim_amount'].rank(pct=True)
        
        # 价值分群
        self.data['value_segment'] = np.select([
            (self.data['premium_pct_rank'] >= 0.6) & (self.data['claim_pct_rank'] >= 0.6),
            (self.data['premium_pct_rank'] >= 0.6) & (self.data['claim_pct_rank'] < 0.6),
            (self.data['premium_pct_rank'] < 0.6) & (self.data['claim_pct_rank'] >= 0.6),
            (self.data['premium_pct_rank'] < 0.6) & (self.data['claim_pct_rank'] < 0.6)
        ], ['高价值', '高保费低理赔', '低保费高理赔', '低价值'], default='一般')
        
        return self.data
    
    def create_loyalty_segment(self):
        """基于忠诚度维度进行分群"""
        # 计算续保率分位数
        self.data['renewal_pct_rank'] = self.data['renewal_rate'].rank(pct=True)
        
        # 忠诚度分群
        self.data['loyalty_segment'] = np.select([
            self.data['renewal_pct_rank'] >= 0.6,
            self.data['renewal_pct_rank'] < 0.4,
            (self.data['renewal_pct_rank'] >= 0.4) & (self.data['renewal_pct_rank'] < 0.6)
        ], ['高忠诚', '低忠诚', '中忠诚'], default='中忠诚')
        
        return self.data
    
    def create_risk_segment(self):
        """基于风险维度进行分群"""
        # 计算风险指标
        self.data['claim_frequency_risk'] = np.where(
            self.data['claim_count'] > 3,
            '高风险',
            np.where(self.data['claim_count'] > 1, '中风险', '低风险')
        )
        
        self.data['churn_risk'] = np.where(
            self.data['renewal_rate'] < 0.3,
            '高流失风险',
            np.where(self.data['renewal_rate'] < 0.6, '中流失风险', '低流失风险')
        )
        
        return self.data
    
    def create_combined_segment(self):
        """创建综合分群"""
        # 先创建各个维度的分群
        self.create_value_segment()
        self.create_loyalty_segment()
        self.create_risk_segment()
        
        # 综合分群逻辑
        self.data['combined_segment'] = np.select([
            (self.data['value_segment'] == '高价值') & (self.data['loyalty_segment'] == '高忠诚'),
            (self.data['value_segment'] == '高价值') & (self.data['loyalty_segment'] != '高忠诚'),
            (self.data['value_segment'] != '高价值') & (self.data['loyalty_segment'] == '高忠诚'),
            (self.data['value_segment'] != '高价值') & (self.data['loyalty_segment'] != '高忠诚')
        ], [
            '高价值忠诚用户',
            '高价值流失风险',
            '低价值忠诚用户',
            '低价值流失风险'
        ], default='一般用户')
        
        self.segmented_data = self.data
        return self.data
    
    def get_segment_statistics(self):
        """获取分群统计信息"""
        if self.segmented_data is None:
            self.create_combined_segment()
        
        segment_stats = self.segmented_data.groupby('combined_segment').agg({
            'user_id': 'count',
            'total_premium': ['mean', 'sum'],
            'total_claim_amount': ['mean', 'sum'],
            'renewal_rate': 'mean',
            'claim_count': 'mean'
        }).round(2)
        
        return segment_stats
    
    def get_segment_recommendations(self):
        """获取分群策略建议"""
        recommendations = {
            '高价值忠诚用户': {
                'strategy': '专属服务 + 加保引导',
                'priority': 1,
                'expected_effect': '提高二开率1.5pp',
                'actions': [
                    '提供专属理赔顾问',
                    '优先处理理赔申请',
                    '推荐高价值附加险',
                    '提供续保优惠'
                ]
            },
            '高价值流失风险': {
                'strategy': '个性化挽回 + 续保优惠',
                'priority': 2,
                'expected_effect': '降低流失率2pp',
                'actions': [
                    '分析流失原因',
                    '提供个性化挽回方案',
                    '提供续保优惠',
                    '改善理赔体验'
                ]
            },
            '低价值忠诚用户': {
                'strategy': '培育计划 + 保额提升',
                'priority': 3,
                'expected_effect': '提升保费10%',
                'actions': [
                    '保险知识教育',
                    '推荐适合的保障产品',
                    '提供保额提升优惠',
                    '培养长期关系'
                ]
            },
            '低价值流失风险': {
                'strategy': '基础保障教育',
                'priority': 4,
                'expected_effect': '提高转化漏斗转化率',
                'actions': [
                    '基础保险知识普及',
                    '提供入门级产品',
                    '简化投保流程',
                    '降低准入门槛'
                ]
            }
        }
        
        return recommendations