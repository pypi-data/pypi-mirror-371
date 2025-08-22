from setuptools import setup, find_packages

setup(
    name='tfx-moe',
    version='0.1.0',
    description='Multi-output evaluator TFX component for deep learning models that utilize TensorFlow and TensorFlow Extended.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Dr. Ahmed Moussa',
    author_email='ahmedyosrihamdy@gmail.com',
    url='https://github.com/real-ahmed-moussa/tfx-multioutput-evaluator',
    license='MIT',
    packages=find_packages(),
    install_requires=[
                        "tfx>=1.15.1,<2.0",
                        "tensorflow>=2.15.1,<2.16",
                        "tensorflow-transform>=1.15.0,<2.0",
                    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.10.8',
)
