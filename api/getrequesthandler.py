from rest_framework import status
import redis
from django.conf import settings

cache_ttl = getattr(settings, "TTL")
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST or 'localhost', port=settings.REDIS_PORT, db=0)


def handle_get_request(request):

    items = {}
    response = {}
    status_code = status.HTTP_200_OK

    try:

        key_list = request.GET.keys()  # Get keys to be queried

        if len(key_list) > 1:  # KeyList contains more than one keys so exception
            raise Exception('KeyExceeded', 0)

        if len(key_list) == 1:

            if request.GET.get('keys'):  # if the key 'keys' exist then extract the value

                # value is separated by comma so get the key list by splitting
                key_values = str(request.GET['keys']).split(",")
                for key in key_values:
                    value = redis_instance.get(key)
                    if value is None:
                        items.clear()
                        raise Exception('KeyNotFound', 0)
                    else:
                        items[key] = value

                for key in key_values:
                    redis_instance.setex(key, cache_ttl, items[key])

                response = items
                status_code = status.HTTP_200_OK

            else:
                raise Exception('InvalidKey', 0)

        else:
            for key in redis_instance.keys("*"):
                value = redis_instance.get(key)
                items[key.decode("utf-8")] = value
                redis_instance.setex(key, cache_ttl, value)
            response = items
            status_code = status.HTTP_200_OK

    except Exception as inst:
        exception_name, param = inst.args
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

    return response, status_code
