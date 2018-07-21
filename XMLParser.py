
import boto3
import os
import logging
import json
import xmltodict

#Uses xmltodict by martinblech (https://github.com/martinblech/xmltodict) 
#Distributed under the MIT license which allows commercial and private use, distribution and modification


# create logger (logs can be found in CloudWatch)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

# get function environmental variables
MWSQUEUE = os.environ.get('AAQUEUE')
MWSMAXMSG =  int(os.environ.get('AASMAXMSG'))

def lambda_handler(event, context):
	
	# uncomment to output function event and context to logs
    #if context:
    #    LOGGER.debug('Function ARN: %s', context.invoked_function_arn)
    #else:
    #    LOGGER.warning('Lambda context is missing')    
    #LOGGER.info(json.dumps(event))
	
    # create  sqs service resource 
    sqs = boto3.resource('sqs')
    
    # get queue 
    queue = sqs.Queue(MWSQUEUE)
    
    # parse xml messages and print xml and json versions to log
    for message in queue.receive_messages(MaxNumberOfMessages=MWSMAXMSG):
        
		#parse xml string to json and then to string
        msgdict = xmltodict.parse(body)
        dictdump = json.dumps(msgdict)
        
		#output data to log
        LOGGER.info('__________________________________________')
        LOGGER.info('Message ID:')
        LOGGER.info(message.message_id)
		LOGGER.info('Message Body in XML:')
        LOGGER.info(message.body)
		LOGGER.info('Message Body as a dict:')
        LOGGER.info(dictdump)
        LOGGER.info('__________________________________________')
    
        # Let the queue know that the message is processed
        message.delete()
    
   
        
    return 
        
    
  