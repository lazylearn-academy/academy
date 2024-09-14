import pika, sys, os
import pickle
from utils import verify_email
from config import RABBIT_USER, RABBIT_PWD, RABBIT_HOST, RABBIT_PORT

def main():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PWD)
    parameters = pika.ConnectionParameters(RABBIT_HOST,
                                   RABBIT_PORT,
                                   '/',
                                   credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue='email_verifications', durable=True)

    def callback(ch, method, properties, body):
        data = pickle.loads(body)
        email = data.get("email")
        code = data.get("code")
        verify_email(email, code)

    channel.basic_consume(queue='email_verifications', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
