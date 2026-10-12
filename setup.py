from setuptools import setup, find_packages

setup(
    name="odoo-upgrader",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "odoo-upgrader=odoo_upgrader.cli:main",
            "upgrade-odoo=odoo_upgrader.cli:main",
        ],
    },
)
