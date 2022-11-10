import json
from msilib.schema import Error

'''

event = {'resource': '/order', 'path': '/order', 'httpMethod': 'GET', 'headers': {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9', 'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-ASN': '3356', 'CloudFront-Viewer-Country': 'US', 'Cookie': 'awsccc=eyJlIjoxLCJwIjoxLCJmIjoxLCJhIjoxLCJpIjoiMTRiM2NlMmMtNWQ5Zi00NDcwLTk0Y2MtMWQxOTE0YmY3Njk2IiwidiI6IjEifQ==', 'Host': 'f1q7j05929.execute-api.us-west-2.amazonaws.com', 'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"macOS"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', 'Via': '2.0 48fa2d8b9525abe889eff7ccc8591f7e.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': 'iGgt0K25UwH5rsrVjqIKQ8Tr5bTimgc0G1YVABs3iFjK7PZIZYaXiA==', 'X-Amzn-Trace-Id': 'Root=1-634f17aa-26a3e3516e04451c45965a85', 'X-Forwarded-For': '4.28.107.176, 15.158.63.4', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'], 'Accept-Encoding': ['gzip, deflate, br'], 'Accept-Language': ['en-US,en;q=0.9'], 'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': ['false'], 'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-ASN': ['3356'], 'CloudFront-Viewer-Country': ['US'], 'Cookie': ['awsccc=eyJlIjoxLCJwIjoxLCJmIjoxLCJhIjoxLCJpIjoiMTRiM2NlMmMtNWQ5Zi00NDcwLTk0Y2MtMWQxOTE0YmY3Njk2IiwidiI6IjEifQ=='], 'Host': ['f1q7j05929.execute-api.us-west-2.amazonaws.com'], 'sec-ch-ua': ['"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"'], 'sec-ch-ua-mobile': ['?0'], 'sec-ch-ua-platform': ['"macOS"'], 'sec-fetch-dest': ['document'], 'sec-fetch-mode': ['navigate'], 'sec-fetch-site': ['none'], 'sec-fetch-user': ['?1'], 'upgrade-insecure-requests': ['1'], 'User-Agent': ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'], 'Via': ['2.0 48fa2d8b9525abe889eff7ccc8591f7e.cloudfront.net (CloudFront)'], 'X-Amz-Cf-Id': ['iGgt0K25UwH5rsrVjqIKQ8Tr5bTimgc0G1YVABs3iFjK7PZIZYaXiA=='], 'X-Amzn-Trace-Id': ['Root=1-634f17aa-26a3e3516e04451c45965a85'], 'X-Forwarded-For': ['4.28.107.176, 15.158.63.4'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'cbv1jx', 'resourcePath': '/order', 'httpMethod': 'GET', 'extendedRequestId': 'aOCiqEIPvHcFvYw=', 'requestTime': '18/Oct/2022:21:16:26 +0000', 'path': '/eng/order', 'accountId': '103384195692', 'protocol': 'HTTP/1.1', 'stage': 'eng', 'domainPrefix': 'f1q7j05929', 'requestTimeEpoch': 1666127786425, 'requestId': '03ce132c-567e-4173-893d-036d574f9c67', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '4.29.107.56', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', 'user': None}, 'domainName': 'f1q7kklj929.e-api.us-west-2.amazonaws.com', 'apiId': 'f1q7j05929'}, 'body': None, 'isBase64Encoded': False}

event2 = {'Records': [{'messageId': '136026a4-4d3c-4e75-a5ce-4319bb8aabd5', 'receiptHandle': 'AQEBPB5qEpe28t0magigWDok1p+TGnL7wrleNV6OHh4qeAi2/ZsAlx25qjbrYHVxSxfHNBKPG6n+W6Dqdc+knM2J6V0AA4KIfhR22zL9YKhh/dpKom44jeAw7gMLRqsz8c3wva70vQQndFM3jzKFA39xSldqR7YmNCgP4p4dURUOWllCExG2fouv3OMmZ8eUEarPYenktCK440z/5GEIByFBvUrz7wfyDtVvSYI5J5nsVciIvUMB0NbwcjzB5dKTYXQg3LKupjqvgMyKXDDpbLpee/AWyZrAvgr4exaViQulnwImoJFQ+U1HGIgt4fbMUncDdd8X5aaYWSVPZORaMml2UV7BgFb952zOQKz687rLB6K6BHmcMGFtuc1ygmv25f5VZXBr0V6nI8ElnnKffz1ZDQ==', 'body': '{"version":"0","id":"0e5ff78d-42de-a0d5-d023-b777c4cb0f86","detail-type":"tr_SendOrder","source":"com.vgt.reviewOrder.sendOrder","account":"103384195692","time":"2022-10-17T22:56:59Z","region":"us-west-2","resources":[],"detail":{"username":"tester","total":"1000"}}', 'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1666047420059', 'SenderId': 'AIDAIE6VAXUQU2DKHA7DK', 'ApproximateFirstReceiveTimestamp': '1666047420067'}, 'messageAttributes': {}, 'md5OfBody': '450b09b1841e7a776459976f1eaff02f', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:us-west-2:1312xyz:tr_OrderQueue', 'awsRegion': 'us-west-2'}]}

    

'''
def handler(event, context):
  print("Event:", event)
  print("Context:", context)
  # message = 'Hello {} {}!'.format(event['first_name'], event['last_name'])  
  # return { 
  #     'message' : "Hello there"
  # }

  try :
      # Check if it's an api gateway invocation
      hm = event['httpMethod']
      print(hm)
      return apiGatewayInvocation(event)
  except KeyError as ke:
      print("key error", ke)
      # e2m = json.loads(event2)
      try:
        body = event['Records'][0]['body']
        print (body)
        bodyD = json.loads(body)
        detail_type = bodyD['detail-type']
        print(detail_type)
        if (detail_type == 'tr_SendOrder'):
          print ("Order Request")
          eventBridgeInvocation(bodyD['detail'])
      except Exception as e:
        print("Error Occured while processing non http request: ", e)


def eventBridgeInvocation(eventDetailDict):
  print ("Event Bridge invocation")
  processOrder(eventDetailDict)
  # return { 
  #     'message' : "Async there"
  # }

async def processOrder(eventDetailDict):
  print("Process Order for: ", eventDetailDict)
  

def apiGatewayInvocation(event):
  print ("API Gateway invocation")
  return { 
      'message' : "Sync Call"
  }
