from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PerSent",
    version="1.3.3",
    author="RezaGooner",
    author_email="RezaAsadiProgrammer@Gmail.com",
    description="Persian Sentiment Analysis Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RezaGooner/PerSent",
    packages=find_packages(),
    package_data={
        'PerSent': ['CommentAnalyzer.py','SentimentAnalyzer.py' , 'models/*'],
    },
    include_package_data=True,
    install_requires=[
    'hazm>=0.7.0',
    'gensim>=4.3.0',
    'numpy<2.0,>=1.26.4',
    'scipy<1.14.0,>=1.11.0',
    'scikit-learn>=1.0.0',
    'pandas>=1.3.0',
    'tqdm>=4.62.0',
    'joblib>=1.1.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    keywords='persian sentiment analysis nlp',
)
