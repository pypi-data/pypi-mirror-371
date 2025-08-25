import sys
import pkgutil
if not hasattr(pkgutil, 'ImpImporter') and hasattr(pkgutil, 'zipimporter'):
    pkgutil.ImpImporter = pkgutil.zipimporter
from setuptools import setup,find_packages
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "高效的混合布尔数组库：通过分段存储（密集段+稀疏段）大幅节省内存，支持超大规模布尔数据操作，适配 Python 3.8+。"
setup(
    name="bool-hybrid-array",
    version="7.9.1",
    py_modules=find_packages(),
    install_requires=["numpy>=1.21.0"],
    author="蔡靖杰",
    author_email="1289270215@qq.com", 
    description="高效节省内存的混合布尔数组",tion_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
    ],
    python_requires=">=3.8", 
)
