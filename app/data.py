import urlparse
import json
import httplib
import urllib
import numpy as np

from time import time

locations = None

'''Methods for pulling data from Parse'''
def get_LocData(limit_num, skip_num, createdAt):
    connection = httplib.HTTPSConnection('api.parse.com', 443)
    params_to_encode = {#"selectKeys":json.dumps(["latitude","longitude","session","stage"]),
                         #  "includeKeys" :json.dumps(["latitude","longitude","session","stage"]),
                           "limit" : limit_num,
                           "skip" : skip_num,
           }
    if createdAt:
            params_to_encode["where"] = json.dumps({
                "createdAt" : {
                    "$gt" : {
                        "__type": "Date",
                        "iso" : createdAt
                    }
                },
                "latitude" : {
                    "$exists" : True
                },
                "longitude" : {
                    "$exists" : True
                },
                "session" : {
                    "$exists" : True
                },
                "stage" : {
                    "$exists" : True
                }
            })
    else:
            params_to_encode["where"] = json.dumps({
                "latitude" : {
                    "$exists" : True
                },
                "longitude" : {
                    "$exists" : True
                },
                "session" : {
                    "$exists" : True
                },
                "stage" : {
                    "$exists" : True
                }
            })

    params = urllib.urlencode(params_to_encode)
    connection.connect()
    connection.request('GET', '/1/classes/Location?%s' % params, '', {
           "X-Parse-Application-Id": "h3zOjOitCZUZNHAOarr1iTdPd7cuoDg7vKjm2M8D",
           "X-Parse-REST-API-Key": "HKVtKtfBMRJ9VT8zwYqkrVdg980RuSZlf11lswxE"
         })
    result = json.loads(connection.getresponse().read())
    return result

def get_allLocData():
    limit_num = 1000
    skip_num = 0
    all_results = []
    createdAt = None
    results = get_LocData(limit_num, skip_num,createdAt)

    if 'results' in results.keys():
        while True:
            print "%s - %s" % (skip_num, limit_num + skip_num)
            try:
                if len(results['results']) > 0:
                    all_results += results['results']
                    skip_num += limit_num
                    results = get_LocData(limit_num, skip_num, createdAt)
                else:
                    break
            except KeyError as ke:
                if results['code'] == 154:
                    createdAt = all_results[-1]['createdAt']
                    limit_num = 1000
                    skip_num = 0
                    results = get_LocData(limit_num, skip_num, createdAt)
                elif "results" not in results.keys():
                    print results
                    return results
                else:
                    print results
                    return results
    return all_results

def get_sessions():
    global locations
    if locations == None:
        locations = get_allLocData()
    return list(set([x['session'] for x in locations]))

def get_locations(session):
    global locations
    if locations == None:
        locations = get_allLocData()
    locations_for_session = [x for x in locations if x['session'] == session]
    return locations_for_session

def get_centerLatLon():
    global locations
    if locations == None:
        locations = get_allLocData()
    lats = []
    lons = []
    for l in locations:
        lats.append(l['latitude'])
        lons.append(l['longitude'])
    return np.mean(lats), np.mean(lons)

'''Methods for finding interactions'''
def check_for_intersection(cc1, cc2):
    ''' if pair intersects, return intersection coordinates
     else return None

     http://www-cs.engr.ccny.cuny.edu/~wolberg/capstone/intersection/Intersection%20point%20of%20two%20lines.html
     '''

    x1 = float(cc1[0]['longitude'])
    y1 = float(cc1[0]['latitude'])
    x2 = float(cc1[1]['longitude'])
    y2 = float(cc1[1]['latitude'])
    x3 = float(cc2[0]['longitude'])
    y3 = float(cc2[0]['latitude'])
    x4 = float(cc2[1]['longitude'])
    y4 = float(cc2[1]['latitude'])

    denom = (y4 - y3)*(x2-x1) - (x4-x3)*(y2-y1)
    if denom != 0:
        ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
        ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom

        if ((ua>=0) and (ua<=1)) and ((ub>=0) and (ub<=1)):
            x = x1 + ua*(x2-x1)
            y = y1 + ua*(y2-y1)
            return [y,x]
        else:
            return None
    else:
        return None

def checkForLoop(coordinates):
    '''takes a list of coordinates that correspond to a
    chronological series of locations for a user.
    if a loop is in the series of coordinates, return subset that comprises the loop,
    else return None'''
    intersections = []
    #pair adjacent cordinates
    coordinate_pairs = []
    for i in range(1, len(coordinates)):
        coordinate_pairs.append((coordinates[i-1], coordinates[i]))
    #return coordinate_pairs
    #iterate through all pairs
    intersections = []
    for i, cp1 in enumerate(coordinate_pairs):
        for j, cp2 in enumerate(coordinate_pairs):
            intersect = check_for_intersection(cp1,cp2)
            if intersect:
                intersections.append((intersect, [cp1, cp2], [i,j]))

    # if subset looks right, return subset of coordinates making up the loop
    diffs = [np.abs(i[2][0] - i[2][1]) for i in intersections]
    if max(diffs) > 20:
        intersection = intersections[np.argmax(diffs)]
        loop_set_pairs = coordinate_pairs[intersection[2][0]:intersection[2][1]]
        loop_set = [loop_set_pairs[0][0]]
        loop_set += [lsp[0] for lsp in loop_set_pairs[1:]]
        return loop_set
    else:
        return None
