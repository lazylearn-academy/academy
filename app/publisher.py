import pika
import pickle
from config import RABBIT_USER, RABBIT_PWD, RABBIT_HOST, RABBIT_PORT

def send_email_verification(data):
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PWD)
    parameters = pika.ConnectionParameters(RABBIT_HOST,
                                   RABBIT_PORT,
                                   '/',
                                   credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='email_verifications', durable=True)
    channel.basic_publish(exchange='',
                          routing_key='email_verifications',
                          body=pickle.dumps(data))
    connection.close()
