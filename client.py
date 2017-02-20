from __future__ import division

import websocket
import sys
import json
import cchelper

def get_status(code):
    if code == 1000:
        return "Finished"
    elif code == 1001:
        return "Ran out of fuel"
    elif code == 1002:
        return "Retired"
    elif code == 1003:
        return "Crashed"
    else:
        return "Unknown status code"

def on_message(ws, msg):
    data = json.loads(msg)
    print data

    # options:

    # initialize global variables
    global retire_early
    global graph
    global has_changed_tire
    global i

    ## FIRST RUN
    # initial weather
    if "weather" in data:
        result = data["weather"]
        temp = result["temp"]
        is_raining = result["isRaining"]

    elif "trackParams" in data:
        results = data["trackParams"]
        num_turns = results["numTurns"]
        num_laps = results["numLaps"]

    ## EACH LAP
    elif "lapResult" in data:
        result = data["lapResult"]
        lap_number = result["lapNumber"]
        lap_time = result["lapTime"]
        fuel = result["fuel"]
        made_pit_stop = result["madePitStop"]
        tire = result["tire"]

        ## Data collection
        graph[i] = lap_time

        ## Determine whether or not to make a pit stop
        need_fuel = fuel < 2
        need_tire = tire < 5
        make_pit_stop = need_fuel or need_tire
        if retire_early:
            response = json.dumps({"instruction":"retire"})
        elif make_pit_stop:
            pit_params = { "instruction": "pit"}
            pit_params["spoilerAngle"] = 5.0 # [0.0, 10.0], default=5.0
            pit_params["camberAngle"] = 2.5 # [0.0, 5.0], default=2.5
            pit_params["airIntakeDiameter"] = 6.0 # # airIntakeDiameter [4.0, 8.0], default=6.0
            pit_params["fuel"] = "C" # A,B,C
            pit_params["tire"] = "A" # A,B,C,D

            # if need_fuel:
            #     pit_params["fuel"] = "A" # A,B,C,D
            # if need_tire < 5:
            #     pit_params["tire"] = "A" # A,B,C

            response = json.dumps(pit_params)
        else:
            response = json.dumps({"instruction":"continue"})

        ws.send(response)
    elif "raceResult" in data:
        print "Race complete!"
        print "Level {}".format(data["raceResult"]["circuit"])
        print "Status: {}".format(get_status(data["raceResult"]["status"]))
        print "Total time: {}".format(data["raceResult"]["totalTime"])
        ws.close()

def on_error(ws, err):
    print "Error:", err

def on_close(ws):
    print "Connection closed."

def on_open(ws):
    print "Connection established."
    global race
    if race == "practice":
        # set weather
        weather = {"instruction": "setWeather"}
        weather["temp"] = 80 # [70, 80]
        weather["isRaining"] = False # True or False
        response = json.dumps(weather)
        ws.send(response)

    # get weather
    response = json.dumps({"instruction": "getWeather"})
    ws.send(response)
    # get vehicle parameters
    # response = json.dumps({"instruction": "getVehicleParams"})
    # ws.send(response)
    # set vehicle parameters
    vehicle_params = {"instruction": "setVehicleParams"}
    vehicle_params["fuel"] = "A" # A,B,C,D
    vehicle_params["tire"] = "A" # A,B,C
    vehicle_params["spoilerAngle"] = 5.0 # [0.0, 10.0], default=5.0
    vehicle_params["camberAngle"] = 2.5 # [0.0, 5.0], default=2.5
    vehicle_params["airIntakeDiameter"] = i # [4.0, 8.0], default=6.0

    response = json.dumps(vehicle_params)
    ws.send(response)
    # get track parameters
    response = json.dumps({"instruction": "getTrackParams"})
    ws.send(response)
    # start race
    response = json.dumps({ "instruction": "beginRace" })
    ws.send(response)


## OPTIONS
race = "practice"
retire_early = True
loop_start = 4
loop_end = 8
loop_iter = 1
x_title = 'air intake diameter'
y_title = 'lap time'

# globals
graph = {}


# url being selected
url_options = {"practice":"wss://play.crederacup.com/season/I/practice",
               "austrian":"wss://play.crederacup.com/season/I/race/AUSTRIANGRANDPRIX",
               "brazilian":"wss://play.crederacup.com/season/I/race/BRAZILIANGRANDPRIX",
               "german":"wss://play.crederacup.com/season/I/race/GERMANGRANDPRIX",
               "italian":"wss://play.crederacup.com/season/I/race/ITALIANGRANDPRIX",
               "monaco":"wss://play.crederacup.com/season/I/race/MONACOGRANDPRIX"
                }
url = url_options[race]

for i in range(loop_start,loop_end + loop_iter,loop_iter):
    print 'iterated value:', i
    if __name__ == "__main__":
        print "Attempting websocket connection to {}".format(url)

        ws = websocket.WebSocketApp(url,
                            header = ["X-Credera-Auth-Token: " + "5c8a27d7-513d-4801-a1bb-b8b4b87a6e43"],
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)

        # global variables
        has_changed_tire = False

        ws.on_open = on_open
        ws.run_forever()
        print 'trying to iterate'

print 'graph:', graph
cchelper.plot_lines([graph], y_title + ' vs ' + x_title, x_title, y_title)
cchelper.show()

    # loop attempt
    # for i in range(1, 3, 1):
    #     print "Attempting websocket connection to {}".format(url)
    #
    #     ws = websocket.WebSocketApp("wss://play.crederacup.com/season/I/practice",
    #                                 header = ["X-Credera-Auth-Token: " + "5c8a27d7-513d-4801-a1bb-b8b4b87a6e43"],
    #                                 on_message = on_message,
    #                                 on_error = on_error,
    #                                 on_close = on_close)
    #
    #     ws.on_open = on_open
    #     ws.run_forever()
