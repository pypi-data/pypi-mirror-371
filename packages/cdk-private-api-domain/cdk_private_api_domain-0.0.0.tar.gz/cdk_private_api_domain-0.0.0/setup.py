import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-private-api-domain",
    "version": "0.0.0",
    "description": "A CDK construct library that provisions a private Amazon API Gateway with a custom domain name, accessible only through VPC endpoints. It simplifies the creation of internal APIs by combining API Gateway, Route 53, and certificate management into a reusable construct.",
    "license": "Apache-2.0",
    "url": "https://github.com/avishayil/cdk-private-api-domain.git",
    "long_description_content_type": "text/markdown",
    "author": "avishayil<avishay.il@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/avishayil/cdk-private-api-domain.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_private_api_domain",
        "cdk_private_api_domain._jsii"
    ],
    "package_data": {
        "cdk_private_api_domain._jsii": [
            "cdk-private-api-domain@0.0.0.jsii.tgz"
        ],
        "cdk_private_api_domain": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
