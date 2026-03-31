import pandas as pd
import numpy as np
from scipy import stats

class ABTest:
    """A/B测试框架"""
    
    def __init__(self, data):
        self.data = data.copy()
        self.test_results = None
    
    def randomize_users(self, test_size=0.5, seed=42):
        """随机分配用户到测试组和对照组"""
        np.random.seed(seed)
        
        # 确保test_group列存在
        if 'test_group' not in self.data.columns:
            self.data['test_group'] = None
        
        # 随机分配
        n_users = len(self.data)
        test_indices = np.random.choice(
            self.data.index,
            size=int(n_users * test_size),
            replace=False
        )
        
        self.data.loc[test_indices, 'test_group'] = 'treatment'
        self.data.loc[~self.data.index.isin(test_indices), 'test_group'] = 'control'
        
        return self.data
    
    def simulate_experiment(self, test_group_effect=0.15, seed=42):
        """模拟实验效果"""
        np.random.seed(seed)
        
        # 确保已随机化
        if 'test_group' not in self.data.columns or self.data['test_group'].isnull().any():
            self.randomize_users()
        
        # 模拟转化率（基于续保率）
        base_conversion_rate = self.data['renewal_rate'].mean()
        
        # 测试组提升效果
        self.data['converted'] = np.random.binomial(
            1,
            np.where(
                self.data['test_group'] == 'treatment',
                base_conversion_rate * (1 + test_group_effect),
                base_conversion_rate
            )
        )
        
        # 模拟收入
        self.data['revenue'] = np.where(
            self.data['converted'] == 1,
            self.data['total_premium'] * np.random.uniform(0.8, 1.2, len(self.data)),
            0
        )
        
        return self.data
    
    def analyze_results(self):
        """分析实验结果"""
        if 'converted' not in self.data.columns:
            self.simulate_experiment()
        
        # 分组统计
        group_stats = self.data.groupby('test_group').agg({
            'user_id': 'count',
            'converted': ['mean', 'sum', 'std'],
            'revenue': ['mean', 'sum']
        })
        
        # 计算转化率差异
        control_conv = group_stats.loc['control', ('converted', 'mean')]
        treatment_conv = group_stats.loc['treatment', ('converted', 'mean')]
        conversion_diff = treatment_conv - control_conv
        
        # 计算收入差异
        control_rev = group_stats.loc['control', ('revenue', 'mean')]
        treatment_rev = group_stats.loc['treatment', ('revenue', 'mean')]
        revenue_diff = treatment_rev - control_rev
        
        # 统计检验
        control_converted = self.data[self.data['test_group'] == 'control']['converted']
        treatment_converted = self.data[self.data['test_group'] == 'treatment']['converted']
        
        # Z检验
        n1 = len(control_converted)
        n2 = len(treatment_converted)
        p1 = control_converted.mean()
        p2 = treatment_converted.mean()
        
        pooled_p = (n1 * p1 + n2 * p2) / (n1 + n2)
        se = np.sqrt(pooled_p * (1 - pooled_p) * (1/n1 + 1/n2))
        z_score = (p2 - p1) / se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        # 计算置信区间
        ci_lower = (p2 - p1) - 1.96 * se
        ci_upper = (p2 - p1) + 1.96 * se
        conversion_ci = f'[{ci_lower:.4f}, {ci_upper:.4f}]'
        
        # 判断是否显著
        is_significant = p_value < 0.05
        
        analysis = {
            'group_stats': group_stats,
            'conversion_diff': conversion_diff,
            'conversion_ci': conversion_ci,
            'revenue_diff': revenue_diff,
            'p_value_conversion': p_value,
            'is_significant': is_significant
        }
        
        return analysis
    
    def generate_experiment_report(self, segment=None, test_group_effect=0.15):
        """生成实验报告"""
        # 选择数据
        if segment:
            experiment_data = self.data[self.data['combined_segment'] == segment].copy()
        else:
            experiment_data = self.data.copy()
        
        # 创建实验实例
        ab_test = ABTest(experiment_data)
        ab_test.randomize_users()
        ab_test.simulate_experiment(test_group_effect=test_group_effect)
        analysis = ab_test.analyze_results()
        
        # 生成报告
        report = {
            'segment': segment if segment else 'all_users',
            'test_group_effect': test_group_effect,
            'analysis': analysis
        }
        
        return report
    
    def calculate_sample_size(self, baseline_rate, min_detectable_effect, alpha=0.05, power=0.8):
        """计算所需样本量"""
        # Z分数
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        # 效应量
        p1 = baseline_rate
        p2 = baseline_rate * (1 + min_detectable_effect)
        
        # 样本量计算
        pooled_p = (p1 + p2) / 2
        n_per_group = (
            (z_alpha + z_beta) ** 2 * 2 * pooled_p * (1 - pooled_p)
        ) / ((p2 - p1) ** 2)
        
        return int(np.ceil(n_per_group))
    
    def check_srm(self, expected_ratio=0.5):
        """检查样本比例不平衡"""
        if 'test_group' not in self.data.columns:
            return None
        
        n_total = len(self.data)
        n_treatment = (self.data['test_group'] == 'treatment').sum()
        observed_ratio = n_treatment / n_total
        
        # 卡方检验
        expected_treatment = n_total * expected_ratio
        expected_control = n_total * (1 - expected_ratio)
        observed_treatment = n_treatment
        observed_control = n_total - n_treatment
        
        chi2, p_value = stats.chisquare(
            [observed_treatment, observed_control],
            f_exp=[expected_treatment, expected_control]
        )
        
        return {
            'observed_ratio': observed_ratio,
            'expected_ratio': expected_ratio,
            'chi2': chi2,
            'p_value': p_value,
            'is_significant': p_value < 0.05
        }