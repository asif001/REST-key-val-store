FROM python:3.7.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY waitForRedis.sh /usr/local/bin/

RUN apt-get update && \
	curl http://download.redis.io/redis-stable.tar.gz | tar xz &&\
    make -C redis-stable &&\
    cp redis-stable/src/redis-cli /usr/local/bin &&\
    rm -rf redis-stable && \
    apt-get install dos2unix && \
	apt-get -y install default-mysql-client && \
    apt-get clean && \
	dos2unix /usr/local/bin/waitForRedis.sh && \
	chmod +x /usr/local/bin/waitForRedis.sh && \
	ln -s /usr/local/bin/waitForRedis.sh
	
RUN pip install -r requirements.txt
COPY . /code/
ENTRYPOINT ["waitForRedis.sh"]