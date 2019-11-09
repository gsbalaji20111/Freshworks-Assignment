import json
import itertools
import sys
import functools
import docopt
import os


MISSING = object()


def json_merge_all(json_objects):
    merged = functools.reduce(json_merge, json_objects, MISSING)
    if merged == MISSING:
        raise ValueError("json_objects was empty")
    return merged


def json_merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return dict(
            (k, json_merge(a_val, b_val))
            for k, a_val, b_val in dictzip_longest(a, b, fillvalue=MISSING)
        )
    elif isinstance(a, list) and isinstance(b, list):
        return list(itertools.chain(a, b))

    if b is MISSING:
        assert a is not MISSING
        return a
    return b


def dictzip_longest(*dicts, **kwargs):
    fillvalue = kwargs.get("fillvalue", None)
    keys = functools.reduce(set.union, [set(d.keys()) for d in dicts], set())
    return [tuple([k] + [d.get(k, fillvalue) for d in dicts]) for k in keys]


if __name__ == "__main__":
    json_objects = []
    indent = 4

    for file in os.listdir(sys.argv[1]):
        if file.startswith(sys.argv[2]):
            json_objects.append(
                json.load(open(os.path.join(sys.argv[1], file))))
    if (len(json_objects) == 0):
        print("No file in " + sys.argv[1] + " starts with " + sys.argv[2])
    else:
        merged = json_merge_all(json_objects)

        with open(sys.argv[3] + ".json", "w") as f:
            json.dump(merged, f, indent=4)

        filename = str(sys.argv[1] + "/" + sys.argv[3] + ".json")
        statinfo = os.stat(filename)
        if(statinfo.st_size > int(sys.argv[4])):
            print(
                "Merged file couldn't be saved as the size was greater than the given maximum size.")
            os.remove(os.path.join(sys.argv[1], sys.argv[3] + ".json"))
