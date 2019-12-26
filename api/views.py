import json
from django.conf import settings
import redis
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

cache_ttl = 5*60    # 5 minutes


@api_view(['GET', 'POST', 'PATCH'])
def manage_items(request, *args, **kwargs):
    if request.method == 'GET':
        items = {}

        if request.GET.get('keys'):

            try:

                txt = str(request.GET['keys']).split(",")

                for key in txt:
                    if redis_instance.get(key):
                        items[key] = redis_instance.get(key)
                        redis_instance.setex(key, cache_ttl, items[key])
                    else:
                        raise Exception("KeyNotFound", key)
                response = items

                return Response(response, status=status.HTTP_200_OK)

            except redis.RedisError:
                response = {
                    'msg': f"Could not retrieve the values"
                }

                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as inst:
                x, y = inst.args
                response = {
                    'msg': f"The key {y} does not exist"
                }

                return Response(response, status=status.HTTP_404_NOT_FOUND)

        else:
            try:
                for key in redis_instance.keys("*"):
                    items[key.decode("utf-8")] = redis_instance.get(key)
                    redis_instance.setex(key, cache_ttl, items[key.decode("utf-8")])
                response = items

                return Response(response, status=status.HTTP_200_OK)

            except redis.RedisError:
                response = {
                    'msg': f"Could not retrieve the values"
                }

                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'POST':
        item = json.loads(request.body)
        keys = list(item.keys())
        response = ""
        try:
            for key in keys:
                if not redis_instance.get(key):
                    redis_instance.set(key, item[key], ex=cache_ttl)
                else:
                    raise Exception("DuplicateKey", key)
            response = {
                'msg': f"Successfully set the values"
            }

            return Response(response, status=status.HTTP_201_CREATED)

        except redis.RedisError:
            response = {
                'msg': f"Could not set the values"
            }

            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as inst:
            x, y = inst.args
            response = {
                'msg': f"The key {y} already exists!"
            }
            return Response(response, status=status.HTTP_409_CONFLICT)

    elif request.method == 'PATCH':
        item = json.loads(request.body)
        keys = list(item.keys())
        response = ""
        try:
            for key in keys:
                if redis_instance.get(key):
                    redis_instance.set(key, item[key], ex=cache_ttl)
                else:
                    raise Exception('KeyNotFound', key)
            response = {
                'msg': f"Successfully updated the values"
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        except redis.RedisError:
            response = {
                'msg': f"Could not patch the values"
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as inst:
            x, y = inst.args
            response = {
                'msg': f"The key {y} does not exist"
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
