# Parse a line from wsjt-x ALL_WSPR.TXT file, and convert to JSON encoding

import json
import sys
import re
import time
import os
from pprint import pprint

# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = os.environ.get('ADAFRUIT_IO_KEY' )

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = os.environ.get( 'ADAFRUIT_IO_USERNAME' )

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)

# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for cen4930c json changes...')
    # Subscribe to changes on a feed named DemoFeed.
    #client.subscribe('CEN4930C/feeds/wspr/20m/json')
    client.subscribe('cen4930c/json')

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

#maiden head to lon/lat
# based on code by: Edwin van Mierlo
# https://ham.stackexchange.com/questions/6462/how-can-one-convert-from-grid-square-to-lat-long

def getLon(one, three):
    startLon = 0
    endLon = 0

    field = ((ord(one.lower()) - 97) * 20) 
    square = int(three) * 2

    startLon = field + square - 180
    endLon = field + square  - 180 

    return startLon, endLon

def getLat(two, four):
    startLat = 0
    endLat = 0

    field = ((ord(two.lower()) - 97) * 10) 
    square = int(four)

    startLat = field + square - 90
    endLat = field + square - 90

    return startLat, endLat

def maidenhead_to_lat_lon( strMaidenHead ):
    startLon = 0
    startLat = 0

    if len(strMaidenHead) == 4: 

        one = strMaidenHead[0:1]
        two = strMaidenHead[1:2]
        three = strMaidenHead[2:3]
        four = strMaidenHead[3:4]

        (startLon, _) = getLon(one, three)
        (startLat, _) = getLat(two, four)
    return startLat, startLon
    
def main():
    # Create an MQTT client instance.
    client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY, secure=True)

    # Setup the callback functions defined above.
    client.on_connect    = connected
    client.on_disconnect = disconnected
    client.on_message    = message

    # Connect to the Adafruit IO server.
    client.connect()

    # Run one loop to get started
    client.loop( )

    # Loop on input from stdin/pipeline
    for input_line in sys.stdin:
        input_line.rstrip()

        # https://stackoverflow.com/questions/32856012/how-do-you-split-a-string-in-python-with-multiple-delimiters
        spot_array = re.split( r' +', input_line )
        print( len( spot_array ) )

        spot_dict = {}
        spot_fields = [ "yymmdd", "utc", "db", "unk1", "freq", "call", "grid", "power" ]
        if len( spot_array ) == 17:
            for field_num in range( len( spot_fields ) ):
                spot_dict[spot_fields[field_num]] = spot_array[field_num]

            (lat, lon) = maidenhead_to_lat_lon( spot_array[6] )
            spot_dict["lat"] = lat
            spot_dict["lon"] = lon
            #json_value_str = json.dumps(spot_dict)
            json_value_str = str(spot_dict)
            json_value_str = re.sub(r'^"|"$', '', json_value_str)
            #print(json_value_str)
            mqtt_json_str = \
                { 
                    "value": json_value_str,
                    "lat": 28.6889,
                    "lon": -1.5152,
                    "ele": 100
                }
            
            #client.publish( 'CEN4930C/feeds/wspr/20m/json', str(mqtt_json_str) )
            client.publish( 'cen4930c/json', str(mqtt_json_str) )
            #print( str(mqtt_json_str))
             # pump message loop
            client.loop( )


if __name__ == "__main__":
    main( )

