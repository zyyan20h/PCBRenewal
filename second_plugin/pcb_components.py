import pcbnew
import math
# from .pcb_file_management import OpenFileDialog
import os
import pathlib

from .poly_comparison import ShapeCollection, as_svg

# TODO: create a parent class calles PcbComponents, and place the common functions in it

IU_PER_MM = pcbnew.PCB_IU_PER_MM

HOLE_NAME = "Holes"

CURRENT_BOARD_EXPORT_TITLE = "current board"

def rotate_point(p: pcbnew.VECTOR2I, angle: float, centre: pcbnew.VECTOR2I = pcbnew.VECTOR2I(0,0)):
            centred_p = p - centre

            angle_rad = math.radians(angle)

            x = int((centred_p[0] * math.cos(angle_rad)) + (centred_p[1] * -math.sin(angle_rad)))
            y = int((centred_p[0] * math.sin(angle_rad)) + (centred_p[1] * math.cos(angle_rad)))

            return (pcbnew.VECTOR2I(x, y) + centre)

def save_board(board):
    pcbnew.IO_MGR.Save(pcbnew.IO_MGR.KICAD_SEXP, board.GetFileName(), board)

def offset_polygon(polygon, offset):
    new_polygon = pcbnew.SHAPE_POLY_SET()
    offsetted_points = pcbnew.SHAPE_LINE_CHAIN()

    curr_points = polygon.Outline(0)

    for point in curr_points.CPoints():
        offsetted_points.Append(point + offset)

    new_polygon.AddOutline(offsetted_points)

    return new_polygon

def align_boards(new_board, old_board, corner_name=None, component=None):
    if not new_board.edge:
        new_board.set_default_edge()
    if not old_board.edge:
        old_board.set_default_edge()

    if corner_name:
        new_corner = new_board.get_corner(corner_name)
        old_corner = old_board.get_corner(corner_name)
        offset_vector = new_corner - old_corner

        if offset_vector != pcbnew.VECTOR2I(0,0):
            old_board.offset(offset_vector)
    pass    

# Will only work on the board the plugin is run on
def get_selection():
    selected_shapes = pcbnew.GetCurrentSelection()

    if not selected_shapes.empty():
        shape = selected_shapes[0]
        shape = shape.Cast()
        return shape
    
    else:
        return None

# Getting all user layers
printable_layers = list(range(pcbnew.User_1, pcbnew.User_1 + 9))

# Stores layers to be exported to
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
    
    def offset(self, offset):
        self.start += offset
        self.end += offset

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

    def offset(self, offset):
        self.position += offset
        self.polygon = offset_polygon(self.polygon, offset)
        if self.hole:
            self.hole = self.hole.offset(offset)
        pass
    
    # This initial point assumes start_angle is 0
    # Create a static function to generalize this
    def get_arc_points(self, centre, radius, start_angle, end_angle, step= 5):
        point = pcbnew.VECTOR2I(centre[0] + radius, centre[1])
        point_lst = []

        angle = start_angle

        while angle < end_angle:
            point_lst.append(rotate_point(point, angle, centre))

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
    def __init__(self, layer=None):
        self.track_lst = []
        self.pad_lst = []
        self.layer = layer

    def add(self, component):
        if type(component) == PcbPad:
            self.pad_lst.append(component)

        elif type(component) == PcbTrack:
            self.track_lst.append(component)

    def plot(self, board, layers):
        for track in self.track_lst:
            if track.layer in layers:
                layer = layers[track.layer]
                board.Add(track.as_drawing(board, layer))

        for pad in self.pad_lst:
            if pad.layer in layers:
                layer = layers[pad.layer]
                board.Add(pad.as_drawing(board, layer))
                
            if pad.hole:
                # board.Add(pad.get_hole_drawing(board, layers["hole"]))
                pad.hole.plot(board, layers)

    def offset(self, offset):
        for track in self.track_lst:
            track.offset(offset)
        for pad in self.pad_lst:
            pad.offset(offset)
        pass

    # Inefficient, Might be better to write a __hash__ and compare sets instead
    def __eq__(self, other):
        if self.layer != other.layer:
            return False

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

    def offset(self, offset):
        self.position += offset
        # self.shape = offset_polygon(self.shape.GetEffectivePolygon(), offset)

    def get_drill_code(self):
        x = (self.position[0] / IU_PER_MM)
        y = (self.position[1] / IU_PER_MM)

        return f"X{x}Y{y}"

class PcbBoard():
    # def __init__(self, board=None, path=None):
    def __init__(self, path=None):  
        if not path:
            board = pcbnew.GetBoard()
            if not board:
                return
        else:
            board = pcbnew.LoadBoard(path)

        self.board = board

        track_lst = filter(lambda x: type(x) == pcbnew.PCB_TRACK, board.GetTracks())
        self.track_lst = [PcbTrack(track) for track in track_lst]

        self.pad_lst = [PcbPad(pad) for pad in board.GetPads()]

        self.net_dict = dict()
        self.gnd_nets = []

        self.holes = []
        self.edge = get_selection()

        self.export_board = None
        self.disp_board = None

        self.path_dict = dict()

        self.add_to_dict(self.track_lst)
        self.add_to_dict(self.pad_lst)

        # So net dict is currently a dictionary of dictionaries, but I want to make it a dictionary of lists of nets
        for layer in self.net_dict.keys():
            net_list = []
            for net in self.net_dict[layer]:
                net_list.append(self.net_dict[layer][net])
            self.net_dict[layer] = net_list

        # Now adding the ground nets separately
        for net in self.gnd_nets:
            self.net_dict[net.layer].append(net)

        self.add_holes()

    def offset(self, offset):
        for track in self.track_lst:
            track.offset(offset)
        for pad in self.pad_lst:
            pad.offset(offset)
        pass

    def change_edge(self):
        new_edge = get_selection()

        if new_edge:
            self.edge = new_edge
            return new_edge.GetStart()
        
        return None

    def get_layers(self):
        # Gets all layers and converts them to their readable names
        layer_list = [self.board.GetLayerName(layer) for layer in self.board.GetEnabledLayers().Seq()]

        return layer_list

    def add_to_dict(self, comp_list):
        for component in comp_list:
            net_name = component.net_name
            layer = component.layer

            if net_name == "GND":
                new_net = PcbNet(layer)
                new_net.add(component)

                self.gnd_nets.append(new_net)

            else:
                if not (layer in self.net_dict):
                    self.net_dict[layer] = dict()

                if not (net_name in self.net_dict[layer]):
                    self.net_dict[layer][net_name] = PcbNet(layer)

                self.net_dict[layer][net_name].add(component)

    def get_corner(self, corner_name):
        topleft = self.edge.GetStart()
        botright = self.edge.GetEnd()
        corner = pcbnew.VECTOR2I(0,0)

        if "top" in corner_name:
            corner[1] = topleft[1]
        else:
            corner[1] = botright[1]

        if "left" in corner_name:
            corner[0] = topleft[0]
        else:
            corner[0] = botright[0]

        return corner
        pass

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

        if not self.edge:
            self.edge = drawings.pop(max_area_ind)

        self.holes = [PcbHole(d.Duplicate()) for d in drawings]

    def set_default_edge(self):      
        # Getting all the shapes on the edge cuts layer
        # return
        drawings = list(filter(lambda x: x.GetLayer() == pcbnew.Edge_Cuts, self.board.GetDrawings()))

        for ind, d in enumerate(drawings):
            curr_area = d.GetBoundingBox().GetArea()
            if curr_area > max_area:
                max_area = curr_area
                max_area_ind = ind

        self.edge = drawings[max_area_ind]

    def create_path_dict(self, net_dict=None, selected_layers=None):
        if not net_dict:
            net_dict = self.net_dict
        if not selected_layers:
            selected_layers = net_dict.keys()

        path_dict = dict()
        
        for layer in selected_layers:
            if layer in self.net_dict:
                path_dict[layer] = ShapeCollection(net_list=net_dict[layer])

        return path_dict

    def compare_paths(self, old_board, selected_layers=None, new_net_dict = None, old_net_dict=None):
        if not new_net_dict:
            new_path_dict = self.create_path_dict(selected_layers=selected_layers)
        else:
            new_path_dict = self.create_path_dict(net_dict=new_net_dict, selected_layers=selected_layers)

        if not old_net_dict:
            old_path_dict = old_board.create_path_dict(selected_layers=selected_layers)
        else:
            old_path_dict = self.create_path_dict(net_dict=old_net_dict, selected_layers=selected_layers)

        # path_comp_result = {"erase":dict(), "write":dict()}
        erase_path_dict = dict()
        write_path_dict = dict()

        # For each layer, compar the paths
        for layer in selected_layers:
            print(f"old path {old_path_dict}")
            if layer in old_path_dict:
                old_path = old_path_dict[layer]
                new_path = new_path_dict[layer]
                erase_path_dict[layer] = new_path.path_difference(old_path)
                write_path_dict[layer] = old_path.path_difference(new_path)

        return erase_path_dict, write_path_dict
        
    def compare_nets(self, old_board, selected_layers = None):

        # old_net_list = old_board.gnd_nets
        # write_nets = self.gnd_nets
        # erase_nets = []

        # Figure out GND nets later, turn them into a dict
        write_net_dict = dict()
        erase_net_dict = dict()

        if not selected_layers:
            selected_layers = old_board.net_dict.keys()

        for layer in selected_layers:
            # Making sure changes to these lists don't affect the originals
            old_net_list = old_board.net_dict[layer] if layer in old_board.net_dict else []
            write_net_dict[layer] = self.net_dict[layer] if layer in self.net_dict else []
            erase_net_dict[layer] = []

            for old_ind, old_net in enumerate(old_net_list):
                is_in_new = False
            
                for new_ind, new_net in enumerate(write_net_dict[layer]):
                    if old_net == new_net:
                        is_in_new = True
                        write_net_dict[layer].pop(new_ind)
                        break

                if not is_in_new:
                    erase_net_dict[layer].append(old_net)

            return erase_net_dict, write_net_dict

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

    def plot_nets(self, net_dict, board, plot_mode):
        for layer in net_dict:
            for net in net_dict[layer]:
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

    # thsi is is an old function, it isn't the one used for path comparisons
    def plot_svg(self, board, folder_path, layer_list = None):

        if not layer_list:
            layer_list = []
            for mode in layer_dict.keys():
                for layer in layer_dict[mode].keys():
                    layer_list.append((mode + "_" + layer, layer_dict[mode][layer]))

        plot_ctrl = pcbnew.PLOT_CONTROLLER(board)
        plot_options = plot_ctrl.GetPlotOptions()

        plot_options.SetOutputDirectory(folder_path)

        for title, layer in layer_list:
            plot_ctrl.SetLayer(layer)
            # TODO Figure out what to name them maybe pcbnew.LayerName(layer) somewhere?
            plot_ctrl.OpenPlotfile(title, pcbnew.PLOT_FORMAT_SVG, title)
            plot_ctrl.PlotLayer()

            plot_ctrl.SetLayer(pcbnew.Edge_Cuts)
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

    def create_board_copy(self, filename):
        print("creating board copy")
        parent_folder_path = pathlib.Path(self.board.GetFileName()).parent
        self.comp_folder_path = os.path.join(parent_folder_path, "compare_result")

        if not os.path.exists(self.comp_folder_path):
            os.mkdir(self.comp_folder_path)

        plot_board_path = os.path.join(self.comp_folder_path, f"{filename}.kicad_pcb")
        print("created path")
        # Setting unnecessary layers to hidden so I don't have to keep hiding them each time
        pcbnew.IO_MGR.Save(pcbnew.IO_MGR.KICAD_SEXP, plot_board_path, self.board)
        new_board = pcbnew.IO_MGR.Load(pcbnew.IO_MGR.KICAD_SEXP, plot_board_path)
        en_layers = []
        for mode in layer_dict.keys():
            en_layers += layer_dict[mode].values()
        
        en_layers.append(pcbnew.Edge_Cuts)

        en_lset = pcbnew.LSET()

        for layer in en_layers:
            en_lset.addLayer(layer)

        new_board.SetEnabledLayers(en_lset)

        pcbnew.IO_MGR.Save(pcbnew.IO_MGR.KICAD_SEXP, plot_board_path, self.board)

        return new_board

    def plot_paths(self, path_dict, layer_dict, plot_board, mode):
        for layer in path_dict:
            path_dict[layer].plot_in_kicad(plot_board, layer_dict[mode][layer])
            path_dict[layer].export_path(self, os.path.join(self.comp_folder_path, f"{mode}_{layer}.svg"))

    def compare_and_plot(self, old_board, selected_layers= None, compare_paths="component"):
        print(f"start of comparinf, method is {compare_paths}")
        erase_holes, write_holes = None, None
        plot_external_holes = False
        if self.board.GetLayerName(pcbnew.Edge_Cuts) in selected_layers:
            erase_holes, write_holes = self.compare_holes(old_board)
            plot_external_holes = True  
        else:
            selected_layers.append(HOLE_NAME)
            pass

        # Assigning each erase and write layer to be exported to a user layer in the plot file
        user_layer_ind = 0
        for mode in layer_dict.keys():
            layer_dict[mode] = dict()

            for layer in selected_layers:
                layer_dict[mode][layer] = printable_layers[user_layer_ind]
                user_layer_ind += 1
        print("layer dict created")

        print(f"selected layers are {selected_layers}")
        print("hoels created")
        if compare_paths == "line":
            erase_paths, write_paths = self.compare_paths(old_board=old_board, selected_layers=selected_layers)
            self.disp_board = self.create_board_copy("comparison")
            self.export_board = self.disp_board

            self.plot_paths(erase_paths, layer_dict, self.disp_board, "erase")
            self.plot_paths(write_paths, layer_dict, self.disp_board, "write")

        elif compare_paths == "component":
            print("about to compare components")         
            erase_nets, write_nets = self.compare_nets(old_board, selected_layers)
            print("finished comparing")
            self.disp_board = self.create_board_copy("comparison")
            self.export_board = self.create_board_copy("export")
            print("created boards")
            # Plotting the nets on the board from which gerbers will be exported
            self.plot_nets(erase_nets, self.export_board, "erase")
            self.plot_nets(write_nets, self.export_board, "write")
    
            # Getting the drill paths of the components that differ between boards
            erase_paths = self.create_path_dict(erase_nets, selected_layers)
            write_paths = self.create_path_dict(write_nets, selected_layers)

            # Plotting them on the boards that will be displayed to the user
            self.plot_paths(erase_paths, layer_dict, self.disp_board, "erase")
            self.plot_paths(write_paths, layer_dict, self.disp_board, "write")

        elif compare_paths == "hybrid":
            print("hybird")
            erase_nets, write_nets = self.compare_nets(old_board, selected_layers)
            self.disp_board = self.create_board_copy("comparison")
            self.export_board = self.disp_board

            # Comparing those paths
            erase_paths, write_paths = self.compare_paths(old_board=old_board, selected_layers=selected_layers, \
                                                          new_net_dict=write_nets, old_net_dict=erase_nets)

            # Plotting them on the boards that will be displayed to the user
            self.plot_paths(erase_paths, layer_dict, self.disp_board, "erase")
            self.plot_paths(write_paths, layer_dict, self.disp_board, "write")

        if erase_holes:
            self.plot_holes(erase_holes, self.export_board, "erase")
            self.plot_holes(write_holes, self.export_board, "write")

        save_board(self.disp_board)
        save_board(self.export_board)
        layer_pngs = None
        return layer_pngs

    def path_svg(self, net_list, name):
        col = ShapeCollection(net_list=net_list)
        as_svg(col.combined_net_paths, os.path.join(self.comp_folder_path, name))

        return col

    def open_disp_board(self):
        if self.disp_board:
            os.startfile(self.disp_board.GetFileName())

    def export_files(self, file_names=None, use_original=False):
        # Go through the layer dict and export each layer as a gerber

        # self.plot_gerbers(self.export_board, self.comp_folder_path, file_names)
        self.plot_svg(self.export_board, self.comp_folder_path)
        
        pass