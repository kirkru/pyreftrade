import { CfnOutput, Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as ddb from "aws-cdk-lib/aws-dynamodb";
import * as lambda from "aws-cdk-lib/aws-lambda";
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
      // removalPolicy: 
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

  }
}
