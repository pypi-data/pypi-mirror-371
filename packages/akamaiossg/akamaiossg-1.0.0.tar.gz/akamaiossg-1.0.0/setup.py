# setup.py

from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='akamaiossg',
    version='1.0.0',
    author='Mirza Milan Farabi',
    author_email='mmfar@gmail.com',
    description='Akamaiossg description for TLLs',
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
        'llm', 'vulnerability', 'prompt', 'ai-security'
    ],
    python_requires='>=3.8',
)