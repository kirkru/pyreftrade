import { CfnOutput, Stack, StackProps, RemovalPolicy } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as ddb from "aws-cdk-lib/aws-dynamodb";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { TEventBus } from './eventbus';
// import { VGTMicroservices } from './microservice';
import { TQueue } from './queue';
import { AttributeType } from "aws-cdk-lib/aws-dynamodb";
import { LambdaRestApi, DomainName } from "aws-cdk-lib/aws-apigateway";

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
    const instrumentTable = new ddb.Table(this, "tr_Instrument_Table", {
      partitionKey: { name: "ticker", type: ddb.AttributeType.STRING },
      billingMode: ddb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    //   timeToLiveAttribute: "ttl",
    });

    // // Add GSI based on sector.
    instrumentTable.addGlobalSecondaryIndex({
      indexName: "sector-index",
      partitionKey: { name: "sector", type: ddb.AttributeType.STRING },
    //   sortKey: { name: "created_time", type: ddb.AttributeType.NUMBER },
    });

    // Create Lambda function for the API.
    const instrumentLambda = new lambda.Function(this, "tr_Instrument_Lambda", {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset("../api/instrument_lambda.zip"),
      handler: "instrument.handler",
      environment: {
        INSTRUMENT_TABLE_NAME: instrumentTable.tableName,
      },
    });

    // Create a URL so we can access the function.
    const instrumentFunctionUrl = instrumentLambda.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
      },
    });

    // Output the API function url.
    new CfnOutput(this, "InstrumentAPIUrl", {
      value: instrumentFunctionUrl.url,
    });

    instrumentTable.grantReadWriteData(instrumentLambda);

    //#region - USERACCOUNTS Microservice
    // Create DDB table to store users, accounts and holdings
    const userAccountsTable = new ddb.Table(this, "tr_UserAccounts_Table", {
      partitionKey: { name: "PK", type: ddb.AttributeType.STRING },
      sortKey: {name: "SK", type: AttributeType.STRING},
      billingMode: ddb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const USERACCOUNTS_TABLE_INDEX =   "GSI1-SK-index"

    // Add GSI for querying holdings
    userAccountsTable.addGlobalSecondaryIndex({
      indexName: USERACCOUNTS_TABLE_INDEX,
      partitionKey: { name: "GSI1", type: ddb.AttributeType.STRING },
      sortKey: { name: "SK", type: ddb.AttributeType.STRING },
    });

    // Create Lambda function for the API
    const userAccountsLambda = new lambda.Function(this, "tr_UserAccounts_Lambda", {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset("../api/userAccounts_lambda.zip"),
      handler: "userAccounts.handler",
      environment: {
        USERACCOUNTS_TABLE_NAME: userAccountsTable.tableName,
        USERACCOUNTS_TABLE_INDEX: USERACCOUNTS_TABLE_INDEX
      },
    });

    userAccountsTable.grantReadWriteData(userAccountsLambda);

    // Set up API Gateway
    const userAccountsAPI = new LambdaRestApi(this, 'tr_UserAccounts_API', {
      restApiName: 'tr_UserAccounts_API',
      handler: userAccountsLambda,
      proxy: false,
      deployOptions: {
          // 👇 stage name `dev`
          stageName: 'eng',
      }
    });     

    // #region /userProfile API

    // Set up resource /userProfile 
    const userProfile = userAccountsAPI.root.addResource('user');
      
    // GET /userProfile    - get all users
    // GET /userProfile?username={userName}         - get user
    userProfile.addMethod('GET');  

    // POST /userProfile  - create user
    userProfile.addMethod('POST'); 

    // PUT /userProfile?username={userName}         - update user
    userProfile.addMethod('PUT');

    // DELETE /userProfile?username={userName}      - delete user
    userProfile.addMethod('DELETE');

    // const singleUser = userProfile.addResource('{userName}'); // userProfile/{userName}
    // singleUser.addMethod('GET'); // GET /userProfile/{userName}         - get user
    // singleUser.addMethod('PUT'); // PUT /userProfile/{userName}         - update user
    // singleUser.addMethod('DELETE'); // DELETE /userProfile/{userName}   - delete user

    //#endregion

    // #region /userAccounts API

    // Set up resource /userAccounts
    const userAccounts = userAccountsAPI.root.addResource('userAccounts');
    
    // GET /userAccounts                      - Get all accounts 
    // GET /userAccounts?userName={userName}  - Get all accounts for user
    userAccounts.addMethod('GET');  
    
    // POST /userAccounts  - create account
    userAccounts.addMethod('POST');  
    
    // PUT /userAccounts?accountID={accountID}         - update an account
    userAccounts.addMethod('PUT'); 

    // DELETE /userAccounts?accountID={accountID}       - delete an account
    userAccounts.addMethod('DELETE'); 

    // const singleAccount = userAccounts.addResource('{accountID}');   // userAccounts/{accountID}
    // // singleAccount.addMethod('GET'); // GET /userAccounts/{userName}          - get an account
    // singleAccount.addMethod('PUT');    // PUT /userAccounts/{accountID}         - update an account
    // singleAccount.addMethod('DELETE'); // DELETE /userAccounts/{accountID}   - delete an account

    //#endregion

    // #region /accountHoldings API

    // Set up resource /accountHoldings
    const accountHoldings = userAccountsAPI.root.addResource('accountHoldings');

    // GET /accountHoldings?accountID={accountID}   - get all holdings for an account
    accountHoldings.addMethod('GET'); 

    // POST /accountHoldings?accountID={accountID}&holdingID={holdingID}   - create a holding in an account
    accountHoldings.addMethod('POST');  

    // PUT /accountHoldings?accountID={accountID}&holdingID={holdingID}    - update a holding in an account
    accountHoldings.addMethod('PUT');  

    // DELETE /accountHoldings?accountID={accountID}&holdingID={holdingID} - delete a holding in an account
    accountHoldings.addMethod('DELETE');  

    // const holdingsAccountID = accountHoldings.addResource('{accountID}');   // accountHoldings/{accountID}
    // holdingsAccountID.addMethod('GET'); // GET /singleAccountHoldings/{accountID}                       - get an account's holdings

    // const singHolding = holdingsAccountID.addResource('{holdingID}')
    // singHolding.addMethod('POST'); // POST /singleAccountHoldings/{accountID}/{holdingID}         - create a holding in an account
    // singHolding.addMethod('PUT'); // PUT /singleAccountHoldings/{accountID}/{holdingID}           - update a holding in an account
    // singHolding.addMethod('DELETE'); // DELETE /singleAccountHoldings/{accountID}/{holdingID}     - delete an account holding
    
    //#endregion

    // #region /holdingAccounts API

    // Set up resource /holdingAccounts
    const holdingInAccounts = userAccountsAPI.root.addResource('holdingInAccounts');

    // GET all accounts with the a particular holding
    // GET /holdingAccounts?holdingID={holdingID}
    holdingInAccounts.addMethod('GET');

    // const holdingInAccounts = holdingAccounts.addResource('{holdingID}');   // holdingAccounts/{{holdingID}}
    // holdingInAccounts.addMethod('GET'); // GET /holdingAccounts/{holdingID}    - get all accounts with given holding

    //#endregion

    //#endregion

    //  REVIEWORDER Microservice
    // Create DDB table to store the tasks.
    const reviewOrderTable = new ddb.Table(this, "tr_ReviewOrder_Table", {
      partitionKey: { name: "userName", type: ddb.AttributeType.STRING },
      // partitionKey: { name: "reviewOrderId", type: ddb.AttributeType.STRING },
      billingMode: ddb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,

    //   timeToLiveAttribute: "ttl",
    });

    // Create Lambda function for the API.
    const reviewOrderLambda = new lambda.Function(this, "tr_ReviewOrder_Lambda", {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset("../api/reviewOrder_lambda.zip"),
      handler: "reviewOrder.handler",
      environment: {
        REVIEWORDER_TABLE_NAME: reviewOrderTable.tableName,
        PRIMARY_KEY: 'userName',
        EVENT_SOURCE: "com.tr.reviewOrder.sendOrder",
        EVENT_DETAILTYPE: "tr_SendOrder",
        EVENT_BUSNAME: "tr_EventBus"
      },
    });

    // Create a URL so we can access the function.
    const reviewOrderFunctionUrl = reviewOrderLambda.addFunctionUrl({
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

    reviewOrderTable.grantReadWriteData(reviewOrderLambda);

    //  Trading Microservice
    // Create DDB table to to process orders.
    const tradingTable = new ddb.Table(this, "tr_Trading_Table", {
      partitionKey: { name: "accountId", type: ddb.AttributeType.STRING },
      sortKey: {name: "tradeProcessedTime", type: AttributeType.STRING},
      // partitionKey: { name: "userName", type: ddb.AttributeType.STRING },
      // sortKey: {name: "orderDate", type: AttributeType.STRING},
      billingMode: ddb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // // Add GSI based on trade processed date/time
    // instrumentTable.addGlobalSecondaryIndex({
    //   indexName: "date-range",
    //   partitionKey: { name: "tradeId", type: ddb.AttributeType.STRING },
    //   sortKey: { name: "tradeProcessedTime", type: ddb.AttributeType.STRING },
    // });

    // Create Lambda function for the API.
    const tradingLambda = new lambda.Function(this, "tr_Trading_Lambda", {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset("../api/trading_lambda.zip"),
      handler: "trading.handler",
      environment: {
        TRADING_TABLE_NAME: tradingTable.tableName,
      },
    });

    
    // // Create a URL so we can access the function.
    // const orderingFunctionUrl = orderingApi.addFunctionUrl({
    //   authType: lambda.FunctionUrlAuthType.NONE,
    //   cors: {
    //     allowedOrigins: ["*"],
    //     allowedMethods: [lambda.HttpMethod.ALL],
    //     allowedHeaders: ["*"],
    //   },
    // });

    // // Output the API function url.
    // new CfnOutput(this, "OrderingAPIUrl", {
    //   value: orderingFunctionUrl.url,
    // });

    tradingTable.grantReadWriteData(tradingLambda);

    // Create a queue to consume from the Event Bus
    const queue = new TQueue(this, 'tr_TradeQueue', {
      consumer: tradingLambda,
    });

    //  Create an Event Bus
    const eventbus = new TEventBus(this, 'tr_EventBus', {
      publisherFuntion: reviewOrderLambda,
      // publisherFuntion: microservices.reviewOrderMicroservice,
      targetQueue: queue.tradeQueue   
    });   

    // Set up API Gateway
    const tradingApi = new LambdaRestApi(this, 'tr_Trading_API', {
      restApiName: 'tr_Trading_API',
      handler: tradingLambda,
      proxy: false,
      deployOptions: {
          // 👇 stage name `dev`
          stageName: 'eng',
      }
    });

    // Set up /trade resource
    const trade = tradingApi.root.addResource('trade');
    // GET /trade?accountID=acc# // defaults to trades since yesterday
    // GET /trade?accountID=acc#&dateRange=1w,1m,3m,6m,1y 
    trade.addMethod('GET');     

    // /trade?accountId-tradeId=123
    // const singleTrade = trade.addResource('{accountId}&{beginDate}&{endDate}');
    // const singleTrade = trade.addResource('{accountId}');

    // singleTrade.addMethod('GET');  // GET /trade/{accountId-tradeId}
    //     // expected request : xxx/trade/vgt?orderDate=timestamp
    //     // ordering ms grap input and query parameters and filter to dynamo db

    // // return singleOrder;

    // const alltrades = tradingApi.root.addResource('alltrades');
    // // alltrades.addMethod('GET');  // GET /trade  

    // const allTradesRes = alltrades.addResource('{accountId}');
    // allTradesRes.addMethod('GET');  // GET /trade/{accountId}
    
  }

}
