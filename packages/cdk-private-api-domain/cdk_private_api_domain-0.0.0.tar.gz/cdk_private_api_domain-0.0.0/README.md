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
