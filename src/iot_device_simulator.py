# Python AWS IoT Device Simulation
# Martin John Madsen
# 
# This python code simulates a device that is looking for resource optimization.
# It choses a set of random resources, then queries the IoT hub to get a prediction as to 
# which set of resources would be the best, then tries them. Finally, it reports the outcome
# of the resources back to the IoT hub.

# Import libraries
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import getopt
import json
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords # Import the stop word list


# Set up MQTT Communications parameters
# Note that the certificate and private keys must be obtained from the AWS IoT hub

useWebsocket = False
host = "XXX.iot.us-east-1.amazonaws.com"
rootCAPath = "pca.pem"
certificatePath = "XXX-certificate.pem.crt"
privateKeyPath = "XXX-private.pem.key"""

nrequests = 20
timeout = 60

#load in dataset of previous movies. I use this to "invent" new movie combinations
df = pd.read_csv("../data/movie_ratings_simple.csv")

#----------------------------------
#
# Build a random title from previous titles
#
#----------------------------------
titlelist = " ".join(df['title'])

# Use regular expressions to do a find-and-replace
letters_only = re.sub("[^a-zA-Z]",           # The pattern to search for
                      " ",                   # The pattern to replace it with
                      titlelist )  # The text to search

words = [x.lower().strip() for x in letters_only.split(" ")]
words = [x for x in words if x != '']

stops = set(stopwords.words("english")) 
# Remove stop words
meaningful_words = [w for w in words if not w in stops]

#Use this to get a new random title for a film
def getTitle(meaningful_words):
    wordseries=pd.Series(meaningful_words)
    newstring = ' '.join(wordseries.sample(n=np.random.randint(1,5)))
    prefixrand = np.random.randint(0,4)
    if prefixrand == 2:
        newstring = 'the ' + newstring
    elif prefixrand == 3:
        newstring = 'a ' + newstring
    return newstring.title()

	
#----------------------------------
#
# Get three random genres (could be 'None' for second and third)
#
#----------------------------------

def getGenres(df):
    #Get genre options from a dataframe
    genrechoices = []
    for k in range(4):
        g1 = df['Genre1'].sample(n=1).values[0]
        g2 = g1
        g3 = g1
        while g2 == g1:
            g2 = df['Genre2'].sample(n=1).values[0]
        if g2 == 'None':
            g3 = 'None'
        else:
            g3 = g1
            g3 = g2
            while g3 == g1 or g3 == g2:
                g3 = df['Genre3'].sample(n=1).values[0]
        genrechoices.append([g1,g2,g3])
    return genrechoices
	

	
#----------------------------------
#
# Utilities to score the reply from the ML endpoint
#
#----------------------------------

def getScore(reply):
    weightedscore = reply['predictedScores.1'] +
					2*reply['predictedScores.2'] +                     
					3*reply['predictedScores.3'] +                     
					4*reply['predictedScores.4'] +                     
					5*reply['predictedScores.5'] +                     
					6*reply['predictedScores.6'] +                     
					7*reply['predictedScores.7'] +                     
					8*reply['predictedScores.8'] +                     
					9*reply['predictedScores.9'] +                     
					10*reply['predictedScores.10']
    return weightedscore

def getActualResult(reply):                

    #build an array for choosing a value for the "actual" performance of the film
    weightarray = np.concatenate( ( np.full(int(np.round(reply['predictedScores.1']*10000)),1,dtype=np.int32),     
	np.full(int(np.round(reply['predictedScores.2']*10000)),2,dtype=np.int32),    
	np.full(int(np.round(reply['predictedScores.3']*10000)),3,dtype=np.int32),    
	np.full(int(np.round(reply['predictedScores.4']*10000)),4,dtype=np.int32),    
	np.full(int(np.round(reply['predictedScores.5']*10000)),5,dtype=np.int32),    
	np.full(int(np.round(reply['predictedScores.6']*10000)),6,dtype=np.int32),    
	np.full(int(np.round(reply['predictedScores.7']*10000)),7,dtype=np.int32),    
	np.full(int(np.round(reply['predictedScores.8']*10000)),8,dtype=np.int32),    
	np.full(int(np.round(reply['predictedScores.9']*10000)),9,dtype=np.int32),    
	np.full(int(np.round(reply['predictedScores.10']*10000)),10,dtype=np.int32)), axis=0)
    return np.random.choice(weightarray)

#----------------------------------
#
# Set up the communications with the AWS IoT hub
#
#----------------------------------


# Store replies from the AWS as items in a dataframe
replydf = pd.DataFrame()
waittime = 0

# Custom MQTT message callback - gathers replies from the AWS and puts them in the replydf
def customCallback(client, userdata, message):
    global replydf
    global waittime
    print("Received a new reply.")
    print(message.payload)
#    print("from topic: ")
#    print(message.topic)
    print("--------------")
    waitForReply = False
    callbackreply = json.loads(message.payload.decode("utf-8") )
    if len(replydf) == 0:
        replydf = pd.io.json.json_normalize(callbackreply)
    else:
        
        if callbackreply['title'] in replydf['title']:
            print("Duplicated title, not recording.")
        else:
            replydf = replydf.append(pd.io.json.json_normalize(callbackreply), ignore_index=True)
    waittime = 0



# Configure logging of the interactions with the AWS
logger = None
if sys.version_info[0] == 3:
    logger = logging.getLogger("core")  # Python 3
else:
    logger = logging.getLogger("AWSIoTPythonSDK.core")  # Python 2
#logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


# Initialize AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub", useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, 443)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect(60)
myAWSIoTMQTTClient.subscribe("$aws/things/MovieSelector/shadow/update", 1, customCallback)


#-------------------------------------------------------
# 
# Main loop sending requests for predictions from the AWS ML endpoint
#
#-------------------------------------------------------

for req in range(nrequests):
    print("Working on request number {}.".format(req))

    #Ok, now we build the array of 36 choices as a new dataframe that we can then plot/work with
    #Three directors
    vc=df['Director1'].value_counts()
    subdir = vc[vc>3]
    directors = subdir.sample(n=3).index.values

    #Three years
    years = df['year'].sample(n=3).values

    #Four sets of genres
    genrechoices = getGenres(df)

    #Create a dataframe of the choices
    datachoices = pd.DataFrame(columns=['title','Director1','year','Genre1','Genre2','Genre3'])
    index = 0
    for director in directors:
        for year in years:
            for choice in genrechoices:
                newdata = dict()
                newdata['title'] = getTitle(meaningful_words) + ' ({})'.format(year)
                newdata['Director1'] = [director]
                newdata['year'] = [str(year)]
                newdata['Genre1'] = [choice[0]]
                newdata['Genre2'] =[choice[1]]
                newdata['Genre3'] = [choice[2]]
                new_df = pd.DataFrame.from_dict(newdata)
                datachoices = datachoices.append(new_df, ignore_index=True)

    #We now have built the request data. Send the requests to the server

    # Send requests and get replies from server
    replydf = pd.DataFrame()
    for r,datarow in datachoices.iterrows():
        global callbackreply

        output = datarow.to_json()

        print("Sending data row {}... ".format(r))
        myAWSIoTMQTTClient.publish("filmrequest", output, 1)
        #spread out the requests so we don't overwhelm the server
        time.sleep(0.3)


    #we now wait for all the data to come in and be compiled
    waittime = 0
    while len(replydf) < len(datachoices) :
        print("Gathering data: now at {0} of {1}... waiting {2}".format(len(replydf),len(datachoices),waittime))
        time.sleep(1)

        if waittime > timeout:
            print("Re-sending remaining information")
            waittime = 0
            #find missing rows:
            if len(replydf) > 0:
                rerunlist = datachoices[~datachoices['title'].isin(replydf['title'])]
            else:
                rerunlist = datachoices
				
			# Resend data if we didn't get a timely reply
            for r,datarow in rerunlist.iterrows():
                global callbackreply

                output = datarow.to_json()

                print("Sending data row {}... ".format(r))
                myAWSIoTMQTTClient.publish("filmrequest", output, 1)
                #spread out the requests so we don't overwhelm the server
                time.sleep(0.3)


        waittime += 1

    

	# Now that we have the predictions, merge them with our original requests
    alldata = pd.merge(datachoices, replydf, how='inner', left_on=['title'], right_on=['title'],
          left_index=False, right_index=False, sort=True,
          suffixes=('_x', '_y'), copy=True, indicator=False)
    alldata.sort_values(['Director1','year','Genre1','Genre2','Genre3'],inplace=True)
    alldata.reset_index(drop=True,inplace=True)
    alldata['predictedscore'] = alldata.apply(lambda x: getScore(x), axis=1)
    bestoption = alldata.loc[alldata['predictedscore'].idxmax()]
	
	# Choose the best option and print it
    print(bestoption)
	
	# Create a "real" score for this option
    score = (getActualResult(alldata.loc[alldata['predictedscore'].idxmax()]))
    print('Final score: {}'.format(score))
    
	# Save the query to our data records
    alldata.to_csv("../data/iotdata/dataset_{0}_score_{1}.csv".format(req,score),index=False)
    #alldata
    
    #send best option back to the server for storage
    outputdb = bestoption[['title','year','Director1','Genre1','Genre2','Genre3']] 
    outputdb["stars"] = str(score)

    output = outputdb.to_json()
    print(output)

    myAWSIoTMQTTClient.publish("filmupdate", output, 1)
    



