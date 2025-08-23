from setuptools import setup, find_packages

setup(
    name="plicat_model",                  # 包名
    version="0.1.0",                   # 版本
    packages=find_packages(),          # 自动发现包
    install_requires=[
        "torch>=2.7.0",
        "transformers>=4.32.0",
        "esm>=0.5.0"                   # 你的依赖
    ],
    python_requires=">=3.8",
    include_package_data=True,
    description="A custom PLiCat model for lipid-binding Protein prediction",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://huggingface.co/Noora68/PLiCat-0.4B",
    author="FeitongDong",
    author_email="12031011@mail.sustech.edu.cn",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
