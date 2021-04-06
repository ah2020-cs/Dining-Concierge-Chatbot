import boto3
import json

client = boto3.client('lex-runtime')

def lambda_handler(event, context):
	userMessage = event["message"]
	userId = event["userId"]
	botError = "Message Error"

	if userMessage is None or len(userMessage) < 1:
		return {'statusCode': 200,'body': json.dumps(botError)}

	response = client.post_text(botName='DiningConciergeBot', botAlias='DCB', 
		userId=userId, inputText=userMessage)

	if response['message'] is not None or len(response['message']) > 0:
		userMessage = response['message']

	return {'statusCode': 200,'body': json.dumps(userMessage)}


def lambda_handler(event, context):
	user_id, text = get_info_from_request(event)
	if user_id is None or text is None:
	print("error")
	chatbot_text = get_chatbot_response(user_id, text)
	if chatbot_text is None:
		return "Error"
	else:
		return get_success_response(chatbot_text, user_id)



