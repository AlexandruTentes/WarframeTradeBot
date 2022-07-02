import requests
import singleton
import globals
from operator import itemgetter
from datetime import datetime

class WMAPIR(metaclass=singleton.Singleton):
    global_data = None
    wmurl = "https://api.warframe.market/v1"
    
    def __init__(self):
        self.global_data = globals.Globals()

    def get_avg_price(self, item, json_user_filter, json_filter):
        json = self.get_item(item, 999999, json_user_filter, json_filter)
        
        if len(json) == 0:
            return 0, 0, 0
        
        prices = {}
        real_avg_count = 0
        real_avg = 0
        estimated_avg_count = 0
        estimated_avg = 0
        ideal_avg_count = 0
        ideal_avg = 0

        for offer in json:
            str_time = ""
            str_time_arr = offer["last_update"].split("-")
            str_time = str_time + str_time_arr[0] + "-" + str_time_arr[1] + "-" + str_time_arr[2][0] + str_time_arr[2][1]
            time_raw = datetime.strptime(str_time, '%Y-%m-%d')
            try:
                time = int(str((datetime.now() - time_raw)).split(' ')[0])
            except:
                time = 1
                
            if offer["platinum"] in prices:
                prices[offer["platinum"]]["ppl"] = prices[offer["platinum"]]["ppl"] + 1
                prices[offer["platinum"]]["status"] = offer["user"]["status"]
                prices[offer["platinum"]]["time"] = min(prices[offer["platinum"]]["time"], time)
            else:
                prices[offer["platinum"]] = {
                    "status": "offline",
                    "weight": 50,
                    "time": time, #in days
                    "ppl": 0
                }

            real_avg_count = real_avg_count + 1
            real_avg = real_avg + offer["platinum"]

        if real_avg_count != 0:
            real_avg = real_avg / real_avg_count
        else:
            return (0, 0, 0)

        for price, data in prices.items():
            if price < real_avg:
                prices[price]["weight"] = prices[price]["weight"] + 5 + 10 * (prices[price]["status"] != "offline")
            else:
                prices[price]["weight"] = prices[price]["weight"] - 25 - 10 * (prices[price]["status"] == "offline")

            time_elapsed_points = 0
            time_elapsed_points = time_elapsed_points - 10 if data["time"] > 7 else time_elapsed_points
            time_elapsed_points = time_elapsed_points + 2 if data["time"] <= 7 else time_elapsed_points
            time_elapsed_points = time_elapsed_points + 5 if data["time"] <= 5 else time_elapsed_points
            time_elapsed_points = time_elapsed_points + 7 if data["time"] <= 3 else time_elapsed_points
            time_elapsed_points = time_elapsed_points + 10 if data["time"] <= 1 else time_elapsed_points

            if real_avg_count != 0:
                normalize_weight = float(data["ppl"] / real_avg_count)
            else:
                normalize_weight = 0
            prices[price]["weight"] = prices[price]["weight"] + 10 * normalize_weight + time_elapsed_points

            if prices[price]["weight"] > 60:
                estimated_avg = estimated_avg + price
                estimated_avg_count = estimated_avg_count + 1

            if prices[price]["weight"] > 90:
                ideal_avg = ideal_avg + price
                ideal_avg_count = ideal_avg_count + 1

        if estimated_avg_count != 0:
            estimated_avg = estimated_avg / estimated_avg_count
        else:
            estimated_avg = 0

        if ideal_avg_count !=0:
            ideal_avg = ideal_avg / ideal_avg_count
        else:
            ideal_avg = 0

        return (real_avg, estimated_avg, ideal_avg)
            

    def get_item(self, item, avg, json_user_filter, json_filter):
        json = requests.get(self.wmurl + '/items/' + item + "/orders").json()["payload"]["orders"]
        output_json = []
        output_json_user_filter = []

        output_json = [x for x in json if x["platinum"] <= avg]

        for key, value in json_filter.items():
            output_json = [x for x in output_json if x[key] == value or x[key] == None]

        for key, value in json_user_filter.items():
            v = value.split(" ")

            for item in v:
                item = item.strip()
                output_json_user_filter = output_json_user_filter + [x for x in output_json if x["user"][key] == item]
                    
        return sorted(output_json_user_filter, key=itemgetter('platinum'))

    
