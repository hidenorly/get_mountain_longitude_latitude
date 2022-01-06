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
from bs4 import BeautifulSoup

def getLongtitudeLatitudeFromUrl( url ):
  result = {}
  result["longitude"] = ""
  result["latitude"] = ""
  pos1 = url.rfind("/")
  pos2 = url.rfind("/", 0, pos1 - 1 )
  if pos1!=-1 and pos2!=-1:
    result["longitude"] = url[pos2+1:pos1]
    result["latitude"] = url[pos1+1:len(url)]
  return result


def getMountainLongitudeLatitude(url):
  result = []
  res = requests.get(url)
  soup = BeautifulSoup(res.content, 'html.parser')
  tables = soup.find_all("table", {})
  if None != tables:
    for aTable in tables:
      rows = aTable.find_all("tr")
      for aRow in rows:
        aResult = {}
        aResult["name"] = None
        aResult["yomi"] = None
        aResult["area"] = None
        aResult["longitude"] = None
        aResult["latitude"] = None
        aResult["altitude"] = None

        links = aRow.findAll("a")
        for aLink in links:
          theUrl = aLink.get("href").strip()
          theText = aLink.get_text().strip()
          aLongLati = getLongtitudeLatitudeFromUrl( theUrl )
          aResult["name"] = theText
          aResult["longitude"] = aLongLati["longitude"]
          aResult["latitude"] = aLongLati["latitude"]
          break

        if aResult["name"]!=None:
          cols = aRow.findAll("td")
          if len(cols)>3:
            aResult["altitude"] = cols[3].text.strip()
            aResult["area"] = cols[1].text.strip()
            aResult["yomi"] = cols[0].text.strip()
            pos = aResult["yomi"].find( aResult["name"] )
            if pos!=-1:
              aResult["yomi"]=aResult["yomi"][0:pos]

        if aResult["name"]!=None:
          result.append( aResult )

  return result

def dump(aMountain):
  print( "  {\"name\":\"" + aMountain["name"] +"\", \"yomi\":\"" + aMountain["yomi"] +"\", \"area\":\"" + aMountain["area"] +"\", \"longitude\":\"" + aMountain["longitude"] +"\", \"latitude\":\"" + aMountain["latitude"] +"\", \"altitude\":\"" + aMountain["altitude"] +"\"}," )


if __name__=="__main__":
  result = getMountainLongitudeLatitude("https://www.gsi.go.jp/kihonjohochousa/kihonjohochousa41140.html")
  print( "mountainLocationDic=[")
  for aMountain in result:
    dump(aMountain)
  print( "]")

  print('''
def getMountainLocationDic():
  return mountainLocationDic
''')