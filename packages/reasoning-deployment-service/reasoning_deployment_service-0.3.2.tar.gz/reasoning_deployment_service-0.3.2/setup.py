from setuptools import setup, find_packages

setup(
    name='reasoning-deployment-service',
    version='0.2.3',
    description='A service for deploying reasoning agents with CLI and GUI editors.',
    author='AxG-AI-Exchange-GenAI-Initiative',
    packages=find_packages(),
    package_data={
        'reasoning_deployment_service.gui_editor': [
            'src/core/*.py',
            'src/ui/*.py', 
            'src/__init__.py',
            'src/core/__init__.py',
            'src/ui/__init__.py',
            'requirements_minimal.txt',
            'run_program.sh',
        ],
        'reasoning_deployment_service.cli_editor': [
            '*.py',
        ],
    },
    include_package_data=True,
    install_requires=[
        # Core reasoning deployment service dependencies
        'google-cloud-aiplatform[agent_engines]>=1.91.0,!=1.92.0',
        'vertexai>=1.43.0',
        'google-auth>=2.40.0',
        'google-auth-oauthlib>=1.2.0',
        'google-api-python-client>=2.178.0',
        'python-dotenv>=1.1.0',
        'requests>=2.32.0',
        'PyYAML>=6.0.0',
        'google-adk>=0.0.2',
        'google-genai>=1.5.0,<2.0.0',
        'pydantic>=2.10.6,<3.0.0',
    ],
    extras_require={
        'gui': [
            # GUI editor dependencies (all from requirements_minimal.txt)
            'google-api-core>=2.25.0',
            'googleapis-common-protos>=1.70.0',
            'grpcio>=1.74.0',
            'protobuf>=6.31.0',
            'google-auth-httplib2>=0.2.0',
            'cachetools>=5.5.0',
            'pyasn1>=0.6.0',
            'pyasn1_modules>=0.4.0',
            'rsa>=4.9.0',
            'certifi>=2025.8.0',
            'urllib3>=2.5.0',
            'six>=1.17.0',
        ],
        'cli': [],  # CLI has no extra requirements beyond base
        'full': [
            # Install everything for complete functionality
            'google-api-core>=2.25.0',
            'googleapis-common-protos>=1.70.0',
            'grpcio>=1.74.0',
            'protobuf>=6.31.0',
            'google-auth-httplib2>=0.2.0',
            'cachetools>=5.5.0',
            'pyasn1>=0.6.0',
            'pyasn1_modules>=0.4.0',
            'rsa>=4.9.0',
            'certifi>=2025.8.0',
            'urllib3>=2.5.0',
            'six>=1.17.0',
        ],
        'dev': [
            # Development dependencies
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
