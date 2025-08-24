from setuptools import setup,find_packages
import os
if not os.path.exists("bool_hybrid_array/__init__.py"):
    with open("bool_hybrid_array/__init__.py", "w") as f:
        pass
setup(
    name="bool-hybrid-array",
    version="7.8.13",
    author="Cai Jingjie",
    author_email="1289270215@qq.com",
    description="Efficient boolean hybrid array library",
    requires=["numpy (>=1.21.0)"],
    py_modules=find_packages()
)
