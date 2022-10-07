import { CfnOutput, Stack, StackProps, RemovalPolicy } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as ddb from "aws-cdk-lib/aws-dynamodb";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { VGTEventBus } from './eventbus';
// import { VGTMicroservices } from './microservice';
import { VGTQueue } from './queue';
import { AttributeType } from "aws-cdk-lib/aws-dynamodb";

// import * as sqs from 'aws-cdk-lib/aws-sqs';

// TODO
// API Gateway
// Refactor ?
// Other APIs

export class TradeInfraStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    //  SYMBOL Microservice
    // Create DDB table to store the tasks.
    const symbolTable = new ddb.Table(this, "tr_Symbol", {
      partitionKey: { name: "ticker", type: ddb.AttributeType.STRING },
      billingMode: ddb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    //   timeToLiveAttribute: "ttl",
    });

    // // Add GSI based on sector.
    symbolTable.addGlobalSecondaryIndex({
      indexName: "sector-index",
      partitionKey: { name: "sector", type: ddb.AttributeType.STRING },
    //   sortKey: { name: "created_time", type: ddb.AttributeType.NUMBER },
    });

    // Create Lambda function for the API.
    const symbolApi = new lambda.Function(this, "tr_SYMBOL_API", {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset("../api/symbol_lambda.zip"),
      handler: "symbol.handler",
      environment: {
        SYMBOL_TABLE_NAME: symbolTable.tableName,
      },
    });

    // Create a URL so we can access the function.
    const symbolFunctionUrl = symbolApi.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
      },
    });

    // Output the API function url.
    new CfnOutput(this, "SymbolAPIUrl", {
      value: symbolFunctionUrl.url,
    });

    symbolTable.grantReadWriteData(symbolApi);

    //  REVIEWORDER Microservice
    // Create DDB table to store the tasks.
    const reviewOrderTable = new ddb.Table(this, "tr_ReviewOrder", {
      partitionKey: { name: "userName", type: ddb.AttributeType.STRING },
      billingMode: ddb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,

    //   timeToLiveAttribute: "ttl",
    });

    // Create Lambda function for the API.
    const reviewOrderApi = new lambda.Function(this, "tr_REVIEWORDER_API", {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset("../api/reviewOrder_lambda.zip"),
      handler: "reviewOrder.handler",
      environment: {
        REVIEWORDER_TABLE_NAME: reviewOrderTable.tableName,
      },
    });

    // Create a URL so we can access the function.
    const reviewOrderFunctionUrl = reviewOrderApi.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
      },
    });

    // Output the API function url.
    new CfnOutput(this, "ReviewOrderAPIUrl", {
      value: reviewOrderFunctionUrl.url,
    });

    reviewOrderTable.grantReadWriteData(reviewOrderApi);

    //  Ordering Microservice
    // Create DDB table to to process orders.
    const orderingTable = new ddb.Table(this, "tr_Ordering", {
      partitionKey: { name: "userName", type: ddb.AttributeType.STRING },
      sortKey: {name: "orderDate", type: AttributeType.STRING},
      billingMode: ddb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // Create Lambda function for the API.
    const orderingApi = new lambda.Function(this, "tr_ORDERING_API", {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset("../api/ordering_lambda.zip"),
      handler: "ordering.handler",
      environment: {
        ORDERING_TABLE_NAME: orderingTable.tableName,
      },
    });

    // Create a URL so we can access the function.
    const orderingFunctionUrl = orderingApi.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
      },
    });

    // Output the API function url.
    new CfnOutput(this, "OrderingAPIUrl", {
      value: orderingFunctionUrl.url,
    });

    orderingTable.grantReadWriteData(orderingApi);

    // Create to consume from the Event Bus
    const queue = new VGTQueue(this, 'Queue', {
      consumer: orderingApi
    });

    //  Create an Event Bus
    const eventbus = new VGTEventBus(this, 'EventBus', {
      publisherFuntion: reviewOrderApi,
      // publisherFuntion: microservices.reviewOrderMicroservice,
      targetQueue: queue.orderQueue   
    });   

  }
}
