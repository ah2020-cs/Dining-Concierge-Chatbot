import json
import random
import boto3
from boto3.dynamodb.conditions import Key
from botocore.vendored import requests

API_KEY = '  '

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # enter Business ID
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 1

def lambda_handler(event, context):
	pollSNS()


def pollSNS():

	sqs = boto3.client('sqs')
	sns = boto3.client('sns')

	queues = sqs.list_queues(QueueNamePrefix='restraunts')  # we filter to narrow down the list
    test_queue = queues['QueueUrls'][0]

	while True:

		response = sqs.recieve_message(
			QueueUrl=test_queue,
            AttributeNames=['All'],
            MaxNumberOfMessages=10,
            MessageAttributeNames=['All'],
            VisibilityTimeout=30,
            WaitTimeSeconds=0
        )

        if 'Messages' in response:  
            for message in response['Messages']: 
            	js = json.loads(message['Body'])

            	cuisine = js['cuisine']
                phone = js['phone']

                url = 'https://...' + cuisine #enter our url here
                response2 = requests.get(url, headers={"Content-Type": "application/json"}).json()

                value = response2['hits']["total"]
                x = random.randint(0, value - 1)

                url2 = 'https://...' + str( #enter our url here but in seperate pieces
                	x) + 'we need to parse end of url here since we are slicing the string here' + cuisine

                response2 = requests.get(url2, headers={"Content-Type": "application/json"}).json()

                res = response2['hits']['hits'][0]['_source']['RestaurantID']

                db_res = table.query(KeyConditionExpression=Key('insertedAtTimestamp').eq(res))
                #print(db_res)

                sqs.delete_message(QueueUrl=test_queue, ReceiptHandle=message['ReceiptHandle'])

                address = str(db_res['Items'][0]['address'])

                for char in "'u[]":
                    address = addr.replace(char, '')

                message = 'We have selected:' + 'Restaurant Name: ' + db_res['Items'][0]['name'] + 'Address: ' + address

                txt = sns.publish(PhoneNumber=str(phone), Message=message)
                # print(str(txt))

        else:
            print('Queue is empty')
            break

