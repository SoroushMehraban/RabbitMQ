import pika
import time


def call_back(ch, method, properties, body):
    body_message = body.decode('utf-8')
    process_time = body_message.count('.')
    print()
    print(f" [x] received {body_message}")
    print(f" [x] Processing {process_time} seconds ...")
    time.sleep(process_time)
    print(" [x] Finished processing.")
    ch.basic_ack(delivery_tag=method.delivery_tag)


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()

channel.queue_declare(queue="task_queue", durable=True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="task_queue", on_message_callback=call_back)
print(" [x] Waiting for the message.")
channel.start_consuming()
