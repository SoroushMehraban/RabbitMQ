# RabbitMQ
RabbitMQ is an open-source message broker that implements AMQP (Advanced Message Queue Protocol).  
In this repository I run this on Docker and write a python program to use it.

## Setup
It can be pulled from the dockerhub using the following command:
```text
docker pull rabbitmq:3-management
```
After that, we can run the container.
```text
docker run --rm -d --hostname my-rabbit --name rabbit1 -p 15672:15672 -p 5672:5672 rabbitmq:3-management
```
Notes about the preceding command:
- **--rm**: Automatically remove the container when it exits.
- **-d**: Detached mode. Run container in background and print container ID.
- **-hostname**: According to the [Official Repsitory](https://hub.docker.com/_/rabbitmq), RabbitMQ stores data based 
  on "Node Name", which defaults to the hostname. So it is mandatory to specify hostname.
- **--name**: Name of the container.
- **-p**: Publish a container's port(s) to the host.

We can then open the RabbitMQ on our browser located on [http://localhost:15672/](http://localhost:15672/). The default
username and password is `guest`.

## Using Python (hello-world)
### Install library
```text
pip install pika
```
### Producer
After importing pika, first, we need to create a connection and a channel.
```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()
```

We can create a queue using the following line.
```python
channel.queue_declare(queue="hello")
```
In the preceding code, it declares a queue in case if it does not exist.

The easiest way to publish a message on the queue is by using `.basic_public` method.
```python
channel.basic_publish(exchange='', routing_key="hello", body=b"Hello World!")
```

Finally, we close the connection.
```python
connection.close()
```
### Consumer
The first part is just like the producer.
```python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()

channel.queue_declare(queue="hello")
```
We can consume the message using the following lines:
```python
def call_back(ch, method, properties, body):
    print(f" [x] received {body}")
    
channel.basic_consume(queue="hello", on_message_callback=call_back, auto_ack=True)
print(" [*] Waiting for the message.")
channel.start_consuming()
```
### Execution procedure
After running `consumer.py` on hello-world directory, we can see the following line printed on the terminal:
```text
[*] Waiting for the message.
```
Then after executing `producer.py`, it sends `b"Hello World!"` to the `hello` queue and consumer receives and prints
that on the terminal.

**What if we have multiple consumers?** By having this kind of implementation, it executes Round-robin algorithm. 
