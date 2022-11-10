from time import sleep
import boto3

# Create SQS client
sqs = boto3.client('sqs')

SQS_QUEUE_URL = "https://sqs.us-west-2.amazonaws.com/103384195692/tr_OrderQueue"
queue_url = SQS_QUEUE_URL

# Send message to SQS queue
# response = sqs.send_message(
#     QueueUrl=queue_url,
#     DelaySeconds=0,
#     MessageAttributes={
#         'Title': {
#             'DataType': 'String',
#             'StringValue': 'The Whistler'
#         },
#         'Author': {
#             'DataType': 'String',
#             'StringValue': 'John Grisham'
#         },
#         'WeeksOn': {
#             'DataType': 'Number',
#             'StringValue': '1'
#         }
#     },
#     MessageBody=(
#         'Information about current NY Times fiction bestseller for '
#         'week of 12/11/2016.'
#     )
# )

# print(response['MessageId'])

# sleep(5)

# Receive message from SQS queue
responseR = sqs.receive_message(
    QueueUrl=queue_url,
    AttributeNames=[
        'SentTimestamp'
    ],
    MaxNumberOfMessages=1,
    MessageAttributeNames=[
        'All'
    ],
    VisibilityTimeout=0,
    WaitTimeSeconds=0
)

print("Response:", responseR)

message = responseR['Messages'][0]
receipt_handle = message['ReceiptHandle']

# Delete received message from queue
sqs.delete_message(
    QueueUrl=queue_url,
    ReceiptHandle=receipt_handle
)
print('Received and deleted message: %s' % message)