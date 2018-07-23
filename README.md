MWS Alerts Consumer
==============================================

This is a Serveless AWS app that composed of an SQS queue, a Lambda function and an SNS Topic. 
The SQS queue is registered with Amazon's MWS api to receive notifications which are then consumed by the Lambda function. The function parses the XML file, transforms it to a dictionary object, dumps the object to a JSON format. It then publishes the JSON string to an email subscription on the SNS Topic.


![Application Architecture](https://raw.githubusercontent.com/depeupleur/MWS-Alerts-SQS-XML-Lambda-Consumer/master/MWSConsumerAppArchitecture.png)


What's in this project
----------------------

This app includes:

* README.md - this file
* buildspec.yml - this file is used by AWS CodeBuild to package your
  application for deployment to AWS Lambda
* XMLParser.py - this file contains the code to consume the SQS event, 
  parse the XML contents, and send the results to SNS
* template.yml - this file contains the AWS Serverless Application Model (AWS SAM) used
  by AWS CloudFormation to deploy your application to AWS Lambda and Amazon API
  Gateway.
* SQSTestEvent.json - this file can be copied into a Lambda test event to test the XMLParser function
* SQSTestMessageBody.xml - this file can be copied into the AWS SQS SendMessage Console 
  to produce a testable SQS Message Event.
* xmltodict - this file and library are used to parse XML to dictionary objects and are distributed 
  under the MIT license by Martin Blech and contributors.
* MWSConsumerAppArchitecture - this file contains the application architecture diagram displayed above.

How to configure this app
-------------------------


What is Amazon Marketplace Web Service (MWS)
--------------------------------------------

Amazon Marketplace Web Service (Amazon MWS) is an integrated web service API that helps Amazon sellers to programmatically exchange data on listings, orders, payments, reports, and more. Data integration with Amazon enables high levels of selling automation, which can help sellers grow their business. By using Amazon MWS, sellers can increase selling efficiency, reduce labor requirements, and improve response time to customers.

There are no fees associated with Amazon MWS, but to use the Amazon MWS API you must have an Amazon MWS-eligible seller account and you must register to use Amazon MWS.

https://developer.amazonservices.com/

What API allows me to subscribe to receive alerts from MWS
---------------------------------------------

The Amazon MWS Subscriptions API section enables you to subscribe to receive notifications that are relevant to your business with Amazon. With the operations in the Subscriptions API section, you can receive important information from Amazon without having to poll the Amazon MWS service. Instead, the information is sent directly to you when an event occurs to which you are subscribed.

Registering a destination
-------------------------

The RegisterDestination operation (part of the MWS Subscriptions API) specifies a location where you want to receive notifications and adds it to the list of registered destinations. For more information on what kinds of destinations can be specified, see Receiving notifications.

After you register a Destination, you must create a Subscription by calling the CreateSubscription operation to begin receiving notifications.

Note: After you register a Destination, Amazon recommends that you call the SendTestNotificationToDestination operation to verify that you can receive notifications.
To remove a Destination that you have registered from the list of registered destinations, call the DeregisterDestination operation.

To register a destination please refer to the reference documentation here: http://docs.developer.amazonservices.com/en_US/subscriptions/Subscriptions_RegisterDestination.html

Example request for registering a destination
---------------------------------------------

POST /Subscriptions/2013-07-01 HTTP/1.1
Content-Type: x-www-form-urlencoded
Host: mws.amazonservices.com
User-Agent: <Your User Agent Header>

AWSAccessKeyId=AKIAEEXAMPLESA
&Action=RegisterDestination
&Destination.AttributeList.member.1.Key=sqsQueueUrl
&Destination.AttributeList.member.1.Value=
  https%3A%2F%2Fsqs.us-east-1.amazonaws.com%2F51471EXAMPLE%2Fmws_notifications
&Destination.DeliveryChannel=SQS
&MWSAuthToken=amzn.mws.4ea38b7b-f563-7709-4bae-87aeaEXAMPLE
&MarketplaceId=ATVPDKIKX0DER
&SellerId=A135KEXAMPLE56
&SignatureMethod=HmacSHA256
&SignatureVersion=2
&Timestamp=2013-07-25T16%3A14%3A01Z
&Version=2013-07-01
&Signature=WgTRuEXAMPLEeIzoJ5tzX06uKV7ongzUserZ6vj8kug%3D

Sending the request to the MWS Subscriptions API
------------------------------------------------

You can use the Amazon MWS to send the registration request to the API:

https://mws.amazonservices.com/scratchpad/index.html


