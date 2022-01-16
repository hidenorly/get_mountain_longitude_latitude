import mountainLocationDic

mountainLocationDicArray = mountainLocationDic.getMountainLocationDic()
gMountainLocationDic = {}

def getMountainLocationDicArray():
  return mountainLocationDicArray

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
    result.append(name)

  if isFlat:
    flatResult = ""
    for aResult in result:
      flatResult = flatResult + aResult + flatSpacer
    if flatResult.endswith(flatSpacer):
      flatResult = flatResult[0:len(flatResult)]
    result = flatResult

  return result


def getMountainLocationDic():
  if len( gMountainLocationDic ) == 0:
    result = {}

    for aMountain in mountainLocationDicArray:
      names = getMountainNames( aMountain["name"] )
      names.extend( getMountainNames( aMountain["yomi"] ) )
      names.extend( aMountain["area"].split(" ") )
      for aName in names:
        if not aName in result:
          result[ aName ] = []
        result[ aName ].append( aMountain )

    for mountainName,mountainLocationInfo in result.items():
      gMountainLocationDic[mountainName] = mountainLocationInfo

  return gMountainLocationDic


def getMountainLocationInfoFromMountainName( mountainName ):
  results = []

  # ensure
  getMountainLocationDic()

  # check in dic
  mountainNames = getMountainNames( mountainName )
  for aMountainName in mountainNames:
    if aMountainName in gMountainLocationDic:
      results.extend( gMountainLocationDic[ aMountainName ] )

  # fallback
  if len( results ) == 0:
    for name, aMountains in gMountainLocationDic.items():
      for aMountain in aMountains:
        if aMountain["name"].find( mountainName )!=-1 or aMountain["yomi"].find( mountainName )!=-1 or aMountain["area"].find( mountainName )!=-1:
          results.append( aMountain )

  return results
