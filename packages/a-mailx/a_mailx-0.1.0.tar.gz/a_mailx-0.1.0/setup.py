from setuptools import setup, find_packages

def read_requirements():
    with open("requirements.txt", encoding="utf-8") as f:
        return f.read().splitlines()

setup(
    name="a_mailx",  # pip install 时的名字
    version="0.1.0",  # 每次发版要改版本号
    description="A Multi-Agent Communication Protocol Solution Based on LangGraph",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="yanghhhhh",
    author_email="developer_yang@qq.com",
    url="https://github.com/dev-yang-ai/A_mail",
    packages=find_packages(),
    install_requires=read_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    include_package_data=True,
)
