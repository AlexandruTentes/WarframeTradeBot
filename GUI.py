from imgui.integrations.glfw import GlfwRenderer
import glfw
import imgui
import OpenGL.GL as gl
import singleton
import globals
import WMAPIR
import configs
import json
import re
import time
import pyperclip
import time
import WindowsBalloonTip
from win10toast import ToastNotifier
import win32gui

class GUI(metaclass=singleton.Singleton):
    window = None
    global_data = None
    req = None
    config_data = None
    wm_json_data = {}
    remove_items_popup = False
    open_item_remove_popup = False
    open_item_pin_popup = False
    remove_items_security_check = False
    max_matrix = False
    
    def __init__(self):
        self.global_data = globals.Globals()
        imgui.create_context()
        self.global_data.program_running = True
        self.config_data = configs.Configs()
        self.req = WMAPIR.WMAPIR()

    def window(self):        
        if not glfw.init():
            return
    
        self.window = glfw.create_window(640, 480, self.global_data.app_name, None, None)

        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)
        gui_render = GlfwRenderer(self.window)

        while not glfw.window_should_close(self.window) \
              and self.global_data.program_running:
            gl.glClearColor(0, 0, 0, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
            gui_render.process_inputs()
            imgui.new_frame()
            self.render()
            imgui.render()
            imgui.end_frame()
            gui_render.render(imgui.get_draw_data())

            glfw.swap_buffers(self.window)
            glfw.poll_events()

        self.global_data.program_running = False
        glfw.terminate()

    def search_items_priority(self):
        curr_index = 0
        
        while self.global_data.program_running:

            if not self.wm_json_data:
                curr_index = self.search_items(curr_index)
            else:
                try:
                    for item in list(self.wm_json_data):
                        self.searchbar_callback(item)

                        if not self.max_matrix:
                            curr_index = self.search_items(curr_index)
                            time.sleep(0.5)
                        else:
                            time.sleep(0.5)
                except Exception as err:
                    print("ERROR in `search_items_priority`: ", err)
                

    def search_items(self, curr_index):
        curr_item = ""
        delay_allowed = 0.5
        delay_set = 0.5
        delay = 0
 
        while self.global_data.program_running:
            if delay >= delay_allowed:
                break
            
            if curr_item in self.wm_json_data:
                curr_index = int(curr_index + 1) % int(len(self.config_data.config["warframeItems"]) - 2)
                curr_item = self.config_data.config["warframeItems"][curr_index + 2]
                continue
            
            curr_item = self.config_data.config["warframeItems"][curr_index + 2]
            curr_index = int(curr_index + 1) % int(len(self.config_data.config["warframeItems"]) - 2)

            time.sleep(delay_set)
            delay = delay + delay_set
            self.searchbar_callback(curr_item)

        return curr_index

    def app_MENU(self):
        menu_bar_size = None

        if imgui.begin_main_menu_bar():
            menu_bar_size = imgui.get_window_size()
            imgui.text("Search: ")
            imgui.push_item_width(imgui.get_window_width() * 0.10)
            searchbar_changed, searched_item = imgui.input_text("", "- input -", 256, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE | imgui.INPUT_TEXT_AUTO_SELECT_ALL)
            imgui.pop_item_width()
            
            imgui.push_item_width(imgui.get_window_width() * 0.10)
            imgui.text("Sale and Plat: ")
            changed, (self.config_data.config["itemsMinAVG"], self.config_data.config["itemsMinPlat"]) = \
                imgui.input_int2(" ", self.config_data.config["itemsMinAVG"], self.config_data.config["itemsMinPlat"])
            imgui.pop_item_width()

            if imgui.begin_menu("Options..."):
                clk_rmv_itm, state_rmv_itm = imgui.menu_item('Remove Item')
                clk_pin_itm, state_pin_itm = imgui.menu_item('Pin Item')
                
                if clk_rmv_itm:
                    self.open_item_remove_popup = True

                if clk_pin_itm:
                    self.open_item_pin_popup = True
                    
                imgui.end_menu()

            # Remove Item Popup
            if self.open_item_remove_popup:
                expand, status = imgui.begin("Remove items from list", imgui.WINDOW_ALWAYS_AUTO_RESIZE)

                if not status:
                    self.open_item_remove_popup = False

                if imgui.button("Remove all" if not self.remove_items_security_check else "Are you sure?"):
                    self.remove_items_security_check = not self.remove_items_security_check

                    if self.remove_items_security_check == False:
                        self.wm_json_data.clear()
                        self.config_data.config["warframeItems"].clear()
                        self.config_data.config["warframeItems"].append(0)
                        self.config_data.config["warframeItems"].append(0)

                rmitem_changed, rmitem_item = imgui.input_text("", "- input -", 256, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE | imgui.INPUT_TEXT_AUTO_SELECT_ALL)

                if rmitem_changed:
                    rmitem_item = rmitem_item.lower()
                    rmitem_item = re.sub(' +', ' ', rmitem_item)
                    rmitem_item = re.sub(' ', '_', rmitem_item)

                    if rmitem_item in self.wm_json_data:
                        del self.wm_json_data[rmitem_item]
                    try:
                        self.config_data.config["warframeItems"].remove(rmitem_item)
                    except:
                        pass
                
                for item in self.config_data.config["warframeItems"]:
                    if item != 0:
                        clicked, state = imgui.menu_item(item)

                        if clicked:
                            if item in self.wm_json_data:
                                del self.wm_json_data[item]
                            try:
                                self.config_data.config["warframeItems"].remove(item)
                            except:
                                pass
                imgui.end()

            # Pin Item Popup
            if self.open_item_pin_popup:
                expand, status = imgui.begin("Pin items from list", imgui.WINDOW_ALWAYS_AUTO_RESIZE)

                if not status:
                    self.open_item_pin_popup = False

                pinitem_changed, pinitem_item = imgui.input_text("", "- input -", 256, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE | imgui.INPUT_TEXT_AUTO_SELECT_ALL)

                if pinitem_changed:
                    pinitem_item = pinitem_item.lower()
                    pinitem_item = re.sub(' +', ' ', pinitem_item)
                    pinitem_item = re.sub(' ', '_', pinitem_item)
                    self.searchbar_callback(pinitem_item, True, True)                  
                
                for item in self.config_data.config["warframeItems"]:
                    if item != 0:
                        clicked, state = imgui.menu_item(item)

                        if clicked:
                            self.searchbar_callback(item, True, True)
                imgui.end()
            
            if searchbar_changed:
                searched_item = searched_item.lower()
                searched_item = re.sub(' +', ' ', searched_item)
                searched_item = re.sub(' ', '_', searched_item)
                self.searchbar_callback(searched_item)

            imgui.end_main_menu_bar()

    def app_GUI(self):
        index = 0
        width_offset = 0
        height_offset = 0
        occupied_cells = 0
        for item, data in self.wm_json_data.items():
            if occupied_cells == self.config_data.config["offerColumnNO"] * self.config_data.config["offerRowNO"]:
                self.max_matrix = True
                break

            self.max_matrix = False
            
            if (float(data["percentile_price"]) < self.config_data.config["itemsMinAVG"] or \
                min(data["estimated_avg"], data["ideal_avg"]) - int(data["platinum"]) < self.config_data.config["itemsMinPlat"]) \
                and not self.wm_json_data[item]["pinned"]:
                del self.wm_json_data[item]
                break
            
            if index != self.config_data.config["offerColumnNO"]:
                width_offset = index * self.config_data.config["offerWindowWidth"]
            else:
                height_offset = height_offset + self.config_data.config["offerWindowHeight"]
                index = 0
                width_offset = 0

            if data["wm_window_open_status"] == False:
                if item in self.wm_json_data:
                    del self.wm_json_data[item]
                try:
                    self.config_data.config["warframeItems"].remove(item)
                except:
                    pass
                break

            occupied_cells = occupied_cells + 1
            imgui.set_next_window_position(0 + width_offset, 20 + height_offset)
            imgui.set_next_window_size(self.config_data.config["offerWindowWidth"], self.config_data.config["offerWindowHeight"])
            data["wm_window_expanded_status"], data["wm_window_open_status"] = imgui.begin(item + " " + data["percentile_price"] +
                "% " + '%.2f' % (min(data["estimated_avg"], data["ideal_avg"]) - int(data["platinum"])), data["wm_window_open_status"], imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE
                | imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_FOCUS_ON_APPEARING
                | imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS)

            imgui.columns(4, 'avg_price')
            imgui.separator()
            imgui.text("Price")
            imgui.next_column()
            imgui.text("Average")
            imgui.next_column()
            imgui.text("Estimate")
            imgui.next_column()
            imgui.text("Ideal")
            imgui.next_column()
            imgui.separator()
            imgui.set_column_offset(1, 50)

            imgui.next_column()
            imgui.text_colored('%.2f' % data["real_avg"], 1, 0.3, 0)
            imgui.next_column()
            imgui.text_colored('%.2f' % data["estimated_avg"], 0.9, 1, 0.1)
            imgui.next_column()
            imgui.text_colored('%.2f' % data["ideal_avg"], 0.3, 1, 0.2)
            imgui.next_column()
            imgui.columns(1)

            imgui.columns(3, 'pinned')
            #imgui.set_column_offset(1, 80)
            _, self.wm_json_data[item]['selected_pin_price'] = imgui.input_int("pin_price", self.wm_json_data[item]['selected_pin_price'])
            imgui.next_column()
            _, self.wm_json_data[item]["notify_check"] = imgui.checkbox("Notify", self.wm_json_data[item]["notify_check"])
            imgui.next_column()
            if imgui.button(data["clipboard_text"]) and data["user"]["ingame_name"] != "-":
                data["clipboard_text"] = "Copied!"
                self.copy_to_clipboard(data["user"]["ingame_name"], item, data["platinum"])
            imgui.next_column()
            
            imgui.columns(3 if "mod_rank" in data else 1, 'clipboard')
            #imgui.set_column_offset(1, 70)
            _, self.wm_json_data[item]["pinned"] = imgui.checkbox("Pin", self.wm_json_data[item]["pinned"])
            imgui.next_column()
            if "mod_rank" in data:
                #changed, self.wm_json_data[item]['selected_mod_rank'] = imgui.slider_int(
                #"", self.wm_json_data[item]['selected_mod_rank'],
                #min_value=0, max_value=10,
                #format="%d")
                imgui.push_item_width(self.config_data.config["offerWindowWidth"] * 0.2)
                changed, self.wm_json_data[item]['selected_mod_rank'] = imgui.input_int("mod_rank", self.wm_json_data[item]['selected_mod_rank'])
                imgui.pop_item_width()
                imgui.next_column()
                _, self.wm_json_data[item]["mod_rank_check"] = imgui.checkbox("Rank", self.wm_json_data[item]["mod_rank_check"])
                imgui.next_column()

            imgui.columns(5, 'item_data')
            imgui.separator()
            imgui.text("Item")
            imgui.next_column()
            imgui.text("Region")
            imgui.next_column()
            imgui.text("Platform")
            imgui.next_column()
            imgui.text("Quantity")
            imgui.next_column()
            imgui.text("Plat")
            imgui.next_column()
            imgui.separator()
            imgui.set_column_offset(1, 50)

            imgui.next_column()
            imgui.text_colored(data["region"], 0.9, 0.6, 1)
            imgui.next_column()
            imgui.text_colored(data["platform"], 1, 0.6, 0)
            imgui.next_column()
            imgui.text_colored('%.2f' % data["quantity"], 0.8, 0.9, 0.3)
            imgui.next_column()
            imgui.text_colored('%.2f' % data["platinum"], 0.6, 1, 0.4)
            imgui.next_column()
            imgui.columns(1)

            imgui.columns(4, 'percentile_price_history')
            imgui.set_column_offset(1, 75)
            imgui.text("Sale min: ")
            imgui.next_column()
            imgui.text_colored(data["percentile_price_min"], 0.9, 0, 0.3)
            imgui.next_column()
            imgui.text("Sale max: ")
            imgui.next_column()
            imgui.text_colored(data["percentile_price_max"], 0.8, 1, 0.3)
            imgui.next_column()
            imgui.columns(1)

            imgui.set_next_window_position(0 + width_offset +
                (not "mod_rank" in data) * self.config_data.config["offerWindowWidth"] * 0.45, 20 + height_offset + self.config_data.config["offerWindowHeight"] * 0.9)
            imgui.begin_child("player_status")
            imgui.columns(4 if "mod_rank" in data else 2, 'online_status')
            imgui.set_column_offset(1, 50)
            if "mod_rank" in data:
                imgui.text("  Rank: ")
                imgui.next_column()
                if data['mod_rank_check']:
                    imgui.text_colored(str(data["mod_rank"]), 0.6, 0.3, 0.1)
                else:
                    imgui.text_colored("-", 0.6, 0.3, 0.1)        
                imgui.next_column()
            imgui.text("Status: ")
            imgui.next_column()
            imgui.text_colored(data["user"]["status"], 0.6, 0.9, 0)
            imgui.next_column()
            imgui.columns(1)
            imgui.end_child()
            
            imgui.end()
            index = index + 1

    def copy_to_clipboard(self, seller, item, price):
        item_text = item.replace("_", " ").title()
        output = "/w " + seller + " Hi! I want to buy: " + \
            item_text + (str(self.wm_json_data[item]["mod_rank"]) if "mod_rank" in self.wm_json_data[item] else "") + \
            " for " + str(price) + " platinum. (warframe.market)"
        pyperclip.copy(output)

    def searchbar_callback(self, item, force_add = False, pin = False):
        try:
            item_in_list = False;
            
            avg_json_user_filter = {
                "status": "offline online ingame"
            }

            avg_json_filter = {
                "order_type": "sell"
            }

            json_user_filter = {
                "status": "online ingame"
            }

            json_filter = {
                "order_type": "sell"
            }

            if item in self.wm_json_data and "mod_rank_check" in self.wm_json_data[item] and self.wm_json_data[item]['mod_rank_check']:
                avg_json_filter.update({'mod_rank': self.wm_json_data[item]['selected_mod_rank']})
                json_filter.update({'mod_rank': self.wm_json_data[item]['selected_mod_rank']})
                item_in_list = True
 
            real_avg, estimated_avg, ideal_avg = self.req.get_avg_price(item, avg_json_user_filter, avg_json_filter)
            min_price = 999999 if (item in self.wm_json_data and self.wm_json_data[item]["pinned"]) or force_add else min(estimated_avg, ideal_avg)
            output_arr = self.req.get_item(item,
                min_price, json_user_filter, json_filter)

            if len(output_arr) == 0:
                if item in self.wm_json_data and not self.wm_json_data[item]["pinned"]:
                     del self.wm_json_data[item]
            
            output = json.dumps(output_arr, indent=4, sort_keys=True)

            if not item in self.config_data.config["warframeItems"]:
                self.config_data.config["warframeItems"].append(item)

            output = json.loads(output)

            if len(output) == 0:
                if item in self.wm_json_data:
                    if not self.wm_json_data[item]["pinned"]:
                        del  self.wm_json_data[item]
                    else:
                        self.wm_json_data[item]["real_avg"] = 0
                        self.wm_json_data[item]["estimated_avg"] = 0
                        self.wm_json_data[item]["ideal_avg"] = 0
                        self.wm_json_data[item]["user"]["ingame_name"] = "-"
                        self.wm_json_data[item]["percentile_price"] = "0"
                        self.wm_json_data[item]["percentile_price_min"] = "0"
                        self.wm_json_data[item]["percentile_price_max"] = "0"
                        self.wm_json_data[item]["platinum"] = 0
                        self.wm_json_data[item]["quantity"] = 0
                        self.wm_json_data[item]["user"]["status"] = "-"
                        self.wm_json_data[item]["region"] = "-"
                        self.wm_json_data[item]["platform"] = "-"
                return
            
            output[0]["wm_window_open_status"] = True
            output[0]["wm_window_expanded_status"] = False
            output[0]["real_avg"] = real_avg
            output[0]["estimated_avg"] = estimated_avg
            output[0]["ideal_avg"] = ideal_avg
            output[0]["clipboard_text"] = "Clipboard"
            output[0]["selected_mod_rank"] = 0 if not item in self.wm_json_data else self.wm_json_data[item]['selected_mod_rank']
            output[0]["percentile_price"] = '%.2f' % ((1 - output[0]["platinum"] / max(min(estimated_avg, ideal_avg), 0.01)) * 100)
            output[0]["mod_rank_check"] = False if not item in self.wm_json_data else self.wm_json_data[item]['mod_rank_check']
            output[0]["pinned"] = self.wm_json_data[item]['pinned'] if item in self.wm_json_data else pin
            output[0]["previous_profit"] = 0 if not item in self.wm_json_data else self.wm_json_data[item]["profit"]
            output[0]["profit"] = min(output[0]["estimated_avg"], output[0]["ideal_avg"]) - int(output[0]["platinum"])
            output[0]["notify_check"] = True if not item in self.wm_json_data else self.wm_json_data[item]["notify_check"]
            output[0]["selected_pin_price"] = 0 if not item in self.wm_json_data else self.wm_json_data[item]["selected_pin_price"]

            if not item in self.wm_json_data:
                output[0]["percentile_price_min"] = output[0]["percentile_price"]
                output[0]["percentile_price_max"] = output[0]["percentile_price"]
            else:
                output[0]["percentile_price_min"] = '%.2f' % min(float(output[0]["percentile_price"]), float(self.wm_json_data[item]["percentile_price_min"]))
                output[0]["percentile_price_max"] = '%.2f' % max(float(output[0]["percentile_price"]), float(self.wm_json_data[item]["percentile_price_max"]))
            
            if ((float(output[0]["percentile_price"]) >= self.config_data.config["itemsMinAVG"] and \
                min(output[0]["estimated_avg"], output[0]["ideal_avg"]) - int(output[0]["platinum"]) >= self.config_data.config["itemsMinPlat"]) or \
                (item in self.wm_json_data and self.wm_json_data[item]["pinned"])) or force_add:

                if item in self.config_data.config["warframeItems"]:
                    focused_window_title = win32gui.GetWindowText (win32gui.GetForegroundWindow())
                    if ((not item in self.wm_json_data and self.config_data.config["notifyOffer"] == "on") or \
                        output[0]["profit"] > output[0]["previous_profit"] and \
                        output[0]["profit"] >= output[0]["selected_pin_price"]) and \
                        focused_window_title != self.global_data.app_name and output[0]["notify_check"]:

                        toast = ToastNotifier()
                        #WindowsBalloonTip.balloon_tip('%.2f' % (min(output[0]["estimated_avg"],
                         #   output[0]["ideal_avg"]) - int(output[0]["platinum"])), item)
                        toast.show_toast(
                            item,
                            '%.2f' % output[0]["profit"],
                            duration = 3,
                            icon_path = "bitcoin.ico",
                            threaded = True,
                        )
                        
                    self.wm_json_data[item] = output[0]                        
                    
                    #print(json.dumps(self.wm_json_data[item], indent=4, sort_keys=True))
                else:
                    if item in self.wm_json_data and not self.wm_json_data[item]["pinned"]:
                        del self.wm_json_data[item]
            else:
                if item in self.wm_json_data and not self.wm_json_data[item]["pinned"]:
                     del self.wm_json_data[item]
            
        except Exception as err:
            print("ERROR in `searchbar_callback`", err)
            pass

    def render(self):
        self.app_GUI()
        self.app_MENU()
