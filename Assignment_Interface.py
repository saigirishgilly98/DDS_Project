#
# Assignment Interface
#

from pymongo import MongoClient
import os
import sys
import json
import math
import re
from pymemcache.client import base


def get_distance_between_points(point2_lat, point2_long, point1_lat, point1_long):
    r = 3959
    phi1 = math.radians(point1_lat)
    phi2 = math.radians(point2_lat)
    delta_phi = math.radians(point2_lat - point1_lat)
    delta_lambda = math.radians(point2_long - point1_long)
    a = math.sin(delta_phi / 2) * math.sin(delta_phi / 2) + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) * math.sin(delta_lambda / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = r * c

    return distance


def FindBusinessBasedOnCity(cityToSearch, saveLocation1, collection):
    result = collection.find({"city": re.compile(cityToSearch, re.IGNORECASE)})
    data = []
    for rec in result:
        data.append(rec["name"] + "$" + rec["full_address"] + "$" + rec["city"] + "$" + rec["state"])

    fh = open(saveLocation1, "w")
    fh.write("\n".join(data).upper())
    fh.close()


def FindBusinessBasedOnLocation(categoriesToSearch, myLocation, maxDistance, saveLocation2, collection):

    key = categoriesToSearch[0].replace(' ', '')
    # for categories in categoriesToSearch:
    #     key += categories.replace(' ', '')
    # key += myLocation[0]
    # key += myLocation[1]
    # key.replace(' ', '')

    # Don't forget to run `memcached' before running this code
    client = base.Client(('localhost', 11211))
    # client.delete(key)
    result = client.get(key)

    # client.set('some_key', 'some_value')
    # print(client.get('some_key').decode('utf-8'))

    if result is None:
        print('Without Cache')
        result = collection.find({"categories": {"$all": categoriesToSearch}})
        value = ''
        for rec in result:
            value += str(rec['latitude']) + '^' + str(rec['longitude']) + '^' + rec['name'] + '*'
        client.set(key, value)
        final_result = result
    else:
        print('With Cache')
        result = result.decode('utf-8')
        result = result[:-1]
        final_result = []
        for rec in result.split('*'):
            rec_ = rec.split('^')
            final_result.append({'latitude': rec_[0], 'longitude': rec_[1], 'name': rec_[2]})
        # print(final_result)

    data = []
    for rec in final_result:
        dist = get_distance_between_points(float(myLocation[0]), float(myLocation[1]), float(rec["latitude"]), float(rec["longitude"]))
        if dist <= maxDistance:
            data.append(rec["name"])

    fh = open(saveLocation2, "w")
    fh.write("\n".join(data).upper())
    fh.close()