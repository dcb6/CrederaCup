from __future__ import division

import websocket
import sys
import json


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
    if "lapResult" in data:
        result = data["lapResult"]
        lap_number = result["lapNumber"]
        fuel = result["fuel"]
        made_pit_stop = result["madePitStop"]

        # Determine whether or not to make a pit stop
        make_pit_stop = False

        response = json.dumps({ "instruction": "pit" if make_pit_stop else "continue" })
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
    response = json.dumps({ "instruction": "beginRace" })
    ws.send(response)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: " + sys.argv[0] + " <server> <token>"
        sys.exit(1)

    print "Attempting websocket connection to {}".format(sys.argv[1])
    ws = websocket.WebSocketApp(sys.argv[1],
                                header = ["X-Credera-Auth-Token: " + sys.argv[2]],
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
