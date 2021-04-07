import boto3
import datetime
import dateutil.parser
import time
import json
import os
import math
import logging
from botocore.vendored import requests


def lambda_handler(event, context):
	os.environ['TZ'] = 'America/New_York'
	time.tzset()
	return dispatch(event)

def get_slots(intent_request):
	return intent_request['currentIntent']['slots']

def build_validation_result(is_valid, violated_slot, message_content):
	#function to build a response based on inputs
	if message_content is None:
		return {
			"isValid": is_valid,
			"violatedSlot": violated_slot
		}

	return {
		'isValid': is_valid,
		'violatedSlot': violated_slot,
		'message': {'contentType': 'PlainText', 'content': message_content}
	}

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
	#funtion to elicit a user input
	return {
		'sessionAttributes': session_attributes,
		'dialogAction': {
			'type': 'ElicitSlot',
			'intentName': intent_name,
			'slots': slots,
			'slotToElicit': slot_to_elicit,
			'message': message
		}
	}

def valid_date(date):
	#date validation function
	try:
		dateutil.parser.parse(date)
		return True
	except ValueError:
		return False

def parse_int(n):
	#basic int validation for numbers entered 
	try:
		return int(n)
	except ValueError:
		return float('nan')

def delegate(session_attributes, slots):
	return {
		'sessionAttributes': session_attributes,
		'dialogAction': {
			'type': 'Delegate',
			'slots': slots
		}
	}


def dispatch(intent_request):
	#to dispatch the 3 intents
	if intent_name == 'GreetingIntent':
		return greeting_intent(intent_request)
	elif intent_name == 'DiningIntent':
		return dining_intent(intent_request)
	elif intent_name == 'ThankyouIntent':
		return thankyou_intent(intent_request)
	raise Exception('This intent is not supported.')

def greeting_intent(intent_request):
	#greeting intent return
	return {
		'dialogAction': {
			"type": "ElicitIntent",
			'message': {
				'contentType': 'PlainText',
				'content': 'Hello!, how can I assist you today?'}
		}
	}

def thankyou_intent(intent_request):
	#thankyou intent return
	return {
		'dialogAction': {
			"type": "ElicitIntent",
			'message': {
				'contentType': 'PlainText',
				'content': 'Your\'re Welcome. Have a great day!'}
		}
	}

def validate_dining_suggestion(location, cuisine, num_people, date, time):
	#validation of user inputs

	locations = ['new york', 'manhattan']
	if location is not None and location.lower() not in locations:
		return build_validation_result(False,
									   'location',
									   'Sorry! We are only serving New York City right now.')


	cuisine = ['indian', 'chinese', 'american', 'mexican', 'italian', 'mediterranean']

	if cuisine is not None and cuisine.lower() not in cuisines:
		return build_validation_result(False,
									   'Cuisine',
									   'We currently do not offer this cuisine.')

	if num_people is not None:
		num_people = int(num_people)
		if num_people > 20 or num_people < 0:
			return build_validation_result(False,
										   'NumberOfPeople',
										   'We are currently only booking for up to 20 people.')

	if date is not None:
		if not valid_date(date):
			return build_validation_result(False, 'Date',
										   'Please try entering your preferred time again.')
		elif datetime.datetime.strptime(date, '%Y-%m-%d').date() <= datetime.date.today():
			return build_validation_result(False, 'Date', 'Please enter a date that has not passed.')

	if time:
		hour, minute = time.split(':')
		hour = parse_int(hour)
		minute = parse_int(minute)
		if math.isnan(hour) or math.isnan(minute):
			return build_validation_result(False, 'time', 'Invalid value entered')

	return build_validation_result(True, None, None)


def dining_suggestion_intent(intent_request):
	#dining suggestion produced here

	location = get_slots(intent_request)["location"]
	cuisine = get_slots(intent_request)["cuisine"]
	num_people = get_slots(intent_request)["num_people"]
	date = get_slots(intent_request)["date"]
	time = get_slots(intent_request)["time"]

	source = intent_request['invocationSource']

	if source == 'DialogCodeHook':
		slots = get_slots(intent_request)

		dining_validation = validate_dining_suggestion(location, cuisine, num_people, date, time)

		if not dining_validation['isValid']:
			slots[dining_validation['violatedSlot']] = None
			return elicit_slot(intent_request['sessionAttributes'],
							   intent_request['currentIntent']['name'],
							   slots,
							   dining_validation['violatedSlot'],
							   dining_validation['message'])

		if intent_request['sessionAttributes'] is not None:
			session_output = intent_request['sessionAttributes']
		else:
			session_output = {}

		return delegate(session_output, get_slots(intent_request))


	phone = get_slots(intent_request)["phone"]
	sqs = boto3.resource('sqs')

	queue = sqs.get_queue_by_name(QueueName='restaurant')
	msg = {"cuisine": cuisine, "phone": phone}
	response = queue.send_message(MessageBody=json.dumps(msg))
	# Add Yelp API endpoint to get the data
	requestData = {
					 "term":cuisine+", restaurants",
					 "location":location,
					 "categories":cuisine,
					 "limit":"3",
					 "peoplenum": num_people,
					 "Date": date,
					 "Time": time
				  }


	resultData = yelp_api(requestData)

	return close(intent_request['sessionAttributes'],
				 'Fulfilled',
				 {'contentType': 'PlainText',
				  'content': 'Thank you! You will recieve a suggestion soon.'})

def yelp_api(request):

	url = "https://api.yelp.com/v3/businesses/search"
	query = request

	payload = ""
	headers = {
		'Authorization': "Bearer --",
		'cache-control': "no-cache"
	}

	response = requests.request("GET", url, data=payload, headers=headers, params=request)

	message = json.loads(response.text)

	if len(message['businesses']) < 0:
		return 'We were unable to find any restaurants.'

	finalStr = "Hello! These are my " + request['categories'] + " restaurant suggestions for " + request[
		'peoplenum'] + " people, for " + request['Date'] + " at " + request['Time'] + ". "
	count = 1
	for business in message['businesses']:
		finalStr = finalStr + " " + str(count) + "." + business['name'] + ", located at " + business['location'][
			'address1'] + " "
		count += 1

	return final
