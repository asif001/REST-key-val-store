import json
import msgpack
from django.conf import settings
import redis
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST or 'localhost', port=settings.REDIS_PORT, db=0)

cache_ttl = getattr(settings, "TTL")    # TTL 5 minutes

items = {}
response = {}
status_code = status.HTTP_200_OK

# URL format - HOST_NAME/api?keys=key1, key2, ...
# Here key is keys and value is 'key1, key2, ...'


@api_view(['GET', 'POST', 'PATCH'])
def manage_items(request, *args, **kwargs):
    global response, status_code, items
    try:
        # Handling Get Request #

        if request.method == 'GET':

            all_keys = redis_instance.scan_iter()  # Get all keys currently in database
            all_keys = [key.decode("utf-8") for key in all_keys]
            set_of_all_keys = set(all_keys)

            key_list = request.GET.keys()   # Get keys to be queried
            print(key_list)

            if len(key_list) > 1:                    # KeyList contains more than one keys so exception
                raise Exception('KeyExceeded', key_list)

            if len(key_list) == 1:

                if request.GET.get('keys'):          # if the key 'keys' exist then extract the value

                    isvalid = 0

                    # value is separated by comma so get the key list by splitting
                    key_values = str(request.GET['keys']).split(",")
                    set_of_keys = set(key_values)

                    # if key_values is subset of all_keys then a valid GET request
                    if set_of_keys.issubset(all_keys):
                        isvalid = 1

                    if isvalid:
                        items = {}
                        for key in key_values:
                            value = redis_instance.get(key)
                            items[key] = value
                            redis_instance.setex(key, cache_ttl, value)
                        response = items
                        status_code = status.HTTP_200_OK

                    else:
                        error_keys = list(set_of_keys.difference(set_of_keys.intersection(set_of_all_keys)))
                        raise Exception('KeyNotFound', error_keys)

                else:
                    raise Exception('InvalidKey', list(key_list)[0])

            else:
                items = {}
                for key in redis_instance.keys("*"):
                    value = redis_instance.get(key)
                    items[key.decode("utf-8")] = value
                    redis_instance.setex(key, cache_ttl, value)
                response = items
                status_code = status.HTTP_200_OK

        # Handling POST Request #

        elif request.method == 'POST':

            all_keys = redis_instance.scan_iter()  # Get all keys currently in database
            all_keys = [key.decode("utf-8") for key in all_keys]
            set_of_all_keys = set(all_keys)

            item = json.loads(request.body)  # Load from key:value from json
            keys = list(item.keys())
            duplicate_keys = list(set(keys).intersection(set_of_all_keys))

            if len(duplicate_keys) > 0:
                raise Exception("DuplicateKey", duplicate_keys)
            else:
                for key in keys:
                    redis_instance.set(key, item[key], ex=cache_ttl)
                response = {
                    "success": f"True",
                    "code": 201,
                    "detail": f"Successfully set the values."
                }
                status_code = status.HTTP_201_CREATED

        # Handling PATCH Request

        elif request.method == 'PATCH':

            all_keys = redis_instance.scan_iter()  # Get all keys currently in database
            all_keys = [key.decode("utf-8") for key in all_keys]
            set_of_all_keys = set(all_keys)

            item = json.loads(request.body)
            keys = list(item.keys())
            set_of_keys = set(keys)
            error_keys = list(set_of_keys.difference(set_of_keys.intersection(set_of_all_keys)))

            if len(error_keys) > 0:
                raise Exception('KeyNotFound', error_keys)
            else:
                for key in keys:
                    redis_instance.set(key, item[key], ex=cache_ttl)
                response = {
                    "success": f"True",
                    "code": 204,
                    'detail': f"Successfully updated the values."
                }
                status_code = status.HTTP_204_NO_CONTENT

    except TypeError:
        response = {
            "success": f"False",
            "error": f"Not Found",
            "code": 404,
            "detail'": f"Type Error in json.loads(). Must be string"
        }
        status_code = status.HTTP_404_NOT_FOUND

    except json.decoder.JSONDecodeError:
        response = {
            "success": f"False",
            'error': f"Bad Request",
            "code": 400,
            "detail": f"Error in JSON format"
        }

        status_code = status.HTTP_400_BAD_REQUEST

    except redis.RedisError:
        response = {
            "success": f"False",
            "error": f"Not Found",
            "code": 404,
            "detail": f"Error retrieving or saving data"
        }

        status_code = status.HTTP_404_NOT_FOUND

    except Exception as inst:
        exception_name, parameters = inst.args
        if exception_name == 'KeyExceeded':
            response = {
                "success": f"False",
                "error": f"Bad Request",
                "code": 400,
                "detail": f"Too many keys."
            }
            status_code = status.HTTP_400_BAD_REQUEST

        elif exception_name == 'KeyNotFound':
            response = {
                "success": f"False",
                "error": f"Bad Request",
                "code": 400,
                "detail": f"Some keys don't exist."
            }
            status_code = status.HTTP_400_BAD_REQUEST

        elif exception_name == 'InvalidKey':
            response = {
                "success": f"False",
                "error": f"Bad Request",
                "code": 400,
                "detail": f"Invalid key name in url."
            }
            status_code = status.HTTP_400_BAD_REQUEST

        elif exception_name == 'DuplicateKey':
            response = {
                "success": f"False",
                "error": f"Conflict",
                "code": 409,
                "detail": f"Can not create new resource - already exist."
            }
            status_code = status.HTTP_409_CONFLICT

    return Response(response, status=status_code)
