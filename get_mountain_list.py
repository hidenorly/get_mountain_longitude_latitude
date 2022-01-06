#   Copyright 2021 hidenorly
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys
import requests
import argparse
import unicodedata
from geopy.distance import geodesic


import mountainLocationDic
mountainLocationDic = mountainLocationDic.getMountainLocationDic()

def dump(aMountain):
  if "distanceDelta" in aMountain:
    print( "  {\"name\":\"" + aMountain["name"] +"\", \"yomi\":\"" + aMountain["yomi"] + "\", \"range\":\"" + str( int( aMountain["distanceDelta"] ) ) + "\", \"area\":\"" + aMountain["area"] +"\", \"longitude\":\"" + aMountain["longitude"] +"\", \"latitude\":\"" + aMountain["latitude"] +"\", \"altitude\":\"" + aMountain["altitude"] +"\"}," )
  else:
    print( "  {\"name\":\"" + aMountain["name"] +"\", \"yomi\":\"" + aMountain["yomi"] +"\", \"area\":\"" + aMountain["area"] +"\", \"longitude\":\"" + aMountain["longitude"] +"\", \"latitude\":\"" + aMountain["latitude"] +"\", \"altitude\":\"" + aMountain["altitude"] +"\"}," )


def getMountainLocationInfoFromMountainName( mountainName ):
  results = []

  for aMountain in mountainLocationDic:
    if aMountain["name"] == mountainName:
      results.append( aMountain )

  return results


def getDistanceKm(longitude1, latitude1, longitude2, latitude2):
  location1 = (longitude1, latitude1)
  location2 = (longitude2, latitude2)

  dis = geodesic(location1, location2).km

  return dis


def getRangedMountains( longitude, latitude, rangeMinKm, rangeMaxKm ):
  result = []

  for aMountain in mountainLocationDic:
    distanceDelta = getDistanceKm( longitude, latitude, aMountain["longitude"], aMountain["latitude"] )
    if( distanceDelta >= rangeMinKm and distanceDelta <= rangeMaxKm ):
      aMountain["distanceDelta"] = distanceDelta
      result.append( aMountain )

  return result


if __name__=="__main__":
  parser = argparse.ArgumentParser(description='Parse command line options.')
  parser.add_argument('args', nargs='*', help='mountain name such as 富士山 or longitude latitude')
  parser.add_argument('-r', '--rangeMax', action='store', default='100', help='Max distance')
  parser.add_argument('-m', '--rangeMin', action='store', default='0', help='Min distance')

  args = parser.parse_args()

  if len(args.args) == 0:
    parser.print_help()
    exit(-1)

  if len(args.args) == 1:
    mountainList = getMountainLocationInfoFromMountainName( args.args[0] )
    for aMountain in mountainList:
      dump(aMountain)
  elif len(args.args) == 2:
    longitude = args.args[0]
    latitude = args.args[1]
    rangeMin = args.rangeMin
    rangeMax = args.rangeMax
    print( "longitude: " + longitude + " , latitude: " + latitude + " range[km]: >=" + rangeMin + ", <=" + rangeMax )

    result = getRangedMountains( longitude, latitude, float(rangeMin), float(rangeMax) )
    result = sorted(result, key=lambda x: x["distanceDelta"], reverse=False)

    for aMountain in result:
      dump(aMountain)
