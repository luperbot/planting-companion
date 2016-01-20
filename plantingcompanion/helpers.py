import json

PLANT_FILE_JSON = 'plantingcompanion/plants.json'


def get_plant_data():
    """
    Load JSON data from plants.
    Map plant values to each key.
    Friendly plants get +10 points, harmful plants get -10 points,
    and similar plants get -5 points.
    """
    with open(PLANT_FILE_JSON, 'r') as plantfile:
        plants = json.load(plantfile)

    plant_values = {}
    for plant, values in plants.items():
        plant_values[plant] = {plant: -5}
        plant_values[plant].update(
            {friend: 10 for friend in values['friends']}
        )
        plant_values[plant].update(
            {foe: -10 for foe in values['foes']}
        )
    return plant_values


def permutations(iterable, r=None):
    """Modified version of itertools.permutations(iterable, r=None)
    Exactly like itertool's permutations, except it does not yield
    mirrored permutations (ie. will return 'AB' but not 'BA').
    """
    mirrors = {}
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = list(range(n))
    cycles = list(range(n, n-r, -1))
    yield tuple(pool[i] for i in indices[:r])
    mirrors = {tuple(pool[i] for i in indices[:r]): True}
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                res = tuple(pool[i] for i in indices[:r])
                if mirrors.get(res[::-1]) is None:
                    mirrors[res] = True
                    yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return
