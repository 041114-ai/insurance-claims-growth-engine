import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 导入模块
from src.data.data_loader import DataLoader
from src.analysis.user_segmentation import UserSegmentation
from src.experiment.ab_test import ABTest

class Dashboard:
    """保险理赔增长运营分析看板"""
    
    def __init__(self):
        self.loader = DataLoader()
        self.data = None
        self.segmented_data = None
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        self.data = self.loader.create_etl_pipeline()
        
        # 进行用户分群
        segmenter = UserSegmentation(self.data)
        self.segmented_data = segmenter.create_combined_segment()
    
    def run(self):
        """运行看板"""
        st.set_page_config(
            page_title="保险理赔增长运营分析",
            page_icon="📊",
            layout="wide"
        )
        
        # 标题
        st.title("保险理赔增长运营分析体系")
        
        # 导航栏
        tab1, tab2, tab3, tab4 = st.tabs([
            "核心指标总览", 
            "用户分层分析", 
            "实验监控", 
            "策略矩阵"
        ])
        
        with tab1:
            self.show_core_metrics()
        
        with tab2:
            self.show_user_segmentation()
        
        with tab3:
            self.show_experiment_monitoring()
        
        with tab4:
            self.show_strategy_matrix()
    
    def show_core_metrics(self):
        """展示核心指标"""
        st.header("核心指标总览")
        
        # 计算核心指标
        total_users = len(self.data)
        total_claims = self.data['claim_count'].sum()
        total_premium = self.data['total_premium'].sum()
        avg_claim_amount = self.data['avg_claim_amount'].mean()
        
        # 布局
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总用户数", f"{total_users:,}")
        
        with col2:
            st.metric("总理赔次数", f"{total_claims:,}")
        
        with col3:
            st.metric("总保费", f"¥{total_premium:,.0f}")
        
        with col4:
            st.metric("平均理赔金额", f"¥{avg_claim_amount:,.0f}")
        
        # 保费趋势
        st.subheader("保费趋势")
        # 生成模拟的时间序列数据
        dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='M')
        monthly_premium = np.random.normal(1000000, 100000, len(dates))
        
        trend_data = pd.DataFrame({
            'date': dates,
            'premium': monthly_premium
        })
        
        fig = px.line(trend_data, x='date', y='premium', title='月度保费趋势')
        st.plotly_chart(fig, use_container_width=True)
    
    def show_user_segmentation(self):
        """展示用户分层分析"""
        st.header("用户分层分析")
        
        # 分群分布
        segment_distribution = self.segmented_data['combined_segment'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("分群分布")
            fig = px.pie(
                names=segment_distribution.index,
                values=segment_distribution.values,
                title="用户分群占比"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("分群特征")
            segment_analysis = self.segmented_data.groupby('combined_segment').agg({
                'user_id': 'count',
                'total_premium': 'mean',
                'claim_count': 'mean',
                'avg_claim_amount': 'mean'
            }).round(2)
            st.dataframe(segment_analysis)
        
        # 分群详情
        st.subheader("分群详情")
        selected_segment = st.selectbox(
            "选择分群",
            self.segmented_data['combined_segment'].unique()
        )
        
        segment_data = self.segmented_data[self.segmented_data['combined_segment'] == selected_segment]
        st.dataframe(segment_data[['user_id', 'age', 'gender', 'total_premium', 'claim_count']].head(20))
    
    def show_experiment_monitoring(self):
        """展示实验监控"""
        st.header("实验监控")
        
        # 运行A/B测试
        ab_test = ABTest(self.segmented_data)
        
        # 选择分群
        selected_segment = st.selectbox(
            "选择实验分群",
            ['all_users'] + list(self.segmented_data['combined_segment'].unique())
        )
        
        # 运行实验
        if selected_segment == 'all_users':
            report = ab_test.generate_experiment_report(test_group_effect=0.15)
        else:
            report = ab_test.generate_experiment_report(
                segment=selected_segment,
                test_group_effect=0.15
            )
        
        # 展示实验结果
        st.subheader("实验结果")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("分组统计:")
            st.dataframe(report['analysis']['group_stats'])
        
        with col2:
            st.write("实验指标:")
            metrics = {
                "转化率差异": f"{report['analysis']['conversion_diff']:.4f}",
                "95% 置信区间": f"{report['analysis']['conversion_ci']}",
                "收入差异": f"¥{report['analysis']['revenue_diff']:.2f}",
                "转化率p值": f"{report['analysis']['p_value_conversion']:.4f}",
                "是否显著": report['analysis']['is_significant']
            }
            for key, value in metrics.items():
                st.metric(key, value)
        
        # 可视化结果
        st.subheader("实验结果可视化")
        
        # 转化率对比
        conversion_data = pd.DataFrame({
            'group': ['控制组', '测试组'],
            'conversion_rate': [
                report['analysis']['group_stats'].loc['control', ('converted', 'mean')],
                report['analysis']['group_stats'].loc['treatment', ('converted', 'mean')]
            ]
        })
        
        fig = px.bar(conversion_data, x='group', y='conversion_rate', title='转化率对比')
        st.plotly_chart(fig, use_container_width=True)
    
    def show_strategy_matrix(self):
        """展示策略矩阵"""
        st.header("策略矩阵")
        
        # 策略建议
        strategy_matrix = pd.DataFrame({
            '分群': ['高价值忠诚用户', '高价值流失风险', '低价值忠诚用户', '低价值流失风险'],
            '策略建议': [
                '提供专属增值服务，引导加保',
                '个性化挽回方案，提高留存',
                '培养保险意识，逐步提升保额',
                '基础保障教育，引导转化'
            ],
            '预期效果': [
                '提高二开率1.5pp',
                '降低流失率2pp',
                '提升保费10%',
                '提高转化漏斗转化率'
            ],
            '优先级': [1, 2, 3, 4]
        })
        
        st.dataframe(strategy_matrix)
        
        # 策略效果预测
        st.subheader("策略效果预测")
        
        # 生成模拟数据
        strategies = ['专属服务', '挽回方案', '保险教育', '基础保障']
        expected_lift = [15, 10, 8, 5]
        confidence = [85, 75, 65, 60]
        
        strategy_data = pd.DataFrame({
            '策略': strategies,
            '预期提升(%)': expected_lift,
            '置信度(%)': confidence
        })
        
        fig = px.bar(
            strategy_data, 
            x='策略', 
            y='预期提升(%)',
            color='置信度(%)',
            title='策略预期效果'
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    dashboard = Dashboard()
    dashboard.run()
