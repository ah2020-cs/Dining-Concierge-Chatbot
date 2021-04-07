import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')
fn = getattr(requests, 'post')


def send(url, body=None):
	fn(url, data=body,headers={"Content-Type": "application/json"})

def putRequests():
	resp = table.scan()
	i = 1
	url = ' '
	headers = {"Content-Type": "application/json"}
	while True:
		for item in resp['Items']:
			body = {"RestaurantID": item['insertedAtTimestamp'], "Cuisine": item['cuisine']}
			r = requests.post(url, data=json.dumps(body).encode("utf-8"), headers=headers)
			i += 1
		if 'LastEvaluatedKey' in resp:
			resp = table.scan(
				ExclusiveStartKey=resp['LastEvaluatedKey']
			)
		else:
			break;
	print(i)