#   Copyright 2021, 2023, 2024, 2025 hidenorly
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

import os
import sys
import re
import csv
import itertools
import requests
import argparse
import unicodedata
from geopy.distance import geodesic
import json
from get_latitude_longitude_from_name import getLatitudeLongitudeFromPlaceName

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


class MountainReportUtil:
  @staticmethod
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

  @staticmethod
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


class MountainInfoUtil:
  @staticmethod
  def getEnsuredMountainInfo(aMountain):
    result = aMountain
    if "name" in aMountain and aMountain["name"] in mountainInfoDic:
      theMountainInfo = mountainInfoDic[aMountain["name"]]
      if "type" in theMountainInfo:
        result["famous"] = theMountainInfo["type"]
      if "difficulty" in theMountainInfo:
        result["difficulty"] = theMountainInfo["difficulty"]
      if "fitnessLevel" in theMountainInfo:
        result["fitnessLevel"] = theMountainInfo["fitnessLevel"]

    return result


class MountainCache:
  @staticmethod
  def getCacheFilename(locationList, rangeMin, rangeMax):
    cacheDir = os.path.expanduser("~/.mountainlistcache/")
    if not os.path.exists(cacheDir):
        os.makedirs(cacheDir)

    names = set()
    for aLocation in locationList:
      #if "name" in aLocation:
      #  names.add(aLocation["name"])
      #else:
      #  if "longitude" in aLocation and "latitude" in aLocation:
      #    names.add(aLocation["longitude"]+"_"+aLocation["latitude"])
      names.add(aLocation)

    names = sorted(names)
    names = "_".join(list(names))
    names = cacheDir+str(rangeMin)+"_"+str(rangeMax)+"_"+names.replace("<", "").replace(">", "").replace("（", "").replace("）", "").replace("[", "").replace("]", "")+".json"
    return names

  @staticmethod
  def getCachedResult(cacheFilename):
    result = []
    if os.path.exists(cacheFilename):
      if os.path.getsize(cacheFilename)>0:
        with open(cacheFilename, "r", encoding="utf-8") as f:
          result = json.load(f)
    return result

  @staticmethod
  def storeCachedData(cacheFilename,result):
    if len(result)>0:
      if len(cacheFilename)<255:
        if not os.path.exists(cacheFilename):
          with open(cacheFilename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False)


class MountainFilterUtil:
  @staticmethod
  def openCsv( fileName, delimiter="," ):
    result = []
    if os.path.exists( fileName ):
      file = open( fileName )
      if file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL, delimiter=delimiter)
        for aRow in reader:
          data = []
          for aCol in aRow:
            aCol = aCol.strip()
            if aCol.startswith("\""):
              aCol = aCol[1:len(aCol)]
            if aCol.endswith("\""):
              aCol = aCol[0:len(aCol)-1]
            data.append( aCol )
          result.append( data )
    return result

  @staticmethod
  def isMatchedMountainRobust(arrayData, search):
    result = not arrayData
    for aData in arrayData:
      if aData.startswith(search) or search.startswith(aData):
        result = True
        break
    return result

  @staticmethod
  def getSetOfCsvs( csvFiles ):
    result = set()
    csvFiles = str(csvFiles).split(",")
    for aCsvFile in csvFiles:
      aCsvFile = os.path.expanduser( aCsvFile )
      theSet = set( itertools.chain.from_iterable( MountainFilterUtil.openCsv( aCsvFile ) ) )
      result = result.union( theSet )
    return result

  @staticmethod
  def getMountainNameList( mountainCsvFiles ):
    result = set()

    for aCsvFile in mountainCsvFiles:
      if os.path.exists(aCsvFile):
        result =  result | MountainFilterUtil.getSetOfCsvs( aCsvFile )

    return list(result)

  @staticmethod
  def getDistanceKm(longitude1, latitude1, longitude2, latitude2):
    location1 = (longitude1, latitude1)
    location2 = (longitude2, latitude2)

    dis = geodesic(location1, location2).km

    return dis

  @staticmethod
  def getStarRank(starLevel):
    result = 0

    nLen = len(starLevel)
    i = 0

    while i < nLen:
      if starLevel[i:i+1]=="★":
        result = result + 1
      i = i + 1

    return result

  @staticmethod
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

  @staticmethod
  def isFamousMountainInfo( theMountain ):
    result = False

    if ( "type" in theMountain and theMountain["type"]!="") or ("famous" in theMountain and theMountain["famous"]!=""):
      result = True

    return result

  @staticmethod
  def isDifficultyAcceptableMountainInfo( theMountain, difficultMin, difficultMax ):
    result = True

    if theMountain!=None:
      if "difficulty" in theMountain and theMountain["difficulty"]:
        difficulty = MountainFilterUtil.getStarRank( theMountain["difficulty"] )
        if difficulty<difficultMin or difficulty>difficultMax:
          result = False

    return result

  @staticmethod
  def isFitnessAcceptableMountainInfo( theMountain, fitnessMin, fitnessMax ):
    result = True

    if theMountain!=None:
      if "fitnessLevel" in theMountain and theMountain["fitnessLevel"]:
        fitnessLevel = MountainFilterUtil.getStarRank( theMountain["fitnessLevel"] )
        if fitnessLevel<fitnessMin or fitnessLevel>fitnessMax:
          result = False

    return result

  @staticmethod
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

  @staticmethod
  def filterOutMountains(mountains, onlyFamousMountain, onlyNoFamous, area, altitudeMin, altitudeMax, difficultMin, difficultMax, fitnessMin, fitnessMax, excludesList):
    result = []

    for aMountain in mountains:
      isFamousMountain = MountainFilterUtil.isFamousMountainInfo( aMountain )
      if ( ( area=="" or aMountain["area"].find(area)!=-1 ) and MountainFilterUtil.isAltitudeAcceptableMountainInfo( aMountain, altitudeMin, altitudeMax ) and ( ( onlyFamousMountain and isFamousMountain ) or ( onlyNoFamous and not isFamousMountain )  or ( not onlyFamousMountain and not onlyNoFamous ) ) and MountainFilterUtil.isFitnessAcceptableMountainInfo( aMountain, fitnessMin, fitnessMax ) and MountainFilterUtil.isDifficultyAcceptableMountainInfo( aMountain, difficultMin, difficultMax ) ):
        if not excludesList or not MountainFilterUtil.isMatchedMountainRobust( excludesList, aMountain["name"] ):
          result.append( aMountain )

    return result

  @staticmethod
  def getRangedMountains( longitude, latitude, rangeMinKm, rangeMaxKm ):
    result = []

    for aMountain in mountainLocationDicHelper.getMountainLocationDicArray():
      distanceDelta = MountainFilterUtil.getDistanceKm( longitude, latitude, aMountain["longitude"], aMountain["latitude"] )
      if( distanceDelta >= rangeMinKm and distanceDelta <= rangeMaxKm ):
        aMountain["distanceDelta"] = distanceDelta

        theMountainInfo = MountainFilterUtil.getCandidateMountainInfo( aMountain["name"] )
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

  @staticmethod
  def getLocationMountainByName(name, nameOfInfo):
    aLocationMountain = None

    results = mountainLocationDicHelper.getMountainLocationInfoFromMountainName(name)
    if len(results) == 0:
      results = mountainLocationDicHelper.getMountainLocationInfoFromMountainName(nameOfInfo)

    if len(results):
      aLocationMountain = results[0]

    return aLocationMountain

  @staticmethod
  def fallbackSearch(name, isMountainNameOnly=False):
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
        if nameOfInfo.find( name )!=-1 or (not isMountainNameOnly and theInfo["area"].find( name )!=-1):
          theMountain = {}
          theMountain["name"] = nameOfInfo

          aLocationMountain = MountainFilterUtil.getLocationMountainByName( name, nameOfInfo )
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

  @staticmethod
  def isValidLongitudeLatitude(val):
    patterns = [
      r"[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)",
      r"[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)"
    ]
    result = False
    for aPattern in patterns:
      result = bool(re.match(aPattern, val))
      if result:
        return result
    return result


class MountainList:
  def get_cached_filtered_mountain_list(argsList, mountainSearchOnly=False, famous=False, nofamous=False, area="", altitudeMin=0, altitudeMax=9000, difficultMin=0, difficultMax=5, fitnessMin=0, fitnessMax=5, excludeMountainList=[], rangeMin=0, rangeMax=0):
    result = []

    locationList = {}

    # argument check. longitude or mountainname or area name
    argsLen = len(argsList)
    isLongitudeLatitudeIncluded = False
    for i in range(0, argsLen):
      theArg = argsList[i]
      if MountainFilterUtil.isValidLongitudeLatitude(theArg):
        if i<(argsLen-1):
          if MountainFilterUtil.isValidLongitudeLatitude(argsList[i+1]):
            aLocation = {}
            aLocation["longitude"] = argsList[i]
            aLocation["latitude"] = argsList[i+1]
            locationList[aLocation["longitude"]+"_"+aLocation["latitude"]] = aLocation
            i = i + 1
            isLongitudeLatitudeIncluded = True
      else:
        mountainList = mountainLocationDicHelper.getMountainLocationInfoFromMountainName( theArg )
        if mountainList:
          for aMountain in mountainList:
            locationList[aMountain["name"]] = MountainInfoUtil.getEnsuredMountainInfo(aMountain)
        else:
          # fallback from place name
          longitude, latitude, _ = getLatitudeLongitudeFromPlaceName(theArg)
          if latitude and longitude:
            aLocation = {}
            aLocation["longitude"] = str(longitude)
            aLocation["latitude"] = str(latitude)
            locationList[aLocation["longitude"]+"_"+aLocation["latitude"]] = aLocation

    #locationList = locationList.values()
    _tmp = []
    for aLocation in locationList.values():
      _tmp.append(MountainInfoUtil.getEnsuredMountainInfo(aLocation))
    locationList = _tmp

    # result cache
    cacheFilename = MountainCache.getCacheFilename(argsList, rangeMin, rangeMax) #locationList, rangeMin, rangeMax)
    result = MountainCache.getCachedResult(cacheFilename)
    isSearchByLocation = False
    if not result:
      # cache not found
      # search by location
      if isLongitudeLatitudeIncluded or rangeMin!=0 or rangeMax!=0:
        isSearchByLocation = True
        for aLocation in locationList:
          aMountainList = MountainFilterUtil.getRangedMountains( aLocation["longitude"], aLocation["latitude"], rangeMin, rangeMax )
          for aMountain in aMountainList:
            result.append( aMountain )
      else:
        result = locationList

    if not result:
      MountainCache.storeCachedData(cacheFilename, result)

    for aMountain in list(result):
      if "distanceDelta" in aMountain:
        isSearchByLocation = True
        break

    # make it unique
    mountainLists = {}
    for aMountain in list(result):
      if "name" in aMountain:
        if not "longitude" in aMountain:
          aMountain["longitude"] = ""
        if not "latitude" in aMountain:
          aMountain["latitude"] = ""
        mountainLists[ aMountain["name"]+aMountain["longitude"]+aMountain["latitude"] ] = aMountain
    if len( mountainLists ) != len( result ):
      result = []
      for id, aMountain in mountainLists.items():
        result.append( MountainInfoUtil.getEnsuredMountainInfo(aMountain) )

    # sort
    if isSearchByLocation:
      result = sorted(result, key=lambda x: x["distanceDelta"], reverse=False)

    # fallback search by name in the mountainInfoDic
    if not result and argsList:
      result = MountainFilterUtil.fallbackSearch( argsList[0], mountainSearchOnly )

    # filter out
    result = MountainFilterUtil.filterOutMountains(result, famous, nofamous, area, altitudeMin, altitudeMax, difficultMin, difficultMax, fitnessMin, fitnessMax, excludeMountainList )

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
  parser.add_argument('-nf', '--nofamous', action='store_true', default=False, help='Only NOT famous mountains')
  parser.add_argument('-a', '--area', action='store', default='', help='Area')
  parser.add_argument('-i', '--altitudeMin', action='store', default='0', help='Min altitude')
  parser.add_argument('-t', '--altitudeMax', action='store', default='9000', help='Max altitude')
  parser.add_argument('-e', '--difficultMin', action='store', default='', help='Min difficulty')
  parser.add_argument('-d', '--difficultMax', action='store', default='★★★★★', help='Max difficulty')
  parser.add_argument('-k', '--fitnessMin', action='store', default='', help='Min fitnessLevel')
  parser.add_argument('-g', '--fitnessMax', action='store', default='★★★★★', help='Max fitnessLevel')
  parser.add_argument('-x', '--exclude', action='append', default=[], help='Exclude mountains (.csv)')
  parser.add_argument('-l', '--include', action='append', default=[], help='Include mountains (.csv)')

  args = parser.parse_args()

  rangeMin = float(args.rangeMin)
  rangeMax = float(args.rangeMax)
  altitudeMin = int(args.altitudeMin)
  altitudeMax = int(args.altitudeMax)
  difficultMin = MountainFilterUtil.getStarRank(args.difficultMin)
  difficultMax = MountainFilterUtil.getStarRank(args.difficultMax)
  fitnessMin = MountainFilterUtil.getStarRank(args.fitnessMin)
  fitnessMax = MountainFilterUtil.getStarRank(args.fitnessMax)
  includeMountainList = MountainFilterUtil.getMountainNameList(args.include)
  excludeMountainList = MountainFilterUtil.getMountainNameList(args.exclude)

  argsList = args.args
  argsList.extend(includeMountainList)

  if len(argsList) == 0:
    parser.print_help()
    exit(-1)

  # get cached filtered mountain list
  result = MountainList.get_cached_filtered_mountain_list(argsList, False, args.famous, args.nofamous, args.area, altitudeMin, altitudeMax, difficultMin, difficultMax, fitnessMin, fitnessMax, excludeMountainList, rangeMin, rangeMax)

  # dump
  mountainOnlyNames = {}
  for aMountain in result:
    if args.json:
      dump( aMountain )
    else:
      if args.mountainNameOnly or args.mountainNameOnlyFlat:
        mountains = MountainReportUtil.getMountainNames( aMountain["name"], not args.mountainNameOnlyFlat)
        if args.mountainNameOnlyFlat:
          for aName in mountains:
            mountainOnlyNames[aName] = aName
        else:
          if len(mountains):
            mountainOnlyNames[mountains[0]] = mountains[0]
      else:
        MountainReportUtil.printMountainInfo( aMountain )

  if args.mountainNameOnly or args.mountainNameOnlyFlat:
    for aName, aName in mountainOnlyNames.items():
      print( aName, end = " ")
    print( "" )

