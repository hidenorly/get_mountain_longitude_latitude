# get_mountain_longitude_latitude

This tool provides the mountain's location information such as longitude and latitude and the altitude, how to read, the area (prefecture name).

And you can search mountains from specified location & range.

Note that the default implementation of mountainLocationDic.py is Japan's mountain provided by ```https://www.gsi.go.jp/kihonjohochousa/kihonjohochousa41140.html```

If you want to get difference mountains, you need to update the above.


# before using this

## create longitude/latitude data

```
$ ./updateDic.sh
```

## setup geopy

```
$ python3 pip install geopy 
```

# how to use?

## dump mountain location, etc. info.

```
$ python3 get_mountain_list.py 男体山
男体山(なんたいさん)
altitude             : 654m
location             : 36.72416666666667 140.41972222222222
area                 : 茨城県
range                : 0km

男体山(なんたいさん)
altitude             : 2486m
location             : 36.765 139.4908333333333
area                 : 栃木県
range                : 0km
```

```
$ python3 get_mountain_list.py 男体山 --json
  {"name":"男体山", "yomi":"なんたいさん", "range":"0", "area":"茨城県", "longitude":"36.72416666666667", "latitude":"140.41972222222222", "altitude":"654m"},
  {"name":"男体山", "yomi":"なんたいさん", "range":"0", "area":"栃木県", "longitude":"36.765", "latitude":"139.4908333333333", "altitude":"2486m"},
```

```
$ python3 get_mountain_list.py なんたいさん
$ python3 get_mountain_list.py 山梨 -n
甲武信ヶ岳 横尾山 瑞牆山 金峰山 朝日岳 国師ヶ岳 北奥千丈岳 乾徳山 小楢山 茅ヶ岳 唐松尾山 大洞山（飛龍山） 鶏冠山（黒川山） 大菩薩嶺 小金沢山 雁ケ腹摺山 権現山 権現山<扇山> 大室山 御正体山 菰釣山 三ッ峠山 黒岳 黒岳<釈迦ヶ岳> 節刀ヶ岳 富士山<剣ヶ峯> 毛無山 赤岳 権現岳 権現岳<三ッ頭> 編笠山 鋸岳 駒ヶ岳 駒津峰 双児山 アサヨ峰 アサヨ峰<栗沢山> 高嶺 地蔵ヶ岳 観音ヶ岳 薬師ヶ岳 辻山 櫛形山 仙丈ヶ岳 伊那荒倉岳 小太郎山 北岳 間ノ岳 農鳥岳<西農鳥岳> 農鳥岳 大唐松山 広河内岳 大籠岳 笹山 笊ヶ岳 布引山 身延山 七面山 山伏 十枚山 篠井山 [高ドッキョウ]
```


## serch mountain with specified location & range

```
$ python3 get_mountain_list.py 36.765 139.4908333333333 --rangeMin=0 --rangeMax=10
男体山(なんたいさん)
altitude             : 2486m
location             : 36.765 139.4908333333333
area                 : 栃木県
range                : 0km

女峰山<大真名子山>(にょほうさん<おおまなごさん>)
altitude             : 2376m
location             : 36.79527777777778 139.50722222222222
area                 : 栃木県
range                : 3km

女峰山<小真名子山>(にょほうさん<こまなごさん>)
altitude             : 2323m
location             : 36.80722222222222 139.51083333333332
area                 : 栃木県
range                : 5km

太郎山(たろうさん)
altitude             : 2368m
location             : 36.81777777777778 139.48277777777778
area                 : 栃木県
range                : 5km

女峰山(にょほうさん)
altitude             : 2483m
location             : 36.811388888888885 139.5363888888889
area                 : 栃木県
range                : 6km
```

```
$ python3 get_mountain_list.py 男体山 --rangeMax=10
```

## Advanced usage

```
$ python3 get_mountain_list.py 男体山 --rangeMax=10 -n | xargs python3 tenkura_get_weather.py -c
```
