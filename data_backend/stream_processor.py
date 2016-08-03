'''
Created on Jul 8, 2016

@author: James

Module designed to run as a data processing server which attaches to a
RabbitMQ test bed stream and regularly adds new data to a patient's profile 
or updates their statistics.
'''

import re
import datetime
import json
import boto3
import pika
import time
from math import sqrt
from boto3.dynamodb.conditions import Key, Attr
import decimal
from datetime import datetime


TEST_ID = "test_patient"
ACTIVE_PATIENT_IDS = []
FMT = "%Y-%m-%d#%H:%M:%S.%f" 
F2 = "%H:%M:%S.%f"
HANDLER = 'C:/Users/James/Desktop/CASAS/test_samples/total_data.txt'

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return decimal.Decimal(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
    
#Gets Items from 
class DataProcessor(object):
    
    def __init__(self, table_name="CASAS_DATA", id='test_patient'):
        self.connection = pika.BlockingConnection(
                                pika.ConnectionParameters(
                                host='smarthomedata.io',
                                port=5672, 
                                credentials=pika.credentials.
                                            PlainCredentials(
                                            'emily','Upd8ta2016!')))
        
        self.channel = self.connection.channel()
        self.database = boto3.resource('dynamodb', region_name='us-east-1', 
                        endpoint_url='https://dynamodb.us-east-1.amazonaws.com',
                        aws_access_key_id='AKIAIJIVXFE554ABXJOA',
                        aws_secret_access_key='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')
        self.table = self.database.Table(table_name)
        self.id = id
    
    #PrePost: accepts a string datum which should be stored in the correct place in 
    #the database   
    def sort_item(self, datum):
        pass
    
    #Pre: takes a input string corresponding to a batch of machine processed 
    # data to be processed
    #Post: processes the data from the text file by calculating statistics and
    #sorting events into the correct day.
    def sort_from_batch(self, input):
        try:
            input_handler = open(input, 'r')
        except:
            print "Illegal file"
            return
        
        def process_request(data, entry_ar, temp_t1, temp_t2, temp_d1, temp_d2):
            name = entry_ar[4].strip()
            
            if "begin" in name:
                temp_t1[0] = entry_ar[1]
                temp_d1[0] = entry_ar[0]
                if name == "Leave_Home begin":
                    temp_t1[1] = entry_ar[1]
            elif name in ("Meal_Preparation end", "Work end", "Relax end", "Enter_Home end"):
                #all the end locations where exact time is needed
                temp_t2[0] = entry_ar[1]
                temp_d2[0] = entry_ar[0]
                if name == "Enter_Home end":
                    form_1 = "{}#{}".format(temp_d1[0], temp_t1[1])
                    path = data["activity"]["travel"]
                else:
                    form_1 = "{}#{}".format(temp_d1[0], temp_t1[0])
                form_2 = "{}#{}".format(temp_d2[0], temp_t2[0])
                diff = str(datetime.strptime(form_2, FMT) -  
                        datetime.strptime(form_1, FMT))   
                
                var = re.split("[:.]", diff)
                
                if (name == "Meal_Preparation end"):
                    path = data["nutrition"]["meal_prep"]
                elif name == "Work end":
                    path = data["activity"]["work"]
                elif name == "Relax end":
                    path = data["activity"]["relax"]
                
                t_hr = path["hours"] + int(var[0])
                t_min = path["minutes"] + int(var[1])
                t_sec = path["seconds"] + int(var[2])
                             
                t_min += t_sec / 60
                t_sec = t_sec % 60
                t_hr += t_min / 60
                t_min = t_min % 60
                
                path["hours"] = t_hr
                path["minutes"] = t_min
                path["seconds"] = t_sec
                path["occurrences"] += 1  
            
            elif name in ("Wash_Dishes end", "Housekeeping end", "Eating end"):
                if name == "Wash_Dishes end":
                    data["hygiene"]["wash_dishes"]["occurrences"] += 1
                elif name == "Housekeeping end":
                    data["activity"]["housekeeping"]["occurrences"] += 1
                elif name == "Eating end":
                    data["nutrition"]["eating"]["occurrences"] += 1
            
            return data
    
        output = open('C:/Users/James/Desktop/CASAS/test_samples/test_batch_sort.txt', 'w')
        
        #temporary times and dates
        temp_t1 = ["", ""]
        temp_t2 = [""]
        temp_d1 = [""]
        temp_d2 = [""]
        #blank data entry
        data = {}
        cur_date = ""
        i = 1
       
        
        for entry in input_handler:
            entry = entry.strip()
            entry = entry.split(" ", 4)
              
            #has the desired tag we want
            if (len(entry) == 5):        
                if str(entry[0]) == cur_date:
                #check if same date, and continue analyzing if the same date 
                    data = process_request(data, entry, temp_t1, temp_t2, temp_d1, temp_d2)
                else: 
                #work on new date and write last one to mem
                    #save to database here
                    if cur_date != "":
                        #Write result to file
                        output.write(json.dumps(data) + "\n")
                        '''
                        data = json.dumps(data)
                        self.table.put_item(Item=json.loads(data, parse_float = decimal.Decimal))
                        '''
                    #start new date entry
                    cur_date = entry[0]
                    
                    try:
                        #sleep = db[cur_date]['sleep_time']
                        sleep = {}
                    except:
                        sleep = {}
                        
                    data = {"USER_ID":TEST_ID,
                            "_date":cur_date , 
                            "date": cur_date,
                            "entry_number": i,
                            "last_rev":time.asctime(time.localtime(time.time())),
                            "nutrition": {"meal_prep":{"hours":0,
                                                       "minutes":0,
                                                       "seconds":0,
                                                       "occurrences":0},
                                          "eating": {"occurrences":0}},
                            "activity":{"relax":{"hours":0,
                                                 "minutes":0,
                                                 "seconds":0,
                                                 "occurrences":0},
                                        "travel":{"hours":0,
                                                  "minutes":0,
                                                  "seconds":0,
                                                  "occurrences":0},
                                        "housekeeping":{"occurrences":0},
                                        "work":{"hours":0,
                                                "minutes":0,
                                                "seconds":0,
                                                "occurrences":0}},
                            "hygiene":{"wash_dishes":{"occurrences":0},
                                       "shower":{"hours":0,
                                                 "minutes":0,
                                                 "seconds":0,
                                                 "occurrences":0}},
                            "sleep_time":sleep
                    }
                    i+=1
                    data = process_request(data, entry, temp_t1, temp_t2, temp_d1, temp_d2)
        #write final result
        output.write(json.dumps(data) + "\n")
        '''
        data = json.dumps(data)
        self.table.put_item(Item=json.loads(data, parse_float = decimal.Decimal))
        '''
        output.close()
        input_handler.close()
    
    #Prototyped sleep analyzer needs to be overhauled and incorporated with
    #the general batch and item analyzer
    '''    
    def finalize_sleep_time(handler, location):
        
        
        start_date = "2010-11-04"
        cur_date =  "2010-11-03"
        last_date = "2010-11-03"
        data = {"_id":cur_date,
                "sleep_time":{'sleep':{"hours": 0, 
                                       "minutes": 0,
                                       "seconds": 0},
                              "start_time": "00:03:50.209589",
                              "end_time": '0',
                              "inter_time":{"hours":0,
                                      "minutes":0,
                                      "seconds":0,
                                      "average":0,
                                      "occurrences": -1}}, 
                "date":cur_date
                }
                
        for entry in handler:
            
            entry = json.loads(entry.strip())
            y = str(entry['sleep_time']['start_time'])
            x = re.split(":", y)
           
            #keep adding to the current 
            if (entry['sleep_time']['start'] == cur_date or (int(x[0]) <= 10 and days_between(entry['sleep_time']['start'], cur_date) <= 1)):
                last_date = entry['sleep_time']['end']
                data['sleep_time']['sleep']['hours'] += int(entry['sleep_time']['hours'])
                data['sleep_time']['inter_time']['occurrences'] += 1
                data['sleep_time']['end_time'] = entry['sleep_time']['end_time']
                
                if (data['sleep_time']['sleep']['seconds'] + int(entry['sleep_time']['seconds']) >= 60):
                    data['sleep_time']['sleep']['minutes'] += 1
                    data['sleep_time']['sleep']['seconds'] += (int(entry['sleep_time']['seconds']) - 60)
                else:
                    data['sleep_time']['sleep']['seconds'] += int(entry['sleep_time']['seconds'])
                    
                if (data['sleep_time']['sleep']['minutes'] + int(entry['sleep_time']['minutes']) >= 60):
                    data['sleep_time']['sleep']['hours'] += 1
                    data['sleep_time']['sleep']['minutes'] += (int(entry['sleep_time']['minutes']) - 60)
                else:
                    data['sleep_time']['sleep']['minutes'] += int(entry['sleep_time']['minutes'])
            else:
                #calculate time of interruptions
                
                t1 = data['sleep_time']['start_time']
                t2 = data['sleep_time']['end_time']
                sd = start_date
                ed = last_date
                form_1 = "{}#{}".format(sd, t1)
                form_2 = "{}#{}".format(ed, t2)
                hd = data['sleep_time']['sleep']
                
                diff = str(datetime.strptime(form_2, FMT) - 
                    datetime.strptime(form_1, FMT))
                d2 = str (datetime.strptime(diff, F2) - 
                          datetime.strptime("{}:{}:{}.0".format(hd['hours'], 
                                                                hd['minutes'], 
                                                                hd['seconds']), F2))
                
               
                var = re.split("[:.]", d2)
                data['sleep_time']['inter_time']['hours'] = int(var[0])
                data['sleep_time']['inter_time']['minutes'] = int(var[1])
                data['sleep_time']['inter_time']['seconds'] = int(var[2])
                if (data['sleep_time']['inter_time']['occurrences'] != 0):
                    data['sleep_time']['inter_time']['average'] = round(((float(var[0]) * 60 + 
                                                      float(var[1])  + 
                                                      float(var[2]) / 60) / 
                                                     data['sleep_time']['inter_time']['occurrences']), 2)
                
                #output.write(json.dumps(data) + "\n")
                db.save(data)
    
                if (int(x[0]) <= 10):
                    cur_date = last_date
                else:
                    cur_date = entry['sleep_time']['start']
                last_date = entry['sleep_time']['end']
                start_date = entry['sleep_time']['start']
                
                data = {"_id":cur_date,
                        "sleep_time":{'sleep':{"hours":int(entry['sleep_time']['hours']), 
                                      "minutes":int(entry['sleep_time']['minutes']),
                                      "seconds":int(entry['sleep_time']['seconds'])},
                                      "start_time": entry['sleep_time']['start_time'],
                                      "end_time": entry['sleep_time']['end_time'],
                                      "inter_time":{"hours":0,
                                      "minutes":0,
                                      "seconds":0,
                                      "average":0,
                                      "occurrences": 0}}, 
                        "date":cur_date
                        }
                
        
        #output.write(json.dumps(data)+"\n")
        db.save(data)
                  
        output.close()
    '''
    
    def __days_between(self, cur, tar):
        cur = cur.split('-')
        tar = tar.split('-')
        thirtyOne = [1, 3, 5, 7, 8, 10, 12]
        thirty = [4,6,9,11]
        weird = [2]
        
        if (cur[1] != tar[1]): # months are diff
            if int(cur[2]) == 1:
                if (int(tar[1]) in  thirtyOne):
                    return (31 - int(tar[2]) + int(cur[2]))
                elif (int(tar[1]) in  thirty):
                    return (30 - int(tar[2]) + int(cur[2]))
                elif (int(tar[1]) in weird):
                    if (int(tar[0]) % 4 == 0 and int(tar[0]) % 100 != 0):
                        return (29 - int(tar[2]) + int(cur[2]))
                    else:
                        return (28 - int(tar[2]) + int(cur[2]))
            else:
                return 5
        else:
            return (int(cur[2]) - int(tar[2]))
    
    #MAKE SURE THAT EVEN ENTRIES WITH FIELDS
    #MISSING GET THEIR DATA INCLUDED EVENTUALLY
    
    #Calculates statistics for a regularity for the table
    def calculate_statistics(self): 
        resp = self.table.get_item(
                                   Key={
                                        'USER_ID':self.id,
                                        '_date':'regularity'
                                        }
                                   )
        if ('Item' not in resp):
            data = self.table.query(
                                       KeyConditionExpression=Key('USER_ID').eq(self.id),
                                       FilterExpression=Attr('date').exists()
                                       )
            
            total_seconds = {"travel":0, "work":0, "relax":0, 
                             "shower":0, "meal_prep":0, "sleep":0, "inter_time":0}
            n = 0
            #mean of time in seconds
            mean = {"travel":0.0, "work":0.0, "relax":0.0, 
                    "shower":0.0, "meal_prep":0.0, "sleep":0.0, "inter_time":0.0}
            #square variance of time in seconds
            M2 = {"travel":0.0, "work":0.0, "relax":0.0, 
                  "shower":0.0, "meal_prep":0.0, "sleep":0.0, "inter_time":0.0}
            
            occurrences = {"travel":0, "work":0, "housekeeping":0, 
                           "relax":0, "wash_dishes":0, "shower":0, 
                           "meal_prep":0, "eating":0, "inter_time":0}
            #mean of occurrences
            meano = {"travel":0.0, "work":0.0, "housekeeping":0.0, 
                           "relax":0.0, "wash_dishes":0.0, "shower":0.0, 
                           "meal_prep":0.0, "eating":0.0, "inter_time":0.0}
            #square variance of occurrences
            M2o = {"travel":0.0, "work":0.0, "housekeeping":0.0, 
                           "relax":0.0, "wash_dishes":0.0, "shower":0.0, 
                           "meal_prep":0.0, "eating":0.0, "inter_time":0.0}
            last_number = 0
        else:
            #update current one
            path = resp['Item']
            last_number = path["last_entry"]
            data = self.table.query(
                    KeyConditionExpression=Key('USER_ID').eq(self.id),
                    FilterExpression=Attr('date').exists() & Attr('entry_number').gt(last_number)                
                                    )

            '''
            total_seconds = {"travel":int(path['activity']['travel']['t_av']) * tot, 
                             "work":int(path['activity']['work']['t_av']) * tot, 
                             "relax":int(path['activity']['relax']['t_av']) * tot, 
                             "shower":int(path['hygiene']['shower']['t_av']) * tot, 
                             "meal_prep":int(path['nutrition']['meal_prep']['t_av']) * tot, 
                             "sleep":int(path['sleep_time']['sleep']['t_av']) * tot, 
                             "inter_time":int(path['sleep_time']['inter_time']['t_av']) * tot}
            '''    
            
            total_seconds = {"travel":0, "work":0, "relax":0, 
                             "shower":0, "meal_prep":0, "sleep":0, "inter_time":0}
                         
            n = int(path['number_items'])
            
            #mean of time in seconds
            mean = {"travel":float(path['activity']['travel']['t_av']), 
                    "work": float(path['activity']['work']['t_av']), 
                    "relax":float(path['activity']['relax']['t_av']), 
                    "shower":float(path['hygiene']['shower']['t_av']), 
                    "meal_prep":float(path['nutrition']['meal_prep']['t_av']), 
                    "sleep":float(path['sleep_time']['sleep']['t_av']), 
                    "inter_time":float(path['sleep_time']['inter_time']['t_av'])}
            
            #square variance of time in seconds
            M2 = {"travel":float(path['activity']['travel']['t_sd'])** 2 * n, 
                    "work": float(path['activity']['work']['t_sd'])** 2 * n, 
                    "relax":float(path['activity']['relax']['t_sd'])** 2 * n, 
                    "shower":float(path['hygiene']['shower']['t_sd'])** 2 * n, 
                    "meal_prep":float(path['nutrition']['meal_prep']['t_sd'])** 2 * n, 
                    "sleep":float(path['sleep_time']['sleep']['t_sd'])** 2 * n, 
                    "inter_time":float(path['sleep_time']['inter_time']['t_sd'])** 2 * n
                    }
            
            occurrences = {"travel":0, "work":0, "housekeeping":0, 
                           "relax":0, "wash_dishes":0, "shower":0, 
                           "meal_prep":0, "eating":0, "inter_time":0}
            #mean of occurrences
            meano = {"travel":float(path['activity']['travel']['o_av']), 
                    "wash_dishes":float(path['hygiene']['wash_dishes']['o_av']),
                    "work": float(path['activity']['work']['o_av']), 
                    "relax":float(path['activity']['relax']['o_av']), 
                    "shower":float(path['hygiene']['shower']['o_av']), 
                    "meal_prep":float(path['nutrition']['meal_prep']['o_av']), 
                    "housekeeping":float(path['activity']['housekeeping']['o_av']), 
                    "eating":float(path['nutrition']['eating']['o_av']),
                    "inter_time":float(path['sleep_time']['inter_time']['o_av'])}
            
            #square variance of occurrences
            M2o = {"travel":float(path['activity']['travel']['o_sd']) ** 2 * n, 
                    "wash_dishes":float(path['hygiene']['wash_dishes']['o_sd']) ** 2 * n,
                    "work": float(path['activity']['work']['o_sd']) ** 2 * n, 
                    "relax":float(path['activity']['relax']['o_sd']) ** 2 * n, 
                    "shower":float(path['hygiene']['shower']['o_sd']) ** 2 * n, 
                    "meal_prep":float(path['nutrition']['meal_prep']['o_sd']) ** 2 * n, 
                    "housekeeping":float(path['activity']['housekeeping']['o_sd']) ** 2 * n, 
                    "eating":float(path['nutrition']['eating']['o_sd']) ** 2 * n,                
                    "inter_time":float(path['sleep_time']['inter_time']['o_sd']) ** 2 * n}
            
            self.table.delete_item(
                                   Key={
                                        'USER_ID':self.id,
                                        '_date':'regularity'
                                        }
                                   )
            
        #calculates the variance and mean
        #using the Welford method
        for item in data[u'Items']:
            try:
                path = item['sleep_time']
                total_seconds['sleep'] = path['sleep']['hours'] * 3600 + path['sleep']['minutes'] * 60 + path['sleep']['seconds']
                total_seconds['inter_time'] = path['inter_time']['hours'] * 3600 + path['inter_time']['minutes'] * 60 + path['inter_time']['seconds']
                occurrences['inter_time'] = path['inter_time']['occurrences']
                path = item['activity']['travel']
                total_seconds['travel'] = path['hours'] * 3600 + path['minutes'] * 60 + path['seconds']
                occurrences['travel'] = path['occurrences']
                path = item['activity']['work']
                total_seconds['work'] = path['hours'] * 3600 + path['minutes'] * 60 + path['seconds']
                occurrences['work'] = path['occurrences']
                path = item['activity']['relax']
                total_seconds['relax'] = path['hours'] * 3600 + path['minutes'] * 60 + path['seconds']
                occurrences['relax'] = path['occurrences']
                path = item['nutrition']['meal_prep']
                total_seconds['meal_prep'] = path['hours'] * 3600 + path['minutes'] * 60 + path['seconds']
                occurrences['meal_prep'] = path['occurrences']
                path = item['hygiene']['shower']
                total_seconds['shower'] = path['hours'] * 3600 + path['minutes'] * 60 + path['seconds']
                occurrences['shower'] = path['occurrences']
                
                occurrences['housekeeping'] = item['activity']['housekeeping']['occurrences']
                occurrences['wash_dishes'] = item['hygiene']['wash_dishes']['occurrences']
                occurrences['eating'] = item['nutrition']['eating']['occurrences']
                
                n += 1
                #calculate online variance and mean
                for key in total_seconds:
                    delta = float(total_seconds[key]) - float(mean[key])
                    mean[key] += delta/n
                    M2[key] += delta * (float(total_seconds[key]) - float(mean[key]))
                    
                for key in occurrences:
                    delta = int(occurrences[key]) - float(meano[key])
                    meano[key] += delta/n
                    M2o[key] += delta * (int(occurrences[key]) - float(meano[key]))
                    
                last_number = int(item['entry_number'])
            except:
                print "{} was missing one or more fields".format(item['date'])
        
        data = {"USER_ID":TEST_ID,
                "_date": "regularity", 
                "last_rev":time.asctime(time.localtime(time.time())),
                "last_entry":last_number,
                "number_items":n,
                "nutrition": {"meal_prep":{"t_av":mean['meal_prep'],
                                           "t_sd":sqrt(M2['meal_prep']/n),
                                           "o_av":meano['meal_prep'],
                                           "o_sd":sqrt(M2o['meal_prep']/n)},
                              "eating": {"o_av":meano['eating'],
                                         "o_sd":sqrt(M2o['eating']/n)}},
                "activity":{"relax":{"t_av":mean['relax'],
                                     "t_sd":sqrt(M2['relax']/n),
                                     "o_av":meano['relax'],
                                     "o_sd":sqrt(M2o['relax']/n)},
                            "travel":{"t_av":mean['travel'],
                                      "t_sd":sqrt(M2['travel']/n),
                                      "o_av":meano['travel'],
                                      "o_sd":sqrt(M2o['travel']/n)},
                            "housekeeping":{"o_av":meano['housekeeping'],
                                            "o_sd":sqrt(M2o['housekeeping']/n)},
                            "work":{"t_av":mean['work'],
                                    "t_sd":sqrt(M2['work']/n),
                                    "o_av":meano['work'],
                                    "o_sd":sqrt(M2o['work']/n)}},
                "hygiene":{"wash_dishes":{"o_av":meano['wash_dishes'],
                                         "o_sd":sqrt(M2o['wash_dishes']/n)},
                           "shower":{"t_av":mean['shower'],
                                     "t_sd":sqrt(M2['shower']/n),
                                     "o_av":meano['shower'],
                                     "o_sd":sqrt(M2o['shower']/n)}},
                "sleep_time": {"sleep":{"t_av":mean['sleep'],
                                        "t_sd":sqrt(M2['sleep']/n)},
                               "inter_time":{"t_av":mean['inter_time'],
                                                "t_sd":sqrt(M2['inter_time']/n),
                                                "o_av":meano['inter_time'],
                                                "o_sd":sqrt(M2o['inter_time']/n)}}
                }
         
        data = json.dumps(data)
        self.table.put_item(Item=json.loads(data, parse_float = decimal.Decimal))
