from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Neurix',                 
    version='0.1.2',                
    author='Avatanshu Gupta',        
    author_email='avatanshugupta@gmail.com',  
    description='Neurix is a simple ML utility library with preprocessing, regression, classification, and evaluation tools',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AvatanshuGupta/EasyML.git', 
    packages=find_packages(),       
    python_requires='>=3.8',      
    install_requires=[            
        'numpy'
        
    ],
    classifiers=[                   
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
