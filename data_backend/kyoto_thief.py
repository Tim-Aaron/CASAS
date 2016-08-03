'''
Created on Jul 14, 2016

@author: James

Takes Data from Kyoto Stream and stores to a file for 
Machine learning analysis
'''

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='smarthomedata.io',
                                                               port=5672,
                                    credentials=pika.credentials.
                                    PlainCredentials('emily','Upd8ta2016!')))
channel = connection.channel()

filo = 'C:/Users/James/Desktop/CASAS/stream_data/kyoto_data_1.txt'
handler = open(filo, 'w')
count = 0

#handler for if a message comes in to steal 5000 pieces of data
def on_request(ch, method, props, body):
    global count
    
    if count < 5000:
        handler.write(str(body) + "\n")
    else:
        print "bye"
        connection.close()
        handler.close()
        
    count += 1
    ch.basic_ack(delivery_tag = method.delivery_tag)
    
channel.basic_consume(on_request, queue='firehose.emily')

channel.start_consuming()