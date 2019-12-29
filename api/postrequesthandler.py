from rest_framework import status
import redis
from django.conf import settings
from . import getkeys

cache_ttl = getattr(settings, "TTL")
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST or 'localhost', port=settings.REDIS_PORT, db=0)


def handle_post_request(request):
    item, keys = getkeys.get_keys(request)
    items = {}
    response = {}
    status_code = status.HTTP_200_OK

    try:

        for key in keys:
            value = redis_instance.get(key)
            if value is None:
                items[key] = item[key]
                redis_instance.set(key, item[key], ex=cache_ttl)
            else:
                for dickey in items.keys():
                    redis_instance.set(dickey, items[dickey], ex=-2)
                items.clear()
                raise Exception('DuplicateKey', 0)

        response = {
            "success": f"True",
            "code": 201,
            "detail": f"Successfully set the values."
        }

        status_code = status.HTTP_201_CREATED

    except Exception as inst:
        exception_name, param = inst.args
        if exception_name == 'DuplicateKey':
            response = {
                "success": f"False",
                "error": f"Conflict",
                "code": 409,
                "detail": f"Can not create new resource - already exist.",
                "path": "/api/values"
            }
            status_code = status.HTTP_409_CONFLICT

    return response, status_code
