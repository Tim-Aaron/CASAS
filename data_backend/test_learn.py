'''
Created on Jun 27, 2016

@author: James

Set of Programs for testing data processing. 
OBSOLETE, USE stream_processor INSTEAD

'''
from time import sleep
import re
import datetime
import json
import couchdb
import time
from datetime import datetime
import math
from math import sqrt
import boto3
import decimal


handler = open('C:/Users/James/Desktop/CASAS/test_samples/total_data.txt', 'r')
loc = 'C:/Users/James/Desktop/CASAS/test_samples/sleep_instances.txt'
supp = 'C:/Users/James/Desktop/CASAS/test_samples/sleep_json.txt'
fin = 'C:/Users/James/Desktop/CASAS/test_samples/fin_sleep.txt'
criki = 'C:/Users/James/Desktop/CASAS/test_samples/alt_fin_sleep.txt'
FMT = "%Y-%m-%d#%H:%M:%S.%f" 
F2 = "%H:%M:%S.%f"

couch = couchdb.Server()
database = couch['casas_test']

TEST_ID = "test_patient"

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', 
                          endpoint_url='https://dynamodb.us-east-1.amazonaws.com')
table = dynamodb.Table('CASAS_DATA')

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return decimal.Decimal(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
    
def sort_data(handler, location):
    
    output  = open(location, 'w')
    
    for entry in handler:
        entry = entry.strip()
        x = entry.split(" ", 4)
        if (len(x) == 5):
            output.write("@".join(x) + "\n")
            
    output.close()

def calculate_time(handler, location, id1, id2, name):
    output = open(location, 'w')
    
    temp_date = ""
    temp_time = ""
    for entry in handler:
        entry = entry.strip()
        x = re.split("@", entry)
        
        if x[4].strip() == id1:
            temp_date = x[0]
            temp_time = x[1]
        elif x[4].strip() == id2:
            temp_date_2 = x[0]
            temp_time_2 = x[1]
            
            
            form_1 = "{}#{}".format(temp_date, temp_time)
            form_2 = "{}#{}".format(temp_date_2, temp_time_2)
            diff = str(datetime.strptime(form_2, FMT) -  
                    datetime.strptime(form_1, FMT))
                
            var = re.split("[:.]", diff)
            string = {name:{"start":temp_date,"end":temp_date_2,
                                    "hours":var[0], 
                                    "minutes":var[1],"seconds":var[2], 
                                    "same_day":(temp_date == temp_date_2),
                                    "start_time": temp_time,
                                    "end_time": temp_time_2}}
            
            output.write(json.dumps(string) + "\n")

    output.close()
#-----------------------------------------------------------------------------------THIS IS THE ONE FOR ADDING SHIT
def analyze_times(table, input_handler):
    
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
    
    output = open('C:/Users/James/Desktop/CASAS/test_samples/testicle.txt', 'w')
    
    temp_t1 = ["", ""]
    temp_t2 = [""]
    temp_d1 = [""]
    temp_d2 = [""]
    db = couch['test']
    #input = open(criki, 'r')
    data = {}
    cur_date = ""
    i = 1
    
    for entry in input_handler:
        entry = entry.strip()
        cat = entry.split("@")
        
        #check if same date
        if str(cat[0]) == cur_date:
            data = process_request(data, cat, temp_t1, temp_t2, temp_d1, temp_d2)
        else: #work on new date and write last one to mem
            #save to database here
            if cur_date != "":
                #output.write(json.dumps(data) + "\n")
                #database.save(data)
                #print data
                data = json.dumps(data)
                table.put_item(Item=json.loads(data, parse_float = decimal.Decimal))
            cur_date = cat[0]
            try:
                sleep = db[cur_date]['sleep_time']
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
            data = process_request(data, cat, temp_t1, temp_t2, temp_d1, temp_d2)
            
    #output.write(json.dumps(data) + "\n")
    #database.save(data)
    data = json.dumps(data)
    
    table.put_item(Item=json.loads(data, parse_float = decimal.Decimal))
    output.close()
    
def finalize_time(handler, location, name):
    output = open(location, 'w')
    cur_date = ''
    data = {}
            
    
    for entry in handler:
        entry = json.loads(entry.strip())
        
        #keep adding if the current date is the same day
        if (entry[name]['start'] == cur_date):
            data[name]['hours'] += int(entry[name]['hours'])
            #data[name]['inter_time']['interruptions'] += 1
            data[name]['end_time'] = entry[name]['end_time']
            
            if (data[name]['seconds'] + int(entry[name]['seconds']) >= 60):
                data[name]['minutes'] += 1
                data[name]['seconds'] += (int(entry[name]['seconds']) - 60)
            else:
                data[name]['seconds'] += int(entry[name]['seconds'])
                
            if (data[name]['minutes'] + int(entry[name]['minutes']) >= 60):
                data[name]['hours'] += 1
                data[name]['minutes'] += (int(entry[name]['minutes']) - 60)
            else:
                data[name]['minutes'] += int(entry[name]['minutes'])
        else:
            if cur_date != '':
                output.write(json.dumps(data) + "\n")
                #database.save(data)
            
            data = {name:{"hours":int(entry[name]['hours']), 
                          "minutes":int(entry[name]['minutes']),
                          "seconds":int(entry[name]['seconds']),
                          "start_time": entry[name]['start_time'],
                          "end_time": entry[name]['end_time']}, 
                    "date":cur_date}
                    
        
def finalize_sleep_time(handler, location):
    db = couch['test']
    output = open(location, 'w')
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

def calculate_averages(database):
    #output = open(ave, 'w')
    
    total = 0                    ##Number of nights
    inter_time_total = []         ##Adds up all the time the sleep was interrupted per night
    inter_amount_total = []      ##Adds up the number of times the sleep was interrupted 
    
    inter_time_sum = 0  
    inter_amount_sum = 0 
    
    #current_sleep_seconds = 0
    total_seconds = {"travel":0, "work":0, "relax":0, 
                     "shower":0, "meal_prep":0, "sleep":0, "interruptions":0.0}
    n = 0
    #mean of time in seconds
    mean = {"travel":0.0, "work":0.0, "relax":0.0, 
            "shower":0.0, "meal_prep":0.0, "sleep":0.0, "interruptions":0.0}
    #square variance of time in seconds
    M2 = {"travel":0.0, "work":0.0, "relax":0.0, 
          "shower":0.0, "meal_prep":0.0, "sleep":0.0, "interruptions":0.0}
    
    occurrences = {"travel":0, "work":0, "housekeeping":0, 
                   "relax":0, "wash_dishes":0, "shower":0, 
                   "meal_prep":0, "eating":0, "interruptions":0}
    #mean of occurrences
    meano = {"travel":0.0, "work":0.0, "housekeeping":0.0, 
                   "relax":0.0, "wash_dishes":0.0, "shower":0.0, 
                   "meal_prep":0.0, "eating":0.0, "interruptions":0.0}
    #square variance of occurrences
    M2o = {"travel":0.0, "work":0.0, "housekeeping":0.0, 
                   "relax":0.0, "wash_dishes":0.0, "shower":0.0, 
                   "meal_prep":0.0, "eating":0.0, "interruptions":0.0}
    
    #calculates the variance and mean
    #using the Welford method
    for id in database:
        try:
            n += 1
            path = database[id]['sleep_time']
            total_seconds['sleep'] = path['sleep']['hours'] * 3600 + path['sleep']['minutes'] * 60 + path['sleep']['seconds']
            occurrences['interruptions'] = path['inter_time']['occurrences']
            path = database[id]['activity']['travel']
            total_seconds['travel'] = path['hours'] * 3600 + path['minutes'] * 60 + path['seconds']
            occurrences['travel'] = path['occurrences']
            path = database[id]['activity']['work']
            total_seconds['work'] = path['hours'] * 3600 + path['minutes'] * 60 + path['seconds']
            occurrences['work'] = path['occurrences']
            path = database[id]['activity']['relax']
            total_seconds['relax'] = path['hours'] * 3600 + path['minutes'] * 60 + path['seconds']
            occurrences['relax'] = path['occurrences']
            path = database[id]['nutrition']['meal_prep']
            total_seconds['meal_prep'] = path['hours'] * 3600 + path['minutes'] * 60 + path['seconds']
            occurrences['meal_prep'] = path['occurrences']
            path = database[id]['hygiene']['shower']
            total_seconds['shower'] = path['hours'] * 3600 + path['minutes'] * 60 + path['seconds']
            occurrences['shower'] = path['occurrences']
            
            occurrences['housekeeping'] = database[id]['activity']['housekeeping']['occurrences']
            occurrences['wash_dishes'] = database[id]['hygiene']['wash_dishes']['occurrences']
            occurrences['eating'] = database[id]['nutrition']['eating']['occurrences']
            
            
            #calculate online variance and mean
            for key in total_seconds:
                delta = total_seconds[key] - mean[key]
                mean[key] += delta/n
                M2[key] += delta * (total_seconds[key] - mean[key])
                
            for key in occurrences:
                delta = occurrences[key] - meano[key]
                meano[key] += delta/n
                M2o[key] += delta * (occurrences[key] - meano[key])
            
            inter_time_total.append(database[id]['sleep_time']['inter_time']['average'] * database[id]['sleep_time']['inter_time']['occurrences']) 
            inter_amount_total.append(database[id]['sleep_time']['inter_time']['occurrences'])
            
            inter_time_sum += inter_time_total[total] 
            inter_amount_sum += inter_amount_total[total]
            
            total += 1
        except:
            print "{} was missing one or more fields".format(id)
    
    ## now all the data is in 3 lists
    ##get sum
    inter_time_average = float(inter_time_sum) / total
    inter_amount_average = float(inter_amount_sum) / total
    
    inter_time_sd = calc_sd(inter_time_total, inter_time_average, total)        ####
    
    
    data = {"USER_ID":TEST_ID,
            "_date": "regularity", 
            "last_rev":time.asctime(time.localtime(time.time())),
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
                           "interruptions":{"t_av":inter_amount_average,
                                            "t_sd":inter_time_sd,
                                            "o_av":meano['interruptions'],
                                            "o_sd":sqrt(M2o['interruptions']/n)}}
            }
    
    #database.save(data)
    data = json.dumps(data)
    table.put_item(Item=json.loads(data, parse_float = decimal.Decimal))
    
def calc_sd(data_list, average, total):
    
    sum_diff_sq = 0
    for data in data_list:
        sum_diff_sq += (data - average) ** 2
        
    return math.sqrt((1.0/float(total)) * sum_diff_sq) 
        
def days_between(cur, tar):
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
                
#formatted = open(loc, 'r')
#calculate_sleep_time(formatted, supp)
#formatted.close()
#sort_data(handler, loc)
#fin_handler = open(supp, 'r')
#finalize_sleep_time(fin_handler, criki)
#fin_handler.close()
sort_data(handler, 'C:/Users/James/Desktop/CASAS/test_samples/unique_ids_2.txt')
#formatted = open('C:/Users/James/Desktop/CASAS/test_samples/unique_ids.txt', 'r')
#calculate_time(formatted, 'C:/Users/James/Desktop/CASAS/test_samples/cooking.txt', "Meal_Preparation begin", 'Meal_Preparation end', 'meal_prep')
#analyze_times(table, formatted)
#formatted.close()
#calculate_averages(couch['casas_test'])
handler.close()