
import boto3
import os
import logging
import json
import urllib.parse
import xmltodict
import xml.etree.cElementTree as xml
import jsondiff

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

AASTOPIC = os.environ.get('AASTOPIC')
AAS3NAME = os.environ.get('AAS3NAME')
AASAOCDTABLE =  os.environ.get('AASAOCDTABLE')

def lambda_handler(event, context):

    if context:
        LOGGER.debug('Function ARN: %s', context.invoked_function_arn)
    else:
        LOGGER.warning('Lambda context is missing')
        
    LOGGER.info(json.dumps(event))
    
    # Get the service resource
    sns = boto3.resource('sns')
    s3 = boto3.client('s3')
    db = boto3.resource('dynamodb')

    #Get the table
    table = db.Table(AASAOCDTABLE)
    
    # Get the queue
    topic = sns.Topic(AASTOPIC)
    
     # Get the object from the event 
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    
    # Get the object from s3
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        
        # full response
        LOGGER.info("s3 Object:")
        LOGGER.info(response)
        
        #read body from StreamingBody
        body = response['Body'].read().decode('utf-8')
        LOGGER.info("BODY: " + body)
        
        #parse xml string to json and then to string
        msgdict = xmltodict.parse(body)
        msg = json.dumps(msgdict)
        
        #parse the xml string into an xml tree object
        tree = xml.fromstring(body)
        #build json string from the xml tree object
        #msg = buildJSONfromXML(tree)
       
        #extract keys from xml
        tasin = tree.findall(".//NotificationPayload/AnyOfferChangedNotification/OfferChangeTrigger/ASIN")
        for i in tasin:
            tasin = i.text
            LOGGER.info("ASIN: " + tasin)    
   
        tsell = tree.findall(".//NotificationMetaData/SellerId")
        for i in tsell:
            tsell = i.text
            LOGGER.info("SellerId: " + tsell)
        
        #query the ddb to find latest offer status
        dbresponse = table.get_item(
            Key={
                 'SellerId': tsell,
                 'ASIN' : tasin
                }
        )
        LOGGER.info(json.dumps(dbresponse))
        if len(dbresponse) == 1:
            LOGGER.info("Single Node response: Item not found")
            for k in dbresponse:
                LOGGER.info("Request singleton node: " + k)
        elif len(dbresponse) > 1:
            dbdict = dbresponse['Item']['Data']
            
            #calculate delta
            #compdbd = makeset("key",dbdict)
            #compmsgd = makeset("key",msgdict)
            
            #diffkeys = [k for k in dict1 if dict1[k] != dict2[k]]
            deltastr = ""
            #deltastr += "-x-ASIN: " + tasin + "-x-" + "SELLER: " + tsell + "-x-"
            deltastr += "-x-ASIN: " + tasin + "-x-" 
            deltastr += calculateDelta(dbdict,msgdict)
           
            #if len(delta) > 0:
            #    for t in delta:
            #        deltastr += t + " | "
                    
            
            #build delta message
            #deltastr = "".join(delta)
            
            deltastr = '{ "body": "'+deltastr+'" }'
            #LOGGER.info("Length db msg:" + str(len(compdbd)))
            #LOGGER.info("Length s3 msg:" + str(len(compmsgd)))
            LOGGER.info("DELTA: " + deltastr)
            
            #insert in db
            insertion = table.put_item(
                Item={
                    'SellerId' : tsell,
                    'ASIN' : tasin,
                    'Data' : msgdict
                }
            )
            LOGGER.info("Insertion result: " + json.dumps(insertion))
        
        subj = "Offer changed:"
        
        if deltastr == "": deltastr = '{ "body": "items identical" }'
        
        response = topic.publish(
            Subject=subj,
            Message=deltastr
            #Message=msg
        )
        
        
        return 
        
    except Exception as e:
        print("Exception:")
        print(e)
        #print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        raise e
        
def calculateDelta(dict1, dict2):
    diff = 0
    #builds a dict of differences between the two dicts
    md1 = dict1["Notification"]["NotificationMetaData"]
    md2 = dict2["Notification"]["NotificationMetaData"]
    mddelta = "-x-"
    for k in md1: 
        if md1[k] != md2[k]:
            #mddelta += k + ":-x- " + md1[k] + " >-x-" + md2[k] + "-x-"
            diff = 1
    if diff == 0:
        return "Repeat notification, please ignore."
    LOGGER.info(mddelta)
    #new offers Amazon
    old = dict1["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["NumberOfOffers"]["OfferCount"][0]["#text"]
    new = dict2["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["NumberOfOffers"]["OfferCount"][0]["#text"]
    if new != old: mddelta += "Offer by Amazon for new products:-x-"+ old +" > " + new + "-x-"
    #new offers Merchant
    old = dict1["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["NumberOfOffers"]["OfferCount"][1]["#text"]
    new = dict2["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["NumberOfOffers"]["OfferCount"][1]["#text"]
    if new != old: mddelta += "Offers by merchants for new products:-x-"+ old +" > " + new + "-x-"
    #collect offers
    old = dict1["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["NumberOfOffers"]["OfferCount"][2]["#text"]
    new = dict2["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["NumberOfOffers"]["OfferCount"][2]["#text"]
    if new != old: mddelta += "Offers for collectible products:-x-"+ old +" > " + new + "-x-"
    #new offers
    # old = dict1["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["NumberOfOffers"]["OfferCount"][3]["#text"]
    # new = dict2["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["NumberOfOffers"]["OfferCount"][3]["#text"]
    # if new != old: mddelta += "OfferCount for used products was "+ old +", is " + new + "-x-"
    
    #no1 = dict1["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["LowestPrices"]["LowestPrice"][0]
    #no2 = dict2["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["LowestPrices"]["LowestPrice"][0]
    
    #new lowest Amazon
    old = dict1["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["LowestPrices"]["LowestPrice"][0]["LandedPrice"]["Amount"]
    new = dict2["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["LowestPrices"]["LowestPrice"][0]["LandedPrice"]["Amount"]
    if new != old: mddelta += "Lowest price by Amazon for new products:-x-"+ old +" > " + new + "-x-"
    #new lowest Merchant
    old = dict1["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["LowestPrices"]["LowestPrice"][1]["LandedPrice"]["Amount"]
    new = dict2["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["LowestPrices"]["LowestPrice"][1]["LandedPrice"]["Amount"]
    if new != old: mddelta += "Lowest price by merchants for new products:-x-"+ old +" > " + new + "-x-"
    #lowest collect
    #old = dict1["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["LowestPrices"]["LowestPrice"][2]["LandedPrice"]["Amount"]
    #new = dict2["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["LowestPrices"]["LowestPrice"][2]["LandedPrice"]["Amount"]
    #if new != old: mddelta += "Lowest price for collectible products was "+ old +", is " + new + "-x-"
    
    #new rank
    old = dict1["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["SalesRankings"]["SalesRank"][0]["Rank"]
    new = dict2["Notification"]["NotificationPayload"]["AnyOfferChangedNotification"]["Summary"]["SalesRankings"]["SalesRank"][0]["Rank"]
    if new != old: mddelta += "Sales rank:-x-"+ old +" > " + new + "-x-"
    
    
    #mddelta += "Prices"
    #for k in no1: 
    #    if no1[k] != no2[k]:
    #        mddelta += k + " was " + no1[k] + ", is " + no2[k] + "-x-"
    #LOGGER.info(mddelta)
    return mddelta
    
    
    
def buildJSONfromXML(tree):
    #XPath example 
    subj = ''
    tempasin = tree.findall(".//ASIN")
    tempid = tree.findall(".//TimeOfOfferChange")
    tempcond = tree.findall(".//ItemCondition")
    
    for i in tempid:
        LOGGER.info("Time: " + i.text)
        subj += '-x-*Time:* ' + i.text
    for i in tempasin:
        LOGGER.info("ASIN: " + i.text)
        subj += '-x-*ASIN:* ' + i.text
    for i in tempcond:
        LOGGER.info("Cond: " + i.text)
        subj += '-x-*Cond:* ' + i.text
    
    msg = '' + subj
    tempmsg = tree.findall(".//LowestPrices/LowestPrice[@condition='new']/LandedPrice/Amount")
    for j in tempmsg:
        LOGGER.info("LowestPrice: " + j.text)
        msg += '-x-*LowestPrice:* ' + j.text + ' '
        
    temprank = tree.findall(".//SalesRankings/SalesRank[1]/Rank")
    for k in temprank:
        LOGGER.info("Rank: " + k.text)
        msg += '-x-*Rank:* ' + k.text + ' '
    
    msg = '{"text": "' + msg + '"}'
    return msg
    
    
def makeset(c,d):
    st = set()
    subst =set()
    if isinstance(d,list):
        for k in d:
            if isinstance(k, dict):
                for f, g in k.items():
                    LOGGER.info("key: " + f)
                    if not isinstance(g,dict): LOGGER.info("value: " + g)
                    subst = makeset(f,g)
                    st |= subst
    elif isinstance(d, dict):
        for k, v in d.items():
            LOGGER.info("key: "+ k )
            subst = makeset(k,v)
            st |= subst
    else:
        st |= set((c,d))
    return st