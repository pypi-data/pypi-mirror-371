from setuptools import setup, find_packages

setup(
        name='nglm-ai',
        version='0.1.1',
        description='nglm base build',
        author='Ra K',
        author_email='your.email@example.com',
        packages=find_packages(),
        install_requires=[
            'pandas'  # List any dependencies here, e.g., 'requests>=2.20.0'
        ],
    )