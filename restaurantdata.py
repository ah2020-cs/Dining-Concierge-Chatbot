import boto3
import datetime
import json
from botocore.vendored import requests
from decimal import *
from elasticSearch import putRequests
from time import sleep
from urlparse import urljoin

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')

API_KEY = '6RGMMDt32XYksV-7zUBFrMPWQ1wmP5Lc-shxun5fd_tmH8_DFajMlB-0XAr7Yol16j6dFIqFEf11BPZHaAVYiGgPrFYgRD0Bqs4vexKbG8hc2JsPaOW9FxAPmZJAYHYx'

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'Manhattan'
restaurants = {}


def search(cuisine, offset):
    url = {
        'location': DEFAULT_LOCATION,
        'offset': offset,
        'limit': 50,
        'term': cuisine + " restaurants",
        'sort_by': 'rating'
    }
    return request(API_HOST, SEARCH_PATH, url_params=url)


def request(host, path, url_params=None):
    url_params = url_params or {}
    url = urljoin(host, path)
    headers = {
		'Authorization': "Bearer 6RGMMDt32XYksV-7zUBFrMPWQ1wmP5Lc-shxun5fd_tmH8_DFajMlB-0XAr7Yol16j6dFIqFEf11BPZHaAVYiGgPrFYgRD0Bqs4vexKbG8hc2JsPaOW9FxAPmZJAYHYx",
		'cache-control': "no-cache"
    }
    response = requests.request('GET', url, headers=headers, params=url_params)
    rjson = response.json()
    return rjson

def scrape():
    cuisines = ['indian', 'chinese', 'american', 'mexican', 'italian', 'mediterranean']
    for cuisine in cuisines:
        offset = 0
        while offset < 1000:
            js = search(cuisine, offset)
            addItems(js["businesses"], cuisine)
            offset += 50


def addItems(data, cuisine):
    global restaurants
    with table.batch_writer() as batch:
        for rec in data:
            try:
                if rec["alias"] in restaurants:
                    continue;
                rec["rating"] = Decimal(str(rec["rating"]))
                restaurants[rec["alias"]] = 0
                rec['cuisine'] = cuisine
                rec['insertedAtTimestamp'] = str(datetime.datetime.now())
                rec["coordinates"]["latitude"] = Decimal(str(rec["coordinates"]["latitude"]))
                rec["coordinates"]["longitude"] = Decimal(str(rec["coordinates"]["longitude"]))
                rec['address'] = rec['location']['display_address']
                rec.pop("distance", None)
                rec.pop("location", None)
                rec.pop("transactions", None)
                rec.pop("display_phone", None)
                rec.pop("categories", None)
                if rec["phone"] == "":
                    rec.pop("phone", None)
                if rec["image_url"] == "":
                    rec.pop("image_url", None)
                batch.put_item(Item=rec)
                sleep(0.001)
            except Exception as e:
                print(e)
                print(rec)


def lambda_handler(event, context):
    putRequests()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }



