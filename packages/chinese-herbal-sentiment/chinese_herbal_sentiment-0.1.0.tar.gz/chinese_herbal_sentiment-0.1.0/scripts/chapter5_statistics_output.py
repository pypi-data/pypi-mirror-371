#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
第五章数学统计结论输出脚本
基于论文中的统计分析结果，输出所有数学统计结论
"""

import warnings
warnings.filterwarnings('ignore')

class Chapter5StatisticsOutput:
    """第五章统计结果输出类"""
    
    def __init__(self):
        """初始化统计数据"""
        self.setup_data()
    
    def setup_data(self):
        """设置论文中的统计数据"""
        # 样本基础信息
        self.sample_info = {
            'total_comments': 212000,  # 有效评论数
            'total_original': 235000,  # 原始评论数
            'platforms': {
                '淘宝': {'count': 85000, 'percentage': 40.1},
                '京东': {'count': 68000, 'percentage': 32.1},
                '天猫': {'count': 42000, 'percentage': 19.8},
                '其他': {'count': 17000, 'percentage': 8.0}
            },
            'enterprise_scale': {
                '大型企业': {'count': 63600, 'percentage': 30.0},
                '中型企业': {'count': 84800, 'percentage': 40.0},
                '小型企业': {'count': 42400, 'percentage': 20.0},
                '个体经营者': {'count': 21200, 'percentage': 10.0}
            },
            'product_types': {
                '原药材': {'count': 95400, 'percentage': 45.0},
                '饮片': {'count': 74200, 'percentage': 35.0},
                '配方颗粒': {'count': 31800, 'percentage': 15.0},
                '其他加工产品': {'count': 10600, 'percentage': 5.0}
            },
            'ratings': {
                '5星': {'count': 131000, 'percentage': 61.8},
                '4星': {'count': 30000, 'percentage': 14.0},
                '3星': {'count': 24000, 'percentage': 11.5},
                '2星': {'count': 16000, 'percentage': 7.5},
                '1星': {'count': 11000, 'percentage': 5.2}
            }
        }
        
        # 描述性统计数据
        self.descriptive_stats = {
            '服务质量': {'mean': 7.85, 'std': 1.42, 'min': 2.1, 'max': 9.8},
            '原料质量': {'mean': 8.12, 'std': 1.35, 'min': 2.5, 'max': 9.9},
            '加工工艺': {'mean': 7.68, 'std': 1.48, 'min': 2.2, 'max': 9.7},
            '物流配送': {'mean': 7.95, 'std': 1.39, 'min': 2.3, 'max': 9.8},
            '售后服务': {'mean': 7.52, 'std': 1.56, 'min': 1.8, 'max': 9.6},
            '信息透明度': {'mean': 7.35, 'std': 1.62, 'min': 1.5, 'max': 9.5}
        }
        
        # 各维度详细指标
        self.dimension_stats = {
            '上游（原料）维度': {
                '原料质量评分': {'mean': 8.25, 'std': 1.32},
                '原料规格一致性': {'mean': 7.95, 'std': 1.38},
                '原材料可追溯性评分': {'mean': 7.15, 'std': 1.75}
            },
            '中游（加工）维度': {
                '工艺技术评价': {'mean': 7.82, 'std': 1.45},
                '产品一致性': {'mean': 7.65, 'std': 1.50},
                '质检标准符合度': {'mean': 7.58, 'std': 1.52}
            },
            '下游（销售与物流）维度': {
                '交货速度': {'mean': 8.15, 'std': 1.35},
                '包装评分': {'mean': 8.05, 'std': 1.36},
                '订单准确性': {'mean': 8.25, 'std': 1.32},
                '售后服务质量': {'mean': 7.52, 'std': 1.56},
                '信息透明度': {'mean': 7.35, 'std': 1.62}
            }
        }
        
        # 不同企业规模的服务质量得分
        self.enterprise_quality = {
            '大型企业': {'mean': 8.15, 'std': 1.32},
            '中型企业': {'mean': 7.85, 'std': 1.42},
            '小型企业': {'mean': 7.65, 'std': 1.50},
            '个体经营者': {'mean': 7.45, 'std': 1.58}
        }
        
        # 不同产品类型的服务质量得分
        self.product_quality = {
            '原药材': {'mean': 7.75, 'std': 1.45},
            '饮片': {'mean': 7.95, 'std': 1.38},
            '配方颗粒': {'mean': 8.05, 'std': 1.36},
            '其他加工产品': {'mean': 7.65, 'std': 1.50}
        }
        
        # 相关性分析结果
        self.correlations = {
            '自变量与因变量': {
                '原料质量与服务质量': {'r': 0.78, 'p': '<0.001'},
                '加工工艺与服务质量': {'r': 0.72, 'p': '<0.001'},
                '物流配送与服务质量': {'r': 0.75, 'p': '<0.001'},
                '售后服务与服务质量': {'r': 0.68, 'p': '<0.001'},
                '信息透明度与服务质量': {'r': 0.65, 'p': '<0.001'}
            },
            '自变量之间': {
                '原料质量与加工工艺': {'r': 0.65, 'p': '<0.001'},
                '原料质量与物流配送': {'r': 0.45, 'p': '<0.001'},
                '加工工艺与物流配送': {'r': 0.48, 'p': '<0.001'},
                '物流配送与售后服务': {'r': 0.62, 'p': '<0.001'},
                '售后服务与信息透明度': {'r': 0.58, 'p': '<0.001'}
            },
            '企业规模相关': {
                '企业规模与服务质量': {'r': 0.42, 'p': '<0.001'},
                '企业规模与原料质量': {'r': 0.38, 'p': '<0.001'},
                '企业规模与加工工艺': {'r': 0.45, 'p': '<0.001'},
                '企业规模与物流配送': {'r': 0.48, 'p': '<0.001'},
                '企业规模与售后服务': {'r': 0.35, 'p': '<0.001'},
                '企业规模与信息透明度': {'r': 0.40, 'p': '<0.001'}
            }
        }
        
        # 回归分析结果
        self.regression_results = {
            '模型拟合度': {
                'R²': 0.782,
                'R²_adj': 0.778,
                'F_statistic': 2285.43,
                'F_df': (7, 44512),
                'F_p': '<0.001',
                'AIC': -12567.2,
                'BIC': -12498.6
            },
            '回归系数': {
                '截距': {'coef': 0.128, 'se': 0.034, 't': 3.76, 'p': '<0.001', 'vif': None},
                '原料质量': {'coef': 0.352, 'se': 0.022, 't': 16.00, 'p': '<0.001', 'vif': 1.34},
                '加工工艺': {'coef': 0.285, 'se': 0.023, 't': 12.39, 'p': '<0.001', 'vif': 1.28},
                '物流配送': {'coef': 0.312, 'se': 0.021, 't': 14.86, 'p': '<0.001', 'vif': 1.15},
                '售后服务': {'coef': 0.245, 'se': 0.024, 't': 10.21, 'p': '<0.001', 'vif': 1.42},
                '信息透明度': {'coef': 0.218, 'se': 0.025, 't': 8.72, 'p': '<0.001', 'vif': 1.38},
                '产品类型': {'coef': 0.067, 'se': 0.026, 't': 2.58, 'p': '0.010', 'vif': 1.08},
                '平台类型': {'coef': 0.021, 'se': 0.018, 't': 1.17, 'p': '0.242', 'vif': 1.05}
            },
            '模型诊断': {
                'Shapiro-Wilk': {'W': 0.998, 'p': 0.112, '结论': '残差服从正态分布'},
                'Breusch-Pagan': {'chi2': 12.45, 'p': 0.085, '结论': '同方差假设成立'},
                'Durbin-Watson': {'DW': 2.02, '结论': '无序列相关'},
                'VIF': '均小于2，不存在严重多重共线性问题'
            }
        }
        
        # 调节效应分析结果
        self.moderation_effects = {
            '企业规模×原料质量': {'coef': 0.125, 't': 5.45, 'p': '<0.001', '效应': '显著正向调节'},
            '企业规模×加工工艺': {'coef': 0.142, 't': 6.25, 'p': '<0.001', '效应': '显著正向调节'},
            '企业规模×物流配送': {'coef': 0.158, 't': 6.95, 'p': '<0.001', '效应': '显著正向调节'},
            '企业规模×售后服务': {'coef': 0.085, 't': 3.75, 'p': '<0.01', '效应': '显著正向调节'},
            '企业规模×信息透明度': {'coef': 0.102, 't': 4.45, 'p': '<0.001', '效应': '显著正向调节'}
        }
    
    def print_sample_overview(self):
        """输出样本概况"""
        print("=" * 80)
        print("第五章 数学统计结论 - 样本概况")
        print("=" * 80)
        
        print(f"\n1. 样本基础信息")
        print(f"   总样本量：{self.sample_info['total_comments']:,}条有效评论")
        print(f"   原始数据：{self.sample_info['total_original']:,}条评论")
        print(f"   数据清洗率：{((self.sample_info['total_original'] - self.sample_info['total_comments']) / self.sample_info['total_original'] * 100):.1f}%")
        
        print(f"\n2. 平台分布")
        for platform, data in self.sample_info['platforms'].items():
            print(f"   {platform}：{data['count']:,}条 ({data['percentage']:.1f}%)")
        
        print(f"\n3. 企业规模分布")
        for scale, data in self.sample_info['enterprise_scale'].items():
            print(f"   {scale}：{data['count']:,}条 ({data['percentage']:.1f}%)")
        
        print(f"\n4. 产品类型分布")
        for product, data in self.sample_info['product_types'].items():
            print(f"   {product}：{data['count']:,}条 ({data['percentage']:.1f}%)")
        
        print(f"\n5. 评分分布")
        positive_count = self.sample_info['ratings']['5星']['count'] + self.sample_info['ratings']['4星']['count']
        positive_rate = (positive_count / self.sample_info['total_comments']) * 100
        for rating, data in self.sample_info['ratings'].items():
            print(f"   {rating}：{data['count']:,}条 ({data['percentage']:.1f}%)")
        print(f"   正面评价（4-5星）：{positive_count:,}条 ({positive_rate:.1f}%)")
    
    def print_descriptive_statistics(self):
        """输出描述性统计"""
        print("\n" + "=" * 80)
        print("描述性统计分析")
        print("=" * 80)
        
        print("\n1. 主要变量描述性统计")
        print("-" * 60)
        print(f"{'变量':<12} {'均值':<8} {'标准差':<8} {'最小值':<8} {'最大值':<8}")
        print("-" * 60)
        
        for var, stats in self.descriptive_stats.items():
            print(f"{var:<12} {stats['mean']:<8.2f} {stats['std']:<8.2f} {stats['min']:<8.1f} {stats['max']:<8.1f}")
        
        print("\n2. 各维度详细指标统计")
        for dimension, indicators in self.dimension_stats.items():
            print(f"\n{dimension}:")
            print("-" * 50)
            print(f"{'指标':<20} {'均值':<8} {'标准差':<8}")
            print("-" * 50)
            for indicator, stats in indicators.items():
                print(f"{indicator:<20} {stats['mean']:<8.2f} {stats['std']:<8.2f}")
        
        print("\n3. 不同企业规模的服务质量得分")
        print("-" * 40)
        print(f"{'企业规模':<12} {'均值':<8} {'标准差':<8}")
        print("-" * 40)
        for scale, stats in self.enterprise_quality.items():
            print(f"{scale:<12} {stats['mean']:<8.2f} {stats['std']:<8.2f}")
        
        print("\n4. 不同产品类型的服务质量得分")
        print("-" * 40)
        print(f"{'产品类型':<12} {'均值':<8} {'标准差':<8}")
        print("-" * 40)
        for product, stats in self.product_quality.items():
            print(f"{product:<12} {stats['mean']:<8.2f} {stats['std']:<8.2f}")
    
    def print_correlation_analysis(self):
        """输出相关性分析"""
        print("\n" + "=" * 80)
        print("相关性分析结果")
        print("=" * 80)
        
        for category, correlations in self.correlations.items():
            print(f"\n{category}:")
            print("-" * 60)
            print(f"{'变量关系':<30} {'相关系数':<10} {'显著性':<10}")
            print("-" * 60)
            for relationship, data in correlations.items():
                print(f"{relationship:<30} {data['r']:<10.3f} {data['p']:<10}")
        
        print("\n相关性分析结论：")
        print("• 所有自变量与因变量之间均存在显著的正相关关系")
        print("• 原料质量与服务质量的相关性最强(r=0.78)")
        print("• 信息透明度与服务质量的相关性相对较弱(r=0.65)")
        print("• 自变量间相关系数均小于0.7，不存在严重多重共线性问题")
        print("• 企业规模与服务质量及各自变量均呈现正相关关系")
    
    def print_regression_analysis(self):
        """输出回归分析结果"""
        print("\n" + "=" * 80)
        print("多元线性回归分析结果")
        print("=" * 80)
        
        # 模型拟合优度
        print("\n1. 模型拟合优度")
        print("-" * 50)
        fit = self.regression_results['模型拟合度']
        print(f"R² = {fit['R²']:.3f}")
        print(f"调整R² = {fit['R²_adj']:.3f}")
        print(f"F统计量 = {fit['F_statistic']:.2f}, df{fit['F_df']}, p {fit['F_p']}")
        print(f"AIC = {fit['AIC']:.1f}, BIC = {fit['BIC']:.1f}")
        
        # 回归系数
        print("\n2. 回归系数表")
        print("-" * 80)
        print(f"{'变量':<12} {'系数':<8} {'标准误':<8} {'t值':<8} {'p值':<10} {'VIF':<6}")
        print("-" * 80)
        
        for var, data in self.regression_results['回归系数'].items():
            vif = data['vif'] if data['vif'] is not None else '-'
            print(f"{var:<12} {data['coef']:<8.3f} {data['se']:<8.3f} {data['t']:<8.2f} {data['p']:<10} {vif:<6}")
        
        # 回归方程
        print("\n3. 回归方程")
        print("-" * 50)
        coefs = self.regression_results['回归系数']
        equation = f"服务质量 = {coefs['截距']['coef']:.3f}"
        equation += f" + {coefs['原料质量']['coef']:.3f} × 原料质量"
        equation += f" + {coefs['加工工艺']['coef']:.3f} × 加工工艺"
        equation += f" + {coefs['物流配送']['coef']:.3f} × 物流配送"
        equation += f" + {coefs['售后服务']['coef']:.3f} × 售后服务"
        equation += f" + {coefs['信息透明度']['coef']:.3f} × 信息透明度 + ε"
        print(equation)
        
        # 模型诊断
        print("\n4. 模型诊断结果")
        print("-" * 50)
        diag = self.regression_results['模型诊断']
        print(f"Shapiro-Wilk正态性检验：W = {diag['Shapiro-Wilk']['W']:.3f}, p = {diag['Shapiro-Wilk']['p']:.3f}")
        print(f"结论：{diag['Shapiro-Wilk']['结论']}")
        print(f"\nBreusch-Pagan同方差检验：χ² = {diag['Breusch-Pagan']['chi2']:.2f}, p = {diag['Breusch-Pagan']['p']:.3f}")
        print(f"结论：{diag['Breusch-Pagan']['结论']}")
        print(f"\nDurbin-Watson独立性检验：DW = {diag['Durbin-Watson']['DW']:.2f}")
        print(f"结论：{diag['Durbin-Watson']['结论']}")
        print(f"\n方差膨胀因子（VIF）：{diag['VIF']}")
        
        # 结果解释
        print("\n5. 回归分析结论")
        print("-" * 50)
        print("• 模型整体显著有效（F检验 p < 0.001）")
        print("• 模型解释了78.2%的服务质量变异（R² = 0.782）")
        print("• 原料质量是最重要的影响因素（β = 0.352）")
        print("• 物流配送次之（β = 0.312），加工工艺第三（β = 0.285）")
        print("• 售后服务（β = 0.245）和信息透明度（β = 0.218）影响相对较弱")
        print("• 所有主要因素均在p < 0.001水平上显著")
    
    def print_moderation_analysis(self):
        """输出调节效应分析"""
        print("\n" + "=" * 80)
        print("调节效应分析结果")
        print("=" * 80)
        
        print("\n企业规模的调节效应：")
        print("-" * 60)
        print(f"{'交互项':<20} {'系数':<8} {'t值':<8} {'p值':<10} {'调节效应':<12}")
        print("-" * 60)
        
        for interaction, data in self.moderation_effects.items():
            print(f"{interaction:<20} {data['coef']:<8.3f} {data['t']:<8.2f} {data['p']:<10} {data['效应']:<12}")
        
        print("\n调节效应分析结论：")
        print("• 企业规模对所有因素与服务质量的关系均有显著调节作用")
        print("• 企业规模对物流配送的调节效应最强（β = 0.158）")
        print("• 企业规模对加工工艺的调节效应次之（β = 0.142）")
        print("• 大型企业在原料质量控制和物流配送方面表现更优")
        print("• 所有调节效应均为正向，表明企业规模越大，各因素对服务质量的正向影响越强")
    
    def print_hypothesis_testing(self):
        """输出假设检验结果"""
        print("\n" + "=" * 80)
        print("假设检验结果汇总")
        print("=" * 80)
        
        hypotheses = [
            ("H1", "原料质量对服务质量有显著正向影响", "支持", "β=0.352, p<0.001"),
            ("H2", "加工工艺对服务质量有显著正向影响", "支持", "β=0.285, p<0.001"),
            ("H3", "物流配送对服务质量有显著正向影响", "支持", "β=0.312, p<0.001"),
            ("H4", "售后服务对服务质量有显著正向影响", "支持", "β=0.245, p<0.001"),
            ("H5", "信息透明度对服务质量有显著正向影响", "支持", "β=0.218, p<0.001"),
            ("H6", "企业规模对各因素与服务质量关系有调节作用", "支持", "所有交互项均显著")
        ]
        
        print(f"{'假设':<6} {'假设内容':<30} {'结果':<8} {'统计证据':<20}")
        print("-" * 70)
        for h_id, content, result, evidence in hypotheses:
            print(f"{h_id:<6} {content:<30} {result:<8} {evidence:<20}")
        
        print(f"\n假设检验总结：")
        print(f"• 共提出6个主要假设，全部得到支持")
        print(f"• 所有影响因素均在p < 0.001水平上显著")
        print(f"• 企业规模的调节效应得到验证")
        print(f"• 研究假设得到充分的统计学证据支持")
    
    def generate_summary_report(self):
        """生成统计结论总结报告"""
        print("\n" + "=" * 80)
        print("第五章数学统计结论总结")
        print("=" * 80)
        
        print("\n📊 主要统计发现：")
        print("1. 样本特征：")
        print(f"   • 有效样本：{self.sample_info['total_comments']:,}条评论")
        print(f"   • 正面评价占比：75.8%（4-5星评价）")
        print(f"   • 服务质量平均得分：7.85分（满分10分）")
        
        print("\n2. 影响因素排序（按回归系数）：")
        factors = [
            ("原料质量", 0.352),
            ("物流配送", 0.312),
            ("加工工艺", 0.285),
            ("售后服务", 0.245),
            ("信息透明度", 0.218)
        ]
        for i, (factor, coef) in enumerate(factors, 1):
            print(f"   {i}. {factor}：β = {coef:.3f}")
        
        print("\n3. 模型性能：")
        print(f"   • 解释度：R² = {self.regression_results['模型拟合度']['R²']:.3f}")
        print(f"   • 模型显著性：F = {self.regression_results['模型拟合度']['F_statistic']:.2f}, p < 0.001")
        print(f"   • 所有假设均得到支持")
        
        print("\n4. 调节效应：")
        print("   • 企业规模对所有因素均有显著正向调节作用")
        print("   • 大型企业在各维度表现更优")
        
        print("\n5. 实践启示：")
        print("   • 优先关注原料质量管控（影响最大）")
        print("   • 重视物流配送体系建设")
        print("   • 完善加工工艺标准化")
        print("   • 提升售后服务水平")
        print("   • 增强信息透明度")
        
        print("\n" + "=" * 80)
        print("统计分析完成")
        print("=" * 80)
    
    def run_all_outputs(self):
        """运行所有统计输出"""
        self.print_sample_overview()
        self.print_descriptive_statistics()
        self.print_correlation_analysis()
        self.print_regression_analysis()
        self.print_moderation_analysis()
        self.print_hypothesis_testing()
        self.generate_summary_report()

def main():
    """主函数"""
    print("第五章数学统计结论输出程序")
    print("基于论文中的统计分析结果")
    print("作者：中药材电商评论分析系统")
    print("时间：2024年")
    
    # 创建统计输出对象
    stats_output = Chapter5StatisticsOutput()
    
    # 运行所有统计输出
    stats_output.run_all_outputs()

if __name__ == "__main__":
    main() 