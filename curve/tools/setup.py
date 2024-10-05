from setuptools import setup, find_packages

setup(
    name="curve",
    version="0.1.0",
    description="Python-based CLI tool to manage Curve and generate targets.",
    author="Katanemo Labs, Inc.",
    packages=find_packages(),
    py_modules = ['cli', 'core', 'targets', 'utils', 'config_generator'],
    include_package_data=True,
    # Specify to include the docker-compose.yml file
    package_data={
        '': ['config/docker-compose.yaml', 'config/curve_config_schema.yaml', 'config/stage.env'] #Specify to include the docker-compose.yml file
    },
    # Add dependencies here, e.g., 'PyYAML' for YAML processing
    install_requires=['pyyaml', 'pydantic', 'click', 'jinja2','pyyaml','jsonschema', 'setuptools'],
    entry_points={
        'console_scripts': [
            'curve=cli:main',
        ],
    },
)
