r'''
# WAF HTTP API

A CDK construct that fronts an HTTP API with a CloudFront distribution and protects it with AWS WAF.

[![npm version](https://badge.fury.io/js/waf-http-api.svg)](https://badge.fury.io/js/waf-http-api)
[![PyPI version](https://badge.fury.io/py/waf-http-api.svg)](https://badge.fury.io/py/waf-http-api)

## Features

* **Enhanced Security:** Protects your HTTP API with AWS WAF rules
* **Global CDN:** Fronts your API with CloudFront for improved performance and availability
* **Custom Domains:** Support for custom domains with automatic SSL certificate management (requires hosted zone for DNS validation)
* **Automatic DNS Records:** Automatically creates Route 53 A and AAAA records for custom domains
* **Origin Verification:** Adds a secret header to ensure requests come through CloudFront
* **Customizable:** Use default WAF rules or provide your own custom rules
* **Easy Integration:** Simple to add to existing AWS CDK stacks

## Installation

### TypeScript/JavaScript

```bash
npm install waf-http-api
```

### Python

```bash
pip install waf-http-api
```

## Examples

Complete working examples demonstrating the usage of `waf-http-api` can be found in the [`example/`](./example/) directory:

* **[TypeScript Example](./example/typescript/)**: Full CDK application with Node.js 22 Lambda, comprehensive tests, and deployment scripts
* **[Python Example](./example/python/)**: Complete CDK application with Python 3.12 Lambda, pytest test suite, and development tools

Both examples include:

* ✅ Complete CDK stacks using the `WafHttpApi` construct
* ✅ Lambda functions with origin verification
* ✅ HTTP API Gateway with multiple routes
* ✅ Comprehensive test suites
* ✅ Build and deployment scripts
* ✅ Detailed documentation

These examples serve as practical references for implementing WAF-protected HTTP APIs in production environments.

## Usage

### Basic Usage

This example shows how to protect an HTTP API with WAF and CloudFront:

```python
import { Stack, StackProps } from "aws-cdk-lib";
import { HttpApi, HttpMethod } from "aws-cdk-lib/aws-apigatewayv2";
import { HttpLambdaIntegration } from "aws-cdk-lib/aws-apigatewayv2-integrations";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Runtime } from "aws-cdk-lib/aws-lambda";
import { WafHttpApi } from "waf-http-api";

class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const myLambda = new NodejsFunction(this, "MyApiHandler", {
      handler: "handler",
      entry: "lambda/handler.ts",
    });

    const httpApi = new HttpApi(this, "MyHttpApi", {
      description: "My example HTTP API",
    });

    httpApi.addRoutes({
      path: "/hello",
      methods: [HttpMethod.GET],
      integration: new HttpLambdaIntegration("MyLambdaIntegration", myLambda),
    });

    const protectedApi = new WafHttpApi(this, "ProtectedMyApi", {
      httpApi: httpApi,
      // Optionally, provide custom WAF rules:
      // wafRules: [ ... ],
    });

    new cdk.CfnOutput(this, "ProtectedApiEndpoint", {
      value: protectedApi.distribution.distributionDomainName,
      description: "The CloudFront URL for the protected API endpoint",
    });

    new cdk.CfnOutput(this, "OriginVerificationSecret", {
      value: protectedApi.secretHeaderValue,
      description: "Secret value to verify CloudFront origin requests",
    });
  }
}
```

### Custom Domain with Automatic Certificate

This example shows how to use a custom domain with automatic SSL certificate generation:

```python
import { Stack, StackProps, CfnOutput } from "aws-cdk-lib";
import { HttpApi, HttpMethod } from "aws-cdk-lib/aws-apigatewayv2";
import { HttpLambdaIntegration } from "aws-cdk-lib/aws-apigatewayv2-integrations";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Runtime } from "aws-cdk-lib/aws-lambda";
import { WafHttpApi } from "waf-http-api";

class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // ... Lambda and HTTP API setup (same as above) ...

    const protectedApi = new WafHttpApi(this, "ProtectedMyApi", {
      httpApi: httpApi,
      domain: "api.example.com", // Custom domain
      // Certificate will be automatically generated with DNS validation
    });

    new CfnOutput(this, "CustomDomainEndpoint", {
      value: `https://${protectedApi.customDomain}`,
      description: "Custom domain API endpoint",
    });

    new CfnOutput(this, "CertificateArn", {
      value: protectedApi.certificate?.certificateArn || "No certificate",
      description: "Auto-generated SSL certificate ARN",
    });
  }
}
```

### Custom Domain Configuration

**Important:** When using a custom domain, you must provide a hosted zone for DNS validation and automatic record creation.

```python
import { Stack, StackProps, CfnOutput } from "aws-cdk-lib";
import { HttpApi, HttpMethod } from "aws-cdk-lib/aws-apigatewayv2";
import { HttpLambdaIntegration } from "aws-cdk-lib/aws-apigatewayv2-integrations";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Runtime } from "aws-cdk-lib/aws-lambda";
import { HostedZone } from "aws-cdk-lib/aws-route53";
import { WafHttpApi } from "waf-http-api";

class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // ... Lambda and HTTP API setup (same as above) ...

    // Reference an existing hosted zone (REQUIRED for custom domains)
    const hostedZone = HostedZone.fromLookup(this, "MyZone", {
      domainName: "example.com",
    });

    const protectedApi = new WafHttpApi(this, "ProtectedMyApi", {
      httpApi: httpApi,
      domain: "api.example.com",
      hostedZone: hostedZone, // REQUIRED when using custom domain
    });

    new CfnOutput(this, "CustomDomainEndpoint", {
      value: `https://${protectedApi.customDomain}`,
      description: "Custom domain API endpoint",
    });

    // Access the automatically created DNS records
    if (protectedApi.aRecord) {
      new CfnOutput(this, "ARecordName", {
        value: protectedApi.aRecord.domainName,
        description: "A record for the API domain",
      });
    }

    if (protectedApi.aaaaRecord) {
      new CfnOutput(this, "AAAARecordName", {
        value: protectedApi.aaaaRecord.domainName,
        description: "AAAA record for the API domain",
      });
    }
  }
}
```

### Custom Domain with Provided Certificate

This example shows how to use a custom domain with your own SSL certificate (hosted zone still required):

```python
import { Stack, StackProps, CfnOutput } from "aws-cdk-lib";
import { Certificate } from "aws-cdk-lib/aws-certificatemanager";
import { HttpApi, HttpMethod } from "aws-cdk-lib/aws-apigatewayv2";
import { HttpLambdaIntegration } from "aws-cdk-lib/aws-apigatewayv2-integrations";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Runtime } from "aws-cdk-lib/aws-lambda";
import { HostedZone } from "aws-cdk-lib/aws-route53";
import { WafHttpApi } from "waf-http-api";

class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // ... Lambda and HTTP API setup (same as above) ...

    // Reference an existing hosted zone (REQUIRED)
    const hostedZone = HostedZone.fromLookup(this, "MyZone", {
      domainName: "example.com",
    });

    // Reference an existing certificate (must be in us-east-1 region)
    const existingCertificate = Certificate.fromCertificateArn(
      this,
      "ExistingCert",
      "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012",
    );

    const protectedApi = new WafHttpApi(this, "ProtectedMyApi", {
      httpApi: httpApi,
      domain: "api.example.com",
      hostedZone: hostedZone, // REQUIRED when using custom domain
      certificate: existingCertificate, // Use provided certificate
    });

    new CfnOutput(this, "CustomDomainEndpoint", {
      value: `https://${protectedApi.customDomain}`,
      description: "Custom domain API endpoint",
    });

    new CfnOutput(this, "CertificateArn", {
      value: protectedApi.certificate?.certificateArn || "No certificate",
      description: "Provided SSL certificate ARN",
    });
  }
}
```

### Advanced Configuration with Custom WAF Rules

This example shows advanced usage with custom domain and custom WAF rules:

```python
import { Stack, StackProps, CfnOutput } from "aws-cdk-lib";
import { HttpApi, HttpMethod } from "aws-cdk-lib/aws-apigatewayv2";
import { HttpLambdaIntegration } from "aws-cdk-lib/aws-apigatewayv2-integrations";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Runtime } from "aws-cdk-lib/aws-lambda";
import { HostedZone } from "aws-cdk-lib/aws-route53";
import { WafHttpApi } from "waf-http-api";

class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // ... Lambda and HTTP API setup (same as above) ...

    // Reference an existing hosted zone (REQUIRED for custom domains)
    const hostedZone = HostedZone.fromLookup(this, "MyZone", {
      domainName: "example.com",
    });

    const protectedApi = new WafHttpApi(this, "ProtectedMyApi", {
      httpApi: httpApi,
      domain: "secure-api.example.com",
      hostedZone: hostedZone, // REQUIRED when using custom domain
      wafRules: [
        {
          name: "RateLimitRule",
          priority: 10,
          statement: {
            rateBasedStatement: {
              limit: 2000,
              aggregateKeyType: "IP",
            },
          },
          action: { block: {} },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: "RateLimitRule",
            sampledRequestsEnabled: true,
          },
        },
        // Add more custom rules as needed
      ],
    });

    new CfnOutput(this, "SecureApiEndpoint", {
      value: `https://${protectedApi.customDomain}`,
      description: "Secure API endpoint with custom WAF rules",
    });
  }
}
```

## Important Notes

### Certificate Requirements

* **Region Requirement**: SSL certificates for CloudFront must be in the `us-east-1` region
* **DNS Validation**: Auto-generated certificates use DNS validation through the provided hosted zone
* **Domain Ownership**: You must own and control the domain and have access to the hosted zone

### Domain Configuration

* **Supported Formats**: Apex domains (`example.com`), subdomains (`api.example.com`), and wildcards (`*.example.com`)
* **Hosted Zone Required**: All custom domains require a corresponding hosted zone for DNS validation and record creation
* **Automatic DNS Setup**: DNS records are automatically created in the provided hosted zone
* **Validation**: Domain format and hosted zone compatibility are validated at synthesis time

### Hosted Zone Requirements

* **Required for Custom Domains**: A hosted zone is required when using custom domains for DNS validation and record creation
* **Automatic DNS Records**: Route 53 A and AAAA records are automatically created for the custom domain
* **Domain Compatibility**: The domain must match or be a subdomain of the hosted zone's domain
* **Record Types**: Both IPv4 (A) and IPv6 (AAAA) records are created pointing to the CloudFront distribution

## API

See [`API.md`](API.md) for full API documentation.

## Development

This project uses [projen](https://github.com/projen/projen) for project management. To synthesize project files after making changes to `.projenrc.ts`, run:

```bash
npx projen
```

## License

MIT © Merapar Technologies Group B.V.
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

import aws_cdk.aws_apigatewayv2 as _aws_cdk_aws_apigatewayv2_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_wafv2 as _aws_cdk_aws_wafv2_ceddda9d
import constructs as _constructs_77d1e7e8


class WafHttpApi(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="waf-http-api.WafHttpApi",
):
    '''
    :class: WafHttpApi
    :description:

    A CDK construct that fronts an AWS HTTP API with a CloudFront distribution
    and protects it with AWS WAF. This enhances security and performance by
    adding a global CDN layer and web application firewall capabilities.
    It also injects a secret header from CloudFront to the origin to allow
    for origin verification by a Lambda Authorizer or similar mechanism.

    **Custom Domain Support:**
    This construct supports custom domains with automatic SSL certificate management.
    When a domain is provided, the CloudFront distribution will be configured to accept
    requests on that domain. If no certificate is provided, an ACM certificate will be
    automatically generated with DNS validation.
    :extends: Construct

    Example::

        // Usage with hosted zone for automatic DNS record creation
        const hostedZone = HostedZone.fromLookup(this, 'MyZone', {
          domainName: 'example.com'
        });
        
        const apiWithDns = new WafHttpApi(this, 'ApiWithDNS', {
          httpApi: myHttpApi,
          domain: 'api.example.com',
          hostedZone: hostedZone
        });
        
        // Access the automatically created DNS records
        if (apiWithDns.aRecord) {
          new CfnOutput(this, 'ARecordName', {
            value: apiWithDns.aRecord.domainName,
            description: 'A record for the API domain'
          });
        }
        
        if (apiWithDns.aaaaRecord) {
          new CfnOutput(this, 'AAAARecordName', {
            value: apiWithDns.aaaaRecord.domainName,
            description: 'AAAA record for the API domain'
          });
        }
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        http_api: _aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        domain: typing.Optional[builtins.str] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        waf_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: The scope in which to define this construct (e.g., a CDK Stack).
        :param id: The unique identifier for this construct within its scope.
        :param http_api: The HTTP API to be protected by the WAF and CloudFront. This should be an instance of ``aws-cdk-lib/aws-apigatewayv2.HttpApi``. The API will be fronted by a CloudFront distribution with WAF protection.
        :param certificate: Optional: SSL certificate for the custom domain. Must be an ACM certificate in the us-east-1 region for CloudFront compatibility. If not provided and a domain is specified, a certificate will be automatically generated using DNS validation. **Important Requirements:** - Certificate must be in us-east-1 region (CloudFront requirement) - Certificate must cover the specified domain (exact match or wildcard) - Certificate must be valid and accessible
        :param domain: Optional: Custom domain name for the CloudFront distribution. When provided, the CloudFront distribution will be configured to accept requests on this domain. If no certificate is provided, an ACM certificate will be automatically generated with DNS validation. Supports various domain formats: - Apex domains: ``example.com`` - Subdomains: ``api.example.com``, ``www.api.example.com`` - Wildcard domains: ``*.example.com``
        :param hosted_zone: Optional: Route 53 hosted zone for automatic DNS record creation. When provided along with a domain, the construct will automatically create Route 53 A and AAAA records pointing to the CloudFront distribution. **Behavior:** - When both ``hostedZone`` and ``domain`` are provided: DNS records are automatically created - When ``hostedZone`` is provided without ``domain``: Hosted zone is ignored with warning - When ``domain`` is provided without ``hostedZone``: No DNS records are created - Domain must match or be a subdomain of the hosted zone's domain
        :param waf_rules: Optional: Custom WAF rules to apply to the WebACL. If not provided, a default set of AWS Managed Rules will be used, specifically "AWSManagedRulesAmazonIpReputationList" and "AWSManagedRulesCommonRuleSet". These rules help protect against common web exploits and unwanted traffic. Default: AWS Managed Rules (AmazonIpReputationList, CommonRuleSet)

        :constructor: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d85ac6423dea7afad65ba02061fbf680d6c1e47b52cc21989650da33e763be0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WafHttpApiProps(
            http_api=http_api,
            certificate=certificate,
            domain=domain,
            hosted_zone=hosted_zone,
            waf_rules=waf_rules,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="SECRET_HEADER_NAME")
    def SECRET_HEADER_NAME(cls) -> builtins.str:
        '''
        :description:

        The name of the custom header CloudFront will add to requests
        forwarded to the origin. This header can be used by your backend (e.g.,
        a Lambda Authorizer for API Gateway) to verify that the request originated
        from CloudFront and not directly from the internet.
        :property: {string} SECRET_HEADER_NAME
        :readonly: true
        :static: true
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SECRET_HEADER_NAME"))

    @builtins.property
    @jsii.member(jsii_name="distribution")
    def distribution(self) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        '''The CloudFront distribution created and managed by this construct.

        You can use this property to retrieve the distribution's domain name or ARN.

        :readonly: true
        :type: {cloudfront.Distribution}

        Example::

            // Access the CloudFront distribution domain name
            const distributionDomain = wafHttpApi.distribution.distributionDomainName;
            
            // Access the distribution ARN
            const distributionArn = wafHttpApi.distribution.distributionArn;
            
            // Use in CloudFormation outputs
            new CfnOutput(this, 'DistributionEndpoint', {
              value: `https://${wafHttpApi.distribution.distributionDomainName}`,
              description: 'CloudFront distribution endpoint'
            });
        '''
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, jsii.get(self, "distribution"))

    @builtins.property
    @jsii.member(jsii_name="secretHeaderValue")
    def secret_header_value(self) -> builtins.str:
        '''The randomly generated secret value for the custom header.

        This value is unique for each deployment of the construct and should be used
        in your HTTP API's authorizer or backend logic to validate that requests
        are coming through CloudFront and not directly from the internet.

        :readonly: true
        :type: {string}

        Example::

            // Use in Lambda authorizer
            export const handler = async (event: APIGatewayProxyEvent) => {
              const secretHeader = event.headers[WafHttpApi.SECRET_HEADER_NAME];
              const expectedSecret = process.env.CLOUDFRONT_SECRET; // Set from wafHttpApi.secretHeaderValue
            
              if (secretHeader !== expectedSecret) {
                throw new Error('Unauthorized: Request not from CloudFront');
              }
            
              // Continue with request processing...
            };
            
            // Set as environment variable in Lambda
            const lambda = new NodejsFunction(this, 'ApiHandler', {
              environment: {
                CLOUDFRONT_SECRET: wafHttpApi.secretHeaderValue
              }
            });
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretHeaderValue"))

    @builtins.property
    @jsii.member(jsii_name="aaaaRecord")
    def aaaa_record(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.AaaaRecord]:
        '''The Route 53 AAAA record created for the custom domain.

        This property will be defined when both ``hostedZone`` and ``domain`` are provided,
        and the construct automatically creates DNS records pointing to the CloudFront distribution.

        The AAAA record maps the custom domain to the CloudFront distribution's IPv6 addresses.

        :readonly: true
        :type: {route53.AaaaRecord | undefined}

        Example::

            // Check if AAAA record was created
            if (wafHttpApi.aaaaRecord) {
              // Output AAAA record details
              new CfnOutput(this, 'AAAARecordName', {
                value: wafHttpApi.aaaaRecord.domainName,
                description: 'AAAA record domain name'
              });
            
              // Reference the record in other resources
              const recordArn = wafHttpApi.aaaaRecord.recordArn;
            }
            
            // The AAAA record will be undefined if:
            // - No hostedZone was provided
            // - No domain was provided
            // - hostedZone was provided without domain (ignored with warning)
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.AaaaRecord], jsii.get(self, "aaaaRecord"))

    @builtins.property
    @jsii.member(jsii_name="aRecord")
    def a_record(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord]:
        '''The Route 53 A record created for the custom domain.

        This property will be defined when both ``hostedZone`` and ``domain`` are provided,
        and the construct automatically creates DNS records pointing to the CloudFront distribution.

        The A record maps the custom domain to the CloudFront distribution's IPv4 addresses.

        :readonly: true
        :type: {route53.ARecord | undefined}

        Example::

            // Check if A record was created
            if (wafHttpApi.aRecord) {
              // Output A record details
              new CfnOutput(this, 'ARecordName', {
                value: wafHttpApi.aRecord.domainName,
                description: 'A record domain name'
              });
            
              // Reference the record in other resources
              const recordArn = wafHttpApi.aRecord.recordArn;
            }
            
            // The A record will be undefined if:
            // - No hostedZone was provided
            // - No domain was provided
            // - hostedZone was provided without domain (ignored with warning)
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord], jsii.get(self, "aRecord"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''The SSL certificate used for the custom domain.

        This property will be defined in the following scenarios:

        - When a certificate is provided via the ``certificate`` prop
        - When a certificate is automatically generated for a custom domain

        The property will be ``undefined`` when no custom domain is configured.

        :readonly: true
        :type: {acm.ICertificate | undefined}

        Example::

            // Check if certificate is available
            if (wafHttpApi.certificate) {
              // Output certificate ARN
              new CfnOutput(this, 'CertificateArn', {
                value: wafHttpApi.certificate.certificateArn,
                description: 'SSL certificate ARN'
              });
            
              // Use certificate in other resources
              const loadBalancer = new ApplicationLoadBalancer(this, 'ALB', {
                // ... other props
              });
            
              loadBalancer.addListener('HttpsListener', {
                port: 443,
                certificates: [wafHttpApi.certificate],
                // ... other listener props
              });
            }
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="customDomain")
    def custom_domain(self) -> typing.Optional[builtins.str]:
        '''The custom domain name configured for this distribution.

        This property will be defined when a domain is provided via the ``domain`` prop.
        It will be ``undefined`` when no custom domain is configured.

        :readonly: true
        :type: {string | undefined}

        Example::

            // Check if custom domain is configured
            if (wafHttpApi.customDomain) {
              // Output custom domain endpoint
              new CfnOutput(this, 'CustomDomainEndpoint', {
                value: `https://${wafHttpApi.customDomain}`,
                description: 'Custom domain API endpoint'
              });
            
              // Use domain in Route53 record
              new ARecord(this, 'ApiRecord', {
                zone: hostedZone,
                recordName: wafHttpApi.customDomain,
                target: RecordTarget.fromAlias(
                  new CloudFrontTarget(wafHttpApi.distribution)
                ),
              });
            } else {
              // Use CloudFront default domain
              new CfnOutput(this, 'DefaultEndpoint', {
                value: `https://${wafHttpApi.distribution.distributionDomainName}`,
                description: 'Default CloudFront endpoint'
              });
            }
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customDomain"))


@jsii.data_type(
    jsii_type="waf-http-api.WafHttpApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "http_api": "httpApi",
        "certificate": "certificate",
        "domain": "domain",
        "hosted_zone": "hostedZone",
        "waf_rules": "wafRules",
    },
)
class WafHttpApiProps:
    def __init__(
        self,
        *,
        http_api: _aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        domain: typing.Optional[builtins.str] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        waf_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param http_api: The HTTP API to be protected by the WAF and CloudFront. This should be an instance of ``aws-cdk-lib/aws-apigatewayv2.HttpApi``. The API will be fronted by a CloudFront distribution with WAF protection.
        :param certificate: Optional: SSL certificate for the custom domain. Must be an ACM certificate in the us-east-1 region for CloudFront compatibility. If not provided and a domain is specified, a certificate will be automatically generated using DNS validation. **Important Requirements:** - Certificate must be in us-east-1 region (CloudFront requirement) - Certificate must cover the specified domain (exact match or wildcard) - Certificate must be valid and accessible
        :param domain: Optional: Custom domain name for the CloudFront distribution. When provided, the CloudFront distribution will be configured to accept requests on this domain. If no certificate is provided, an ACM certificate will be automatically generated with DNS validation. Supports various domain formats: - Apex domains: ``example.com`` - Subdomains: ``api.example.com``, ``www.api.example.com`` - Wildcard domains: ``*.example.com``
        :param hosted_zone: Optional: Route 53 hosted zone for automatic DNS record creation. When provided along with a domain, the construct will automatically create Route 53 A and AAAA records pointing to the CloudFront distribution. **Behavior:** - When both ``hostedZone`` and ``domain`` are provided: DNS records are automatically created - When ``hostedZone`` is provided without ``domain``: Hosted zone is ignored with warning - When ``domain`` is provided without ``hostedZone``: No DNS records are created - Domain must match or be a subdomain of the hosted zone's domain
        :param waf_rules: Optional: Custom WAF rules to apply to the WebACL. If not provided, a default set of AWS Managed Rules will be used, specifically "AWSManagedRulesAmazonIpReputationList" and "AWSManagedRulesCommonRuleSet". These rules help protect against common web exploits and unwanted traffic. Default: AWS Managed Rules (AmazonIpReputationList, CommonRuleSet)

        :description:

        Properties for configuring the WafHttpApi construct.
        This interface defines all the configuration options available when creating
        a WAF-protected HTTP API with CloudFront distribution and optional custom domain support.
        :interface: WafHttpApiProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd0c48f02a0f3dbd44bbc23e0a023c8d596dcba9ca17bc8c97e123086b4cdef3)
            check_type(argname="argument http_api", value=http_api, expected_type=type_hints["http_api"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument waf_rules", value=waf_rules, expected_type=type_hints["waf_rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "http_api": http_api,
        }
        if certificate is not None:
            self._values["certificate"] = certificate
        if domain is not None:
            self._values["domain"] = domain
        if hosted_zone is not None:
            self._values["hosted_zone"] = hosted_zone
        if waf_rules is not None:
            self._values["waf_rules"] = waf_rules

    @builtins.property
    def http_api(self) -> _aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi:
        '''The HTTP API to be protected by the WAF and CloudFront.

        This should be an instance of ``aws-cdk-lib/aws-apigatewayv2.HttpApi``.
        The API will be fronted by a CloudFront distribution with WAF protection.

        :type: {HttpApi}

        Example::

            const httpApi = new HttpApi(this, 'MyApi', {
              description: 'My protected HTTP API'
            });
        '''
        result = self._values.get("http_api")
        assert result is not None, "Required property 'http_api' is missing"
        return typing.cast(_aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi, result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''Optional: SSL certificate for the custom domain.

        Must be an ACM certificate in the us-east-1 region for CloudFront compatibility.
        If not provided and a domain is specified, a certificate will be automatically generated
        using DNS validation.

        **Important Requirements:**

        - Certificate must be in us-east-1 region (CloudFront requirement)
        - Certificate must cover the specified domain (exact match or wildcard)
        - Certificate must be valid and accessible

        :type: {acm.ICertificate}

        Example::

            // Using existing certificate
            const existingCert = Certificate.fromCertificateArn(
              this,
              'ExistingCert',
              'arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012'
            );
            
            // In props
            certificate: existingCert
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Optional: Custom domain name for the CloudFront distribution.

        When provided, the CloudFront distribution will be configured to accept requests on this domain.
        If no certificate is provided, an ACM certificate will be automatically generated with DNS validation.

        Supports various domain formats:

        - Apex domains: ``example.com``
        - Subdomains: ``api.example.com``, ``www.api.example.com``
        - Wildcard domains: ``*.example.com``

        :type: {string}

        Example::

            // Apex domain
            domain: 'example.com'
            
            // Subdomain
            domain: 'api.example.com'
            
            // Wildcard domain
            domain: '*.api.example.com'
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hosted_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''Optional: Route 53 hosted zone for automatic DNS record creation.

        When provided along with a domain, the construct will automatically create
        Route 53 A and AAAA records pointing to the CloudFront distribution.

        **Behavior:**

        - When both ``hostedZone`` and ``domain`` are provided: DNS records are automatically created
        - When ``hostedZone`` is provided without ``domain``: Hosted zone is ignored with warning
        - When ``domain`` is provided without ``hostedZone``: No DNS records are created
        - Domain must match or be a subdomain of the hosted zone's domain

        :type: {route53.IHostedZone}

        Example::

            // Using existing hosted zone
            const hostedZone = HostedZone.fromLookup(this, 'MyZone', {
              domainName: 'example.com'
            });
            
            // In props with automatic DNS record creation
            const protectedApi = new WafHttpApi(this, 'MyApi', {
              httpApi: myHttpApi,
              domain: 'api.example.com',
              hostedZone: hostedZone
            });
            
            // Access created DNS records
            if (protectedApi.aRecord) {
              new CfnOutput(this, 'ARecordName', {
                value: protectedApi.aRecord.domainName
              });
            }
        '''
        result = self._values.get("hosted_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    @builtins.property
    def waf_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty]]:
        '''Optional: Custom WAF rules to apply to the WebACL.

        If not provided, a default set of AWS Managed Rules will be used,
        specifically "AWSManagedRulesAmazonIpReputationList" and "AWSManagedRulesCommonRuleSet".
        These rules help protect against common web exploits and unwanted traffic.

        :default: AWS Managed Rules (AmazonIpReputationList, CommonRuleSet)

        :type: {wafv2.CfnWebACL.RuleProperty[]}

        Example::

            wafRules: [
              {
                name: 'RateLimitRule',
                priority: 10,
                statement: {
                  rateBasedStatement: {
                    limit: 2000,
                    aggregateKeyType: 'IP',
                  },
                },
                action: { block: {} },
                visibilityConfig: {
                  cloudWatchMetricsEnabled: true,
                  metricName: 'RateLimitRule',
                  sampledRequestsEnabled: true,
                },
              },
            ]
        '''
        result = self._values.get("waf_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WafHttpApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "WafHttpApi",
    "WafHttpApiProps",
]

publication.publish()

def _typecheckingstub__0d85ac6423dea7afad65ba02061fbf680d6c1e47b52cc21989650da33e763be0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    http_api: _aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    domain: typing.Optional[builtins.str] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    waf_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd0c48f02a0f3dbd44bbc23e0a023c8d596dcba9ca17bc8c97e123086b4cdef3(
    *,
    http_api: _aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    domain: typing.Optional[builtins.str] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    waf_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass
