#!/usr/bin/env python3
"""
保险理赔增长运营分析体系主脚本
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# 导入模块
from src.data.data_loader import DataLoader
from src.analysis.user_segmentation import UserSegmentation
from src.experiment.ab_test import ABTest

def main():
    """主函数"""
    print("=== 保险理赔增长运营分析体系 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 数据加载与预处理
    print("\n1. 数据加载与预处理...")
    loader = DataLoader()
    data = loader.create_etl_pipeline()
    print(f"数据加载完成，共 {len(data)} 条用户记录")
    
    # 2. 用户分群分析
    print("\n2. 用户分群分析...")
    segmenter = UserSegmentation(data)
    segmented_data = segmenter.create_combined_segment()
    
    # 分析分群结果
    segment_analysis = segmenter.analyze_segments()
    print("\n分群分析结果:")
    print(segment_analysis)
    
    # 识别高潜力分群
    high_potential = segmenter.identify_high_potential_segments()
    print("\n高潜力分群:")
    print(high_potential)
    
    # 3. A/B测试分析
    print("\n3. A/B测试分析...")
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
    
    print("\n实验结果:")
    print(report['analysis']['group_stats'])
    print(f"转化率差异: {report['analysis']['conversion_diff']:.4f}")
    print(f"是否显著: {report['analysis']['is_significant']}")
    
    # 4. 生成报告
    print("\n4. 生成分析报告...")
    generate_report(segment_analysis, report)
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("分析完成！")

def generate_report(segment_analysis, experiment_report):
    """生成分析报告"""
    # 创建报告目录
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # 生成报告文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'reports/claims_growth_analysis_{timestamp}.txt'
    
    # 写入报告
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 保险理赔增长运营分析报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. 用户分群分析\n")
        f.write(segment_analysis.to_string())
        f.write("\n\n")
        
        f.write("## 2. A/B测试结果\n")
        f.write(experiment_report['analysis']['group_stats'].to_string())
        f.write("\n\n")
        
        f.write("## 3. 关键指标\n")
        f.write(f"转化率差异: {experiment_report['analysis']['conversion_diff']:.4f}\n")
        f.write(f"95% 置信区间: {experiment_report['analysis']['conversion_ci']}\n")
        f.write(f"收入差异: {experiment_report['analysis']['revenue_diff']:.2f}\n")
        f.write(f"转化率p值: {experiment_report['analysis']['p_value_conversion']:.4f}\n")
        f.write(f"是否显著: {experiment_report['analysis']['is_significant']}\n")
    
    print(f"报告已生成: {report_file}")

if __name__ == '__main__':
    main()
