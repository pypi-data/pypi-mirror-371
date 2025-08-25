r'''
# cdk-private-api-domain

A reusable [AWS CDK](https://aws.amazon.com/cdk/) construct that provisions a **private Amazon API Gateway** with a **custom domain name**, accessible only through VPC endpoints.

This construct simplifies the creation of internal APIs by automatically handling:

* **Private API Gateway** with `disable_execute_api_endpoint=true`.
* **VPC endpoint integration** (`EndpointType.PRIVATE`).
* **Custom domain name** setup with ACM certificate.
* **Route 53 record creation** in a provided hosted zone.
* **IAM policy enforcement** to restrict access to VPC endpoints only.
* **Lambda integration** (or any CDK `IFunction` backend).

---


## 🚀 Features

* Provision **internal/private APIs** for secure access inside your VPC.
* Assign a **custom subdomain** (e.g. `api.internal.example.com`).
* Automatically manages **Route 53 DNS records** and **ACM certificates**.
* Attach your **Lambda function** (or extend to other backends).
* **Reusable** in multiple stacks and environments.

---


## 📦 Installation

### TypeScript / Node.js (npm)

```sh
npm install cdk-private-api-domain
```

### Python (PyPI)

```sh
pip install cdk-private-api-domain
```

---


## 🛠 Usage

### TypeScript

```python
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as route53 from 'aws-cdk-lib/aws-route53';
import { PrivateApiDomainConstruct } from 'cdk-private-api-domain';

export class MyStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = ec2.Vpc.fromLookup(this, 'Vpc', { vpcId: 'vpc-1234567890' });
    const fn = new lambda.Function(this, 'MyFunction', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda'),
    });
    const hostedZone = route53.HostedZone.fromLookup(this, 'HostedZone', {
      domainName: 'example.com',
    });

    new PrivateApiDomainConstruct(this, 'PrivateApi', {
      vpc,
      handler: fn,
      hostedZone,
      subdomain: 'api',
    });
  }
}
```

### Python

```python
from aws_cdk import (
    App, Stack, aws_ec2 as ec2, aws_lambda as _lambda, aws_route53 as route53
)
from cdk_private_api_domain import PrivateApiDomainConstruct

class MyStack(Stack):
    def __init__(self, scope: App, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "Vpc", vpc_id="vpc-1234567890")

        fn = _lambda.Function(
            self, "MyFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda"),
        )

        hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name="example.com"
        )

        PrivateApiDomainConstruct(
            self, "PrivateApi",
            vpc=vpc,
            handler=fn,
            hosted_zone=hosted_zone,
            subdomain="api"
        )

app = App()
MyStack(app, "MyStack")
app.synth()
```

---


## 🔑 Props

| Property   | Type                          | Description |
|------------|-------------------------------|-------------|
| `vpc`      | `ec2.IVpc`                   | The VPC where the API will be deployed. |
| `handler`  | `lambda.IFunction`           | The Lambda function to integrate with API Gateway. |
| `hostedZone` | `route53.IHostedZone`      | The hosted zone where the custom domain record will be created. |
| `subdomain` | `str` (Python) / `string` (TS) | The subdomain for the API (e.g. `api` for `api.example.com`). |

---


## ✅ Example Result

* Creates a **private API Gateway** endpoint, accessible only via VPC interface endpoints.
* Deploys with a **custom domain** (e.g., `api.example.com`).
* DNS is automatically set up in Route 53.
* Secured with an ACM certificate.

---


## 📄 License

Distributed under the [Apache-2.0 License](./LICENSE).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import constructs as _constructs_77d1e7e8


class PrivateApiWithDomain(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-private-api-domain.PrivateApiWithDomain",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        subdomain: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        base_path: typing.Optional[builtins.str] = None,
        certificate_arn: typing.Optional[builtins.str] = None,
        create_interface_endpoint: typing.Optional[builtins.bool] = None,
        deploy_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        endpoint_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        endpoint_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        rest_api_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param handler: (experimental) Lambda function to integrate as proxy.
        :param hosted_zone: (experimental) Private hosted zone for the custom domain.
        :param subdomain: (experimental) Subdomain (left-hand label) under the hosted zone.
        :param vpc: (experimental) VPC to host the execute-api Interface VPC Endpoint.
        :param base_path: (experimental) Base path mapping on the domain (default: empty).
        :param certificate_arn: (experimental) Reuse an existing ACM cert ARN (same region). If omitted, a DNS-validated cert is created.
        :param create_interface_endpoint: (experimental) Create the Interface VPC Endpoint (execute-api) automatically.
        :param deploy_options: (experimental) Optional stage options.
        :param endpoint_security_groups: (experimental) Security groups for the VPC endpoint.
        :param endpoint_subnets: (experimental) Subnet selection for the VPC endpoint.
        :param rest_api_name: (experimental) Optional API name.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a483f7f91c64d718dd27c33b250d3788a9ec0e784b2e1b2bfb17a6727a6a43a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PrivateApiWithDomainProps(
            handler=handler,
            hosted_zone=hosted_zone,
            subdomain=subdomain,
            vpc=vpc,
            base_path=base_path,
            certificate_arn=certificate_arn,
            create_interface_endpoint=create_interface_endpoint,
            deploy_options=deploy_options,
            endpoint_security_groups=endpoint_security_groups,
            endpoint_subnets=endpoint_subnets,
            rest_api_name=rest_api_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="aliasRecord")
    def alias_record(self) -> _aws_cdk_aws_route53_ceddda9d.CfnRecordSet:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.CfnRecordSet, jsii.get(self, "aliasRecord"))

    @builtins.property
    @jsii.member(jsii_name="api")
    def api(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, jsii.get(self, "api"))

    @builtins.property
    @jsii.member(jsii_name="basePathMapping")
    def base_path_mapping(
        self,
    ) -> _aws_cdk_aws_apigateway_ceddda9d.CfnBasePathMappingV2:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.CfnBasePathMappingV2, jsii.get(self, "basePathMapping"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="domainAccessAssociation")
    def domain_access_association(
        self,
    ) -> _aws_cdk_aws_apigateway_ceddda9d.CfnDomainNameAccessAssociation:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.CfnDomainNameAccessAssociation, jsii.get(self, "domainAccessAssociation"))

    @builtins.property
    @jsii.member(jsii_name="domainNameV2")
    def domain_name_v2(self) -> _aws_cdk_aws_apigateway_ceddda9d.CfnDomainNameV2:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.CfnDomainNameV2, jsii.get(self, "domainNameV2"))

    @builtins.property
    @jsii.member(jsii_name="vpce")
    def vpce(self) -> _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint, jsii.get(self, "vpce"))


@jsii.data_type(
    jsii_type="cdk-private-api-domain.PrivateApiWithDomainProps",
    jsii_struct_bases=[],
    name_mapping={
        "handler": "handler",
        "hosted_zone": "hostedZone",
        "subdomain": "subdomain",
        "vpc": "vpc",
        "base_path": "basePath",
        "certificate_arn": "certificateArn",
        "create_interface_endpoint": "createInterfaceEndpoint",
        "deploy_options": "deployOptions",
        "endpoint_security_groups": "endpointSecurityGroups",
        "endpoint_subnets": "endpointSubnets",
        "rest_api_name": "restApiName",
    },
)
class PrivateApiWithDomainProps:
    def __init__(
        self,
        *,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        subdomain: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        base_path: typing.Optional[builtins.str] = None,
        certificate_arn: typing.Optional[builtins.str] = None,
        create_interface_endpoint: typing.Optional[builtins.bool] = None,
        deploy_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        endpoint_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        endpoint_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        rest_api_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param handler: (experimental) Lambda function to integrate as proxy.
        :param hosted_zone: (experimental) Private hosted zone for the custom domain.
        :param subdomain: (experimental) Subdomain (left-hand label) under the hosted zone.
        :param vpc: (experimental) VPC to host the execute-api Interface VPC Endpoint.
        :param base_path: (experimental) Base path mapping on the domain (default: empty).
        :param certificate_arn: (experimental) Reuse an existing ACM cert ARN (same region). If omitted, a DNS-validated cert is created.
        :param create_interface_endpoint: (experimental) Create the Interface VPC Endpoint (execute-api) automatically.
        :param deploy_options: (experimental) Optional stage options.
        :param endpoint_security_groups: (experimental) Security groups for the VPC endpoint.
        :param endpoint_subnets: (experimental) Subnet selection for the VPC endpoint.
        :param rest_api_name: (experimental) Optional API name.

        :stability: experimental
        '''
        if isinstance(deploy_options, dict):
            deploy_options = _aws_cdk_aws_apigateway_ceddda9d.StageOptions(**deploy_options)
        if isinstance(endpoint_subnets, dict):
            endpoint_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**endpoint_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06ca57ffd4561e02f59db6ac4c5690161a5abcd3cde2308fee399be2c80a3462)
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument subdomain", value=subdomain, expected_type=type_hints["subdomain"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument base_path", value=base_path, expected_type=type_hints["base_path"])
            check_type(argname="argument certificate_arn", value=certificate_arn, expected_type=type_hints["certificate_arn"])
            check_type(argname="argument create_interface_endpoint", value=create_interface_endpoint, expected_type=type_hints["create_interface_endpoint"])
            check_type(argname="argument deploy_options", value=deploy_options, expected_type=type_hints["deploy_options"])
            check_type(argname="argument endpoint_security_groups", value=endpoint_security_groups, expected_type=type_hints["endpoint_security_groups"])
            check_type(argname="argument endpoint_subnets", value=endpoint_subnets, expected_type=type_hints["endpoint_subnets"])
            check_type(argname="argument rest_api_name", value=rest_api_name, expected_type=type_hints["rest_api_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "handler": handler,
            "hosted_zone": hosted_zone,
            "subdomain": subdomain,
            "vpc": vpc,
        }
        if base_path is not None:
            self._values["base_path"] = base_path
        if certificate_arn is not None:
            self._values["certificate_arn"] = certificate_arn
        if create_interface_endpoint is not None:
            self._values["create_interface_endpoint"] = create_interface_endpoint
        if deploy_options is not None:
            self._values["deploy_options"] = deploy_options
        if endpoint_security_groups is not None:
            self._values["endpoint_security_groups"] = endpoint_security_groups
        if endpoint_subnets is not None:
            self._values["endpoint_subnets"] = endpoint_subnets
        if rest_api_name is not None:
            self._values["rest_api_name"] = rest_api_name

    @builtins.property
    def handler(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''(experimental) Lambda function to integrate as proxy.

        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    @builtins.property
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''(experimental) Private hosted zone for the custom domain.

        :stability: experimental
        '''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, result)

    @builtins.property
    def subdomain(self) -> builtins.str:
        '''(experimental) Subdomain (left-hand label) under the hosted zone.

        :stability: experimental
        '''
        result = self._values.get("subdomain")
        assert result is not None, "Required property 'subdomain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) VPC to host the execute-api Interface VPC Endpoint.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def base_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Base path mapping on the domain (default: empty).

        :stability: experimental
        '''
        result = self._values.get("base_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) Reuse an existing ACM cert ARN (same region).

        If omitted, a DNS-validated cert is created.

        :stability: experimental
        '''
        result = self._values.get("certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_interface_endpoint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create the Interface VPC Endpoint (execute-api) automatically.

        :stability: experimental
        '''
        result = self._values.get("create_interface_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.StageOptions]:
        '''(experimental) Optional stage options.

        :stability: experimental
        '''
        result = self._values.get("deploy_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.StageOptions], result)

    @builtins.property
    def endpoint_security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) Security groups for the VPC endpoint.

        :stability: experimental
        '''
        result = self._values.get("endpoint_security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def endpoint_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Subnet selection for the VPC endpoint.

        :stability: experimental
        '''
        result = self._values.get("endpoint_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def rest_api_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional API name.

        :stability: experimental
        '''
        result = self._values.get("rest_api_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrivateApiWithDomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PrivateApiWithDomain",
    "PrivateApiWithDomainProps",
]

publication.publish()

def _typecheckingstub__6a483f7f91c64d718dd27c33b250d3788a9ec0e784b2e1b2bfb17a6727a6a43a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    subdomain: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    base_path: typing.Optional[builtins.str] = None,
    certificate_arn: typing.Optional[builtins.str] = None,
    create_interface_endpoint: typing.Optional[builtins.bool] = None,
    deploy_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    endpoint_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    endpoint_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    rest_api_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06ca57ffd4561e02f59db6ac4c5690161a5abcd3cde2308fee399be2c80a3462(
    *,
    handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    subdomain: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    base_path: typing.Optional[builtins.str] = None,
    certificate_arn: typing.Optional[builtins.str] = None,
    create_interface_endpoint: typing.Optional[builtins.bool] = None,
    deploy_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.StageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    endpoint_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    endpoint_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    rest_api_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
