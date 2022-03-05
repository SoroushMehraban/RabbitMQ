import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()

channel.queue_declare(queue="task_queue", durable=True)

body_message = " ".join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(exchange='', routing_key="task_queue", body=body_message.encode(),
                      properties=pika.BasicProperties(delivery_mode=2))
print(f" [x] sent `{body_message}`")
connection.close()
