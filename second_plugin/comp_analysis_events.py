import configparser
from .poly_comparison import NetCollection, IU_PER_MM
import wx
from .comp_analysis_ui import AnalysisDialog

import os
current_folder = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_FILE = os.path.join(current_folder, 'config.ini')

CONFIG_FILE_PARAMS = {
    "Deposition": {
        "diameter": {
            "FriendlyName":"Diameter",
            "Unit":"mm",
            "Default":0.4
        },
        "epoxy_overflow": {
            "FriendlyName":"Epoxy Overflow",
            "Unit":"mm",
            "Default":0
        },
        "deposition_feedrate": {
            "FriendlyName":"Depostion Feedrate",
            "Unit":"mm/s",
            "Default":1
        },
        "deposition_wattage": {
            "FriendlyName":"Depositon Wattage",
            "Unit":"W",
            "Default":10
        }
    },

    "Engraving": {
        "engraving_feedrate": {
            "FriendlyName":"Engraving Feedrate",
            "Unit":"mm/s",
            "Default":20
        },
        "plunge_amount": {
            "FriendlyName":"Plunge Amount",
            "Unit":"mm",
            "Default":0.05
        },
        "engraving_wattage": {
            "FriendlyName":"Engraving Wattage",
            "Unit":"W",
            "Default":100000
        }
    },

    "Material": {
        "epoxy_density": {
            "FriendlyName":"Epoxy Density",
            "Unit":"g/cm3",
            "Default":3.72
        },
        "epoxy_price": {
            "FriendlyName":"Epoxy Price",
            "Unit":"$/g",
            "Default":13.44
        },
        "epoxy_curing_time": {
            "FriendlyName":"Curing Time",
            "Unit":"s",
            "Default":3600
        },
        "fr4_price": {
            "FriendlyName":"FR4 Price",
            "Unit":"$",
            "Default":10.99
        },
        "copper_thickness": {
            "FriendlyName":"Copper Thickness",
            "Unit":"oz",
            "Default":1
        },
        "copper_density": {
            "FriendlyName":"Copper Density",
            "Unit":"g/cm3",
            "Default":8.96
        },
        "fiberglass_thickness": {
            "FriendlyName":"Fiberglass Thickness",
            "Unit":"mm",
            "Default":1.6
        },
        "fiberglass_density": {
            "FriendlyName":"Fiberglass Density",
            "Unit":"g/cm3",
            "Default":1.850
        },
    }
}

CONFIG_USER_PARAMS = {
    "engraving": {
        "groove_depth": {
            "FriendlyName": "Groove Depth",
            "Unit":"mm",
            "Default":0.2
        }
    }
}

WRITE_PATH_LEN = 10
ERASE_PATH_LEN = 10
NEW_BOARD_PATH_LEN = 100

def format_float(num, places=2):
    return f"{round(num, places):.2f}"
    
def create_config_file():
    config = configparser.ConfigParser()
    for category in CONFIG_FILE_PARAMS:
        p_dict = dict()
        for param in CONFIG_FILE_PARAMS[category]:
            p_dict[param] = CONFIG_FILE_PARAMS[category][param]["Default"]
        config[category] = p_dict

    with open(DEFAULT_CONFIG_FILE, 'w') as con_file:
        config.write(con_file)

# create_config_file()

class PathParams():
    def __init__(self, board=None, path_dict=None):
        if board:
            self.path_dict = board.create_path_dict()
            self.bb_area = board.board.GetBoardEdgesBoundingBox().GetArea() // (IU_PER_MM * IU_PER_MM)

        self.length_dict = dict()

        for layer in self.path_dict:
            self.length_dict[layer] = self.path_dict[layer].length
        pass

class CompAnalysisDialog(AnalysisDialog):
    def __init__(self, old_board, new_board, erase_paths, write_paths, config_file=DEFAULT_CONFIG_FILE):
        super(CompAnalysisDialog, self).__init__(None)

        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        print(self.config.sections())
        # self.old_board = old_board
        # self.new_board = new_board
        # self.erase_paths = erase_paths
        # self.write_paths = write_paths
        
        self.user_params = dict()

        self.AddFileParams()
        self.AddUserParams()
        pass

    def AddFileParams(self):
        params_sizer = wx.BoxSizer(wx.VERTICAL)
        self.PanelConfigParams.SetSizer(params_sizer)
        for category in CONFIG_FILE_PARAMS:
            cat_label = wx.StaticText(self.PanelConfigParams, label=f"---{category}---")
            params_sizer.Add(cat_label)
            
            for param in CONFIG_FILE_PARAMS[category]:
                param_info = CONFIG_FILE_PARAMS[category][param]
                single_sizer = wx.BoxSizer(wx.HORIZONTAL)
                name_label = wx.StaticText(self.PanelConfigParams,
                                             label=param_info["FriendlyName"] + ":\t")
                single_sizer.Add(name_label)
                unit_label = wx.StaticText(self.PanelConfigParams, 
                                           label=param_info["Unit"])
                input_box = wx.TextCtrl(self.PanelConfigParams)
                input_box.SetValue(self.config.get(category, param))

                if param_info["Unit"] == "$":
                    single_sizer.Add(unit_label)
                    single_sizer.Add(input_box)
                else:
                    single_sizer.Add(input_box)
                    single_sizer.Add(unit_label)
                
                CONFIG_FILE_PARAMS[category][param]["InputBox"] = input_box

                params_sizer.Add(single_sizer)

        self.Layout()
        pass

    def AddUserParams(self):
        params_sizer = wx.BoxSizer(wx.VERTICAL)
        self.PanelUserParams.SetSizer(params_sizer)
        for category in CONFIG_USER_PARAMS:
            for param in CONFIG_USER_PARAMS[category]:
                param_info = CONFIG_USER_PARAMS[category][param]
                single_sizer = wx.BoxSizer(wx.HORIZONTAL)
                name_label = wx.StaticText(self.PanelUserParams,
                                             label=param_info["FriendlyName"] + ": ")
                single_sizer.Add(name_label)
                unit_label = wx.StaticText(self.PanelUserParams, 
                                           label=param_info["Unit"])
                input_box = wx.TextCtrl(self.PanelUserParams)
                input_box.SetValue(str(param_info["Default"]))
                def text_chang_fn(event, p=param):
                    self.user_params[p] = input_box.GetValue()
                input_box.Bind(wx.EVT_TEXT, text_chang_fn)

                self.user_params[param] = str(param_info["Default"])

                if param_info["Unit"] == "$":
                    single_sizer.Add(unit_label)
                    single_sizer.Add(input_box)
                else:
                    single_sizer.Add(input_box)
                    single_sizer.Add(unit_label)
                
                params_sizer.Add(single_sizer)

        self.Layout()

    def CalcResources(self):
        time = self.CalcTime()
        material = self.CalcMaterial()
        price = self.CalcPrice()
        energy = self.CalcEnergy()
        text = f'''
=====Sustainability Evaluation=====
Time Saved = {time}\nEpoxy Used = {material}\nMoney Saved = {price}\nEnergy Saved = {energy}'''
        
        return text
        pass

    def CalcTime(self):
        dep_fr = float(self.config.get("Deposition", "deposition_feedrate"))
        eng_fr = float(self.config.get("Engraving", "engraving_feedrate"))

        self.original_time = (NEW_BOARD_PATH_LEN * eng_fr)
        original_time_min = (NEW_BOARD_PATH_LEN * eng_fr) / 60

        self.erase_time = (dep_fr * ERASE_PATH_LEN)
        self.write_time = (eng_fr * WRITE_PATH_LEN)
        erase_n_write_time_min = (self.erase_time + self.write_time) / 60

        return f"{format_float(original_time_min)} min - {format_float(erase_n_write_time_min)} min = {format_float(original_time_min - erase_n_write_time_min)} min"
        pass
    
    def CalcMaterial(self):
        epoxy_diameter = float(self.config.get("Deposition", "diameter"))
        epoxy_volume = float(self.user_params["groove_depth"]) * epoxy_diameter * ERASE_PATH_LEN
        self.epoxy_volume = epoxy_volume
        return f"{format_float(epoxy_volume)} cm3"
        pass

    def CalcPrice(self):
        # Maybe just do price per ml?
        epoxy_density = float(self.config.get("Material", "epoxy_density"))
        epoxy_price = float(self.config.get("Material", "epoxy_price"))
        fr4_price = float(self.config.get("Material", "fr4_price"))
        erase_n_write_price = self.epoxy_volume * epoxy_price
        original_price = fr4_price
        return f"${format_float(original_price)} - ${format_float(erase_n_write_price)} = ${format_float(original_price - erase_n_write_price)}"
        pass
    
    def CalcEnergy(self):
        dep_wtt = float(self.config.get("Deposition", "deposition_wattage"))
        eng_wtt = float(self.config.get("Engraving", "engraving_wattage"))
        original_energy = eng_wtt * self.original_time
        erase_n_write_energy = (eng_wtt * self.write_time) + (dep_wtt * self.erase_time)
        return f"{format_float(original_energy)} J - {format_float(erase_n_write_energy)} J = {format_float(original_energy - erase_n_write_energy)} J"
        pass

    def OnClose(self, event):
        self.Destroy()