#   Copyright 2025 hidenorly
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
import argparse

from geopy.geocoders import Nominatim

def getLatitudeLongitudeFromPlaceName(place_name):
	geolocator = Nominatim(user_agent="my_usera_gent")
	location = geolocator.geocode(place_name)
	if location:
		return location.latitude, location.longitude, location.address
	return None, None, None


if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Location from place_name')
	parser.add_argument('args', nargs='*', help='place names such as 富士山')
	args = parser.parse_args()

	for place_name in args.args:
		latitude, longitude, address = getLatitudeLongitudeFromPlaceName(place_name)
		if latitude and longitude and address:
			print(address)
			print(latitude, longitude)
