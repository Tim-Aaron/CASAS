'''
Created on Jul 8, 2016

@author: James
'''
import pika
import time
'''

Used for reusing old data to simulate a live data stream.
'''

handler = open('C:/Users/James/Desktop/CASAS/test_samples/unique_ids.txt', 'r')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='smarthomedata.io',
                                                               port=5672, 
                                    credentials=pika.credentials.
                                    PlainCredentials('emily','')))
                                     
channel = connection.channel()
channel.queue_declare(queue='test.firehose.emily')

#populates with one sensor activation every five seconds 20 times
def populate(inpt, channel):
    for i in range(20):
        event = inpt.next()
        event = event.strip()
        channel.basic_publish(exchange='',
                              routing_key='firehose.emily',
                              body=event)
        time.sleep(5)

populate(handler, channel)
handler.close()