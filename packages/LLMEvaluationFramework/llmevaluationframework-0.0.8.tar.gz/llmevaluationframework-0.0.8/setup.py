from setuptools import setup, find_packages

setup(
    name="LLMEvaluationFramework",
    version="0.0.8",
    author="Sathishkumar Nagarajan",
    author_email="mail@sathishkumarnagarajan.com",
    description="End-to-End LLM Evaluation and Auto-Suggestion Framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/isathish/LLMEvaluationFramework",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
