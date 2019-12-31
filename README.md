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
* Every key has default TTL 5 min. After 5 minutes the store key is automatically deleted
* On every GET or PATCH request, the corresponding keys' TTL is reset to default  


# Quick start running the project
## Docker
*	Install and configure Docker for your system - https://docs.docker.com/install/
* Clone the project
```
git clone https://github.com/asif001/REST-key-val-store.git
```
*	Change directory to REST-key-val-store 
* 	Launch CLI
*	Run the docker services 
```
docker-compose up -d
```
*	See the logs 
```
docker logs <container_name> -f
```
*	Service is running at https://127.0.0.1:8000/api/values at host machine
*	Send POST, GET or PATCH request (Instructions below) at https://127.0.0.1:8000/api/values to see the REST API in action

## Linux
*  Install and configure Redis for Linux following - https://redis.io/topics/quickstart
* Clone the project
```
git clone https://github.com/asif001/REST-key-val-store.git
```
*	Change directory to REST-key-val-store
*  Create environment for python-3.7.5
*  Activate the environment
*  Install required packages in the environment  
```               
pip install -r requirements.txt
```
*  Run migration
```
python manage.py makemigrations && python manage.py migrate
```
*   Start the server
```
python manage.py runserver
``` 

#   Instructions
*   POST
```
URL: https://127.0.0.1:8000/api/values
#Format: {key1:val1, key2:val2, key3:val3, ...}
```
*   GET
```
#Fetch all values           
URL: https://127.0.0.1:8000/api/values
#Fetch specific key values
URL: https://127.0.0.1:8000/api/values?keys=key1,key2,key3,..
```

*   PATCH
```
URL: https://127.0.0.1:8000/api/values
#Format: {key1:val1, key2:val2, key3:val3, ...}
```

## Contributing
The main reason to publish something open source, is that anyone can just jump in and start contributing to my project.
So If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.


## Author
Asifur Rahman
asifurarahman@gmail.com
Student at Department of Computer Science and Engineering
Khulna University of Engineering & Technology, Khulna
Bangladesh