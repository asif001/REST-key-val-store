# REST key-val Store


## Python Package Dependencies
1. Django
2. djangorestframework
3. msgpack
4. django-redis
5. redis 


## Introduction
In this project a REST API has been developed. The target of the API is to store, fetch and update arbitrary length key:value. 


## Features
* Store arbitrary length key-val
* Every key has default TTL 5 min. After 5 miniutes the store key is automatically deleted
* On every GET or PATCH request, the corresponding keys' TTL is reset to default  


# Quick start running the project
## Via Docker
1.	Install and configure Docker for your system - https://docs.docker.com/install/
2. `git clone https://github.com/asif001/REST-key-val-store.git`
2.	cd to REST-key-val-store project directory 
3. 	Launch CLI
4.	Run `docker-compose up` or `docker-compose up -d` (-d for running in detached mode)
5.	To see the logs run `docker logs <container_name> -f`
6.	The service is running at https://127.0.0.1:8000/api/values at host machine
7.	Send POST, GET or PATCH request (Instructions below) at https://127.0.0.1:8000/api/values to see the REST API in action


## Contributing
The main reason to publish something open source, is that anyone can just jump in and start contributing to my project.
So If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.


## Author
Asifur Rahman
asifurarahman@gmail.com
Student at Department of Computer Science and Engineering
Khulna University of Engineering & Technology, Khulna
Bangladesh