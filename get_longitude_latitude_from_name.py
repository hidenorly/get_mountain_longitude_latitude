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

if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Location from place_name')
	parser.add_argument('args', nargs='*', help='place names such as 富士山')
	args = parser.parse_args()

	geolocator = Nominatim(user_agent="my_usera_gent")
	for place_name in args.args:
		location = geolocator.geocode(place_name)
		if location:
			print(location.address)
			print(location.latitude, location.longitude)
