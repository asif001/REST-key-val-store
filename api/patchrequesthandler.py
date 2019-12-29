from rest_framework import status
import redis
from django.conf import settings
from . import getkeys

cache_ttl = getattr(settings, "TTL")
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST or 'localhost', port=settings.REDIS_PORT, db=0)


def handle_patch_request(request):
    item, keys = getkeys.get_keys(request)
    items = {}
    response = {}
    status_code = status.HTTP_200_OK

    try:

        for key in keys:
            value = redis_instance.get(key)
            if value is None:
                for dickey in items.keys():
                    redis_instance.set(dickey, items[dickey], ex=-2)
                items.clear()
                raise Exception('KeyNotFound', 0)
            else:
                items[key] = item[key]
                redis_instance.set(key, item[key], ex=cache_ttl)

            response = {
                "success": f"True",
                "code": 204,
                'detail': f"Successfully updated the values."
            }

            status_code = status.HTTP_204_NO_CONTENT

    except Exception as inst:
        exception_name, param = inst.args
        if exception_name == 'KeyNotFound':
            response = {
                "success": f"False",
                "error": f"Bad Request",
                "code": 400,
                "detail": f"Some keys don't exist."
            }
            status_code = status.HTTP_400_BAD_REQUEST

    return response, status_code
