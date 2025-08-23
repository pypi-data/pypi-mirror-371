from setuptools import setup, find_packages

setup(
    name='hdgdk',
    version='0.1.0',
    description='HD RPG 引擎框架(GDK) Python API',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='HD GDK API',
    author_email='hdgdk@example.com',
    url='https://github.com/hdgdk/hdgdk-python',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.6',
    install_requires=[],
    include_package_data=True,
    package_data={
        # 可以在这里指定要包含的额外文件
    },
)