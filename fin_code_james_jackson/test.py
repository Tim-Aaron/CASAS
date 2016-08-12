'''
Created on Jun 24, 2016

@author: James

A Quick Program for sending test queries to the QandA machine to simulate
Emily
'''

import time
import rpc_module

try:
    handler = rpc_module.RabbitMQRPCClient()
except:
    print "Connection Failure"
    
            
data = {    
        'request_time': {
            'time' : time.asctime(time.localtime(time.time()))
        },
        'user_information': {
            'name' : 'Louisa',
            'patient': 'Ingle',
            'relationship': 'Great Aunt',
            'id': 'casas_test'
        },
        'request_type': {
            'information_type': 'sleep',
            'time_type': 'month',
            'time_modifier': '2010-12'
        }
    }   


response = handler.call(data, 'question_queue')

for key in response:
    print "{}: {}".format(key,response[key])