'''
Created on Jun 28, 2016

@author: James

@description: The CASAS question and answer prototype server code.
Establishes a connection to the RabbitMQ server, Bunny, to wait for requests
which appear on the emily exchange. Returns an answer in Json format.

@response_format: {'response': message which is returned. Default is 'Okay' : str,
                    'time_done': standard time code for completion time : str,
                    'date': the date, or date modifier if a date was not given : str,
                    'general':  ONLY PRESENT FOR A GENERAL CALL.
                                contains a dictionary with all the statistics for
                                categories with unusual data : dict,
                    Rtype('activity', 'sleep', etc): ONLY PRESENT FOR NON-GENERAL CALL.
                                Contains a dictionary with statitics based on the 
                                time and request type. (See Rtype format below)
                    'regularity': Contains a dictionary which has the overall statistics
                                  for all categories as keys paired to more dicts: dict,
                    'types': {'Ttype':contains 'day', 'month', 'week' or 'year' depending
                                on the requested statistic type : str.
                              'Rtype':The type of data the user wants to know about.
                                      Contains the name of the category contained in 
                                      the JSON packet. : str},
                    'start_date' ONLY PRESENT IF Ttype IS 'week'.
                                Contains the starting date of the week. : str,
                    'end_date' ONLY PRESENT IF Ttype IS 'week'.
                                Contains the ending date of the week. : str,
                    }
                    
@Rtype_format: {FIELD('relax', 'meal_prep', etc):
                    { (NOTE: all fields are optional and may or may not exist
                       depending on the nature of the data)
                        'hours' : (DAY) hours of performance in a day : float,
                        'minutes' : (DAY) minutes of performance in a day : float,
                        'seconds' : (DAY) seconds of performance in a day : float,
                        't_hr' : (WEEK, MONTH, YEAR) total hours doing an activity : float,
                        't_min' : (WEEK, MONTH, YEAR) total hours doing an activity : float,
                        't_sec' : (WEEK, MONTH, YEAR) total hours doing an activity : float,
                        't_occurrences': (WEEK, MONTH, YEAR) total times an activity is done: int,
                        'av_occurrences': (WEEK, MONTH, YEAR) average times an activity is done: int,
                        'av_length_occurrences': (WEEK, MONTH, YEAR) average length of time the occurrences happened for: float
                    }
'''

import pika
import json

import threading
from time import sleep
import time
import datetime
from multiprocessing import Queue
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr

#------------------------------Globals-----------------------------------------

threads = []

MONTHS = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June',
          7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 
          12:'December'}

OPTIONS =  {'activity' : 'activity', 
            'hygiene': 'hygiene', 
            'nutrition': 'nutrition',
            'sleep': 'sleep_time',
            'medicine': 'medicine'}  

FIELDS = {'activity' : ['travel', 'work', 'housekeeping', 'relax'], 
          'hygiene': ['shower', 'wash_dishes'], 
          'nutrition': ['eating','meal_prep'],
          'sleep_time': ['inter_time', 'sleep'],
          'medicine': []}

DEFAULT_RESP = {'response': "Error: No data available for that Request Type",
                            'time_done':"Not Available"}


#-----------------------------

#Pre: Accepts the question in the formatted JSON interface
# and a queue to return information from the thread. It also accepts
# multiple extra arguments to be determined later.
#Post: Returns the formatted JSON response with all the pertinent information.
# For now the data contains a speechlet response and a timestamp when the
# request was completed.
def fetch(question, q, props, ch, method, start_time):
    try:
        db = dynamodb.Table('CASAS_DATA')
    except:
        data = {'response': "Error: Database not found",
                            'time_done':time.asctime(
                                        time.localtime(time.time()))}
        q.put(data)
        return
    
    Rtype = question['request_type']['information_type']
    print threading.current_thread()
    
    #nested functions in place of a switch statement.
    #one option for each type of request
    def gen(question, Rtype, database):
        #need to think about least resource intensive method
        return general_analysis(question, Rtype, database)
    def activity(question, Rtype, database):
        return create_response(question, Rtype, database)
    def hygiene(question, Rtype, database):
        return create_response(question, Rtype, database)
    def nutrition(question, Rtype, database):
        return create_response(question, Rtype, database)
    def sleep(question, Rtype, database):
        return create_response(question, Rtype, database)
    def medicine(question, Rtype, database):
        #no medical data available currently
        return DEFAULT_RESP
    def elope(question, Rtype, database):
        #no elopement data available rn
        return DEFAULT_RESP
    
    options = {'activity' : activity,
               'general': gen, 
               'hygiene': hygiene, 
               'nutrition': nutrition,
               'sleep': sleep,
               'medicine': medicine,
               'elopement':elope}  
    
    #chooses the appropriate function
    if (Rtype in options):
        data = options[Rtype](question, Rtype, db)
    else:
        data = {'response': "Error: Incorrect request type",
                            'time_done':time.asctime(
                                        time.localtime(time.time()))}
    try:
        print time.time() - start_time
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=
                                        props.correlation_id),
                                        body=json.dumps(data, cls=DecimalEncoder))
    except:
        print "Return Queue does not exist or the incorrect data was given"
        #print answer['response']
    finally:
        ch.basic_ack(delivery_tag = method.delivery_tag)

#Pre: The handler    
def on_request(ch, method, props, body):
    qid = props.correlation_id
    try:
        start_time = time.time()
        question = json.loads(body)
        print ("Receiving Request Id: {}").format(str(qid))
        q = Queue()
        worker = threading.Thread(target=fetch, name="Worker Thread", 
                                  args=(question,q, props, ch, method, start_time))
        threads.append(worker)
        worker.start()
       
    except:
        print "Incorrect message format"
        
#---------------Helper Functions------------------------------------------------

#Pre: Accepts the end date of any week and calculates all the dates in the week 
#that occurred since the last Sunday
#Post: Returns a tuple containing all the dates in the format 'yyyy-mm-dd' from
# the given date to the last Sunday 
def week(end_date):
    #Include a case for if the date is in an incorrect format
    date = end_date.split('-')
    num_date = [int(date[0]),int(date[1]),int(date[2])]
    thirtyOne = (1, 3, 5, 7, 8, 10, 12)
    thrity = (4,6,9,11)
    week = []
    
    if (int(date[0])%4 == 0 and int(date[0])% 100 != 0):
        is_leap = True
    else:
        is_leap = False
    
    #If the week likely spans 2 months   
    if (num_date[2] < 7):
        #if the initial month isn't January
        if (num_date[1] > 1):
            i = 0
            cur_mon = num_date[1]
            cur_day = num_date[2]
            while (datetime.date(num_date[0], cur_mon, cur_day).weekday() != 6):
                if (num_date[2] - i > 0):
                    cur_day = num_date[2]-i
                    week.append("{}-{}-{}".format(date[0], date[1], str(cur_day).zfill(2)))
                else:
                    cur_mon = int(num_date[1])-1
                    if (cur_mon in thirtyOne):
                        cur_day = (31 + num_date[2] - i)
                        week.append("{}-{}-{}".format(date[0], str(cur_mon).zfill(2), str(cur_day).zfill(2)))
                    elif (cur_mon in thrity):
                        cur_day = (30 + num_date[2] - i)
                        week.append("{}-{}-{}".format(date[0], str(cur_mon).zfill(2), str(cur_day).zfill(2)))
                    else:
                        if is_leap:
                            cur_day = (29 + num_date[2] - i)
                            week.append("{}-{}-{}".format(date[0], str(cur_mon).zfill(2), str(cur_day).zfill(2)))
                        else:
                            cur_day = (28 + num_date[2] - i)
                            week.append("{}-{}-{}".format(date[0], str(cur_mon).zfill(2), str(cur_day).zfill(2)))
                    
                i+=1
        #If the initial month is January
        else:
            i = 0
            cur_yr = num_date[0]
            cur_mon = num_date[1]
            cur_day = num_date[2]
            while (datetime.date(num_date[0], num_date[1], (num_date[2]-i)).weekday() != 6):
                if (num_date[2] - i > 0):
                    cur_day = num_date[2]-i
                    week.append("{}-{}-{}".format(date[0], date[1], str(cur_day ).zfill(2)))
                else:
                    cur_mon = 12
                    cur_yr = num_date[0] - 1
                    cur_day = (31 + num_date[2] - i)
                    week.append("{}-{}-{}".format(str(cur_yr), str(cur_mon).zfill(2), str(cur_day).zfill(2)))
                i+=1
    #If the week is in the middle of the month and does not cross months
    else:
        for i in range(7):
            if (datetime.date(num_date[0], num_date[1], (num_date[2]-i)).weekday() == 6):
                week.append("{}-{}-{}".format(date[0], date[1], str(int(date[2])-i).zfill(2)))
                break
            else:
                week.append("{}-{}-{}".format(date[0], date[1], str(int(date[2])-i).zfill(2)))
            
            
    return tuple(week)

#Pre: accepts the total hours, minutes, seconds and occurrences if 
# they exist for any category. Also accepts the number of days
#Post: calculates the averages based on number of days 
def calculate_averages(total_hours = 0, total_seconds = 0, total_minutes = 0, total_occurrences = 0, num_days = 1):
        try:
            total_time = (float(total_hours) + float(total_minutes) / 60 + 
                          float(total_seconds) / 3600)
            average = round((float(total_time) / num_days), 2)
            av_hr = int(average * 60) / 60
            av_min = int(average * 60) % 60
            
            if (total_occurrences != 0):
                av_len_o = round((float(total_time) / total_occurrences), 2)
            else: 
                av_len_o = 0.0
                
            if (num_days != 0):    
                av_occurences = round((float(total_occurrences) / num_days), 2)
            else:
                av_occurences = 0.0
        except:
            average = 0.0
            av_occurences = 0.0
            av_len_o = 0.0
            av_hr = 0.0
            av_min = 0.0
        
        return average, av_hr, av_min, av_occurences, av_len_o

#Pre: accepts the original question as well as the database address and 
# the Request type.
#Post: Normally returns a completed response giving general statistics on out of the 
#ordinary activity stats. Returns the default error response if either regularity
# cannot be found or the user or date don't exist
def general_analysis(question, Rtype='default', db=None):
    Ttype = str(question['request_type']['time_type'].strip())
    mod = question['request_type']['time_modifier']
    
    try:     
        reg = db.get_item(
                    Key = {
                           'USER_ID' : 'test_patient',
                           '_date' : 'regularity'
                        }                          
                    )
        reg = json.dumps(reg[u'Item'], cls=DecimalEncoder)
        reg = json.loads(reg)
    except:
        return DEFAULT_RESP
    
    try:
        path = db.get_item(
                    Key = {
                           'USER_ID' : 'test_patient',
                           '_date' : mod
                        }                          
                    )['Item']
    except:
        return DEFAULT_RESP
    
    data = {'response': "Okay",
                    'time_done':time.asctime(time.localtime(time.time())),
                    'date': mod,
                    'general': {},
                    'regularity': reg,
                    'types': {'Ttype':Ttype,
                              'Rtype':Rtype}}
    
    #Go through activity hygiene and nutrition etc
    for category in path:
        #go through each
        spath = path[category]
        if category in FIELDS:
            for subcat in spath:
                if ('hours' in spath[subcat]):
                    tt = (int(spath[subcat]['hours']) * 3600 +
                          int(spath[subcat]['minutes']) * 60 +
                          int(spath[subcat]['seconds']) 
                        )
                    t_av = float(reg[category][subcat]['t_av'])    
                    t_sd = float(reg[category][subcat]['t_sd'])
                    if (abs(tt-t_av) >= 2 * t_sd and round(t_sd, 2) != 0):
                        data['general'].update({subcat:{"tt":tt}})
                    
                if ('occurrences' in spath[subcat]):
                    occ = float(spath[subcat]['occurrences'])
                    o_av = float(reg[category][subcat]['o_av'])
                    o_sd = float(reg[category][subcat]['o_sd'])
                    
                    if (abs(occ-o_av) >= o_sd and round(o_sd, 2) != 0):
                        data['general'].update({subcat:{"to": occ}})
                
    return data
    
#Pre: accepts the question, the request type, and database object
#Post: creates and returns a data structure with all the relevant information 
#to answer the given question such as stats.
def create_response(question, Rtype = "default", db = None):
    #Rtypes can be 'sleep', 'gen', 'medicine', 'activity' 'hygiene', 'nutrition' 
    Ttype = str(question['request_type']['time_type'].strip())
    mod = question['request_type']['time_modifier']
    total_hours = 0
    total_minutes = 0
    total_seconds = 0
    total_occurrences = 0
    num_days = 0
    
    #check if regularity feature is in the 
    #repository for the patient
    try:     
        reg = db.get_item(
                    Key = {
                           'USER_ID' : 'test_patient',
                           '_date' : 'regularity'
                        }                          
                    )
        reg = json.dumps(reg[u'Item'], cls=DecimalEncoder)
        reg = json.loads(reg)
    except:
        reg = None
                
    if (Ttype == 'day'):
        #modifier should be in the form of a date (yyyy-mm-dd)
        try:
            #The path to the day's data
            path = db.get_item(
                    Key = {
                           'USER_ID' : 'test_patient',
                           '_date' : mod
                        }                          
                    )
            #improve
            path = json.dumps(path[u'Item'], cls=DecimalEncoder)
            path = json.loads(path)
            
            data = {'response': "Okay",
                    'time_done':time.asctime(time.localtime(time.time())),
                    'date': mod,
                    Rtype: path[OPTIONS[Rtype]],
                    'regularity': reg,
                    'types': {'Ttype':Ttype,
                              'Rtype':Rtype}}
        except:
            data = {'response': "Error: Illegal Date",
                    'time_done':time.asctime(
                                time.localtime(time.time()))}
                                      
    elif (Ttype  in ('month', 'year', 'week')):
        #modifier should be in the form of a date (yyyy or yyyy-mm)
        #improve efficiency of setup
        try:
            data = {'response': "Okay",
                    'time_done':time.asctime(time.localtime(time.time())),
                    'date': mod,
                    Rtype:{},
                    'regularity': reg,
                    'types': {'Ttype':Ttype,
                              'Rtype':Rtype}}   
            
            if (Ttype  in ('month', 'year')):
                response = db.query(
                                ProjectionExpression="#id, #date, {}".format(OPTIONS[Rtype]),
                                ExpressionAttributeNames={ "#id": "USER_ID", "#date": "_date"}, 
                                KeyConditionExpression=Key('USER_ID').eq('test_patient'),
                                FilterExpression=Attr('date').contains(mod)
                )
            else:
                wk = week(mod)
                response = db.query(
                                ProjectionExpression="#id, #date, {}".format(OPTIONS[Rtype]),
                                ExpressionAttributeNames={ "#id": "USER_ID", "#date": "_date"}, 
                                KeyConditionExpression=Key('USER_ID').eq('test_patient'),
                                FilterExpression=Attr('date').is_in(wk)
                )
                
                data.update({"end_date":wk[0]})
                data.update({"start_date": wk[len(wk)-1]})
            #iterate once for each field in the request type
            for cur_type in FIELDS[OPTIONS[Rtype]]:
                for i in response[u'Items']:    
                    path = i[OPTIONS[Rtype]][cur_type]   
                    #check to see if they have time related fields
                    if ('hours' and 'minutes' and 'seconds' in path):
                        total_hours += int(path['hours'])
                        total_minutes += int(path['minutes'])
                        total_seconds += int(path['seconds'])
                    if ('occurrences' in path): 
                        total_occurrences += int(path['occurrences'])
                    num_days += 1
                        
                total_minutes += total_seconds / 60
                total_seconds = total_seconds % 60
                total_hours += total_minutes / 60
                total_minutes = total_minutes % 60
                    
                temp = calculate_averages(total_hours, total_seconds, 
                                   total_minutes, total_occurrences, 
                                   num_days)
                tempd = {}
                if ('occurrences' in path):
                    tempd.update({'av_occurrences': temp[3], 'av_length_occurrences': temp[4], 
                                  't_occurrences' : total_occurrences})
                if ('hours' and 'minutes' and 'seconds' in path):
                    tempd.update({'av_hours': temp[1], 'av_min':temp[2], 
                                  't_hr': total_hours, 't_min': total_minutes, 
                                  't_sec': total_seconds})
                    
                data[Rtype].update({cur_type : tempd})  
                   
                total_hours = 0
                total_minutes = 0
                total_seconds = 0
                total_occurrences = 0
                num_days = 0
        except:
            data = {'response': "Error: Illegal Date",
                    'time_done':time.asctime(
                                time.localtime(time.time()))}
                        
    else:
        data = {'response': "Error: Unknown time type.",
                'time_done':time.asctime(
                            time.localtime(time.time()))}
    
    return data
#---------------Helper Classes--------------------------------------------------
#Converts to decimal to help with json encoding and decoding.  
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)
    
#---------------Server Exectution-----------------------------------------------

#connect to the server and the database server
not_connected = True
connection = None

#connect to the RabbitMQ server
while(not_connected):
    try:
        connection = pika.BlockingConnection(
                                pika.ConnectionParameters(
                                    host='smarthomedata.io',
                                    port=5672, 
                                    credentials=pika.credentials.
                                                PlainCredentials(
                                                'emily','Upd8ta2016!')))
        not_connected = False
    except:
        print "RabbitMQ Server Connection Failure"
        not_connected = True
        
channel = connection.channel()

#access the dynamodb resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1', 
                          endpoint_url='https://dynamodb.us-east-1.amazonaws.com',
                           aws_access_key_id='AKIAIJIVXFE554ABXJOA',
                           aws_secret_access_key='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')

'''
-prefetch better for multiple servers, not great for multithreading
-uncomment if multiple servers running  
'''
#channel.basic_qos(prefetch_count=5)

channel.queue_purge(queue='work.emily')
channel.basic_consume(on_request, queue='work.emily')

print(" [x] Awaiting Questions")
channel.start_consuming()