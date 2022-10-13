from setuptools import setup

setup (
    name='stripe-migrate',
    version='0.1.0',
    py_modules=['stripe-migrate'],
    install_requires=['click', 'stripe'],
    entry_points={ 'console_scripts': [
        'stripe-migrate = stripe-migrate:cli'
    ]}
)
