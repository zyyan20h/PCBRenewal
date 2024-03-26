import pcbnew
import math
# from .pcb_file_management import OpenFileDialog
import os
import pathlib

# TODO: create a parent class calles PcbComponents, and place the common fucntions in it

ERASE_F_CU_LAYER = pcbnew.User_1
ERASE_B_CU_LAYER = pcbnew.User_2
ERASE_HOLE_LAYER = pcbnew.User_3

WRITE_F_CU_LAYER = pcbnew.User_4
WRITE_B_CU_LAYER = pcbnew.User_5
WRITE_HOLE_LAYER = pcbnew.User_6

IU_PER_MM = pcbnew.PCB_IU_PER_MM

HOLE_NAME = "Holes"

CURRENT_BOARD_EXPORT_TITLE = "current board"

# Getting all user layers
printable_layers = list(range(pcbnew.User_1, pcbnew.User_1 + 9))

# layer_dict = {
#     "erase": {
#         "front": ERASE_F_CU_LAYER,
#         "back" : ERASE_B_CU_LAYER,
#         "hole" : ERASE_HOLE_LAYER,
#     },

#     "write": {
#         "front": WRITE_F_CU_LAYER,
#         "back" : WRITE_B_CU_LAYER,
#         "hole" : WRITE_HOLE_LAYER,
#     }
# }

layer_dict = {"erase": dict(),
              "write": dict()}

class PcbTrack():    
    def __init__(self, track):

        start = track.GetStart()
        end = track.GetEnd()

        # Making sure that all the tracks are aligned
        if start.EuclideanNorm() < end.EuclideanNorm():
            self.start = start
            self.end = end
        
        elif start.EuclideanNorm == end.EuclideanNorm():
            if start[1] < end[1]:
                self.start = start
                self.end = end
            else:
                self.start = end
                self.end = start
        
        else:
            self.start = end
            self.end = start


        self.width = track.GetWidth()
        self.net_name = track.GetNetname()
        self.layer = track.GetLayerName()
    
    # Maybe instead of saying unit vector, just make __eq__ and see if cross product is 0
    def same_dir(self, __value: object) -> bool:
        return self.direction.Cross(__value.direction) == 0
    
    def as_drawing(self, board, layer):
        drawing = pcbnew.PCB_SHAPE(board)

        drawing.SetShape(pcbnew.SHAPE_T_SEGMENT)

        drawing.SetLayer(layer)

        drawing.SetStart(self.start)
        drawing.SetEnd(self.end)

        drawing.SetWidth(self.width)

        return drawing

    def __eq__(self, __value: object) -> bool:
        if not __value:
            return False
        
        return False or \
        (((__value.start == self.start and __value.end == self.end) or (__value.start == self.end and __value.end == self.start)) and \
        __value.width == self.width and \
        __value.layer == self.layer) 
    
    def __str__(self):
        return f"start {self.start} end {self.end}"
        
class PcbPad():
    def __init__(self, pad):
        self.position = pad.GetPosition()
        # self.size = size
        self.layer = pad.GetLayerName()
        self.polygon = pad.GetEffectivePolygon()
        # self.orientation = orientation
        self.net_name = pad.GetNetname()
        
        self.hole = None

        if pad.HasHole():
            # Creating my own polygon for a hole shape because I have to
            self.hole = self.create_hole_shape(pad.GetEffectiveHoleShape(), pad.GetDrillShape())

    def get_arc_points(self, centre, radius, start_angle, end_angle, step= 5):
        point = pcbnew.VECTOR2I(centre[0] + radius, centre[1])
        point_lst = []

        angle = start_angle

        def rotate(p, centre, angle):
            centred_p = p - centre

            angle_rad = math.radians(angle)

            x = int((centred_p[0] * math.cos(angle_rad)) + (centred_p[1] * -math.sin(angle_rad)))
            y = int((centred_p[0] * math.sin(angle_rad)) + (centred_p[1] * math.cos(angle_rad)))

            return (pcbnew.VECTOR2I(x, y) + centre)

        while angle < end_angle:
            point_lst.append(rotate(point, centre, angle))

            angle += step

        return point_lst

    def create_hole_shape(self, eff_hole_shape, shape_type):    
        point_lst = []
        diameter = None
        centre = None

        if shape_type == pcbnew.PAD_DRILL_SHAPE_CIRCLE:
            centre = eff_hole_shape.Centre()

            diameter = eff_hole_shape.GetWidth()
            radius = diameter // 2

            point_lst = self.get_arc_points(centre, radius, 0, 360)

        elif shape_type == pcbnew.PAD_DRILL_SHAPE_OBLONG:
            # Use GetSeg() to get a seg (shocker)
            # This is basically a line segment, its points represented by A and B
            # You can construct the hole by crratign a rectangle and two half circls
            pass

        hole_outline = pcbnew.SHAPE_LINE_CHAIN()

        for p in point_lst:
            hole_outline.Append(p)

        hole_poly = pcbnew.SHAPE_POLY_SET()
        hole_poly.AddOutline(hole_outline)

        hole_shape = pcbnew.PCB_SHAPE()
        hole_shape.SetShape(pcbnew.S_POLYGON)
        hole_shape.SetPolyShape(hole_poly)

        hole_shape.SetFilled(True)
        hole_shape.SetWidth(0)

        # Following line adds a hole to the pad shape, but it messes things up when exporting
        # self.polygon.AddHole(hole_outline)

        return PcbHole(hole_shape, diameter)

    def as_drawing(self, board, layer):
        drawing = pcbnew.PCB_SHAPE(board)
        drawing.SetShape(pcbnew.S_POLYGON)
        drawing.SetPolyShape(self.polygon)

        drawing.SetFilled(True)
        drawing.SetWidth(0)

        drawing.SetLayer(layer)

        return drawing
    
    def get_hole_drawing(self, board, layer):
        drawing = pcbnew.PCB_SHAPE(board)
        drawing.SetShape(pcbnew.S_POLYGON)
        drawing.SetPolyShape(self.hole_shape)

        drawing.SetFilled(True)
        drawing.SetWidth(0)

        drawing.SetLayer(layer)

        return drawing

    # TODO FIND A WAY TO COMPARE SHAPES, CAN PROBABLY JUST COMPARE ALL POINTS IN IT
    def __eq__(self, __value):
        # return (__value.position == self.position and \
        # __value.size == self.size and \
        # __value.layer == self.layer and \
        # # __value.shape == self.shape and \
        # __value.orientation == self.orientation)

        poly1 = self.polygon
        poly2 = __value.polygon

        if poly1.OutlineCount() != poly2.OutlineCount():
            return False
        
        for i in range(poly1.OutlineCount()):
            equivalent_outline = False
            for j in range(poly2.OutlineCount()):
                if poly1.Outline(i).CompareGeometry(poly2.Outline(j)):
                    equivalent_outline = True
                    break

            if not equivalent_outline:
                return False
            
        return True
        # return __value.position == self.position
        
class PcbNet():
    def __init__(self):
        self.track_lst = []
        self.pad_lst = [] 

    def add(self, component):
        if type(component) == PcbPad:
            self.pad_lst.append(component)

        elif type(component) == PcbTrack:
            self.track_lst.append(component)

    def plot(self, board, layers):
        for track in self.track_lst:
            layer = layers[track.layer]
            board.Add(track.as_drawing(board, layer))

        for pad in self.pad_lst:
            layer = layers[pad.layer]
            board.Add(pad.as_drawing(board, layer))
            
            if pad.hole:
                # board.Add(pad.get_hole_drawing(board, layers["hole"]))
                pad.hole.plot(board, layers)


    # Inefficient, Might be better to write a __hash__ and compare sets instead
    def __eq__(self, other):
        if (len(self.track_lst) != len(other.track_lst)) or (len(self.pad_lst) != len(other.pad_lst)):
            return False
        
        return all([track in other.track_lst for track in self.track_lst]) and \
                    all([pad in other.pad_lst for pad in self.pad_lst])  

class PcbHole():
    # For now, we'll only care about circular holes/
    # Need to figure out how to differentiate between plated and not plated through holes
    # Additionally, the value stored in 
    def __init__(self, hole_shape, diameter = None, position = None):
        self.shape = hole_shape
        self.diameter = diameter
        self.position = position

        if not diameter:
            self.diameter = 2 * (self.shape.GetStart() - self.shape.GetEnd()).EuclideanNorm()

        if not position:
            self.position = self.shape.GetPosition()

    def plot(self, board, layers):
        hole_layer = layers[HOLE_NAME if HOLE_NAME in layers else board.GetLayerName(pcbnew.Edge_Cuts)]
        self.shape.SetLayer(hole_layer)
        board.Add(self.shape)

    def get_drill_code(self):
        x = (self.position[0] / IU_PER_MM)
        y = (self.position[1] / IU_PER_MM)

        return f"X{x}Y{y}"

class PcbBoard():
    def __init__(self, board=None, path=None):
        
        if (not board) and (not path):
            board = pcbnew.GetBoard()

        elif not board:
            board = pcbnew.LoadBoard(path)

        self.board = board

        track_lst = filter(lambda x: type(x) == pcbnew.PCB_TRACK, board.GetTracks())
        self.track_lst = [PcbTrack(track) for track in track_lst]

        self.pad_lst = [PcbPad(pad) for pad in board.GetPads()]

        self.net_dict = dict()
        self.gnd_nets = []

        self.holes = []

        self.add_to_dict(self.track_lst)
        self.add_to_dict(self.pad_lst)
        self.add_holes()

    def get_layers(self):
        # Gets all layers and converts them to their readable names
        layer_list = [self.board.GetLayerName(layer) for layer in self.board.GetEnabledLayers().Seq()]

        return layer_list

    def add_to_dict(self, comp_list):
        for component in comp_list:
            net_name = component.net_name
            layer = component.layer

            if net_name == "GND":
                new_net = PcbNet()
                new_net.add(component)

                self.gnd_nets.append(new_net)

            else:
                if not (layer in self.net_dict):
                    self.net_dict[layer] = dict()

                if not (net_name in self.net_dict[layer]):
                    self.net_dict[layer][net_name] = PcbNet()

                self.net_dict[layer][net_name].add(component)

    def add_holes(self):      
        # Getting all the shapes on the edge cuts layer
        drawings = list(filter(lambda x: x.GetLayer() == pcbnew.Edge_Cuts, self.board.GetDrawings()))

        # However this includes the outer edge of the board
        # So let's remove the one that has the most area
        max_area = 0
        max_area_ind = 0

        for ind, d in enumerate(drawings):
            curr_area = d.GetBoundingBox().GetArea()
            if curr_area > max_area:
                max_area = curr_area
                max_area_ind = ind

        drawings.pop(max_area_ind)

        self.holes = [PcbHole(d.Duplicate()) for d in drawings]

    def compare_nets(self, old_board, selected_layers = None):

        old_net_list = old_board.gnd_nets
        write_nets = self.gnd_nets
        erase_nets = []

        if selected_layers:
            for layer in selected_layers:
                if layer in old_board.net_dict:
                    old_net_list += list(old_board.net_dict[layer].values())

                if layer in self.net_dict:
                    write_nets += list(self.net_dict[layer].values())
        else:
            for layer in old_board.net_dict.keys():
                    old_net_list += list(old_board.net_dict[layer].values())

            for layer in self.net_dict.keys():
                    write_nets += list(self.net_dict[layer].values())

        
        

        # for layer in self.net_dict.keys():
        #     old_net_list += list(self.net_dict[layer].values())

        for old_ind, old_net in enumerate(old_net_list):
            is_in_new = False

            for new_ind, new_net in enumerate(write_nets):
                if old_net == new_net:
                    is_in_new = True
                    write_nets.pop(new_ind)
                    break

            if not is_in_new:
                erase_nets.append(old_net)

        return erase_nets, write_nets

    def compare_holes(self, old_board):
        erase_holes = []
        write_holes = self.holes

        for old_hole in old_board.holes:
            is_in_new = False

            for new_ind, new_hole in enumerate(write_holes):
                if old_hole == new_hole:
                    is_in_new = True
                    write_holes.pop(new_ind)
                    break
                
            if not is_in_new:
                erase_holes.append(old_hole)

        return erase_holes, write_holes

    def plot_holes(self, hole_list, board, plot_mode):
        for hole in hole_list:
            hole.plot(board, layer_dict[plot_mode])

    def plot_nets(self, net_list, board, plot_mode):
        for net in net_list:
            net.plot(board, layer_dict[plot_mode])

    def plot_gerbers(self, board, folder_path, layer_list = None):

        if not layer_list:
            layer_list = []
            for mode in layer_dict.keys():
                for side in layer_dict[mode].keys():
                    layer_list.append((mode + "_" + side, layer_dict[mode][side]))

        plot_ctrl = pcbnew.PLOT_CONTROLLER(board)
        plot_options = plot_ctrl.GetPlotOptions()

        plot_options.SetOutputDirectory(folder_path)

        for title, layer in layer_list:
            plot_ctrl.SetLayer(layer)
            # TODO Figure out what to name them maybe pcbnew.LayerName(layer) somewhere?
            plot_ctrl.OpenPlotfile(title, pcbnew.PLOT_FORMAT_GERBER, title)
            plot_ctrl.PlotLayer()

        plot_ctrl.ClosePlot()
    
    def plot_drill(self, board, file_path, hole_lst):
        
        with open(file_path, "w") as drill_file:

            drill_file.write("M48\n")
            drill_file.write("FMAT,2\n")
            drill_file.write("METRIC\n")

            # Write tool specifications here

            drill_file.write("%") #end of header

            # Choose tool

            for hole in hole_lst:
                drill_file.write(hole.get_drill_code() + "\n")

            drill_file.write("M30") #end


    def compare_and_plot(self, old_board, selected_layers= None):
        erase_nets, write_nets = self.compare_nets(old_board, selected_layers)
        
        erase_holes, write_holes = None, None
        plot_external_holes = False
        if self.board.GetLayerName(pcbnew.Edge_Cuts) in selected_layers:
            erase_holes, write_holes = self.compare_holes(old_board)
            plot_external_holes = True
        else:
            selected_layers.append(HOLE_NAME)

        self.export_file_names = dict()

        user_layer_ind = 0
        for mode in layer_dict.keys():
            self.export_file_names[mode] = []

            for layer in selected_layers:
                layer_dict[mode][layer] = printable_layers[user_layer_ind]

                # Storing the layer name, file name, and the layer id
                self.export_file_names[mode].append((layer, mode + "_" + layer, printable_layers[user_layer_ind]))
                user_layer_ind += 1

            # # Adding a layer to plot pad holes if the edge cut layer isn't being compared
            # if not plot_external_holes:
            #     layer_dict[mode]["hole"] = printable_layers[user_layer_ind]
            #     self.export_file_names[mode].append((mode + "_" + "hole", printable_layers[user_layer_ind]))
            #     user_layer_ind += 1

        # Then we add the whole copper layers and holes of the current board
        cu_layers = self.board.GetEnabledLayers().CuStack()
        self.export_file_names[CURRENT_BOARD_EXPORT_TITLE] = []

        for layer_id in cu_layers:
            layer_name = self.board.GetLayerName(layer_id)
            self.export_file_names[CURRENT_BOARD_EXPORT_TITLE].append((layer_name, layer_name, layer_id))

        # TODO This doesn't export the pad holes
        self.export_file_names[CURRENT_BOARD_EXPORT_TITLE].append((HOLE_NAME, HOLE_NAME, pcbnew.Edge_Cuts))

        parent_folder_path = pathlib.Path(self.board.GetFileName()).parent
        self.comp_folder_path = os.path.join(parent_folder_path, "compare_result")

        if not os.path.exists(self.comp_folder_path):
            os.mkdir(self.comp_folder_path)

        plot_board_path = os.path.join(self.comp_folder_path, "comparison.kicad_pcb")

        pcbnew.IO_MGR.Save(pcbnew.IO_MGR.KICAD_SEXP, plot_board_path, self.board)

        self.plot_board = pcbnew.IO_MGR.Load(pcbnew.IO_MGR.KICAD_SEXP, plot_board_path)

        self.plot_nets(erase_nets, self.plot_board, "erase")
        self.plot_nets(write_nets, self.plot_board, "write")

        if erase_holes:
            self.plot_holes(erase_holes, self.plot_board, "erase")
            self.plot_holes(write_holes, self.plot_board, "write")
        
        # # Not working?? TODO: FIX
        # # Setting unnecessary layers to hidden so I don't have to keep hiding them each time
        # # Probably won't work
        # # Look into setting enabled layers instead of visible ones
        # vis_layers = [pcbnew.User_1, pcbnew.User_2, pcbnew.User_3, \
        #               pcbnew.User_4, pcbnew.User_5, pcbnew.User_6]

        # vis_lset = pcbnew.LSET()

        # for layer in vis_layers:
        #     vis_lset.addLayer(layer)

        # self.plot_board.SetVisibleLayers(vis_lset)

        pcbnew.IO_MGR.Save(pcbnew.IO_MGR.KICAD_SEXP, plot_board_path, self.plot_board)

        # os.system(plot_board_path)

        return self.export_file_names

    def export_files(self, file_names):
        self.plot_gerbers(self.plot_board, self.comp_folder_path, file_names)
        pass