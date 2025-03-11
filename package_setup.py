import os
from setuptools import setup, find_packages

# requirements.txt 파일에서 의존성 읽기
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# README.md 파일이 있으면 읽기
long_description = ''
if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='ailabs_llm_xml_transformer',
    version='1.0.0',
    description='XML 변환 및 LLM 처리를 위한 통합 도구',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='',
    author_email='',
    url='https://github.com/yourusername/ailabs-llm-xml-transformer',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'xml-transformer=python.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
    # Node.js 관련 파일 포함
    package_data={
        'ailabs_llm_xml_transformer': [
            'node/**/*',
            'node/.env',
        ],
    },
)