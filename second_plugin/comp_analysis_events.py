import configparser
from .poly_comparison import NetCollection, IU_PER_MM
import wx
from .comp_analysis_ui import AnalysisDialog
import math

import os
current_folder = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_FILE = os.path.join(current_folder, 'config.ini')

CONFIG_FILE_PARAMS = {
    "Deposition": {
        # "diameter": {
        #     "FriendlyName":"Diameter",
        #     "Unit":"mm",
        #     "Default":0.4
        # },
        # "epoxy_overflow": {
        #     "FriendlyName":"Epoxy Overflow",
        #     "Unit":"mm",
        #     "Default":0
        # },
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
        # "plunge_amount": {
        #     "FriendlyName":"Plunge Amount",
        #     "Unit":"mm",
        #     "Default":0.05
        # },
        "engraving_wattage": {
            "FriendlyName":"Engraving Wattage",
            "Unit":"W",
            "Default":100000
        },
        "engraving_stepdown": {
            "FriendlyName":"Engraving Stepdown",
            "Unit":"mm",
            "Default":0.05
        }
    },

    "Outline": {
        "outline_feedrate": {
            "FriendlyName":"Outline Cutting Feedrate",
            "Unit":"mm/s",
            "Default":20
        },
        "outline_stepdown": {
            "FriendlyName":"Outline Cutting Stepdown",
            "Unit":"mm",
            "Default":0.05
        },
    },

    "Laser Cutter": {
        "laser_feedrate": {
            "FriendlyName":"Laser Cutter Feedrate",
            "Unit":"mm/s",
            "Default":20
        },
        "laser_wattage": {
            "FriendlyName":"Laser Cutter Wattage",
            "Unit":"W",
            "Default":8
        }
    },

    "Curing Heater": {
        "heating_wattage": {
            "FriendlyName":"Curing Heater Wattage",
            "Unit":"W",
            "Default":26
        },
        "epoxy_curing_time": {
            "FriendlyName":"Curing Time",
            "Unit":"s",
            "Default":900
        },
    },

    "Material": {
        "epoxy_density": {
            "FriendlyName":"Epoxy Density",
            "Unit":"g/cm3",
            "Default":3.72
        },
        "copper_thickness": {
            "FriendlyName":"Copper Thickness",
            "Unit":"oz",
            "Default":1
        },
        # "copper_density": {
        #     "FriendlyName":"Copper Density",
        #     "Unit":"g/cm3",
        #     "Default":8.96
        # },
        # "fiberglass_thickness": {
        #     "FriendlyName":"Fiberglass Thickness",
        #     "Unit":"mm",
        #     "Default":1.6
        # },
        # "fiberglass_density": {
        #     "FriendlyName":"Fiberglass Density",
        #     "Unit":"g/cm3",
        #     "Default":1.850
        # },
    },

    "Price": {
        "epoxy_price": {
            "FriendlyName":"Epoxy Price",
            "Unit":"$/g",
            "Default":13.44
        },
        "fr4_price": {
            "FriendlyName":"FR4 Price",
            "Unit":"$/mm2",
            "Default":10.99
        },
        "stencil_price": {
            "FriendlyName":"Stencil Price",
            "Unit":"$/mm2",
            "Default":0.99
        }
    }
}

CONFIG_USER_PARAMS = {
    "Engraving": {
        "groove_depth": {
            "FriendlyName": "Groove Depth",
            "Unit":"mm",
            "Default":0.2
        }
    },
    "Material": {
        "board_thickness": {
            "FriendlyName": "Board Thickness",
            "Unit":"mm",
            "Default":1.7
        }
    },
    "Renewal": {
        "iteration_number": {
            "FriendlyName": "Iteration Number",
            "Unit":"",
            "Default":2
        }
    }
}

MM2_TO_FT2 = 1.07639 * (10**-5)
OZ_TO_G = 28.3495

COPPER_DENSITY = 8.96
FIBERGLASS_DENSITY = 1.850

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
        self.path_dict = path_dict

        if board:
            self.path_dict = board.create_path_dict()
            self.edge_area = board.edge.get_area_mm()
            self.edge_length = board.edge.get_length_mm()

        self.length_dict = dict()
        self.total_path_length = 0
        self.area_dict = dict()
        self.total_path_area = 0

        for layer in self.path_dict:
            length = self.path_dict[layer].get_length_mm()
            self.length_dict[layer] = length
            self.total_path_length += length

            area = self.path_dict[layer].get_area_mm()
            self.area_dict[layer] = area
            self.total_path_area += area
        pass

class CompAnalysis():
    def __init__(self, old_board, new_board):
        pass

    def RunAnalysis():
        pass

class CompAnalysisDialog(AnalysisDialog):
    def __init__(self, parent, config_file=DEFAULT_CONFIG_FILE):
        super(CompAnalysisDialog, self).__init__(None)

        self.parent = parent

        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        print(self.config.sections())
        
        self.file_params = dict()
        self.user_params = dict()

        self.AddFileParams()
        self.AddUserParams()
        pass

    def AddFileParams(self):
        params_sizer = wx.BoxSizer(wx.VERTICAL)
        self.PanelConfigParams.SetSizer(params_sizer)
        for category in CONFIG_FILE_PARAMS:
            cat_label = wx.StaticText(self.PanelConfigParams, label=f"---{category}---")
            cat_label.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Arial" ) )
            params_sizer.Add(cat_label)
            
            self.file_params[category] = dict()

            for param in CONFIG_FILE_PARAMS[category]:
                param_info = CONFIG_FILE_PARAMS[category][param]
                single_sizer = wx.BoxSizer(wx.HORIZONTAL)
                name_label = wx.StaticText(self.PanelConfigParams,
                                             label=param_info["FriendlyName"] + ":\t")
                single_sizer.Add(name_label)
                unit_label = wx.StaticText(self.PanelConfigParams, 
                                           label=param_info["Unit"])
                input_box = wx.TextCtrl(self.PanelConfigParams)

                value = self.config.get(category, param)
                self.file_params[category][param] = value

                input_box.SetValue(value)

                def text_chang_fn(event, c=category, p=param, i=input_box):
                    self.file_params[c][p] = i.GetValue()
                    # print("text changed", p, self.file_params[c][p])
                input_box.Bind(wx.EVT_TEXT, text_chang_fn)

                CONFIG_FILE_PARAMS[category][param]["TextCtrlRef"] = input_box

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

    def SaveParameters(self, event):
        config = configparser.ConfigParser()
        for category in self.file_params:
            config[category] = self.file_params[category]

        with open(DEFAULT_CONFIG_FILE, 'w') as con_file:
            config.write(con_file)
            # con_file.write("AAA")

        self.parent.AddToLog(F"Saved parameters to {DEFAULT_CONFIG_FILE}")

    def RestoreDefaults(self, event):
        for category in CONFIG_FILE_PARAMS:
            for param in CONFIG_FILE_PARAMS[category]:
                default_val = CONFIG_FILE_PARAMS[category][param]["Default"]
                self.file_params[category][param] = default_val
                CONFIG_FILE_PARAMS[category][param]["TextCtrlRef"].SetValue(str(default_val))

        self.Layout()
        pass

    def CalcResources(self, old_board, new_board, erase_paths, write_paths, erase_edges):
        self.old_board = PathParams(board=old_board)
        self.new_board = PathParams(board=new_board)
        self.erase_paths = PathParams(path_dict=erase_paths)
        self.write_paths = PathParams(path_dict=write_paths)
        self.erase_edges = erase_edges

        original_time, renewal_time, time_diff = self.CalcTime()
        epoxy_weight, stencil_area, fr4_area, weight_diff = self.CalcMaterial()
        original_price, renewal_price, price_diff = self.CalcPrice()
        original_energy, renewal_energy, energy_diff = self.CalcEnergy()
#         text = f'''
# =====Sustainability Evaluation=====
# Time Saved = {time}\nEpoxy Used = {epoxy}\nCopper Saved = {copper}\nFiberglass Saved = {fiberglass}\nMoney Saved = {price}\nEnergy Saved = {energy}'''
        text = f'''
=====Sustainability Evaluation=====
Material Saved = {weight_diff}
    PCB Renewal Weight = {epoxy_weight}
    New FR4 Weight = {format_float(self.original_weight)} mg
Money Saved = {price_diff}
    PCB Renewal Price = {renewal_price}
    New FR4 Price = {original_price}
Time Saved = {time_diff}
    PCB Renewal Time = {renewal_time}
    New FR4 Time = {original_time}
Energy Saved = {energy_diff}
    PCB Renewal Energy = {renewal_energy}
    New FR4 Energy = {original_energy}

========Itemized Consumption========
Epoxy Used = {epoxy_weight}
Stencil Area Used = {stencil_area}
FR4 Area Saved = {fr4_area}

Epoxy Price = $ {format_float(self.epoxy_price)}
Stencil Price = $ {format_float(self.stencil_price)}
FR4 Price = {original_price}

Deposition Time = {format_float(self.deposition_time / 60)} min
Curing Time = {format_float(self.curing_time / 60)} min
Laser Cutting Time = {format_float(self.stencil_time / 60)} min
Renewal Engraving Time = {format_float(self.write_time / 60)} min
New FR4 Engraving Time = {format_float(self.original_time / 60)} min

Deposition Energy = {format_float(self.deposition_energy)} J
Curing Energy = {format_float(self.curing_energy)} J
Laser Cutting Energy = {format_float(self.laser_energy)} J
Renewal Engraving Energy = {format_float(self.renewal_engraving_energy)} J
New FR4 Engraving Energy = {original_energy}
'''
        return text
        pass

    def CalcTime(self):
        dep_fr = float(self.file_params["Deposition"][ "deposition_feedrate"])
        erase_len = self.erase_paths.total_path_length

        eng_fr = float(self.file_params["Engraving"]["engraving_feedrate"])
        eng_stepdown = float(self.file_params["Engraving"]["engraving_stepdown"])
        original_len = self.new_board.total_path_length

        out_fr = float(self.file_params["Outline"]["outline_feedrate"])
        out_stepdown = float(self.file_params["Outline"]["outline_stepdown"])
        original_out_length = self.new_board.edge_length
        board_thickness = float(self.user_params["board_thickness"]) 

        las_fr = float(self.file_params["Laser Cutter"]["laser_feedrate"])

        iter_num = int(self.user_params["iteration_number"])
        groove_depth = float(self.user_params["groove_depth"])

        eng_depth = groove_depth + (0.05 * (iter_num - 1))

        print(f"original len = {original_len}")

        self.original_time = \
            ((original_len / eng_fr) * math.ceil(eng_depth / eng_stepdown)) +  ((original_out_length / out_fr) * math.ceil(board_thickness / out_stepdown))
        original_time_min = self.original_time / 60

        self.curing_time = float(self.file_params["Curing Heater"]["epoxy_curing_time"])
        self.stencil_time = self.erase_paths.total_path_length / las_fr
        self.deposition_time = erase_len / dep_fr

        write_eng_depth = eng_depth + (0.05 * (iter_num - 1))
        write_len = self.write_paths.total_path_length
        write_out_len = self.erase_edges.cut_length

        # print(f"{}")
        
        self.write_time = \
            ((write_len / eng_fr) * math.ceil(write_eng_depth / eng_stepdown)) + ((write_out_len / out_fr) * math.ceil(board_thickness / out_stepdown))

        renewal_time_min = (self.curing_time + self.stencil_time + self.deposition_time + self.write_time) / 60

        return f"{format_float(original_time_min)} min", f"{format_float(renewal_time_min)}", f"{format_float(original_time_min - renewal_time_min)} min"
        pass
    
    def CalcMaterial(self):
        epoxy_density = float(self.file_params["Material"]["epoxy_density"])
        erase_area = self.erase_paths.total_path_area
        groove_depth = float(self.user_params["groove_depth"])
        iter_num = float(self.user_params["iteration_number"])
        print(epoxy_density, erase_area, groove_depth)
        self.epoxy_filling_depth = groove_depth + ((iter_num - 2) * 0.05)

        # The 1000 is because we're converting mm3 to cm3
        epoxy_weight = epoxy_density * erase_area * groove_depth #/ 1000 Ignoring the divide by 1000 so it'll be in miligrams
        self.epoxy_weight = epoxy_weight
        stencil_area = self.old_board.edge_area

        fr4_area = self.new_board.edge_area

        copper_per_ft2 = float(self.file_params["Material"]["copper_thickness"]) 
        fbr_thickness = float(self.user_params["board_thickness"]) - 0.1
        # fbr_density = float(self.file_params["Material"]["fiberglass_density"])

        # original_area = self.new_board.edge.get_area_mm() * MM2_TO_FT2

        # fbr_weight = original_area * fbr_thickness * fbr_density

        copper_weight = copper_per_ft2 * (fr4_area * MM2_TO_FT2) * OZ_TO_G
        print(fr4_area, fbr_thickness, FIBERGLASS_DENSITY, 1000)
        fiberglass_weight = fr4_area * fbr_thickness * FIBERGLASS_DENSITY #/ 1000 # cm3 to mm3 in mg
        # print("weights", copper_weight, fiberglass_weight)
        
        self.original_weight = copper_weight + fiberglass_weight

        return f"{format_float(epoxy_weight)} mg", f"{format_float(stencil_area)} mm2",f"{format_float(fr4_area)} mm2", f"{format_float(self.original_weight - epoxy_weight)} mg"
        pass

    def CalcPrice(self):
        # Maybe just do price per ml?
        # epoxy_density = float(self.file_params["Material"]["epoxy_density"])
        epoxy_rate = float(self.file_params["Price"]["epoxy_price"])
        fr4_rate = float(self.file_params["Price"]["fr4_price"])
        stencil_rate = float(self.file_params["Price"]["stencil_price"])

        self.stencil_price = (self.new_board.edge_area * stencil_rate)
        self.epoxy_price = (self.epoxy_weight * epoxy_rate)

        renewal_price = self.epoxy_price + self.stencil_price
        original_price = fr4_rate * self.new_board.edge_area
        return f"${format_float(original_price)}", f"${format_float(renewal_price)}", f"${format_float(original_price - renewal_price)}"
        pass
    
    def CalcEnergy(self):
        dep_wtt = float(self.file_params["Deposition"]["deposition_wattage"])
        eng_wtt = float(self.file_params["Engraving"]["engraving_wattage"])
        heat_wtt = float(self.file_params["Curing Heater"]["heating_wattage"])
        las_wtt = float(self.file_params["Laser Cutter"]["laser_wattage"])

        original_energy = eng_wtt * self.original_time
        self.renewal_engraving_energy = (eng_wtt * self.write_time)
        self.deposition_energy = (dep_wtt * self.deposition_time)
        self.curing_energy = (heat_wtt * self.curing_time)
        self.laser_energy = (las_wtt * self.stencil_time)
        renewal_energy = (eng_wtt * self.write_time) + (dep_wtt * self.deposition_time) + (heat_wtt * self.curing_time) + (las_wtt * self.stencil_time)
        return f"{format_float(original_energy)} J", f"{format_float(renewal_energy)} J", f"{format_float(original_energy - renewal_energy)} J"
        pass

    def OKClicked(self, event):
        # self.EndModal(wx.ID_OK)
        self.Hide()

    def OnClose(self, event):
        # self.Destroy()
        # self.EndModal(wx.ID_OK)
        self.Hide()
        pass