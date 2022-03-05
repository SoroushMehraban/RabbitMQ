# RabbitMQ
RabbitMQ is an open-source message broker that implements AMQP (Advanced Message Queue Protocol).  
In this repository I run this on Docker and write a python program to use it.

# Setup
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
