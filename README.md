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

1. Find the Endpoint line in template.yml as shown below and replace with your email address:
		#replace with the email that should be notified with the alerts
		Endpoint: 'user@email.com'
2. Subscribe to the MWS Subscription API as shown below under the MWS section (you must be an Amazon Seller or have access to an Amazon Seller professional account)

How to test this app
--------------------

Once your app has been deployed you can test the XMLParser Lambda function like this:
1. Click Configure Test Evenets next to the Test Button in the AWS Lambda Console
2. Click Create New Test Event
3. Provide a name for the New Test Event
4. Copy the contents of the SQSTestEvent.json into the text field 
5. Click Save
6. Click Test on the AWS Lambda Console

Once you have completed this test, you can test the SQS Event like this:
1. Open the SQS AWS Console.
2. Select the MWSQueue
3. From Queue Actions, select Send a Message
4. Copy the contents of SQSMessageBody.xml into the Body text field
5. Click Send Message

Once you complete this test you can go ahead and cofigure the app as described below.


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

Example POST request for registering a destination
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

Sending the register destination request to the MWS Subscriptions API
------------------------------------------------

You can use the Amazon MWS to send the registration request to the API:

https://mws.amazonservices.com/scratchpad/index.html

Use the following values:

API Section: Subscriptions
Operation: RegisterDestination
SellerId: (Your sellerId found in the permissions section of Settings in SellerCentral)
AWSAccessKeyId: (AccessKeyId generated n the user permissions section of Settings in SellerCentral)
SecretKey: (AccessKeyId generated n the user permissions section of Settings in SellerCentral)
MarketplaceId: (MarketplaceId value as per this list https://docs.developer.amazonservices.com/en_IT/dev_guide/DG_Endpoints.html )
Destination.DeliveryChannel: SQS
Destination.AttributeList.member.1.Key: (sqsQueueUrl)
Destination.AttributeList.member.1.Value: (the sqsQueueUrl found in the environmental variables section in your Lambda function)

Creating a Subscription
-----------------------

The CreateSubscription operation indicates that the specified notification type should be delivered to the specified Destination. Before you can subscribe, you must first register the Destination by calling the RegisterDestination operation.

Note: After you register a Destination, Amazon recommends that you call the SendTestNotificationToDestination operation to verify that you can receive notifications.

Read more here: http://docs.developer.amazonservices.com/en_US/subscriptions/Subscriptions_CreateSubscription.html

Example POST request for creating a subscription
------------------------------------------------

POST /Feeds/2009-01-01 HTTP/1.1
Content-Type: x-www-form-urlencoded
Host: mws.amazonservices.com
User-Agent: <Your User Agent Header>

AWSAccessKeyId=0PExampleR2
&Action=CancelFeedSubmissions
&FeedSubmissionIdList.Id.1=1058369303
&FeedTypeList.Type.1=_POST_PRODUCT_DATA_
&FeedTypeList.Type.2=_POST_PRODUCT_PRICING_DATA_
&MWSAuthToken=amzn.mws.4ea38b7b-f563-7709-4bae-87aeaEXAMPLE
&Marketplace=ATExampleER
&SellerId=A1ExampleE6
&SignatureMethod=HmacSHA256
&SignatureVersion=2
&Timestamp=2009-02-04T17%3A34%3A14.203Z
&Version=2009-01-01
&Signature=0RExample0%3D

Sending the subscription request to the MWS Subscriptions API
------------------------------------------------

You can use the Amazon MWS to send the registration request to the API:

https://mws.amazonservices.com/scratchpad/index.html

Use the following values:

API Section: Subscriptions
Operation: CreateSubscription
SellerId: (Your sellerId found in the permissions section of Settings in SellerCentral)
AWSAccessKeyId: (AccessKeyId generated n the user permissions section of Settings in SellerCentral)
SecretKey: (AccessKeyId generated n the user permissions section of Settings in SellerCentral)
MarketplaceId: (MarketplaceId value as per this list https://docs.developer.amazonservices.com/en_IT/dev_guide/DG_Endpoints.html )
Subscription.NotificationType: (pick one of the three available)
Destination.DeliveryChannel: SQS
Destination.AttributeList.member.1.Key: (sqsQueueUrl)
Destination.AttributeList.member.1.Value: (the sqsQueueUrl found in the environmental variables section in your Lambda function)
Subscription.IsEnabled: true

Confirmation of setup
---------------------

You can verify that your queue is properly subscribed by running the ListSubscription operation on the ScratchPad. 
In the AWS SQS Console you should see messages coming in and being consumed by your function as they do. 

Congratulations, your setup is complete!