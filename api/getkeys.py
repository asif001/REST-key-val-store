import msgpack
import ast


def get_keys(request):

    item = []
    keys = []

    try:
        item = msgpack.dumps(request.body)  # Load from key:value from json
        for i in range(0, len(item)):
            if item[i] == 123:
                item = item[i:].decode('utf-8')
                break
        item = ast.literal_eval(item)
        keys = list(item.keys())

    except msgpack.FormatError:
        pass

    return item, keys
