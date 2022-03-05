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
Note that when `exhchange` is an empty string, it means that only on consumer should receive the message.

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
In the preceding code, `auto_ack=True` means that it automatically acknowledges receipt of the message.
### Execution procedure
After running `consumer.py` on hello-world directory, we can see the following line printed on the terminal:
```text
[*] Waiting for the message.
```
Then after executing `producer.py`, it sends `b"Hello World!"` to the `hello` queue and consumer receives and prints
that on the terminal.

**What if we have multiple consumers?** By having this kind of implementation, it executes Round-robin algorithm.  
**But what if after receiving the third message, the first consumer is busy, and the second consumer is free?** Since it
uses Round-robin algorithm, it could be problematic.
## Change the default receiving order (workers)
### Producer
Although we don't need to change anything here, we can make the message persistent. Simply put, if the message broker rebooted in the middle, the message that the producer published wouldn't be lost.  
There are two slight modifications needed for that:
```python
channel.queue_declare(queue="task_queue", durable=True)

body_message = " ".join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(exchange='', routing_key="task_queue", body=body_message.encode(),
                      properties=pika.BasicProperties(delivery_mode=2))
```
The first modification is that we added the `durable=True` parameter when declaring the queue to Survive a reboot of RabbitMQ.
The second change is adding the `properties` parameter with `delivery_mode=2`, which means that the message should be persistent.

### Consumer
The consumer code after modification.
```python
import pika
import time


def call_back(ch, method, properties, body):
    body_message = body.decode('utf-8')
    process_time = body_message.count('.')
    
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
```
The first modification is adding `.basic_qos` method before `.basic_consume`. Here `prefetch_count=1` means that it can
only fetch one message from queue at the time. In other words, if two messages are received and this consumer is busy
processing the previous message, the message broker assigns the message to another consumer.

**But how message broker can detect that this consumer is busy?** By acknowledgement. Note that `auto_ack` parameter is
removed from `.basic_consume`. Additionally, on `call_back` function, we send `basic_ack` after the processing.
### Execution scenario
Imagine we have one instance of producer called `producer` and two instances of consumers called `consumer1` and
`consumer2`.  
Now, the `producer` is executed three times by the user consecutively:
```text
> python producer.py Hello World ................................
> python producer.py Hello World 1
> python producer.py Hello World 2
> python producer.py Hello World 3
```
The first execution sends Hello world, followed by 32 dots. This means the receiver should wait 32 seconds to process it.

So the `consumer1` receives the message and prints these outputs on the terminal:
```text
 [x] Waiting for the message.

 [x] received Hello World ................................
 [x] Processing 32 seconds ...
```
Now, since the `consumer1` is busy, the message broker sends the rest to the `consumer2`. Hence, the `consumer2` outputs on the terminal are:
```text
 [x] Waiting for the message.

 [x] received Hello World 1
 [x] Processing 0 seconds ...
 [x] Finished processing.

 [x] received Hello World 2
 [x] Processing 0 seconds ...
 [x] Finished processing.

 [x] received Hello World 3
 [x] Processing 0 seconds ...
 [x] Finished processing.
```
