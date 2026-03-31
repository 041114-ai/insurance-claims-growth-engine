import pandas as pd
import numpy as np
from scipy import stats
from math import sqrt

class ABTest:
    """A/B测试框架"""
    
    def __init__(self, data):
        self.data = data
    
    def calculate_sample_size(self, baseline_conversion, minimum_detectable_effect, 
                           significance_level=0.05, power=0.8):
        """计算所需样本量"""
        # 计算样本量
        z_alpha = stats.norm.ppf(1 - significance_level / 2)
        z_beta = stats.norm.ppf(power)
        
        p1 = baseline_conversion
        p2 = p1 * (1 + minimum_detectable_effect)
        p = (p1 + p2) / 2
        
        sample_size = (z_alpha * sqrt(2 * p * (1 - p)) + z_beta * sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2
        
        return int(np.ceil(sample_size))
    
    def randomize_users(self, segment=None, test_group_size=0.5):
        """随机分流用户"""
        # 如果指定了分群，只对该分群用户进行分流
        if segment:
            target_users = self.data[self.data['combined_segment'] == segment]
        else:
            target_users = self.data
        
        # 随机分流
        np.random.seed(42)
        test_group = np.random.binomial(1, test_group_size, size=len(target_users))
        
        # 标记分组
        target_users['test_group'] = test_group
        target_users['test_group'] = target_users['test_group'].map({0: 'control', 1: 'treatment'})
        
        # 合并回原数据
        self.data = self.data.merge(
            target_users[['user_id', 'test_group']],
            on='user_id',
            how='left'
        )
        
        # 未分配的用户标记为控制组
        self.data['test_group'] = self.data['test_group'].fillna('control')
        
        return self.data
    
    def generate_experiment_data(self, test_group_effect=0.15):
        """生成实验结果数据"""
        # 为测试组添加效果
        self.data['conversion_probability'] = 0.05  # 基础转化率
        self.data.loc[self.data['test_group'] == 'treatment', 'conversion_probability'] *= (1 + test_group_effect)
        
        # 生成转化结果
        np.random.seed(42)
        self.data['converted'] = np.random.binomial(1, self.data['conversion_probability'])
        
        # 生成保费数据
        self.data['premium'] = np.where(
            self.data['converted'],
            np.random.uniform(1000, 5000, size=len(self.data)),
            0
        )
        
        return self.data
    
    def analyze_results(self):
        """分析实验结果"""
        # 按组统计
        group_stats = self.data.groupby('test_group').agg({
            'user_id': 'count',
            'converted': ['sum', 'mean'],
            'premium': ['sum', 'mean']
        }).round(4)
        
        # 提取数据
        control_size = group_stats.loc['control', ('user_id', 'count')]
        treatment_size = group_stats.loc['treatment', ('user_id', 'count')]
        
        control_conversion = group_stats.loc['control', ('converted', 'mean')]
        treatment_conversion = group_stats.loc['treatment', ('converted', 'mean')]
        
        control_revenue = group_stats.loc['control', ('premium', 'sum')]
        treatment_revenue = group_stats.loc['treatment', ('premium', 'sum')]
        
        # 计算差异
        conversion_diff = treatment_conversion - control_conversion
        revenue_diff = treatment_revenue - control_revenue
        
        # 统计显著性检验
        # 转化率检验（卡方检验）
        control_converted = group_stats.loc['control', ('converted', 'sum')]
        treatment_converted = group_stats.loc['treatment', ('converted', 'sum')]
        
        contingency_table = [[control_converted, control_size - control_converted],
                           [treatment_converted, treatment_size - treatment_converted]]
        
        chi2, p_value_conversion, _, _ = stats.chi2_contingency(contingency_table)
        
        # 收入检验（t检验）
        control_premiums = self.data[self.data['test_group'] == 'control']['premium']
        treatment_premiums = self.data[self.data['test_group'] == 'treatment']['premium']
        
        t_stat, p_value_revenue = stats.ttest_ind(treatment_premiums, control_premiums)
        
        # 计算置信区间
        conversion_se = sqrt(
            control_conversion * (1 - control_conversion) / control_size +
            treatment_conversion * (1 - treatment_conversion) / treatment_size
        )
        
        conversion_ci = (conversion_diff - 1.96 * conversion_se, 
                        conversion_diff + 1.96 * conversion_se)
        
        # 计算效应量
        pooled_p = (control_converted + treatment_converted) / (control_size + treatment_size)
        effect_size = conversion_diff / sqrt(pooled_p * (1 - pooled_p))
        
        # 生成分析报告
        analysis = {
            'group_stats': group_stats,
            'conversion_diff': conversion_diff,
            'conversion_ci': conversion_ci,
            'revenue_diff': revenue_diff,
            'p_value_conversion': p_value_conversion,
            'p_value_revenue': p_value_revenue,
            'effect_size': effect_size,
            'is_significant': p_value_conversion < 0.05
        }
        
        return analysis
    
    def generate_experiment_report(self, segment=None, test_group_effect=0.15):
        """生成实验报告"""
        # 随机分流
        self.randomize_users(segment)
        
        # 生成实验数据
        self.generate_experiment_data(test_group_effect)
        
        # 分析结果
        analysis = self.analyze_results()
        
        # 生成报告
        report = {
            'segment': segment or 'all_users',
            'sample_size': len(self.data),
            'test_group_size': len(self.data[self.data['test_group'] == 'treatment']),
            'control_group_size': len(self.data[self.data['test_group'] == 'control']),
            'analysis': analysis
        }
        
        return report
    
    def run_power_analysis(self, baseline_conversion, effect_sizes):
        """功效分析"""
        results = []
        
        for effect in effect_sizes:
            sample_size = self.calculate_sample_size(baseline_conversion, effect)
            results.append({
                'effect_size': effect,
                'sample_size': sample_size
            })
        
        return pd.DataFrame(results)

if __name__ == '__main__':
    from src.data.data_loader import DataLoader
    from src.analysis.user_segmentation import UserSegmentation
    
    # 加载数据
    loader = DataLoader()
    data = loader.create_etl_pipeline()
    
    # 分群
    segmenter = UserSegmentation(data)
    segmented_data = segmenter.create_combined_segment()
    
    # 运行A/B测试
    ab_test = ABTest(segmented_data)
    
    # 计算样本量
    sample_size = ab_test.calculate_sample_size(
        baseline_conversion=0.05,
        minimum_detectable_effect=0.15
    )
    print(f"所需样本量: {sample_size}")
    
    # 运行实验
    report = ab_test.generate_experiment_report(
        segment='高价值忠诚用户',
        test_group_effect=0.15
    )
    
    print("\n=== 实验报告 ===")
    print(f"分群: {report['segment']}")
    print(f"总样本量: {report['sample_size']}")
    print(f"测试组样本量: {report['test_group_size']}")
    print(f"控制组样本量: {report['control_group_size']}")
    
    print("\n分组统计:")
    print(report['analysis']['group_stats'])
    
    print(f"\n转化率差异: {report['analysis']['conversion_diff']:.4f}")
    print(f"95% 置信区间: {report['analysis']['conversion_ci']}")
    print(f"收入差异: {report['analysis']['revenue_diff']:.2f}")
    print(f"转化率p值: {report['analysis']['p_value_conversion']:.4f}")
    print(f"收入p值: {report['analysis']['p_value_revenue']:.4f}")
    print(f"效应量: {report['analysis']['effect_size']:.4f}")
    print(f"是否显著: {report['analysis']['is_significant']}")
