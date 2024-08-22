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
            "Default":0
        },
        "epoxy_overflow": {
            "FriendlyName":"Epoxy Overflow",
            "Unit":"mm",
            "Default":0
        },
        "deposition_feedrate": {
            "FriendlyName":"Depostion Feedrate",
            "Unit":"mm/s",
            "Default":0
        },
        "depostion_wattage": {
            "FriendlyName":"Depositon Wattage",
            "Unit":"W",
            "Default":0
        }
    },

    "Engraving": {
        "engraving_feedrate": {
            "FriendlyName":"Engraving Feedrate",
            "Unit":"mm/s",
            "Default":0
        },
        "plunge_amount": {
            "FriendlyName":"Plunge Amount",
            "Unit":"mm",
            "Default":0.05
        },
        "engraving_wattage": {
            "FriendlyName":"Engraving Wattage",
            "Unit":"W",
            "Default":0
        }
    },

    "Material": {
        "epoxy_density": {
            "FriendlyName":"Epoxy Density",
            "Unit":"g/cm3",
            "Default":0
        },
        "epoxy_price": {
            "FriendlyName":"Epoxy Price",
            "Unit":"$",
            "Default":0
        },
        "fr4_price": {
            "FriendlyName":"FR4 Price",
            "Unit":"$",
            "Default":0
        },
        "copper_thickness": {
            "FriendlyName":"Copper Thickness",
            "Unit":"oz",
            "Default":1
        },
        "copper_density": {
            "FriendlyName":"Copper Density",
            "Unit":"g/cm3",
            "Default":0
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
            "Default":0
        }
    }
}

def create_config_file():
    config = configparser.ConfigParser()
    for category in CONFIG_FILE_PARAMS:
        p_dict = dict()
        for param in CONFIG_FILE_PARAMS[category]:
            p_dict[param] = CONFIG_FILE_PARAMS[category][param]["Default"]
        config[category] = p_dict

    with open(DEFAULT_CONFIG_FILE, 'w') as con_file:
        config.write(con_file)

create_config_file()

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
        return "0"
        pass
    
    def CalcMaterial(self):
        return "0"
        pass

    def CalcPrice(self):
        return "0"
        pass
    
    def CalcEnergy(self):
        return "0"
        pass

    def OnClose(self, event):
        self.Destroy()