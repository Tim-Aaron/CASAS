from __future__ import print_function
'''

Created on Jun 22, 2016

@author: James, Jackson

@description:
This program is the Lambda function for the 
user interface and care assistant "Emily".

Designed to help care givers access pertinent updates on their patients
remotely.


This project is the  work of CASAS
and Washington State University
'''

import json
import rpc_module
import time
from math import floor

time_start = time.time()

REQUEST_TYPES = {"HygieneIntent": "hygiene", "GeneralIntent": "general", 
                 "NutritionIntent": "nutrition", "SleepIntent": "sleep", 
                 "ElopementIntent": "elopement", "MedicineIntent": "medicine", 
                 "ActivityIntent": "activity"}
                                                                                  
FIELDS = {'activity' : ['travel', 'work', 'housekeeping', 'relax'], 
          'hygiene': ['shower', 'wash_dishes'], 
          'nutrition': ['eating','meal_prep'],
          'sleep_time': ['inter_time', 'sleep'],
          'medicine': []}

"The time spent {} was abnormally high. "

REAL_RESPONSES_OCC = {'housekeeping': 'times they cleaned the house',
                      'wash_dishes': 'times they washed the dishes',
                      'eating' : 'times they ate',
                      'relax' : 'times they relaxed',
                      'travel': 'times they left the house',
                      'work': 'times they worked',
                      'shower' : 'times they took a shower',
                      'meal_prep': 'times they prepared a meal',
                      'inter_time': 'interruptions they experienced while sleeping'
                      }
REAL_RESPONSES_TIME = {'relax': 'relaxing',
                       'travel': 'away from the house',
                       'work': 'working',
                       'shower': 'showering',
                       'meal_prep': 'preparing meals',
                       'inter_time': 'being interrupted at night',
                       'sleep': 'sleeping'
                       }

#TEST DATE. FINAL SHOULD USE CURRENT DATE
DATE = '2010-12-07'

#-----------------------INVOCATION FUNCTION-------------------------------------

#Pre: accepts an event and a context object. Event is a json object which has
#all the pertinent information regarding the user request. The context object
#has state information.
#Post: handles the session starting up.
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    
    print("event.session.application.applicationId=" + 
        event['session']['application']['applicationId'])
        
    if event['session']['new']:
        on_session_start({'requestId': event['request']['requestId']},
                           event['session'])
        
    if (event['request']['type'] == "LaunchRequest"):
        return on_launch(event['request'], event['session'])
    elif (event['request']['type'] == "IntentRequest"):
        return on_intent(event['request'], event['session'])
    elif (event['request']['type'] == "EndRequest"):
        return on_session_end(event['request'], event['session'])
    
#--------------Functions that control the startup behavior----------------------

#function which is called for every new sesssion  
def on_session_start(session_started_request, session):
    """Prints the RequestID"""
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

#function that is called whenever user says "Ask Emily"
def on_launch(launch_request, session):
    """
    Launches when people call the app without a specific intent
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    
    return get_welcome_message()

#Launches the app when people ask Emily to do perform a specific action.
def on_intent(intent_request, session):
          
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent_name = intent_request['intent']['name']
        
    if intent_name == "GeneralIntent":                                                                      
        return ask_question(intent_request, session, 
                                 'General Health', analyze_general_response)                              
    elif intent_name == "HygieneIntent":                                            
        return ask_question(intent_request, session, 
                                 "Hygiene", analyze_hygiene_response)
    elif intent_name == "ElopementIntent":
        return ask_question(intent_request, session, 
                                 "Elopement", None)
    elif intent_name == "NutritionIntent":
        return ask_question(intent_request, session, 
                                 "Nutrition", analyze_nutrition_response)
    elif intent_name == "SleepIntent":
        return ask_question(intent_request, session, 
                                 "Sleeping", analyze_sleep_response)
    elif intent_name == "MedicineIntent":
        return ask_question(intent_request, session, 
                                 "Medicine", None)
    elif intent_name == "ActivityIntent":
        return ask_question(intent_request, session, 
                                 "Activity", analyze_activity_response)
    elif intent_name == "AMAZON.HelpIntent":
        return handle_help_request()
    elif (intent_name == "AMAZON.CancelIntent" or 
          intent_name == "AMAZON.StopIntent"):
        return handle_session_end()
    elif intent_name == 'DontKnowIntent':
        return handle_help_request()
    else:
        raise ValueError("Invalid intent")
 
#called whenever the user ends the session.      
def on_session_end(end_request, session):
    
    print("on_session_ended requestId=" + end_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    
    
    
# --------------- Functions that control the skill's behavior ------------------

#OBSOLETE FUNCTION
def get_time(intent, session):
    """
    If the user says "Has she been showering" this will prompt the user to
    Give a time frame (today/this month/this year)
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    speech_output = "Please specify a time"
    reprompt_text = "Please specify a time"
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#Post: Says a welcome message and prompts the user to ask it a question
def get_welcome_message():
    card_title = "Welcome to CASAS"
    session_attributes = {}
    should_end_session = False
    
    speech_output = "Hello, I am Emily, your personal assistant to your loved "\
                    "ones or patients living in casas smart homes. " \
                    "You may ask how your family member is doing, or say help" \
                    " for more options."
                                        
    reprompt_text = "You may ask how your family member is doing, or say help" \
                    " for more options." 
                    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#called when the user prompts the session to end       
def handle_session_end():
    card_title = "Session End"
    speech_output = "Good Bye."
    should_end_session = True
    
    return build_response(None, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

#called when the user asks for help or says an illegitimate phrase 
def handle_help_request():
    session_attributes = {}
    card_title = "Help"
    should_end_session = False
    speech_output = "You can use me to ask questions regarding the health of "\
                    "the patient you are currently registered to. " \
                    "This can be questions about their hygiene, activity, "\
                    "nutrition, medication, and sleep."
    reprompt_text = "You can use me to ask questions regarding the health of "\
                    "the patient you are currently registered to. " \
                    "This can be questions about their hygiene, activity, "\
                    "nutrition, medication, and sleep." \
                    " Try asking. How is the patient doing today. replacing " \
                    "the patient with their personal name."
                    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#Pre: accepts intent and session objects which hold query variables. 
# accepts a function to be called according to the type and accepts a card title. 
#Post:    
def ask_question(intent, session, card_title, function=None):
    session_attributes = {}
    should_end_session = False                                                  

    user_id = 'casas_test'
    timestamp = intent['timestamp']
    #change when the CIRCLE OF CARE system is ready
    #user_id = session['user']['userId']
    request_type = REQUEST_TYPES[intent['intent']['name']]
    if ('value' in intent['intent']['slots']['Time']):
        request_duration = intent['intent']['slots']['Time']['value']
    else:
        request_duration = 'day'
        
    date_list = convert_date_request(timestamp, request_duration)
    
    #change when the CIRCLE OF CARE system is ready
    json_file = build_JSON(timestamp, "James", "Jackson", "Cousin", user_id, 
                           request_type, date_list[1], date_list[0])
    
    response = get_data_from_rpc(json_file)
    if (response['response'].strip().lower() == 'okay'):
        if function != None:    
            speech_output = function(response)
        else:
            speech_output = "The {} method is not available.".format(request_type)
    else: 
        speech_output = response['response']
    
    if (speech_output.strip().endswith('.')):
        speech_output = speech_output.strip() + " Is there anything else I can help you with?"
    else:
        speech_output = speech_output.strip() + ". Is there anything else I can help you with?"
        
    reprompt_text = "Is there anything else I can help you with?"
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    
# --------------- Helpers that build all of the responses ----------------------
#Pre:accepts a string title, output, reprompt_text and a boolean for if the
# session should end or not
#Post: creates a JSON object for alexa to use as a response.
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
    
def build_JSON(time_of_request, user_name, patient_name, relationship, 
               user_id, request_type, time_type, time_modifier):
    
    return {
        'request_time': {
            'time': time_of_request
        },
        'user_information': {
            'name': user_name,
            'patient': patient_name,
            'relationship': relationship,
            'id': user_id
        },
        'request_type': {
            'information_type': request_type,
            'time_type': time_type,
            'time_modifier': time_modifier
        }
    }

#Pre: accepts a float number value
#Post: turns a float into a number Alexa can read that will be easy to
#understand
def make_understandable(value):
    whole = floor(value) #43.234 -> 43
    
    remaining = value - whole #43.234 -> 0.23
    
    #to get 2 decimal places
    remaining = remaining * 10 
    remaining = floor(remaining)
    
    whole = int(whole)
    remaining = int(remaining)
    
    if (int(remaining) != 0):
        return str(whole) + " point " + str(remaining)
    else: 
        return str(whole)

#Post: converts a date code into an understandable
#string representation 
def date_to_day(date):
    
    year = date[0:4] 
    month = date[5:7]
    day = date[8:10]
    
    month_int = int(month)
    
    month_name = ["January", "February", "March", "April", "May", 
                  "June", "July", "August", "September", "October", 
                  "November", "December"]
    
    month_act = month_name[month_int-1]
    
    return month_act + " , " + day + " , " + year

#Pre: Requires a timestamp or date and a time_value string corresponding to the 
#time related phrase
#Post: returns a string corresponding to the time request.   
def convert_date_request(timestamp, time_value):
    
    date = DATE.split("-")
    
    year = int(date[0]) ## int(timestamp[0:4]) 
    month = int(date[1]) ## 01 ##int(timestamp[5:7])
    day = int(date[2]) ## 12 ##int(timestamp[8:10])
    
    date_list = [DATE, "day"]
        
    if time_value == "this year":
        return [str(year), "year"]
    if time_value == "last year": 
        return [str(year-1), "year"]
    elif time_value == "2 years ago":
        return [str(year-2), "year"]
    
    ##if time_value == "Today" Wont change anything
    if time_value == "yesterday":
        date_list[1] = "day"  
        day = day - 1
    elif time_value == "2 days ago":
        date_list[1] = "day"
        day = day - 2
    if time_value == "today":
        date_list[1] = "day"
    if day <= 0:
        month = month - 1
        if month == 0:
            month = 12
            year = year - 1
        if month in [1,3,5,7,8,10,12]:
            day = 31+ day
        if month in [4,6,9,11]:
            day = 30 + day
        if month in [2]:
            if year % 4 == 0:
                day = 29 + day
            else:
                day = 28 + day
    if day < 10:
        day = "0" + str(day)
    else:
        day = str(day)
    
    
    if time_value == "this month":
        date_list[1] = "month"
    elif time_value == "last month":
        date_list[1] = "month"
        month = month - 1
    elif time_value == "2 months ago":
        date_list[1] = "month"
        month = month - 2
    if month == 0:
        month = 12
        year = year - 1
        
    if month >= 10:
        month = str(month)
    else:
        month = "0" + str(month)
        
    if time_value == "this week":
        ##panic
        date_list[1] = "week"
    if time_value == "last week":
        ##panic more
        date_list[1] = "week"
    
    if(date_list[1] == "day" or date_list[1] == "week"):
        date_list[0] = str(year) + "-" + month + "-" + day  
    elif(date_list[1] == "month"):
        date_list[0] = str(year) + "-" + month
        
    
    return date_list

#Pre: accepts session_attributes to be temporarily saved and 
# a speechlet_response string to be read off
#Post: returns the correct JSON package.
def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

#----------------Helpers that build and return requests-------------------------

#Pre: accepts a question in the correct format for the QandA server
#Post: returns the response from the QandA server.
def get_data_from_rpc(request):
    try:
        rpc_handler = rpc_module.RabbitMQRPCClient()
        
        response = rpc_handler.call(request, 'rpc_request')
    except:
        response = {'response':"Connection Error"}
    finally:
        return response
    
#------------------------ Data Analyzers ---------------------------------------

#ONLY WORKS FOR A DAILY RESPONSE FOR NOW
#Creates and returns general health overview string
#response based on the response    
def analyze_general_response(response):
    reg = response['regularity']
    date = response['date']
    print(response)
    
    if len(response['general'].items()) == 0:
        speech_output = "The patient's activity is normal. " + \
        "For questions regarding a specific aspect of " + \
        "the patient's life, please ask about a specific attribute."
        
    else:
        speech_output = "The patient experienced some unusual behavior. "
        for item in response['general']:            
            sCat = ""
            for field in FIELDS:
                if item in FIELDS[field]:
                    sCat = field
                    break
            if sCat != "":
                print("success")
                if 'to' in response['general'][item]:
                    if (float(response['general'][item]['to']) > 
                        float(reg[sCat][item]['o_av'])):
                        speech_output += "The amount of {} was abnormally high. ".format(REAL_RESPONSES_OCC[item])
                    else:
                        speech_output += "The amount of {} was abnormally low. ".format(REAL_RESPONSES_OCC[item])
                
                if 'tt' in response['general'][item]:
                    if (float(response['general'][item]['tt']) > 
                        float(reg[sCat][item]['t_av'])):
                        speech_output += "The time spent {} was abnormally high. ".format(REAL_RESPONSES_TIME[item])
                    else:
                        speech_output += "The time spent {} was abnormally low. ".format(REAL_RESPONSES_TIME[item])
            else:
                print("failure")       
    
    return speech_output  

#Pre: takes in the response from the QandA server
#Post: builds and returns a string response to be read back 
# which is an overview of the type.  
def analyze_sleep_response(response):    
    reg = response['regularity']['sleep_time']
    date = response['date'] #Fine as is
    date_type = response['types']['Ttype']
    if (date_type in ('week', 'month','year')):
        sleep = (float(response['sleep']['sleep']['t_hr']) + 
                 float(response['sleep']['sleep']['t_min']) / 60 + 
                 float(response['sleep']['sleep']['t_sec']) / 3600)
        inter_amount = int(response['sleep']['inter_time']['t_occurrences']) 
        inter_time = (float(response['sleep']['inter_time']['t_hr']) + 
                      float(response['sleep']['inter_time']['t_min']) / 60 + 
                      float(response['sleep']['inter_time']['t_sec']) / 3600) 
        average_sleep = (float(response['sleep']['sleep']['av_hours']) + 
                         float(response['sleep']['sleep']['av_min']) / 60)
        av_inter_num = float(response['sleep']['inter_time']['av_occurrences'])
        av_inter_time = float(response['sleep']['inter_time']['av_length_occurrences'])
        
    else:
        sleep = (float(response['sleep']['sleep']['hours']) + 
                 float(response['sleep']['sleep']['minutes']) / 60 +
                 float(response['sleep']['sleep']['seconds']) / 3600)
        inter_amount = int(response['sleep']['inter_time']['occurrences']) 
        inter_time = (float(response['sleep']['inter_time']['hours']) + 
                      float(response['sleep']['inter_time']['minutes']) / 60 + 
                      float(response['sleep']['inter_time']['seconds']) / 3600) 
    
    regularity = [float(reg['sleep']['t_av']), 
                  float(reg['sleep']['t_sd']), 
                  float(reg['inter_time']['t_av']), 
                  float(reg['inter_time']['t_sd']), 
                  float(reg['inter_time']['o_av']), 
                  float(reg['inter_time']['o_sd'])]
    
    date_ar = response['date'].split("-")
    month_name = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", 
                  "December"]
    try:
        month_num = int(date_ar[1])
    except:
        month_num = 0
    
    year = int(date_ar[0])
    
    start_date = response['start_date']
    end_date = response['end_date']
    
    sleep_difference = "" #will be "high" if over avg + sd and "low" if below
    inter_time_difference = ""
    inter_time_amount = ""
    
    if date_type == "day":
        if sleep > regularity[0] + regularity[1]:
            sleep_difference = "high"
        elif sleep < regularity[0] - regularity[1]:
            sleep_difference = "low"
        else:
            sleep_difference = "normal"
        
        if inter_time > regularity[2] + regularity[3]:
            inter_time_difference = "high"
        elif inter_time < regularity[2] - regularity[3]:
            inter_time_difference = "low"
        else:
            inter_time_difference = "normal"
            
        if inter_amount > regularity[4] + regularity[5]:
            inter_time_amount = "high"
        elif inter_amount < regularity[4] - regularity[5]:
            inter_time_amount = "low"
        else:
            inter_time_amount = "normal"
        
        date = date_to_day(date)
            
        speech_output = "Last night, The patient slept for " + \
                        "" + make_understandable(sleep) + \
                        " hours with " + make_understandable(inter_amount) + \
                        " interruptions for a total of " + \
                        make_understandable(inter_time) + " minutes. The " + \
                        "amount of sleep the patient got was " + \
                        sleep_difference + ". The number of interruptions " + \
                        "was " + inter_time_difference + \
                        ". The time of interruptions was " + inter_time_amount
    
    elif date_type in  ["week", "month", "year"]:
        if date_type == "week":
            speech_output = "On the week beginning " + start_date + \
            " and ending on " + end_date
        elif date_type == "month":
            speech_output = "In " + month_name[month_num-1]
        else:
            speech_output = "In " + str(year)
        
        if average_sleep > regularity[0] + regularity[1]:
            sleep_difference = "high"
        elif average_sleep < regularity[0] - regularity[1]:
            sleep_difference = "low"
        else:
            sleep_difference = "normal"
        
        if av_inter_time > regularity[2] + regularity[3]:
            inter_time_difference = "high"
        elif av_inter_time < regularity[2] - regularity[3]:
            inter_time_difference = "low"
        else:
            inter_time_difference = "normal"
            
        if av_inter_num > regularity[4] + regularity[5]:
            inter_time_amount = "high"
        elif av_inter_num < regularity[4] - regularity[5]:
            inter_time_amount = "low"
        else:
            inter_time_amount = "normal"
            
        speech_output = speech_output + " The patient slept for an average of " + make_understandable(sleep) + \
                        " hours with " + make_understandable(inter_amount) + " average interruptions with an average of " + \
                        make_understandable(inter_time) + " minutes. The amount of sleep the patient got was " + \
                        sleep_difference + ". The number of interruptions was " + inter_time_difference + \
                        ". The time of interruptions was " + inter_time_amount                                               
    return speech_output

#Pre: takes in the response from the QandA server
#Post: builds and returns a string response to be read back 
# which is an overview of the type.  
def analyze_activity_response(response):
    date = response['date']
    
    date_type = response['types']['Ttype']
    
    date_ar = response['date'].split("-")
    month_name = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", 
                  "December"]
    try:
        month_num = int(date_ar[1])
    except:
        month_num = 0
    
    year = int(date_ar[0])
    
    start_date = response['start_date']
    end_date = response['end_date']
    
    housekeeping_difference = "" 
    relax_difference = "" 
    travel_difference = "" 
    work_difference = "" 
    
    reg = response['regularity']['activity']
    date = response['date'] 
    date_type = response['types']['Ttype']
    if (date_type in ('week', 'month','year')):
        housekeeping_occ_ave = float(response['activity']['housekeeping']['av_occurrences'])
        housekeeping_occ_total = int(response['activity']['housekeeping']['t_occurrences'])
        
        relax_time_total = (float(response['activity']['relax']['t_hr']) + 
                           float(response['activity']['relax']['t_min']) / 60 + 
                           float(response['activity']['relax']['t_sec']) / 3600)#time relaxing in hours as float
        relax_time_ave_length = float(response['activity']['relax']['av_hours']) + float(response['activity']['relax']['av_min']) / 60 
        relax_occ_ave =int(response['activity']['relax']['t_occurrences'])
        
        travel_time_total = (float(response['activity']['travel']['t_hr']) + 
                           float(response['activity']['travel']['t_min']) / 60 + 
                           float(response['activity']['travel']['t_sec']) / 3600)#time relaxing in hours as float
        travel_time_ave_length = float(response['activity']['travel']['av_hours']) + float(response['activity']['travel']['av_min']) / 60 
        travel_occ_ave =int(response['activity']['travel']['t_occurrences'])
        
        work_time_total = (float(response['activity']['work']['t_hr']) + 
                           float(response['activity']['work']['t_min']) / 60 + 
                           float(response['activity']['work']['t_sec']) / 3600)#time relaxing in hours as float
        work_time_ave_length = float(response['activity']['work']['av_hours']) + float(response['activity']['work']['av_min']) / 60 
        work_occ_ave =int(response['activity']['work']['t_occurrences'])
    else:
        housekeeping_occ = int(response['activity']['housekeeping']['occurrences'])
        
        relax_time = (float(response['activity']['relax']['hours']) + 
                     float(response['activity']['relax']['minutes']) / 60 + 
                     float(response['activity']['relax']['seconds']) / 3600)#time relaxing in hours as float
        
        travel_time = (float(response['activity']['travel']['hours']) + 
                     float(response['activity']['travel']['minutes']) / 60 + 
                     float(response['activity']['travel']['seconds']) / 3600)#time traveling in hours as float
        
        work_time = (float(response['activity']['work']['hours']) + 
                     float(response['activity']['work']['minutes']) / 60 + 
                     float(response['activity']['work']['seconds']) / 3600)#time working in hours as float
    
    regularity = [float(reg['housekeeping']['o_av']), 
                  float(reg['housekeeping']['o_sd']), 
                  float(reg['relax']['o_av']), 
                  float(reg['relax']['o_sd']), 
                  float(reg['relax']['t_av']), 
                  float(reg['relax']['t_sd']),
                  float(reg['travel']['o_av']), 
                  float(reg['travel']['o_sd']), 
                  float(reg['travel']['t_av']), 
                  float(reg['travel']['t_sd']),
                  float(reg['work']['o_av']), 
                  float(reg['work']['o_sd']), 
                  float(reg['work']['t_av']), 
                  float(reg['work']['t_sd'])]
    
    if date_type == "day":
        #housekeeping
        if housekeeping_occ > regularity[0] + regularity[1]:
            housekeeping_difference = "higher than average"
        elif housekeeping_occ < regularity[0] - regularity[1]:
            housekeeping_difference = "lower than average"
        else:
            housekeeping_difference = "normal"
        
        #relax
        if relax_time * 3600 > regularity[4] + regularity[5]:
            relax_difference = "higher than average"
        elif relax_time * 3600 < regularity[4] - regularity[5]:
            relax_difference = "lower than average"
        else:
            relax_difference = "normal"
        
        #travel    
        if travel_time * 3600 > regularity[8] + regularity[9]:
            travel_difference = "higher than average"
        elif travel_time * 3600 < regularity[8] - regularity[9]:
            travel_difference = "lower than average"
        else:
            travel_difference = "normal"
        
        #work    
        if work_time * 3600 > regularity[12] + regularity[13]:
            work_difference = "high"
        elif work_time * 3600 < regularity[12] - regularity[13]:
            work_difference = "lower than average"
        else:
            work_difference = "normal"
        
        date = date_to_day(date)
            
        speech_output = "On " + date + ". The patient cleaned the house for a " + housekeeping_difference + \
                        make_understandable(housekeeping_occ) + " times. They relaxed for a " + relax_difference + \
                        make_understandable(relax_time) + " hours. They traveled for a " + travel_difference + \
                        make_understandable(travel_time) + " hours. They worked for a " + work_difference + \
                        make_understandable(work_time) + "hours."
    
    
    elif date_type in ["week", "month", "year"]:
        if date_type == "week":
            speech_output = "On the week beginning " + start_date + " and ending on " + end_date
        elif date_type == "month":
            speech_output = "In " + month_name[month_num-1]
        else:
            speech_output = "In " + str(year)
            
        if housekeeping_occ_ave > regularity[0] + regularity[1]:
            housekeeping_difference = "higher than average"
        elif housekeeping_occ_ave < regularity[0] - regularity[1]:
            housekeeping_difference = "lower than average"
        else:
            housekeeping_difference = "normal"
        
        #relax
        if relax_time_ave_length * 3600 > regularity[4] + regularity[5]:
            relax_difference = "higher than average"
        elif relax_time_ave_length * 3600 < regularity[4] - regularity[5]:
            relax_difference = "lower than average"
        else:
            relax_difference = "normal"
        
        #travel    
        if travel_time_ave_length * 3600 > regularity[8] + regularity[9]:
            travel_difference = "higher than average"
        elif travel_time_ave_length * 3600 < regularity[8] - regularity[9]:
            travel_difference = "lower than average"
        else:
            travel_difference = "normal"
        
        #work    
        if work_time_ave_length * 3600 > regularity[12] + regularity[13]:
            work_difference = "higher than average"
        elif work_time_ave_length * 3600 < regularity[12] - regularity[13]:
            work_difference = "lower than average"
        else:
            work_difference = "normal"
            
            
 
        speech_output = speech_output + " The patient cleaned the house for a " + housekeeping_difference + make_understandable(housekeeping_occ_ave) + \
                        " times per day, totaling "+ make_understandable(housekeeping_occ_total) + " times. They relaxed for a"+ relax_difference + make_understandable(relax_time_ave_length) +\
                         " hours for " + make_understandable(relax_occ_ave) + " average times per day, totaling " + make_understandable(relax_time_total) + " times. They traveled for a" + travel_difference +\
                         make_understandable(travel_time_ave_length) + " hours for " + make_understandable(travel_occ_ave) + " average times per day, totaling " + make_understandable(travel_time_total) + \
                        ". They worked for " + work_difference + make_understandable(work_time_ave_length) + " hours for " + make_understandable(work_occ_ave) + " average times per day, totaling " + \
                        make_understandable(work_time_total)
    
    
    return speech_output

#Pre: takes in the response from the QandA server
#Post: builds and returns a string response to be read back 
# which is an overview of the type.  
def analyze_hygiene_response(response):  
    date = response['date'] 
    date_type = response['types']['Ttype']
    date_ar = date.split("-")
    month_name = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    try:
        month_num = int(date_ar[1])
    except:
        month_num = 0
    
    year = int(date_ar[0])
    
    reg = response['regularity']['hygiene']
    
    start_date = response['start_date']
    end_date = response['end_date']
    
    wash_dishes_difference = "" 
    shower_difference = ""  
    
    if (date_type in ('week', 'month','year')):
        wash_dishes_occ_ave = float(response['hygiene']['wash_dishes']['av_occurrences'])
        wash_dishes_occ_total = int(response['hygiene']['wash_dishes']['t_occurrences'])
        
        shower_time_total = (float(response['hygiene']['shower']['t_hr']) + 
                           float(response['hygiene']['shower']['t_min']) / 60 + 
                           float(response['hygiene']['shower']['t_sec']) / 3600)#time showering in hours as float
        shower_time_ave_length = float(response['hygiene']['shower']['av_hours']) + float(response['hygiene']['shower']['av_min']) / 60 
        shower_occ_ave =int(response['hygiene']['shower']['t_occurrences'])
    else:
        wash_dishes_occ = int(response['hygiene']['wash_dishes']['occurrences'])
        
        shower_time = (float(response['hygiene']['shower']['hours']) + 
                     float(response['hygiene']['shower']['minutes']) / 60 + 
                     float(response['hygiene']['shower']['seconds']) / 3600)#time showering in hours as float
    
    regularity = [float(reg['wash_dishes']['o_av']), 
                  float(reg['wash_dishes']['o_sd']), 
                  float(reg['shower']['o_av']), 
                  float(reg['shower']['o_sd']), 
                  float(reg['shower']['t_av']), 
                  float(reg['shower']['t_sd'])]
        
    
    if date_type == "day":
        #wash_dishes
        if wash_dishes_occ > regularity[0] + regularity[1]:
            wash_dishes_difference = "higher than average"
        elif wash_dishes_occ < regularity[0] - regularity[1]:
            wash_dishes_difference = "lower than average"
        else:
            wash_dishes_difference = "normal"
        
        #shower
        if shower_time * 3600 > regularity[4] + regularity[5]:
            shower_difference = "higher than average"
        elif shower_time * 3600 < regularity[4] - regularity[5]:
            shower_difference = "lower than average"
        else:
            shower_difference = "normal"
        
        date = date_to_day(date)
            
        speech_output = "On " + date + ". The patient washed dishes for a " + wash_dishes_difference + \
                        " " + make_understandable(wash_dishes_occ) + " times. They showered for a " + shower_difference + \
                        " " + make_understandable(shower_time) + " hours." 



                        
    elif date_type in ["week", "month", "year"]:
        if date_type == "week":
            speech_output = "On the week beginning " + start_date + " and ending on " + end_date
        elif date_type == "month":
            speech_output = "In " + month_name[month_num-1]
        else:
            speech_output = "In " + str(year)
        
        if wash_dishes_occ_ave > regularity[0] + regularity[1]:
            wash_dishes_difference = "higher than average"
        elif wash_dishes_occ_ave < regularity[0] - regularity[1]:
            wash_dishes_difference = "lower than average"
        else:
            wash_dishes_difference = "normal"
        
        #relax
        if shower_time_ave_length * 3600 > regularity[4] + regularity[5]:
            shower_difference = "higher than average"
        elif shower_time_ave_length * 3600 < regularity[4] - regularity[5]:
            shower_difference = "lower than average"
        else:
            shower_difference = "no different than"    
        

        speech_output = speech_output + " The patient washed dishes for a " + wash_dishes_difference + make_understandable(wash_dishes_occ_ave) + \
                        " times per day, totaling "+ make_understandable(wash_dishes_occ_total) + " times. They showered for a"+ shower_difference + make_understandable(shower_time_ave_length) +\
                         " hours for " + make_understandable(shower_occ_ave) + " average times per day, totaling " + make_understandable(shower_time_total) + " times"
    
    return speech_output

#Pre: takes in the response from the QandA server
#Post: builds and returns a string response to be read back 
# which is an overview of the type.  
def analyze_nutrition_response(response):
    date = response['date'] 
    date_type = response['types']['Ttype']
    date_ar = date.split("-")
    month_name = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    try:
        month_num = int(date_ar[1])
    except:
        month_num = 0
    
    year = int(date_ar[0])
    
    reg = response['regularity']['nutrition']
    
    start_date = response['start_date']
    end_date = response['end_date']
    
    eating_difference = "" 
    meal_prep_difference = ""
        
    if (date_type in ('week', 'month','year')):
        eating_occ_ave = float(response['nutrition']['eating']['av_occurrences'])
        eating_occ_total = int(response['nutrition']['eating']['t_occurrences'])
        
        meal_prep_time_total = (float(response['nutrition']['meal_prep']['t_hr']) + 
                           float(response['nutrition']['meal_prep']['t_min']) / 60 + 
                           float(response['nutrition']['meal_prep']['t_sec']) / 3600)#time showering in hours as float     NOT SURE ABOUT THIS BECAUSE CANNOT SEE EXACT FORMAT
        meal_prep_time_ave_length = float(response['nutrition']['meal_prep']['av_hours']) + float(response['nutrition']['meal_prep']['av_min']) / 60
        meal_prep_occ_ave =int(response['nutrition']['meal_prep']['t_occurrences'])
    else:
        eating_occ = int(response['nutrition']['eating']['occurrences'])
        
        meal_prep_time = (float(response['nutrition']['meal_prep']['hours']) + 
                     float(response['nutrition']['meal_prep']['minutes']) / 60 + 
                     float(response['nutrition']['meal_prep']['seconds']) / 3600)#time showering in hours as float
    
    regularity = [float(reg['eating']['o_av']), 
                  float(reg['eating']['o_sd']), 
                  float(reg['meal_prep']['o_av']), 
                  float(reg['meal_prep']['o_sd']), 
                  float(reg['meal_prep']['t_av']), 
                  float(reg['meal_prep']['t_sd'])]
    
    
    if date_type == "day":
        #eating
        if eating_occ > regularity[0] + regularity[1]:
            eating_difference = "higher than average"
        elif eating_occ < regularity[0] - regularity[1]:
            eating_difference = "lower than average"
        else:
            eating_difference = "normal"
        
        #shower
        if meal_prep_time * 3600 > regularity[4] + regularity[5]:
            meal_prep_difference = "higher than average"
        elif meal_prep_time * 3600 < regularity[4] - regularity[5]:
            meal_prep_difference = "lower than average"
        else:
            meal_prep_difference = "normal"
        
        date = date_to_day(date)
            
        speech_output = "On " + date + ". The patient ate for a " + eating_difference + \
                        " " + make_understandable(eating_occ) + " times. They prepared their meals for a " + meal_prep_difference + \
                        " " + make_understandable(meal_prep_time) + " hours." 
                   
    elif date_type in ["week", "month", "year"]:
        if date_type == "week":
            speech_output = "On the week beginning " + start_date + " and ending on " + end_date
        elif date_type == "month":
            speech_output = "In " + month_name[month_num-1]
        else:
            speech_output = "In " + str(year)
        
        if eating_occ_ave > regularity[0] + regularity[1]:
            eating_difference = "higher than average"
        elif eating_occ_ave < regularity[0] - regularity[1]:
            eating_difference = "lower than average"
        else:
            eating_difference = "normal"
        
        #relax
        if meal_prep_time_ave_length * 3600 > regularity[4] + regularity[5]:
            meal_prep_difference = "higher than average"
        elif meal_prep_time_ave_length * 3600 < regularity[4] - regularity[5]:
            meal_prep_difference = "lower than average"
        else:
            meal_prep_difference = "no different than"    
        

        speech_output = speech_output + " The patient ate for a " + eating_difference + make_understandable(eating_occ_ave) + \
                        " times per day, totaling "+ make_understandable(eating_occ_total) + " times. They prepared their meals for a"+meal_prep_difference + make_understandable(meal_prep_time_ave_length) +\
                         " hours for " + make_understandable(meal_prep_occ_ave) + " average times per day, totaling " + make_understandable(meal_prep_time_total) + " times"
    
    return speech_output
