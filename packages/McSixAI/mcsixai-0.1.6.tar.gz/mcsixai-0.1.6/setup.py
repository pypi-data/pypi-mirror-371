from setuptools import setup, find_packages

setup(
    name="McSixAI",
    version="0.1.6",
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'python-dotenv>=0.19.0',
    ],
    entry_points={
        'console_scripts': [
            'mcsixai=McSixAI.cli:main',
        ],
    },
    author="McSix",
    author_email="mcsixhelps@gmail.com",
    description="AI ассистент для программирования с интерактивным интерфейсом",
    keywords="ai programming assistant openrouter",
    python_requires='>=3.7',
)