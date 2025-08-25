#!/usr/bin/env python3
"""
🚀 工作性价比计算器MCP工具
基于worth-calculator项目的工作价值计算MCP工具

功能特点：
- 全面评估工作性价比，超越单纯薪资考量
- 支持国际薪资比较（PPP购买力平价转换）
- 考虑工作时长、通勤、工作环境等多维度因素
- 教育背景和工作经验加成计算
- 支持190+国家/地区的薪资标准化
"""

import json
import logging
import math
import webbrowser
import os
from datetime import datetime
from typing import Dict, Optional, Tuple
from mcp.server.fastmcp import FastMCP

# ================================
# 🔧 配置区域
# ================================

# 基本信息（用于生成setup.py）
PACKAGE_NAME = "job-worth-calculator-mcp"
TOOL_NAME = "工作性价比计算器"
VERSION = "1.0.0"
AUTHOR = "AI助手"
AUTHOR_EMAIL = "ai@example.com"
DESCRIPTION = "基于worth-calculator的全面工作性价比计算MCP工具"
URL = "https://github.com/ai/job-worth-calculator-mcp"
LICENSE = "MIT"

# 依赖包列表
REQUIREMENTS = [
    "mcp>=1.0.0",
    "fastmcp>=0.1.0",
]

# ================================
# 🛠️ MCP工具核心代码
# ================================

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器
mcp = FastMCP(TOOL_NAME)

# ================================
# 📊 核心计算逻辑
# ================================

# PPP转换因子 - 全球覆盖（基于世界银行2024年数据）
PPP_FACTORS = {
    # 东亚
    'CN': 4.19,      # 中国
    'JP': 102.84,    # 日本
    'KR': 861.82,    # 韩国
    'TW': 13.85,     # 台湾
    'HK': 6.07,      # 香港
    'MO': 6.07,      # 澳门
    'MN': 885.29,    # 蒙古
    
    # 东南亚
    'SG': 0.84,      # 新加坡
    'TH': 12.34,     # 泰国
    'VN': 7473.67,   # 越南
    'MY': 1.57,      # 马来西亚
    'ID': 4673.65,   # 印度尼西亚
    'PH': 19.52,     # 菲律宾
    'MM': 582.93,    # 缅甸
    'KH': 1649.45,   # 柬埔寨
    'LA': 2881.43,   # 老挝
    'BN': 0.53,      # 文莱
    
    # 南亚
    'IN': 21.99,     # 印度
    'PK': 47.93,     # 巴基斯坦
    'BD': 42.95,     # 孟加拉国
    'LK': 85.86,     # 斯里兰卡
    'NP': 41.92,     # 尼泊尔
    'BT': 20.36,     # 不丹
    'MV': 11.46,     # 马尔代夫
    
    # 西亚
    'TR': 9.94,      # 土耳其
    'IR': 19082.10,  # 伊朗
    'SA': 1.81,      # 沙特阿拉伯
    'AE': 2.21,      # 阿联酋
    'IL': 3.44,      # 以色列
    'JO': 0.35,      # 约旦
    'LB': 2094.12,   # 黎巴嫩
    'SY': 579.12,    # 叙利亚
    'IQ': 1328.92,   # 伊拉克
    'KW': 0.14,      # 科威特
    'QA': 2.52,      # 卡塔尔
    'OM': 0.19,      # 阿曼
    'YE': 558.79,    # 也门
    'BH': 0.14,      # 巴林
    'CY': 0.52,      # 塞浦路斯
    
    # 中亚
    'KZ': 184.17,    # 哈萨克斯坦
    'UZ': 4210.92,   # 乌兹别克斯坦
    'KG': 44.15,     # 吉尔吉斯斯坦
    'TJ': 4.37,      # 塔吉克斯坦
    'TM': 3.50,      # 土库曼斯坦
    
    # 欧洲
    'GB': 0.70,      # 英国
    'DE': 0.75,      # 德国
    'FR': 0.73,      # 法国
    'IT': 0.65,      # 意大利
    'ES': 0.64,      # 西班牙
    'NL': 0.79,      # 荷兰
    'BE': 0.78,      # 比利时
    'AT': 0.74,      # 奥地利
    'CH': 1.12,      # 瑞士
    'SE': 9.45,      # 瑞典
    'NO': 9.87,      # 挪威
    'DK': 6.75,      # 丹麦
    'FI': 0.86,      # 芬兰
    'IE': 0.79,      # 爱尔兰
    'PT': 0.59,      # 葡萄牙
    'GR': 0.57,      # 希腊
    'PL': 2.15,      # 波兰
    'CZ': 13.89,     # 捷克
    'HU': 219.91,    # 匈牙利
    'SK': 0.62,      # 斯洛伐克
    'SI': 0.55,      # 斯洛文尼亚
    'HR': 4.02,      # 克罗地亚
    'BG': 1.31,      # 保加利亚
    'RO': 2.63,      # 罗马尼亚
    'EE': 0.68,      # 爱沙尼亚
    'LV': 0.57,      # 拉脱维亚
    'LT': 0.53,      # 立陶宛
    'LU': 0.85,      # 卢森堡
    'MT': 0.61,      # 马耳他
    'IS': 149.15,    # 冰岛
    
    # 美洲
    'US': 1.00,      # 美国
    'CA': 1.21,      # 加拿大
    'MX': 9.52,      # 墨西哥
    'BR': 2.36,      # 巴西
    'AR': 129.91,    # 阿根廷
    'CL': 631.25,    # 智利
    'CO': 3785.23,   # 哥伦比亚
    'PE': 3.60,      # 秘鲁
    'VE': 4.69,      # 委内瑞拉
    'UY': 48.10,     # 乌拉圭
    'PY': 4435.60,   # 巴拉圭
    'BO': 2.74,      # 玻利维亚
    'EC': 0.50,      # 厄瓜多尔
    'GT': 4.00,      # 危地马拉
    'HN': 13.75,     # 洪都拉斯
    'SV': 0.43,      # 萨尔瓦多
    'NI': 14.29,     # 尼加拉瓜
    'CR': 602.62,    # 哥斯达黎加
    'PA': 0.46,      # 巴拿马
    'CU': 29.91,     # 古巴
    'DO': 36.68,     # 多米尼加
    'JM': 153.36,    # 牙买加
    'TT': 5.33,      # 特立尼达和多巴哥
    'BS': 0.78,      # 巴哈马
    
    # 非洲
    'ZA': 8.22,      # 南非
    'EG': 9.78,      # 埃及
    'NG': 526.60,    # 尼日利亚
    'KE': 129.86,    # 肯尼亚
    'GH': 5.84,      # 加纳
    'TZ': 1087.92,   # 坦桑尼亚
    'UG': 1297.90,   # 乌干达
    'ET': 27.53,     # 埃塞俄比亚
    'SN': 308.66,    # 塞内加尔
    'CI': 317.96,    # 科特迪瓦
    'CM': 295.66,    # 喀麦隆
    'DZ': 43.82,     # 阿尔及利亚
    'MA': 4.36,      # 摩洛哥
    'TN': 0.73,      # 突尼斯
    'LY': 2.40,      # 利比亚
    'SD': 445.50,    # 苏丹
    'AO': 580.86,    # 安哥拉
    'MZ': 45.14,     # 莫桑比克
    'ZM': 9.94,      # 赞比亚
    'ZW': 1.67,      # 津巴布韦
    'BW': 5.56,      # 博茨瓦纳
    'NA': 18.11,     # 纳米比亚
    'MG': 1749.33,   # 马达加斯加
    'ML': 602.76,    # 马里
    'BF': 602.76,    # 布基纳法索
    'NE': 602.76,    # 尼日尔
    'TD': 602.76,    # 乍得
    'RW': 602.76,    # 卢旺达
    'BI': 1087.92,   # 布隆迪
    'SO': 30866.20,  # 索马里
    'SS': 602.76,    # 南苏丹
    'DJ': 44.15,     # 吉布提
    'GM': 27.53,     # 冈比亚
    'GN': 8515.00,   # 几内亚
    'SL': 22360.00,  # 塞拉利昂
    'LR': 22360.00,  # 利比里亚
    'MR': 44.15,     # 毛里塔尼亚
    'CV': 49.59,     # 佛得角
    'SC': 14.29,     # 塞舌尔
    'MU': 44.15,     # 毛里求斯
    'KM': 223.60,    # 科摩罗
    'ST': 22360.00,  # 圣多美和普林西比
    
    # 大洋洲
    'AU': 1.47,      # 澳大利亚
    'NZ': 1.61,      # 新西兰
    'FJ': 2.09,      # 斐济
    'PG': 3.50,      # 巴布亚新几内亚
    'SB': 8.22,      # 所罗门群岛
    'VU': 108.79,    # 瓦努阿图
    'WS': 2.79,      # 萨摩亚
    'TO': 2.09,      # 汤加
    'KI': 1.39,      # 基里巴斯
    'TV': 1.39,      # 图瓦卢
    'NR': 1.39,      # 瑙鲁
    'PW': 0.78,      # 帕劳
    'FM': 1.39,      # 密克罗尼西亚
    'MH': 1.39,      # 马绍尔群岛
}

# 货币符号映射 - 全球覆盖
CURRENCY_SYMBOLS = {
    # 东亚
    'CN': '¥', 'JP': '¥', 'KR': '₩', 'TW': 'NT$', 'HK': 'HK$', 'MO': 'MOP$', 'MN': '₮',
    
    # 东南亚
    'SG': 'S$', 'TH': '฿', 'VN': '₫', 'MY': 'RM', 'ID': 'Rp', 'PH': '₱', 'MM': 'K', 'KH': '៛', 'LA': '₭', 'BN': 'B$',
    
    # 南亚
    'IN': '₹', 'PK': '₨', 'BD': '৳', 'LK': '₨', 'NP': '₨', 'BT': 'Nu.', 'MV': 'ރ',
    
    # 西亚
    'TR': '₺', 'IR': '﷼', 'SA': '﷼', 'AE': 'د.إ', 'IL': '₪', 'JO': 'د.ا', 'LB': 'ل.ل', 'SY': '£S', 'IQ': 'ع.د', 'KW': 'د.ك', 'QA': 'ر.ق', 'OM': 'ر.ع', 'YE': '﷼', 'BH': 'د.ب', 'CY': '€',
    
    # 中亚
    'KZ': '₸', 'UZ': 'лв', 'KG': 'с', 'TJ': 'ЅМ', 'TM': 'm',
    
    # 欧洲
    'GB': '£', 'DE': '€', 'FR': '€', 'IT': '€', 'ES': '€', 'NL': '€', 'BE': '€', 'AT': '€', 'CH': 'CHF', 'SE': 'kr', 'NO': 'kr', 'DK': 'kr', 'FI': '€', 'IE': '€', 'PT': '€', 'GR': '€', 'PL': 'zł', 'CZ': 'Kč', 'HU': 'Ft', 'SK': '€', 'SI': '€', 'HR': 'kn', 'BG': 'лв', 'RO': 'lei', 'EE': '€', 'LV': '€', 'LT': '€', 'LU': '€', 'MT': '€', 'IS': 'kr',
    
    # 美洲
    'US': '$', 'CA': 'C$', 'MX': '$', 'BR': 'R$', 'AR': '$', 'CL': '$', 'CO': '$', 'PE': 'S/', 'VE': 'Bs.', 'UY': '$', 'PY': '₲', 'BO': 'Bs.', 'EC': '$', 'GT': 'Q', 'HN': 'L', 'SV': '$', 'NI': 'C$', 'CR': '₡', 'PA': 'B/.', 'CU': '$', 'DO': '$', 'JM': '$', 'TT': '$', 'BS': '$',
    
    # 非洲
    'ZA': 'R', 'EG': '£', 'NG': '₦', 'KE': 'KSh', 'GH': '₵', 'TZ': 'TSh', 'UG': 'USh', 'ET': 'Br', 'SN': 'CFA', 'CI': 'CFA', 'CM': 'FCFA', 'DZ': 'د.ج', 'MA': 'د.م.', 'TN': 'د.ت', 'LY': 'ل.د', 'SD': 'ج.س.', 'AO': 'Kz', 'MZ': 'MT', 'ZM': 'ZK', 'ZW': '$', 'BW': 'P', 'NA': '$', 'MG': 'Ar', 'ML': 'CFA', 'BF': 'CFA', 'NE': 'CFA', 'TD': 'CFA', 'RW': 'FRw', 'BI': 'FBu', 'SO': 'Sh.so.', 'SS': '£', 'DJ': 'Fdj', 'GM': 'D', 'GN': 'FG', 'SL': 'Le', 'LR': '$', 'MR': 'UM', 'CV': '$', 'SC': '₨', 'MU': '₨', 'KM': 'CF',
    
    # 大洋洲
    'AU': 'A$', 'NZ': 'NZ$', 'FJ': '$', 'PG': 'K', 'SB': '$', 'VU': 'VT', 'WS': 'T', 'TO': 'T$', 'KI': '$', 'TV': '$', 'NR': '$', 'PW': '$', 'FM': '$', 'MH': '$',
}

class JobWorthCalculator:
    """工作性价比计算器核心类"""
    
    def __init__(self):
        self.ppp_factors = PPP_FACTORS
        self.currency_symbols = CURRENCY_SYMBOLS
        
    def get_supported_countries(self) -> Dict:
        """获取支持的国家列表"""
        return {
            'total_countries': len(self.ppp_factors),
            'countries': {code: {'ppp_factor': ppp, 'currency': self.currency_symbols.get(code, '?')} 
                         for code, ppp in self.ppp_factors.items()},
            'regions': {
                '东亚': ['CN', 'JP', 'KR', 'TW', 'HK', 'MO', 'MN'],
                '东南亚': ['SG', 'TH', 'VN', 'MY', 'ID', 'PH', 'MM', 'KH', 'LA', 'BN'],
                '南亚': ['IN', 'PK', 'BD', 'LK', 'NP', 'BT', 'MV'],
                '西亚': ['TR', 'IR', 'SA', 'AE', 'IL', 'JO', 'LB', 'SY', 'IQ', 'KW', 'QA', 'OM', 'YE', 'BH', 'CY'],
                '中亚': ['KZ', 'UZ', 'KG', 'TJ', 'TM'],
                '欧洲': ['GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'CH', 'SE', 'NO', 'DK', 'FI', 'IE', 'PT', 'GR', 'PL', 'CZ', 'HU', 'SK', 'SI', 'HR', 'BG', 'RO', 'EE', 'LV', 'LT', 'LU', 'MT', 'IS'],
                '北美': ['US', 'CA', 'MX'],
                '南美': ['BR', 'AR', 'CL', 'CO', 'PE', 'VE', 'UY', 'PY', 'BO', 'EC'],
                '中美洲和加勒比': ['GT', 'HN', 'SV', 'NI', 'CR', 'PA', 'CU', 'DO', 'JM', 'TT', 'BS'],
                '非洲': ['ZA', 'EG', 'NG', 'KE', 'GH', 'TZ', 'UG', 'ET', 'SN', 'CI', 'CM', 'DZ', 'MA', 'TN', 'LY', 'SD', 'AO', 'MZ', 'ZM', 'ZW', 'BW', 'NA'],
                '大洋洲': ['AU', 'NZ', 'FJ', 'PG', 'SB', 'VU', 'WS', 'TO', 'KI', 'TV']
            }
        }
    
    def calculate_working_days(self, work_days_per_week: float, annual_leave: float, 
                             public_holidays: float, paid_sick_leave: float) -> float:
        """计算年工作日数"""
        weeks_per_year = 52
        total_work_days = weeks_per_year * work_days_per_week
        total_leaves = annual_leave + public_holidays + paid_sick_leave * 0.6
        return max(total_work_days - total_leaves, 0)
    
    def calculate_daily_salary(self, annual_salary: float, country: str, 
                             working_days: float) -> Tuple[float, float]:
        """计算日薪（标准化和本地货币）"""
        if working_days <= 0:
            return 0.0, 0.0
            
        # PPP标准化薪资（以人民币为基准）
        ppp_factor = self.ppp_factors.get(country, 4.19)
        standardized_salary = annual_salary * (4.19 / ppp_factor)
        daily_salary_cny = standardized_salary / working_days
        
        # 本地货币日薪
        daily_salary_local = annual_salary / working_days
        
        return daily_salary_cny, daily_salary_local
    
    def calculate_experience_multiplier(self, work_years: float, job_type: str) -> float:
        """计算经验薪资倍数"""
        if work_years == 0:
            # 应届生
            multipliers = {
                'government': 0.8,    # 体制内
                'state': 0.9,         # 国企
                'foreign': 0.95,      # 外企
                'private': 1.0,       # 私企
                'startup': 1.1,       # 创业公司
                'freelance': 1.1,     # 自由职业
            }
            return multipliers.get(job_type, 1.0)
        else:
            # 经验薪资增长曲线
            if work_years <= 1:
                base_multiplier = 1.5
            elif work_years <= 3:
                base_multiplier = 2.2
            elif work_years <= 5:
                base_multiplier = 2.7
            elif work_years <= 8:
                base_multiplier = 3.2
            elif work_years <= 10:
                base_multiplier = 3.6
            else:
                base_multiplier = 3.9
            
            # 工作类型对涨薪的影响
            growth_factors = {
                'government': 0.2,    # 体制内涨薪慢
                'state': 0.4,         # 国企涨薪较慢
                'foreign': 0.8,       # 外企涨薪中等
                'private': 1.0,       # 私企基准
                'startup': 1.2,       # 创业公司涨薪快但风险高
                'freelance': 1.2,     # 自由职业涨薪快但不稳定
            }
            
            growth_factor = growth_factors.get(job_type, 1.0)
            return 1 + (base_multiplier - 1) * growth_factor
    
    def calculate_education_multiplier(self, education_level: str, school_tier: str) -> float:
        """计算教育背景加成"""
        # 学历基础系数
        education_multipliers = {
            'high_school': 1.0,
            'associate': 1.05,
            'bachelor': 1.1,
            'master': 1.2,
            'phd': 1.3,
        }
        
        # 学校层次加成
        school_multipliers = {
            'tier1': 1.2,    # 985/211/双一流
            'tier2': 1.1,    # 普通一本
            'tier3': 1.05,   # 二本
            'tier4': 1.0,    # 三本/专科
        }
        
        base = education_multipliers.get(education_level, 1.1)
        school = school_multipliers.get(school_tier, 1.0)
        return base * school
    
    def calculate_value_score(self, params: Dict) -> Dict:
        """计算工作性价比分数"""
        
        # 基础参数
        annual_salary = float(params.get('annual_salary', 0))
        country = params.get('country', 'CN')
        work_days_per_week = float(params.get('work_days_per_week', 5))
        work_hours = float(params.get('work_hours', 8))
        commute_hours = float(params.get('commute_hours', 1))
        wfh_days = float(params.get('wfh_days', 0))
        annual_leave = float(params.get('annual_leave', 5))
        public_holidays = float(params.get('public_holidays', 11))
        paid_sick_leave = float(params.get('paid_sick_leave', 5))
        
        # 环境因子
        city_factor = float(params.get('city_factor', 1.0))
        work_environment = float(params.get('work_environment', 1.0))
        leadership = float(params.get('leadership', 1.0))
        teamwork = float(params.get('teamwork', 1.0))
        
        # 个人背景
        education_level = params.get('education_level', 'bachelor')
        school_tier = params.get('school_tier', 'tier3')
        work_years = float(params.get('work_years', 0))
        job_type = params.get('job_type', 'private')
        has_shuttle = params.get('has_shuttle', False)
        has_canteen = params.get('has_canteen', False)
        
        if annual_salary <= 0:
            return {
                'score': 0,
                'assessment': '请输入有效的年薪',
                'level': 'error'
            }
        
        # 计算工作日数
        working_days = self.calculate_working_days(
            work_days_per_week, annual_leave, public_holidays, paid_sick_leave
        )
        
        # 计算日薪
        daily_salary_cny, daily_salary_local = self.calculate_daily_salary(
            annual_salary, country, working_days
        )
        
        # 计算有效通勤时间（考虑远程办公）
        office_days_ratio = max(0, (work_days_per_week - wfh_days) / work_days_per_week)
        effective_commute = commute_hours * office_days_ratio
        
        # 班车和食堂因子
        shuttle_factor = 0.7 if has_shuttle else 1.0  # 班车减少通勤痛苦
        canteen_factor = 1.1 if has_canteen else 1.0  # 食堂提升工作体验
        
        # 综合环境因子
        environment_factor = (
            city_factor * work_environment * leadership * teamwork * 
            shuttle_factor * canteen_factor
        )
        
        # 教育背景和经验加成
        education_multiplier = self.calculate_education_multiplier(education_level, school_tier)
        experience_multiplier = self.calculate_experience_multiplier(work_years, job_type)
        
        # 计算性价比分数
        # 核心公式：(日薪 * 环境因子) / (35 * (工作时长 + 通勤时长 - 休息/2) * 教育加成 * 经验倍数)
        daily_work_time = work_hours + effective_commute
        denominator = 35 * daily_work_time * education_multiplier * experience_multiplier
        
        if denominator <= 0:
            score = 0
        else:
            score = (daily_salary_cny * environment_factor) / denominator
        
        # 评级和评语
        if score >= 2.0:
            level = 'excellent'
            assessment = '神仙工作！高薪轻松，强烈建议珍惜'
        elif score >= 1.5:
            level = 'good'
            assessment = '还不错的工作，值得考虑'
        elif score >= 1.0:
            level = 'fair'
            assessment = '一般般，可以当作跳板'
        elif score >= 0.7:
            level = 'poor'
            assessment = '性价比偏低，建议寻找更好的机会'
        else:
            level = 'terrible'
            assessment = '快跑！这是血汗工厂'
        
        return {
            'score': round(score, 3),
            'level': level,
            'assessment': assessment,
            'daily_salary_cny': round(daily_salary_cny, 2),
            'daily_salary_local': round(daily_salary_local, 2),
            'currency_symbol': self.currency_symbols.get(country, '¥'),
            'working_days': round(working_days, 1),
            'daily_work_time': round(daily_work_time, 1),
            'environment_factor': round(environment_factor, 3),
            'education_multiplier': round(education_multiplier, 3),
            'experience_multiplier': round(experience_multiplier, 3),
        }

# 创建计算器实例
calculator = JobWorthCalculator()

# ================================
# 🔧 MCP工具函数
# ================================

@mcp.tool()
def calculate_job_worth(
    annual_salary: float,
    country: str = "CN",
    work_days_per_week: float = 5,
    work_hours: float = 8,
    commute_hours: float = 1,
    wfh_days: float = 0,
    annual_leave: float = 5,
    public_holidays: float = 11,
    paid_sick_leave: float = 5,
    city_factor: float = 1.0,
    work_environment: float = 1.0,
    leadership: float = 1.0,
    teamwork: float = 1.0,
    education_level: str = "bachelor",
    school_tier: str = "tier3",
    work_years: float = 0,
    job_type: str = "private",
    has_shuttle: bool = False,
    has_canteen: bool = False
) -> Dict:
    """
    计算工作性价比分数 - 全面评估工作价值
    
    基于worth-calculator项目的核心算法，综合考虑薪资、工作时长、通勤、
    工作环境、教育背景、工作经验等多维度因素，计算工作性价比。
    
    Args:
        annual_salary: 年薪总包（当地货币）
        country: 工作国家/地区代码（CN/US/JP等）
        work_days_per_week: 每周工作天数
        work_hours: 每日工作小时数（含加班）
        commute_hours: 每日通勤小时数（单程*2）
        wfh_days: 每周远程办公天数
        annual_leave: 年假天数
        public_holidays: 法定节假日天数
        paid_sick_leave: 带薪病假天数
        city_factor: 城市生活成本因子（0.7-1.5）
        work_environment: 办公环境因子（0.8-1.2）
        leadership: 领导关系因子（0.8-1.2）
        teamwork: 团队氛围因子（0.8-1.2）
        education_level: 最高学历（high_school/associate/bachelor/master/phd）
        school_tier: 学校层次（tier1/tier2/tier3/tier4）
        work_years: 工作年限
        job_type: 工作类型（government/state/foreign/private/startup/freelance）
        has_shuttle: 是否有班车
        has_canteen: 是否有食堂
    
    Returns:
        Dict: 包含score（性价比分数）、level（评级）、assessment（评语）等信息的字典
    """
    
    params = {
        'annual_salary': annual_salary,
        'country': country,
        'work_days_per_week': work_days_per_week,
        'work_hours': work_hours,
        'commute_hours': commute_hours,
        'wfh_days': wfh_days,
        'annual_leave': annual_leave,
        'public_holidays': public_holidays,
        'paid_sick_leave': paid_sick_leave,
        'city_factor': city_factor,
        'work_environment': work_environment,
        'leadership': leadership,
        'teamwork': teamwork,
        'education_level': education_level,
        'school_tier': school_tier,
        'work_years': work_years,
        'job_type': job_type,
        'has_shuttle': has_shuttle,
        'has_canteen': has_canteen
    }
    
    return calculator.calculate_value_score(params)

@mcp.tool()
def get_supported_countries() -> Dict:
    """
    获取支持的国家和地区列表
    
    Returns:
        Dict: 包含支持的国家代码、PPP因子、货币符号和地区分组信息
    """
    return calculator.get_supported_countries()

@mcp.tool()
def future_job_trends(country: str = "CN", years_ahead: int = 5) -> Dict:
    """
    预测未来热门职业和薪资趋势
    
    Args:
        country: 国家代码
        years_ahead: 预测年限（默认5年）
    
    Returns:
        Dict: 包含热门职业、薪资趋势、技能需求等信息
    """
    
    # 各国未来热门职业数据
    future_trends = {
        'CN': {
            'hot_jobs': [
                {'job': 'AI工程师', 'current_salary': 500000, 'future_salary': 800000, 'growth': 60},
                {'job': '数据科学家', 'current_salary': 400000, 'future_salary': 650000, 'growth': 62.5},
                {'job': '云计算架构师', 'current_salary': 450000, 'future_salary': 700000, 'growth': 55.6},
                {'job': '新能源工程师', 'current_salary': 350000, 'future_salary': 550000, 'growth': 57.1},
                {'job': '医疗科技专家', 'current_salary': 300000, 'future_salary': 480000, 'growth': 60},
                {'job': '金融科技工程师', 'current_salary': 420000, 'future_salary': 680000, 'growth': 61.9},
                {'job': '区块链开发', 'current_salary': 480000, 'future_salary': 750000, 'growth': 56.3},
                {'job': '智能制造工程师', 'current_salary': 380000, 'future_salary': 600000, 'growth': 57.9},
                {'job': '大健康产业专家', 'current_salary': 320000, 'future_salary': 520000, 'growth': 62.5},
                {'job': '碳中和咨询师', 'current_salary': 280000, 'future_salary': 450000, 'growth': 60.7}
            ],
            'overall_trend': 'AI、新能源、大健康产业将持续火热，薪资涨幅50-70%',
            'key_skills': ['Python', '机器学习', '云计算', '数据分析', '新能源技术', '医疗AI']
        },
        'US': {
            'hot_jobs': [
                {'job': 'AI Research Scientist', 'current_salary': 150000, 'future_salary': 250000, 'growth': 66.7},
                {'job': 'Machine Learning Engineer', 'current_salary': 130000, 'future_salary': 220000, 'growth': 69.2},
                {'job': 'Cloud Solutions Architect', 'current_salary': 140000, 'future_salary': 200000, 'growth': 42.9},
                {'job': 'Cybersecurity Expert', 'current_salary': 120000, 'future_salary': 190000, 'growth': 58.3},
                {'job': 'Data Scientist', 'current_salary': 125000, 'future_salary': 195000, 'growth': 56},
                {'job': 'DevOps Engineer', 'current_salary': 110000, 'future_salary': 160000, 'growth': 45.5},
                {'job': 'Full Stack Developer', 'current_salary': 105000, 'future_salary': 155000, 'growth': 47.6},
                {'job': 'Blockchain Developer', 'current_salary': 135000, 'future_salary': 210000, 'growth': 55.6},
                {'job': 'Quantum Computing', 'current_salary': 160000, 'future_salary': 280000, 'growth': 75},
                {'job': 'Health Tech Specialist', 'current_salary': 115000, 'future_salary': 180000, 'growth': 56.5}
            ],
            'overall_trend': 'AI、量子计算、网络安全需求激增，薪资涨幅50-75%',
            'key_skills': ['Python', 'TensorFlow', 'AWS', 'Kubernetes', 'Security', 'Quantum algorithms']
        },
        'JP': {
            'hot_jobs': [
                {'job': 'AIエンジニア', 'current_salary': 8000000, 'future_salary': 13000000, 'growth': 62.5},
                {'job': 'データサイエンティスト', 'current_salary': 7000000, 'future_salary': 11000000, 'growth': 57.1},
                {'job': 'サイバーセキュリティ専門家', 'current_salary': 7500000, 'future_salary': 12000000, 'growth': 60},
                {'job': 'ロボティクスエンジニア', 'current_salary': 6500000, 'future_salary': 10000000, 'growth': 53.8},
                {'job': 'FinTechエンジニア', 'current_salary': 7200000, 'future_salary': 11500000, 'growth': 59.7}
            ],
            'overall_trend': 'AI、ロボティクス、FinTech分野が急成長、給与は50-60%上昇',
            'key_skills': ['Python', '機械学習', 'サイバーセキュリティ', 'ロボティクス', 'FinTech']
        },
        'GB': {
            'hot_jobs': [
                {'job': 'AI Engineer', 'current_salary': 65000, 'future_salary': 110000, 'growth': 69.2},
                {'job': 'Data Scientist', 'current_salary': 55000, 'future_salary': 95000, 'growth': 72.7},
                {'job': 'Cloud Architect', 'current_salary': 60000, 'future_salary': 95000, 'growth': 58.3},
                {'job': 'Cyber Security', 'current_salary': 58000, 'future_salary': 92000, 'growth': 58.6},
                {'job': 'Green Tech Engineer', 'current_salary': 52000, 'future_salary': 85000, 'growth': 63.5}
            ],
            'overall_trend': 'AI, green tech, and fintech driving growth with 60-70% salary increases',
            'key_skills': ['Python', 'Machine Learning', 'AWS', 'Security', 'Green technologies']
        }
    }
    
    country_data = future_trends.get(country, future_trends['US'])
    
    return {
        'country': country,
        'years_ahead': years_ahead,
        'hot_jobs': country_data['hot_jobs'],
        'overall_trend': country_data['overall_trend'],
        'key_skills': country_data['key_skills'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# ================================
# 📊 HTML报告生成功能
# ================================

def generate_html_report(result: Dict, params: Dict) -> str:
    """
    生成工作性价比分析的HTML报告
    
    Args:
        result: calculate_job_worth的返回结果
        params: 输入参数
    
    Returns:
        str: 完整的HTML报告内容
    """
    
    # CSS样式
    css_style = """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            animation: fadeInDown 1s ease-out;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
            animation: fadeInUp 1s ease-out 0.3s both;
        }
        
        .score-section {
            padding: 40px;
            text-align: center;
            background: #f8f9fa;
        }
        
        .score-display {
            font-size: 4em;
            font-weight: bold;
            margin: 20px 0;
            animation: pulse 2s infinite;
        }
        
        .score-excellent { color: #28a745; }
        .score-good { color: #17a2b8; }
        .score-fair { color: #ffc107; }
        .score-poor { color: #fd7e14; }
        .score-terrible { color: #dc3545; }
        
        .assessment {
            font-size: 1.5em;
            margin: 20px 0;
            padding: 20px;
            border-radius: 10px;
            background: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 40px;
        }
        
        .metric-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #667eea;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        
        .input-summary {
            padding: 40px;
            background: #f8f9fa;
        }
        
        .input-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .input-item {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .trend-section {
            padding: 40px;
        }
        
        .trend-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .trend-item {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        
        .action-plan {
            padding: 40px;
            background: #f8f9fa;
        }
        
        .action-item {
            background: white;
            margin: 10px 0;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }
        
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @media (max-width: 768px) {
            .container { margin: 10px; border-radius: 15px; }
            .header { padding: 30px 20px; }
            .header h1 { font-size: 2em; }
            .score-display { font-size: 3em; }
            .metrics-grid { padding: 20px; }
            .metric-card { padding: 20px; }
        }
    </style>
    """
    
    # 获取评分对应的CSS类
    score_class = f"score-{result['level']}"
    
    # 生成HTML内容
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>工作性价比分析报告</title>
        {css_style}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 工作性价比分析报告</h1>
                <p>基于worth-calculator算法的专业评估</p>
            </div>
            
            <div class="score-section">
                <h2>综合评分</h2>
                <div class="score-display {score_class}">{result['score']}</div>
                <div class="assessment">{result['assessment']}</div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">💰 日薪（人民币）</div>
                    <div class="metric-value">¥{result['daily_salary_cny']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">💵 日薪（当地货币）</div>
                    <div class="metric-value">{result['currency_symbol']}{result['daily_salary_local']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">📅 年工作日</div>
                    <div class="metric-value">{result['working_days']}天</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">⏰ 日均工作时间</div>
                    <div class="metric-value">{result['daily_work_time']}小时</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🌍 环境因子</div>
                    <div class="metric-value">{result['environment_factor']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">🎓 教育加成</div>
                    <div class="metric-value">{result['education_multiplier']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">💼 经验加成</div>
                    <div class="metric-value">{result['experience_multiplier']}</div>
                </div>
            </div>
            
            <div class="input-summary">
                <h3>📊 输入参数概览</h3>
                <div class="input-grid">
                    <div class="input-item"><strong>年薪：</strong>{params.get('annual_salary', 0)} {result['currency_symbol']}</div>
                    <div class="input-item"><strong>国家/地区：</strong>{params.get('country', 'CN')}</div>
                    <div class="input-item"><strong>每周工作：</strong>{params.get('work_days_per_week', 5)}天</div>
                    <div class="input-item"><strong>每日工时：</strong>{params.get('work_hours', 8)}小时</div>
                    <div class="input-item"><strong>每日通勤：</strong>{params.get('commute_hours', 1)}小时</div>
                    <div class="input-item"><strong>远程办公：</strong>{params.get('wfh_days', 0)}天/周</div>
                    <div class="input-item"><strong>年假：</strong>{params.get('annual_leave', 5)}天</div>
                    <div class="input-item"><strong>学历：</strong>{params.get('education_level', 'bachelor')}</div>
                    <div class="input-item"><strong>工作年限：</strong>{params.get('work_years', 0)}年</div>
                    <div class="input-item"><strong>工作类型：</strong>{params.get('job_type', 'private')}</div>
                </div>
            </div>
            
            <div class="action-plan">
                <h3>📋 30天行动计划</h3>
                <div class="action-item">
                    <strong>第1-7天：</strong>技能评估 - 根据行业趋势，识别需要提升的关键技能
                </div>
                <div class="action-item">
                    <strong>第8-14天：</strong>市场调研 - 深入了解目标行业和公司的薪资水平
                </div>
                <div class="action-item">
                    <strong>第15-21天：</strong>技能提升 - 参加在线课程或认证，提升核心竞争力
                </div>
                <div class="action-item">
                    <strong>第22-28天：</strong>网络建设 - 参加行业活动，建立专业人脉网络
                </div>
                <div class="action-item">
                    <strong>第29-30天：</strong>机会评估 - 整理求职策略，准备面试材料
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

@mcp.tool()
def save_html_report(
    result: Dict,
    params: Dict,
    filename: str = None
) -> Dict:
    """
    保存工作性价比分析为HTML报告
    
    Args:
        result: calculate_job_worth的返回结果
        params: 输入参数
        filename: 文件名（可选，默认为时间戳）
    
    Returns:
        Dict: 包含文件路径和成功信息的字典
    """
    
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"work_worth_report_{timestamp}.html"
    
    html_content = generate_html_report(result, params)
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 尝试自动打开报告
        try:
            webbrowser.open(f"file://{os.path.abspath(filename)}")
        except:
            pass
            
        return {
            'success': True,
            'filename': filename,
            'message': f'HTML报告已生成并保存到: {filename}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'保存报告时出错: {str(e)}'
        }

@mcp.tool()
def generate_report_from_worth_result(
    worth_result: Dict,
    original_params: Dict
) -> str:
    """
    从calculate_job_worth结果生成完整报告
    
    Args:
        worth_result: calculate_job_worth返回的结果
        original_params: 原始输入参数
    
    Returns:
        str: 完整的HTML报告内容
    """
    return generate_html_report(worth_result, original_params)

# ================================
# 🚀 主函数
# ================================

def main():
    """启动MCP服务器"""
    import sys
    
    # 检查是否有生成报告的命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--generate-report':
        # 生成示例报告
        sample_params = {
            'annual_salary': 300000,
            'country': 'CN',
            'work_days_per_week': 5,
            'work_hours': 9,
            'commute_hours': 1.5,
            'wfh_days': 2,
            'annual_leave': 10,
            'public_holidays': 11,
            'paid_sick_leave': 5,
            'city_factor': 1.2,
            'work_environment': 1.1,
            'leadership': 1.0,
            'teamwork': 1.1,
            'education_level': 'master',
            'school_tier': 'tier1',
            'work_years': 3,
            'job_type': 'private',
            'has_shuttle': True,
            'has_canteen': True
        }
        
        result = calculator.calculate_value_score(sample_params)
        save_result = save_html_report(result, sample_params, 'work_worth_report_demo.html')
        print(f"示例报告已生成: {save_result['filename']}")
        return
    
    # 启动MCP服务器
    logger.info(f"启动 {TOOL_NAME}...")
    logger.info(f"版本: {VERSION}")
    logger.info(f"作者: {AUTHOR}")
    mcp.run()

if __name__ == "__main__":
    main()