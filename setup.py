from setuptools import setup, find_packages

setup(
    name='leakage_circuit_compiler',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'qulacs',
        'numpy',
        'scipy'
    ],
    description='Leakage-aware hybrid qutrit-qubit circuit simulator based on Qulacs',
    author='Your Name',
    license='MIT'
)