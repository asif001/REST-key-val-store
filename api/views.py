import json
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
                    'msg': f"Successfully set the values"
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
                    'msg': f"Successfully updated the values"
                }
                status_code = status.HTTP_204_NO_CONTENT

    except TypeError:
        response = {
            'msg': f"Type Error in json.loads(). Must be string"
        }
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    except json.decoder.JSONDecodeError:
        response = {
            'msg': f"Error in json format"
        }

        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    except redis.RedisError:
        response = {
            'msg': f"Error reading from or writing to the memory"
        }

        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    except Exception as inst:
        exception_name, parameters = inst.args
        if exception_name == 'KeyExceeded':
            response = {
                'msg': f"Too many keys in url - {parameters}"
            }
            status_code = status.HTTP_404_NOT_FOUND

        elif exception_name == 'KeyNotFound':
            response = {
                'msg': f"The keys don't exist - {parameters}"
            }
            status_code = status.HTTP_404_NOT_FOUND

        elif exception_name == 'InvalidKey':
            response = {
                'msg': f"Invalid key in url - {parameters}"
            }
            status_code = status.HTTP_404_NOT_FOUND

        elif exception_name == 'DuplicateKey':
            response = {
                'msg': f"Can not perform post request. Duplicate keys found - {parameters}"
            }
            status_code = status.HTTP_409_CONFLICT

    return Response(response, status=status_code)
