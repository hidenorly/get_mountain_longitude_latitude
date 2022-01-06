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
  {"name":"男体山", "yomi":"なんたいさん", "area":"茨城県", "longitude":"36.72416666666667", "latitude":"140.41972222222222", "altitude":"654m"},
  {"name":"男体山", "yomi":"なんたいさん", "area":"栃木県", "longitude":"36.765", "latitude":"139.4908333333333", "altitude":"2486m"},
```

## serch mountain with specified location & range

```
$ python3 get_mountain_list.py 36.765 139.4908333333333 --rangeMin=0 --rangeMax=10
longitude: 36.765 , latitude: 139.4908333333333 range[km]: >=0, <=10
  {"name":"男体山", "yomi":"なんたいさん", "range":"0", "area":"栃木県", "longitude":"36.765", "latitude":"139.4908333333333", "altitude":"2486m"},
  {"name":"女峰山<大真名子山>", "yomi":"にょほうさん<おおまなごさん>", "range":"3", "area":"栃木県", "longitude":"36.79527777777778", "latitude":"139.50722222222222", "altitude":"2376m"},
  {"name":"女峰山<小真名子山>", "yomi":"にょほうさん<こまなごさん>", "range":"5", "area":"栃木県", "longitude":"36.80722222222222", "latitude":"139.51083333333332", "altitude":"2323m"},
  {"name":"太郎山", "yomi":"たろうさん", "range":"5", "area":"栃木県", "longitude":"36.81777777777778", "latitude":"139.48277777777778", "altitude":"2368m"},
  {"name":"女峰山", "yomi":"にょほうさん", "range":"6", "area":"栃木県", "longitude":"36.811388888888885", "latitude":"139.5363888888889", "altitude":"2483m"},
```
