import { LambdaRestApi, DomainName } from "aws-cdk-lib/aws-apigateway";
import { IFunction } from "aws-cdk-lib/aws-lambda";
import { Construct } from "constructs";
// import { DomainName, HttpApi, CorsHttpMethod } from '@aws-cdk/aws-apigatewayv2';
import { Certificate } from 'aws-cdk-lib/aws-certificatemanager';
// import { HttpLambdaIntegration } from '@aws-cdk/aws-apigatewayv2-integrations-alpha';
import { ARecord, RecordTarget, HostedZone } from 'aws-cdk-lib/aws-route53';
import { ApiGatewayv2DomainProperties, ApiGatewayDomain } from 'aws-cdk-lib/aws-route53-targets';

interface VRTApiGatewayProps {
    proxyMicroservice: IFunction,
    // symbolMicroservice: IFunction,
    // accountMicroservice: IFunction,
    // reviewOrderMicroservice: IFunction,
    // orderingMicroservices: IFunction,
    stage: string
}

export class VGTApiGateway extends Construct {    

    constructor(scope: Construct, id: string, props: VRTApiGatewayProps) {
        super(scope, id);

        this.createProxyApi(props.proxyMicroservice, props.stage);

        // // Symbol api gateway
        // this.createSymbolApi(props.symbolMicroservice, props.stage);
    
        // // Account api gateway
        // this.createAccountApi(props.accountMicroservice, props.stage);

        // // ReviewOrder api gateway
        // this.createReviewOrderApi(props.reviewOrderMicroservice, props.stage);
        // // Ordering api gateway
        // this.createOrderApi(props.orderingMicroservices, props.stage);

        // // Define Custom Domain
        // const apiDomain = new DomainName(this, 'apiDomain', {
        //     domainName: 'vgipoc.net',
        //     // domainName: context.apiDomain,
        //     certificate: Certificate.fromCertificateArn(this, 'apiDomainCert', "certARN"),
        //     // certificate: Certificate.fromCertificateArn(this, 'apiDomainCert', context.regionalCertArn),
        // });
        
        // // Add Route 53 entry for Api
        // new ARecord(this, 'apiDNSRecord', {
        //     zone: HostedZone.fromHostedZoneAttributes(this, 'apiHostedZone', {
        //     hostedZoneId: context.hostedZoneId,
        //     zoneName: context.baseDomain,
        //     }),
        //     recordName: context.apiDomain,
        //     target: RecordTarget.fromAlias(apiDomain.domainName),
        //     // target: RecordTarget.fromAlias(new ApiGatewayv2DomainProperties(apiDomain.regionalDomainName, apiDomain.regionalHostedZoneId)),
        // });
                
    //     // Define Custom Domain
    //     const apiDomain = new DomainName(this, 'apiDomain', {
    //         domainName: context.apiDomain,
    //         certificate: Certificate.fromCertificateArn(this, 'apiDomainCert', context.regionalCertArn),
    //     });
    
    //     // Add Route 53 entry for Api
    //     new ARecord(this, 'apiDNSRecord', {
    //         zone: HostedZone.fromHostedZoneAttributes(this, 'apiHostedZone', {
    //         hostedZoneId: context.hostedZoneId,
    //         zoneName: context.baseDomain,
    //         }),
    //         recordName: context.apiDomain,
    //         target: RecordTarget.fromAlias(new ApiGatewayv2DomainProperties(apiDomain.regionalDomainName, apiDomain.regionalHostedZoneId)),
    //     });

    }

    private createProxyApi(proxyMicroservice: IFunction, stage: string) {
        // Symbol microservices api gateway
        // root name = symbol
  
        // GET /symbol
        // POST /symbol
  
        // Single symbol with ticker parameter
        // GET /symbol/{ticker}
        // PUT /symbol/{ticker}
        // DELETE /symbol/{ticker}
  
        const apigw = new LambdaRestApi(this, 'proxyApi', {
          restApiName: 'Proxy Service',
          handler: proxyMicroservice,
          proxy: false,
          deployOptions: {
              // 👇 stage name `dev`
              stageName: stage,
          }
        });
    
        const symbol = apigw.root.addResource('proxy');
        // symbol.addMethod('GET'); // GET /symbol
        // symbol.addMethod('POST');  // POST /symbol
        
        // const singleSymbol = symbol.addResource('{ticker}'); // symbol/{ticker}
        // singleSymbol.addMethod('GET'); // GET /symbol/{ticker}
        // singleSymbol.addMethod('PUT'); // PUT /symbol/{ticker}
        // singleSymbol.addMethod('DELETE'); // DELETE /symbol/{ticker}
      }

    private createSymbolApi(symbolMicroservice: IFunction, stage: string) {
        // Symbol microservices api gateway
        // root name = symbol
  
        // GET /symbol
        // POST /symbol
  
        // Single symbol with ticker parameter
        // GET /symbol/{ticker}
        // PUT /symbol/{ticker}
        // DELETE /symbol/{ticker}
  
        const apigw = new LambdaRestApi(this, 'symbolApi', {
          restApiName: 'Symbol Service',
          handler: symbolMicroservice,
          proxy: false,
          deployOptions: {
              // 👇 stage name `dev`
              stageName: stage,
          }
        });
    
        const symbol = apigw.root.addResource('symbol');
        symbol.addMethod('GET'); // GET /symbol
        symbol.addMethod('POST');  // POST /symbol
        
        const singleSymbol = symbol.addResource('{ticker}'); // symbol/{ticker}
        singleSymbol.addMethod('GET'); // GET /symbol/{ticker}
        singleSymbol.addMethod('PUT'); // PUT /symbol/{ticker}
        singleSymbol.addMethod('DELETE'); // DELETE /symbol/{ticker}
      }


    private createAccountApi(accountMicroservice: IFunction, stage: string) {
        // Account microservices api gateway
        // root name = account
  
        // GET /account
        // POST /account
  
        // Single account with accountId parameter
        // GET /symbol/{accountId}
        // PUT /symbol/{accountId}
        // DELETE /symbol/{accountId}
  
        const apigw = new LambdaRestApi(this, 'accountApi', {
          restApiName: 'Account Service',
          handler: accountMicroservice,
          proxy: false,
          deployOptions: {
              // 👇 stage name `dev`
              stageName: stage,
          }
        });
    
        const account = apigw.root.addResource('account');
        account.addMethod('GET'); // GET /account
        account.addMethod('POST');  // POST /account
        
        const singleAccount = account.addResource('{accountId}'); // account/{accountId}
        singleAccount.addMethod('GET'); // GET /account/{accountId}
        singleAccount.addMethod('PUT'); // PUT /account/{accountId}
        singleAccount.addMethod('DELETE'); // DELETE /account/{accountId}
      }
        
    private createReviewOrderApi(reviewOrderMicroservice: IFunction, stage: string) {
        // ReviewOrder microservices api gateway
        // root name = reviewOrder

        // GET /reviewOrder
        // POST /reviewOrder

        // // Single reviewOrder with userName parameter - resource name = reviewOrder/{userName}
        // GET /reviewOrder/{userName}
        // DELETE /reviewOrder/{userName}

        // send reviewOrder async flow
        // POST /reviewOrder/send

        const apigw = new LambdaRestApi(this, 'reviewOrderApi', {
            restApiName: 'ReviewOrder Service',
            handler: reviewOrderMicroservice,
            proxy: false,
            deployOptions: {
                // 👇 stage name `dev`
                stageName: stage,
            }
        });

        const reviewOrder = apigw.root.addResource('reviewOrder');
        reviewOrder.addMethod('GET');  // GET /reviewOrder
        reviewOrder.addMethod('POST');  // POST /reviewOrder

        const singleReviewOrder = reviewOrder.addResource('{userName}');
        singleReviewOrder.addMethod('GET');  // GET /reviewOrder/{userName}
        singleReviewOrder.addMethod('DELETE'); // DELETE /reviewOrder/{userName}

        const reviewOrderCheckout = reviewOrder.addResource('send');
        reviewOrderCheckout.addMethod('POST'); // POST /reviewOrder/send
            // expected request payload : { userName : vgt }
    }

    private createOrderApi(orderingMicroservices: IFunction, stage: string) {
        // Ordering microservices api gateway
        // root name = order

        // GET /order
	    // GET /order/{userName}
        // expected request : xxx/order/vgt?orderDate=timestamp
        // ordering ms grap input and query parameters and filter to dynamo db

        const apigw = new LambdaRestApi(this, 'orderApi', {
            restApiName: 'Order Service',
            handler: orderingMicroservices,
            proxy: false,
            deployOptions: {
                // 👇 stage name `dev`
                stageName: stage,
            }
        });
    
        const order = apigw.root.addResource('order');
        order.addMethod('GET');  // GET /order        
    
        const singleOrder = order.addResource('{userName}');
        singleOrder.addMethod('GET');  // GET /order/{userName}
            // expected request : xxx/order/vgt?orderDate=timestamp
            // ordering ms grap input and query parameters and filter to dynamo db
    
        return singleOrder;
    }
}