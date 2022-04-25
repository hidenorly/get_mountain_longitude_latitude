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

import mountainLocationDicHelper

import mountainInfoDic
mountainInfoDic = mountainInfoDic.getMountainInfoDic()

def ljust_jp(value, length, pad = " "):
  count_length = 0
  for char in value.encode().decode('utf8'):
    if ord(char) <= 255:
      count_length += 1
    else:
      count_length += 2
  return value + pad * (length-count_length)

def getMountainNames(name, isAll = True, isFlat = False, flatSpacer=" "):
  result = []

  minPos = []
  pos = name.find("<")
  if pos!=-1:
    minPos.append(pos)
    pos2 = name.find(">")
    result.append( name[pos+1:pos2] )
  pos = name.find("(")
  if pos!=-1:
    minPos.append(pos)
    pos2 = name.find(")")
    result.append( name[pos+1:pos2] )
  pos = name.find("（")
  if pos!=-1:
    minPos.append(pos)
    pos2 = name.find("）")
    result.append( name[pos+1:pos2] )

  if len(minPos):
    minPos = min(minPos)
    result.insert(0, name[0:minPos] )

  if isAll or len( result ) == 0:
    result.insert(0, name)

  if isFlat:
    flatResult = ""
    for aResult in result:
      flatResult = flatResult + aResult + flatSpacer
    if flatResult.endswith(flatSpacer):
      flatResult = flatResult[0:len(flatResult)]
    result = flatResult

  return result

def printMountainInfo(aMountain):
  yomi = ""
  if "yomi" in aMountain:
    yomi = "(" + aMountain["yomi"] + ")"
  print( aMountain["name"] + yomi )
  print( ljust_jp( "altitude", 20 ) + " : " + aMountain["altitude"] )
  if "longitude" in aMountain and "latitude" in aMountain:
    print( ljust_jp( "location", 20 ) + " : " + aMountain["longitude"] + " " + aMountain["latitude"] )
  print( ljust_jp( "area", 20 ) + " : " + aMountain["area"] )
  if "distanceDelta" in aMountain and aMountain["distanceDelta"]:
    print( ljust_jp( "range", 20 ) + " : " + str( int( aMountain["distanceDelta"] ) ) + "km" )
  if "difficulty" in aMountain and aMountain["difficulty"]:
    print( ljust_jp( "difficulty", 20 ) + " : " + aMountain["difficulty"] )
  if "fitnessLevel" in aMountain and aMountain["fitnessLevel"]:
    print( ljust_jp( "fitnessLevel", 20 ) + " : " + aMountain["fitnessLevel"] )
  if "famous" in aMountain and aMountain["famous"]:
    print( ljust_jp( "famous", 20 ) + " : " + aMountain["famous"] )
  print( "" )

def dump(aMountain):
  if "distanceDelta" in aMountain:
    print( "  {\"name\":\"" + aMountain["name"] +"\", \"yomi\":\"" + aMountain["yomi"] + "\", \"range\":\"" + str( int( aMountain["distanceDelta"] ) ) + "\", \"area\":\"" + aMountain["area"] +"\", \"longitude\":\"" + aMountain["longitude"] +"\", \"latitude\":\"" + aMountain["latitude"] +"\", \"altitude\":\"" + aMountain["altitude"] +"\"}," )
  else:
    print( "  {\"name\":\"" + aMountain["name"] +"\", \"yomi\":\"" + aMountain["yomi"] +"\", \"area\":\"" + aMountain["area"] +"\", \"longitude\":\"" + aMountain["longitude"] +"\", \"latitude\":\"" + aMountain["latitude"] +"\", \"altitude\":\"" + aMountain["altitude"] +"\"}," )


def getDistanceKm(longitude1, latitude1, longitude2, latitude2):
  location1 = (longitude1, latitude1)
  location2 = (longitude2, latitude2)

  dis = geodesic(location1, location2).km

  return dis


def getStarRank(starLevel):
  result = 0

  nLen = len(starLevel)
  i = 0

  while i < nLen:
    if starLevel[i:i+1]=="★":
      result = result + 1
    i = i + 1

  return result

def getCandidateMountainInfo( name ):
  # 1st phase name match
  theMountain = {}
  if name in mountainInfoDic:
    theMountain = mountainInfoDic[name]
  else:
    pos = name.find("<")
    if pos!=-1:
      name = name[0:pos]
    pos = name.find("(")
    if pos!=-1:
      name = name[0:pos]
    pos = name.find("（")
    if pos!=-1:
      name = name[0:pos]
    for nameOfInfo, theInfo in mountainInfoDic.items():
      if nameOfInfo.find( name )!=-1:
        theMountain = theInfo
        break

  return theMountain

def isFamousMountainInfo( theMountain ):
  result = False

  if ( "type" in theMountain and theMountain["type"]!="") or ("famous" in theMountain and theMountain["famous"]!=""):
    result = True

  return result

def isDifficultyAcceptableMountainInfo( theMountain, difficultMin, difficultMax ):
  result = True

  if theMountain!=None:
    if "difficulty" in theMountain and theMountain["difficulty"]:
      difficulty = getStarRank( theMountain["difficulty"] )
      if difficulty<difficultMin or difficulty>difficultMax:
        result = False

  return result

def isFitnessAcceptableMountainInfo( theMountain, fitnessMin, fitnessMax ):
  result = True

  if theMountain!=None:
    if "fitnessLevel" in theMountain and theMountain["fitnessLevel"]:
      fitnessLevel = getStarRank( theMountain["fitnessLevel"] )
      if fitnessLevel<fitnessMin or fitnessLevel>fitnessMax:
        result = False

  return result

def isAltitudeAcceptableMountainInfo(aMountain, altitudeMin, altitudeMax):
  isAltitudeOk = True

  if "altitude" in aMountain:
    theAltitude = aMountain["altitude"]
    pos = theAltitude.find("m")
    if pos!=-1:
      theAltitude = theAltitude[0:pos]
    theAltitude = int( theAltitude )
    if theAltitude<altitudeMin or theAltitude>altitudeMax:
      isAltitudeOk = False

  return isAltitudeOk


def filterOutMountains(mountains, onlyFamousMountain, area, altitudeMin, altitudeMax, difficultMin, difficultMax, fitnessMin, fitnessMax):
  result = []

  for aMountain in mountains:
    if ( ( area=="" or aMountain["area"].find(area)!=-1 ) and isAltitudeAcceptableMountainInfo( aMountain, altitudeMin, altitudeMax ) and ( onlyFamousMountain and isFamousMountainInfo( aMountain ) or (not onlyFamousMountain) ) and isFitnessAcceptableMountainInfo( aMountain, fitnessMin, fitnessMax ) and isDifficultyAcceptableMountainInfo( aMountain, difficultMin, difficultMax ) ):
      result.append( aMountain )

  return result


def getRangedMountains( longitude, latitude, rangeMinKm, rangeMaxKm ):
  result = []

  for aMountain in mountainLocationDicHelper.getMountainLocationDicArray():
    distanceDelta = getDistanceKm( longitude, latitude, aMountain["longitude"], aMountain["latitude"] )
    if( distanceDelta >= rangeMinKm and distanceDelta <= rangeMaxKm ):
      aMountain["distanceDelta"] = distanceDelta

      theMountainInfo = getCandidateMountainInfo( aMountain["name"] )
      if "altitude" in theMountainInfo and aMountain["altitude"].find("(")==-1:
        aMountain["altitude"] = aMountain["altitude"] + " (" + theMountainInfo["altitude"] + ")"
      if "difficulty" in theMountainInfo:
        aMountain["difficulty"] = theMountainInfo["difficulty"]
      if "fitnessLevel" in theMountainInfo:
        aMountain["fitnessLevel"] = theMountainInfo["fitnessLevel"]
      if "type" in theMountainInfo:
        aMountain["famous"] = theMountainInfo["type"]

      result.append( aMountain )

  return result

def getLocationMountainByName(name, nameOfInfo):
  aLocationMountain = None

  results = mountainLocationDicHelper.getMountainLocationInfoFromMountainName(name)
  if len(results) == 0:
    results = mountainLocationDicHelper.getMountainLocationInfoFromMountainName(nameOfInfo)

  if len(results):
    aLocationMountain = results[0]

  return aLocationMountain


def fallbackSearch(name):
  result = []

  theMountain = {}
  if name in mountainInfoDic:
    result.append( mountainInfoDic[name] )
  else:
    pos = name.find("<")
    if pos!=-1:
      name = name[0:pos]
    pos = name.find("(")
    if pos!=-1:
      name = name[0:pos]
    for nameOfInfo, theInfo in mountainInfoDic.items():
      if nameOfInfo.find( name )!=-1 or theInfo["area"].find( name )!=-1:
        theMountain = {}
        theMountain["name"] = nameOfInfo

        aLocationMountain = getLocationMountainByName( name, nameOfInfo )
        if aLocationMountain:
          theMountain["yomi"] = aLocationMountain["yomi"]
          theMountain["longitude"] = aLocationMountain["longitude"]
          theMountain["latitude"] = aLocationMountain["latitude"]
          theMountain["area"] = theInfo["area"] + " (" + aLocationMountain["area"] +")"
        else:
          theMountain["yomi"] = ""
          theMountain["longitude"] = ""
          theMountain["latitude"] = ""
          theMountain["area"] = theInfo["area"]

        theMountain["altitude"] = theInfo["altitude"]
        theMountain["range"] = 0
        theMountain["difficulty"] = theInfo["difficulty"]
        theMountain["fitnessLevel"] = theInfo["fitnessLevel"]
        theMountain["famous"] = theInfo["type"]

        result.append( theMountain )

  return result


if __name__=="__main__":
  parser = argparse.ArgumentParser(description='Parse command line options.')
  parser.add_argument('args', nargs='*', help='mountain name such as 富士山 or longitude latitude')
  parser.add_argument('-r', '--rangeMax', action='store', default='0', help='Max distance')
  parser.add_argument('-m', '--rangeMin', action='store', default='0', help='Min distance')
  parser.add_argument('-n', '--mountainNameOnly', action='store_true', default=False, help='List up mountain name only')
  parser.add_argument('-nn', '--mountainNameOnlyFlat', action='store_true', default=False, help='List up mountain name only (list up alternative name too)')
  parser.add_argument('-j', '--json', action='store_true', default=False, help='output in json manner')
  parser.add_argument('-f', '--famous', action='store_true', default=False, help='Only famous mountains such as 100th, 200th and 300th mountains')
  parser.add_argument('-a', '--area', action='store', default='', help='Area')
  parser.add_argument('-i', '--altitudeMin', action='store', default='0', help='Min altitude')
  parser.add_argument('-t', '--altitudeMax', action='store', default='9000', help='Max altitude')
  parser.add_argument('-e', '--difficultMin', action='store', default='', help='Min difficulty')
  parser.add_argument('-d', '--difficultMax', action='store', default='★★★★★', help='Max difficulty')
  parser.add_argument('-k', '--fitnessMin', action='store', default='', help='Min fitnessLevel')
  parser.add_argument('-g', '--fitnessMax', action='store', default='★★★★★', help='Max fitnessLevel')

  args = parser.parse_args()

  rangeMin = float(args.rangeMin)
  rangeMax = float(args.rangeMax)
  altitudeMin = int(args.altitudeMin)
  altitudeMax = int(args.altitudeMax)
  difficultMin = getStarRank(args.difficultMin)
  difficultMax = getStarRank(args.difficultMax)
  fitnessMin = getStarRank(args.fitnessMin)
  fitnessMax = getStarRank(args.fitnessMax)

  if len(args.args) == 0:
    parser.print_help()
    exit(-1)

  locationList = []

  # search by longitude/latitude or name in mountainLocationDicHelper.getMountainLocationDicArray()
  if len(args.args) == 1:
    mountainList = mountainLocationDicHelper.getMountainLocationInfoFromMountainName( args.args[0] )
    for aMountain in mountainList:
      locationList.append( aMountain )
  elif len(args.args) == 2:
    aLocation = {}
    aLocation["longitude"] = args.args[0]
    aLocation["latitude"] = args.args[1]
    locationList.append( aLocation )

  result = []

  # search by location
  for aLocation in locationList:
    aMountainList = getRangedMountains( aLocation["longitude"], aLocation["latitude"], rangeMin, rangeMax )
    for aMountain in aMountainList:
      result.append( aMountain )

  # make it unique
  mountainLists = {}
  for aMountain in result:
    mountainLists[ aMountain["name"]+aMountain["longitude"]+aMountain["latitude"] ] = aMountain
  if len( mountainLists ) != len( result ):
    result = []
    for id, aMountain in mountainLists.items():
      result.append( aMountain )

  # sort
  result = sorted(result, key=lambda x: x["distanceDelta"], reverse=False)

  # fallback search by name in the mountainInfoDic
  if len( result ) == 0:
    result = fallbackSearch( args.args[0] )

  # filter out
  result = filterOutMountains(result, args.famous, args.area, altitudeMin, altitudeMax, difficultMin, difficultMax, fitnessMin, fitnessMax )

  # dump
  mountainOnlyNames = {}
  for aMountain in result:
    if args.json:
      dump( aMountain )
    else:
      if args.mountainNameOnly or args.mountainNameOnlyFlat:
        mountains = getMountainNames( aMountain["name"], not args.mountainNameOnlyFlat)
        if args.mountainNameOnlyFlat:
          for aName in mountains:
            mountainOnlyNames[aName] = aName
        else:
          if len(mountains):
            mountainOnlyNames[mountains[0]] = mountains[0]
      else:
        printMountainInfo( aMountain )

  if args.mountainNameOnly or args.mountainNameOnlyFlat:
    for aName, aName in mountainOnlyNames.items():
      print( aName, end = " ")
    print( "" )
