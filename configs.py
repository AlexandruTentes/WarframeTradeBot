import singleton
import log
import globals
import utility
import time
import os
import platform

class Configs(metaclass=singleton.Singleton):
    config = {
        "toggleConfigRuntimeRead": "on",
        "toggleCMD": "off",
        "warframeItems" : [],
        "offerWindowWidth": 300,
        "offerWindowHeight": 150,
        "offerRowNO": 5,
        "offerColumnNO": 3,
        "itemsMinAVG": 10,
        "itemsMinPlat": 0,
        "notifyOffer": "on"
    }
    
    configs_instance = None
    initial_config_read_status = False

    global_data = None
    logger = None
    util = None

    config_file_sanity = True
    prev_config_change_time = 0
    curr_config_change_time = 0
    config_runtime_thread = True
    read_cfg_ptr = None
    
    def __init__(self):
        self.global_data = globals.Globals()
        self.logger = log.Logger()
        self.util = utility.Utility()

        print("Reading startup config file data...")
        self.config = self.read_config_bootup(self.global_data.config_path + ".txt", self.config)
        self.initial_config_read_status = True

    def get_file_changedate(self, path):
        try:
            if platform.system() == 'Windows':
                return os.path.getmtime(path)

        except Exception as err:
            if self.config_file_sanity == True:
                self.logger.log(log.SEVERITY.HARD,
                    "The config file path was wrong!", err)
                self.config_file_sanity = False
                
            return None

        self.logger.log(log.SEVERITY.HARD,
            "Program only works correctly on a Windows OS!")

        return None

    def read_config_runtime(self, path):
        while self.global_data.program_running:
            while self.config_runtime_thread and self.config["toggleConfigRuntimeRead"] == "on":
                self.curr_config_change_time = self.get_file_changedate(path + ".txt")
                
                if self.curr_config_change_time != self.prev_config_change_time and self.prev_config_change_time != 0:
                    self.config = self.read_config_bootup(path + ".txt", self.config)

                self.prev_config_change_time = self.curr_config_change_time
                time.sleep(1)
            time.sleep(1)

    def read_config_bootup(self, path, dict = None):
        read_config = None
        data = {}
        dict_data = {}

        try:
            read_config = open(path, "r")
            self.read_cfg_ptr = read_config

        except Exception as err:
            self.logger.log(log.SEVERITY.HARD,
                "ERROR: Could not open config files at path " + path, err)
            return dict

        content = read_config.readlines()

        for line in content:
            if line == "\n" or line == "\t" or line[0] == " ":
                continue

            if line[0] == '#':
                continue

            remove_line_comment = line.split("#")[0]
            line_data = remove_line_comment.split(":")
            data_key = None
            data_value = None

            if len(line_data) > 1:
                data_key = line_data[0].strip()
                data_value = line_data[1].strip()

                if "," in data_value:
                    tmp_data_value = data_value.split(",")
                    new_data_value = []

                    for item in tmp_data_value:
                        item = ''.join(item.split())
                        new_data_value.append(self.util.string_to_number(item))

                    data_value = new_data_value
                else:
                    data_value = self.util.string_to_number(data_value)

                data[data_key] = data_value

        read_config.close()

        if dict != None:
            for key, value in data.items():
                if key in dict:
                    dict[key] = value
            return dict

        return data

    def update_config(self, path, dict = None):
        read_config = None
        new_config = ""

        if dict == None:
            dict = self.config
    
        try:
            read_config = open(path, "r")

        except Exception as err:
            self.logger.log(log.SEVERITY.HARD,
                "ERROR: Could not open config files at path " + path, err)
            return None

        content = read_config.readlines()

        for line in content:
            if line == "\n" or line == "\t" or line[0] == " " or line[0] == "#":
                new_config = new_config + line
                continue

            split_comma = line.split(":")
            split_comment = line.split("#")

            if len(split_comma) in [0, 1]:
                new_config = new_config + line
                continue

            key = split_comma[0]
            value = split_comma[1]
            pivot_index_start = -1
            pivot_index_end = -1

            if key in dict:
                new_value = ""
                new_comment = ""

                if len(split_comment) > 1:
                    new_comment = split_comment[1]

                if isinstance(dict[key], (int, float)):
                    new_value = str(dict[key])
                elif isinstance(dict[key], str):
                    new_value = dict[key]
                elif isinstance(dict[key], list):
                    for i in range(0, len(dict[key])):
                        delimiter = ", "

                        if i == len(dict[key]) - 1:
                            delimiter = ""

                        new_value = new_value + str(dict[key][i]) + delimiter

                if new_comment != "":
                    new_comment = "#" + new_comment + ""
                else:
                    new_comment = "\n"

                left_value_spacing = ""
                right_value_spacing = ""

                for i in range(0, len(value)):
                    if value[i] in [" ", "\t"]:
                        left_value_spacing = left_value_spacing + value[i]
                    else:
                        break

                left_comment_value = value.split("#")[0]

                for index in range(0, len(left_comment_value)):
                    i = len(left_comment_value) - index - 1
                    if left_comment_value[i] in [" ", "\t"]:
                        right_value_spacing = right_value_spacing + left_comment_value[i]
                    else:
                        break
                
                new_config = new_config + key + ":" + left_value_spacing + new_value + right_value_spacing + new_comment

        read_config.close()

        try:
            read_config = open(path, "w")

        except Exception as err:
            self.logger.log(log.SEVERITY.HARD,
                "ERROR: Could not open config files at path " + path, err)
            return None

        read_config.write(new_config)
        read_config.close()

    def clear(self):
        print("\t\t-clearing CONFIG data from memory...")
        
        if self.read_cfg_ptr != None:
            self.read_cfg_ptr.close()
