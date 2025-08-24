# setup.py

from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='sentiebl',
    version='0.1.1',
    author='Mirza Milan Farabi',
    author_email='mmfarabi28m@gmail.com',
    description='Systematic Elicitation of Non-Trivial and Insecure Emergent Behaviors in LLMs',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/mmfarabi/sentiebl',
    packages=find_packages(),
    install_requires=[
        'openai',
        'ollama',
        'pandas',
        'matplotlib',
        'ipython'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Security',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Testing',
    ],
    keywords=[
        'llm', 'gpt-oss', 'red-teaming', 
        'openai', 'ollama', 'ai-safety', 
        'vulnerability-analysis', 'prompt-injection', 'ai-security', 
        'sentiebl', 'llm-testing', 'llm-auditor'
    ],
    python_requires='>=3.8',
)