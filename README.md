# Dining-Concierge-Chatbot 

# Summary

Dining Concierge Chatbot is an AWS-based serverless cloud application that sends you restaurant suggestions given a set of preferences that you provide the chatbot with through conversation.

  -Based on a conversation with the customer, LEX chatbot will identify the customer's preferred 'cuisine'.

  -Then it will search a dynamo DB database through Elastic Search to get random suggestions of restaurant IDs with this cuisine.
  
  -AWS services used:
    S3
    API Gateway
    Lambda
    Lex
    SQS
    SNS
    Elastic Search
    DynamoDB
    
    
- Architecture Diagram

![Overview](overview.png)
