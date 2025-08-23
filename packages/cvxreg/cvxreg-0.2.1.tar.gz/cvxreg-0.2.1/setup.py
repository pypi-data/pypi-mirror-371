from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='cvxreg',
    version='0.2.1',
    description='A Python Package for Convex Regression',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Zhiqiang Liao',
    author_email='zhiqiang.liao@aalto.fi',
    keywords=['ML', 'Prediction', 'Regression'],
    url='https://github.com/ConvexRegression/cvxreg',
    download_url='https://pypi.org/project/cvxreg/',
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_data={'': ['*.csv']},
)

install_requires = [
    'numpy>=1.19.2',
    'pandas>=1.1.3',
    'scipy>=1.5.2',
    'cvxpy>=1.1.7',
    'scikit-learn>=0.23.2',
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)