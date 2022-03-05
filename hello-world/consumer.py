import pika


def call_back(ch, method, properties, body):
    print(f" [x] received {body}")


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()

channel.queue_declare(queue="hello")

channel.basic_consume(queue="hello", on_message_callback=call_back, auto_ack=True)
print(" [x] Waiting for the message.")
channel.start_consuming()
