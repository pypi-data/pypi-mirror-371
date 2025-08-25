from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="job-worth-calculator-mcp",
    version="1.0.0",
    author="AI助手",
    author_email="ai@example.com",
    description="基于worth-calculator的全面工作性价比计算MCP工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai/job-worth-calculator-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "fastmcp>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "job-worth-calculator-mcp=job_worth_calculator_mcp.main:main",
        ],
    },
    keywords="mcp, job, worth, calculator, salary, comparison, career",
    project_urls={
        "Bug Reports": "https://github.com/ai/job-worth-calculator-mcp/issues",
        "Source": "https://github.com/ai/job-worth-calculator-mcp",
    },
)