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
    ## EACH LAP
    if "lapResult" in data:
        result = data["lapResult"]
        lap_number = result["lapNumber"]
        lap_time = result["lapTime"]
        fuel = result["fuel"]
        made_pit_stop = result["madePitStop"]
        tire = result["tire"]

        global retire_early
        global graph
        global has_changed_tire
        global i

        global best_time
        global best_fuel
        global best_tire
        global best_spoiler
        global best_camber
        global best_air_intake

        global fuel
        global tire
        global spoiler
        global camber
        global intake

        if lap_time < best_time:
            best_time = lap_time
            best_fuel = fuel
            best_tire = tire
            best_spoiler = spoiler
            best_camber = camber
            best_air_intake = air_intake

        response = json.dumps({"instruction":"retire"})
        ws.send(response)

    elif "raceResult" in data:
        # print "Race complete!"
        # print "Level {}".format(data["raceResult"]["circuit"])
        # print "Status: {}".format(get_status(data["raceResult"]["status"]))
        # print "Total time: {}".format(data["raceResult"]["totalTime"])
        ws.close()

def on_error(ws, err):
    print "Error:", err

def on_close(ws):
    print "Connection closed."

def on_open(ws):
    global fuel
    global tire
    global spoiler
    global camber
    global intake

    print "Connection established."

    vehicle_params = {"instruction": "setVehicleParams"}
    vehicle_params["fuel"] = fuel # A,B,C,D
    vehicle_params["tire"] = tire # A,B,C
    vehicle_params["spoilerAngle"] = spoiler # [0.0, 10.0], default=5.0
    vehicle_params["camberAngle"] = camber # [0.0, 5.0], default=2.5
    vehicle_params["airIntakeDiameter"] = intake # [4.0, 8.0], default=6.0

    response = json.dumps(vehicle_params)
    ws.send(response)

    # start race
    response = json.dumps({ "instruction": "beginRace" })
    ws.send(response)

#
# ## OPTIONS
race = "practice"
#
# # globals
# best_time = float('inf')
#
# best_fuel = 0
# best_tire = 0
# best_spoiler = 0
# best_camber = 0
# best_air_intake = 0

# url being selected
url_options = {"practice":"wss://play.crederacup.com/season/I/practice",
               "austrian":"wss://play.crederacup.com/season/I/race/AUSTRIANGRANDPRIX",
               "brazilian":"wss://play.crederacup.com/season/I/race/BRAZILIANGRANDPRIX",
               "german":"wss://play.crederacup.com/season/I/race/GERMANGRANDPRIX",
               "italian":"wss://play.crederacup.com/season/I/race/ITALIANGRANDPRIX",
               "monaco":"wss://play.crederacup.com/season/I/race/MONACOGRANDPRIX"
                }

url = url_options[race]

ws = websocket.WebSocketApp(url,
                    header = ["X-Credera-Auth-Token: " + "5dd8c4eb-32f5-4d09-8db3-652feeac4f61"],
                    on_message = on_message,
                    on_error = on_error,
                    on_close = on_close)

ws.on_open = on_open
ws.run_forever()

sys.exit()

for fuel in ['A','B','C','D']:
    for tire in ['A','B','C']:
        for spoiler in range(0, 11, 5):
            for camber in range(0, 6, 5):
                for intake in range(4, 9, 2):
                    if __name__ == "__main__":
                        print "Attempting websocket connection to {}".format(url)

                        ws = websocket.WebSocketApp(url,
                                            header = ["X-Credera-Auth-Token: " + "0b9e130c-2ee9-4477-8a1a-6a68df512bdb"],
                                            on_message = on_message,
                                            on_error = on_error,
                                            on_close = on_close)

                        ws.on_open = on_open
                        ws.run_forever()
                        print 'trying to iterate'

print 'best_tire: ', best_tire
print 'best_camber: ', best_camber
print 'best_fuel: ', best_fuel
print 'best_spoiler: ', best_spoiler
print 'best_air_intake: ', best_air_intake
print 'best_time: ', best_time



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
