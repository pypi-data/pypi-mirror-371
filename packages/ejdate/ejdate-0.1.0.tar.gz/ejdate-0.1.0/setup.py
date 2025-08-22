from setuptools import setup, find_packages

setup(
    name='ejdate',
    version='0.1.0',
    description='Easy and clean Jalali-Gregorian date conversion and formatting',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Alireza Asadiyan',
    author_email='ali.r.asadiyan@gmail.com',
    url='https://github.com/alireza85as/ejdate',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'jdatetime',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
    ],
    include_package_data=True,
)
