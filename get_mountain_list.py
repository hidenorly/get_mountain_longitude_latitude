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

def ljust_jp(value, length, pad = " "):
  count_length = 0
  for char in value.encode().decode('utf8'):
    if ord(char) <= 255:
      count_length += 1
    else:
      count_length += 2
  return value + pad * (length-count_length)

def printMountainInfo(aMountain, showMountainNameOnly):
  if showMountainNameOnly:
    print( aMountain["name"], end=" ")
  else:
    print( aMountain["name"] + "(" + aMountain["yomi"] + ")" )
    print( ljust_jp( "altitude", 20 ) + " : " + aMountain["altitude"] )
    print( ljust_jp( "location", 20 ) + " : " + aMountain["longitude"] + " " + aMountain["latitude"] )
    print( ljust_jp( "area", 20 ) + " : " + aMountain["area"] )
    print( ljust_jp( "range", 20 ) + " : " + str( int( aMountain["distanceDelta"] ) ) + "km" )
    print( "" )

def dump(aMountain):
  if "distanceDelta" in aMountain:
    print( "  {\"name\":\"" + aMountain["name"] +"\", \"yomi\":\"" + aMountain["yomi"] + "\", \"range\":\"" + str( int( aMountain["distanceDelta"] ) ) + "\", \"area\":\"" + aMountain["area"] +"\", \"longitude\":\"" + aMountain["longitude"] +"\", \"latitude\":\"" + aMountain["latitude"] +"\", \"altitude\":\"" + aMountain["altitude"] +"\"}," )
  else:
    print( "  {\"name\":\"" + aMountain["name"] +"\", \"yomi\":\"" + aMountain["yomi"] +"\", \"area\":\"" + aMountain["area"] +"\", \"longitude\":\"" + aMountain["longitude"] +"\", \"latitude\":\"" + aMountain["latitude"] +"\", \"altitude\":\"" + aMountain["altitude"] +"\"}," )


def getMountainLocationInfoFromMountainName( mountainName ):
  results = []

  for aMountain in mountainLocationDic:
    if aMountain["name"].find( mountainName )!=-1 or aMountain["yomi"].find( mountainName )!=-1 or aMountain["area"].find( mountainName )!=-1:
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
  parser.add_argument('-r', '--rangeMax', action='store', default='0', help='Max distance')
  parser.add_argument('-m', '--rangeMin', action='store', default='0', help='Min distance')
  parser.add_argument('-n', '--mountainNameOnly', action='store_true', default=False, help='List up mountain name only')
  parser.add_argument('-j', '--json', action='store_true', default=False, help='output in json manner')

  args = parser.parse_args()

  if len(args.args) == 0:
    parser.print_help()
    exit(-1)

  locationList = []

  if len(args.args) == 1:
    mountainList = getMountainLocationInfoFromMountainName( args.args[0] )
    for aMountain in mountainList:
      locationList.append( aMountain )
  elif len(args.args) == 2:
    aLocation = {}
    aLocation["longitude"] = args.args[0]
    aLocation["latitude"] = args.args[1]
    locationList.append( aLocation )

  rangeMin = args.rangeMin
  rangeMax = args.rangeMax

  result = []

  for aLocation in locationList:
    aMountainList = getRangedMountains( aLocation["longitude"], aLocation["latitude"], float(rangeMin), float(rangeMax) )
    for aMountain in aMountainList:
      result.append( aMountain )

  result = sorted(result, key=lambda x: x["distanceDelta"], reverse=False)

  for aMountain in result:
    if args.json:
      dump( aMountain )
    else:
      printMountainInfo( aMountain, args.mountainNameOnly )

  if args.mountainNameOnly:
    print( "" )
