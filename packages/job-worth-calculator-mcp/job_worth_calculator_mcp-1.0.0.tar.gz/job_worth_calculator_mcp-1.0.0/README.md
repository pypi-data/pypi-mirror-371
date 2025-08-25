# 🚀 工作性价比计算器MCP工具

基于worth-calculator项目的全面工作价值计算MCP工具，支持190+国家/地区的薪资标准化比较。

## ✨ 功能特点

- **全面评估**：超越单纯薪资考量，综合工作时长、通勤、工作环境等多维度因素
- **国际比较**：支持190+国家/地区的PPP购买力平价转换
- **教育加成**：考虑学历背景和学校层次对薪资的影响
- **经验曲线**：基于工作年限和职业类型的薪资增长预测
- **现代化报告**：生成响应式HTML报告，支持移动端查看
- **未来趋势**：提供各国未来热门职业和薪资趋势预测

## 📊 核心功能

### 1. 工作性价比计算
计算工作性价比的核心公式：
```
性价比 = (日薪 × 环境因子) / (35 × 工作时间 × 教育加成 × 经验倍数)
```

### 2. 国际薪资比较
- 支持190+国家/地区的PPP购买力平价转换
- 以人民币为基准的薪资标准化
- 实时货币符号显示

### 3. HTML报告生成
- 现代化响应式设计
- 动画效果和交互体验
- 30天行动计划建议
- 移动端友好界面

### 4. 未来趋势预测
- 各国热门职业薪资预测
- 5年薪资增长趋势
- 关键技能需求分析

## 🚀 快速开始

### 安装

```bash
pip install job-worth-calculator-mcp
```

### 作为MCP工具使用

在Trae AI或其他支持MCP的客户端中配置：

```json
{
  "mcpServers": {
    "job-worth-calculator": {
      "command": "uvx",
      "args": ["job-worth-calculator-mcp"]
    }
  }
}
```

### 命令行使用

```bash
# 启动MCP服务器
job-worth-calculator-mcp

# 生成示例报告
job-worth-calculator-mcp --generate-report
```

## 📖 使用示例

### 基本工作性价比计算

```python
from job_worth_calculator_mcp.main import calculate_job_worth

result = calculate_job_worth(
    annual_salary=300000,
    country="CN",
    work_days_per_week=5,
    work_hours=9,
    commute_hours=1.5,
    wfh_days=2,
    annual_leave=10,
    education_level="master",
    work_years=3
)
print(f"工作性价比评分: {result['score']}")
print(f"评估结果: {result['assessment']}")
```

### 生成HTML报告

```python
from job_worth_calculator_mcp.main import save_html_report

# 使用上面的计算结果
save_result = save_html_report(result, params)
print(f"报告已保存: {save_result['filename']}")
```

### 获取支持的国家列表

```python
from job_worth_calculator_mcp.main import get_supported_countries

countries = get_supported_countries()
print(f"支持{countries['total_countries']}个国家/地区")
```

### 未来趋势预测

```python
from job_worth_calculator_mcp.main import future_job_trends

trends = future_job_trends(country="CN", years_ahead=5)
for job in trends['hot_jobs'][:5]:
    print(f"{job['job']}: {job['growth']}%增长")
```

## 🌍 支持的国家/地区

覆盖全球主要经济体，包括：
- 东亚：中国、日本、韩国、香港、台湾等
- 东南亚：新加坡、泰国、越南、马来西亚等
- 欧洲：英国、德国、法国、意大利等
- 北美：美国、加拿大、墨西哥
- 南美：巴西、阿根廷、智利等
- 澳洲：澳大利亚、新西兰

完整列表可通过 `get_supported_countries()` 获取。

## 📊 评分标准

| 评分范围 | 等级 | 说明 |
|---------|------|------|
| ≥2.0 | Excellent | 神仙工作！高薪轻松 |
| 1.5-2.0 | Good | 还不错的工作 |
| 1.0-1.5 | Fair | 一般般，可作跳板 |
| 0.7-1.0 | Poor | 性价比偏低 |
| <0.7 | Terrible | 快跑！血汗工厂 |

## 🎯 使用场景

- **求职决策**：评估offer性价比
- **薪资谈判**：了解市场薪资水平
- **职业规划**：制定技能提升计划
- **国际比较**：跨国工作机会评估
- **团队管理**：了解员工满意度因素

## 🔧 技术特性

- **MCP兼容**：完全符合MCP协议标准
- **响应式设计**：支持桌面端和移动端
- **国际化**：支持多国家/地区薪资标准
- **实时计算**：即时生成分析结果
- **可视化报告**：美观的HTML报告输出

## 📈 未来规划

- [ ] 支持更多行业特定参数
- [ ] 添加历史薪资趋势分析
- [ ] 集成更多外部数据源
- [ ] 支持团队协作功能
- [ ] 添加薪资预测模型

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [worth-calculator原项目](https://github.com/ai/worth-calculator)
- [MCP协议文档](https://modelcontextprotocol.io)
- [PyPI包页面](https://pypi.org/project/job-worth-calculator-mcp/)