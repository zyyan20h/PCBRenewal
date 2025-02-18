import pcbnew
import math
# from .pcb_file_management import OpenFileDialog
import os
import pathlib

from .poly_comparison import NetCollection, EdgeCollection, convert_to_mm_coords, get_warnings

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

def get_offset(new_board, old_board, old_edge_ind=-1, new_edge_ind=-1, corner_name=None, 
                 old_component_ind=-1, new_component_ind=-1):

    offset_vector = pcbnew.VECTOR2I(0,0)
    # print(f"dealing with components {old_component_ind} and {new_component_ind}")

    if corner_name:
        new_edge = new_board.edge_cut_shapes[new_edge_ind]
        old_edge = old_board.edge_cut_shapes[old_edge_ind]
        new_corner = new_board.get_corner(corner_name, new_edge)
        old_corner = old_board.get_corner(corner_name, old_edge)
        offset_vector = new_corner - old_corner

    elif old_component_ind >= 0 and new_component_ind >= 0:
        _, new_pos, new_component = new_board.footprint_names[new_component_ind]
        _, old_pos, old_component = old_board.footprint_names[old_component_ind]
        offset_vector = new_pos - old_pos
        pass
    
    return offset_vector

def get_arc_points(centre, radius, start_angle, end_angle, step= 5):
        point = pcbnew.VECTOR2I(centre[0] + radius, centre[1])
        point_lst = []

        angle = start_angle

        while angle < end_angle:
            point_lst.append(rotate_point(point, angle, centre))

            angle += step

        return point_lst

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
    def __init__(self, pad, position=None, layer=None, polygon=None, net_name=None):
        self.hole = None
        
        if pad:    
            self.position = pad.GetPosition()
            self.layer = pad.GetParentFootprint().GetLayerName()
            self.polygon = pad.GetEffectivePolygon()
            self.net_name = pad.GetNetname()

            if pad.HasHole():
                # Creating my own polygon for a hole shape because I have to
                self.hole = self.create_hole_shape(pad.GetEffectiveHoleShape(), pad.GetDrillShape())
        else:
            self.position = position
            self.layer = layer
            self.polygon = polygon
            self.net_name = net_name

        self.poly_points = None

        if self.polygon.OutlineCount() > 0:
            line_chain = self.polygon.Outline(0)
            self.poly_points = [ p for p in line_chain.CPoints()]
        # self.orientation = orientation   

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

class PcbVia():
    def __init__(self, via):
        self.position = via.GetPosition()
        # Diameter of the hole in the centre
        self.drill = via.GetDrill()

        # Outer circle of copper around the hole
        self.annulus = via.GetWidth()
        self.net_name = via.GetNetname()

        self.hole_shape = self.create_hole_shape()
    # Doing duplicate things
    def create_hole_shape(self, board=None, mode=None):
        # Offsetting diameter by 0.1
        radius = (self.drill // 2) + int(0.05 * IU_PER_MM) if mode == "erase" else (self.drill // 2)
        hole_point_lst = get_arc_points(self.position, radius, 0, 360)

        hole_outline = pcbnew.SHAPE_LINE_CHAIN()

        for p in hole_point_lst:
            hole_outline.Append(p)

        hole_poly = pcbnew.SHAPE_POLY_SET()
        hole_poly.AddOutline(hole_outline)

        if board:
            hole_shape = pcbnew.PCB_SHAPE(board)
            hole_shape.SetShape(pcbnew.S_POLYGON)
            hole_shape.SetPolyShape(hole_poly)

        else:
            hole_shape = pcbnew.PCB_SHAPE()
            hole_shape.SetShape(pcbnew.S_POLYGON)
            hole_shape.SetPolyShape(hole_poly)

        hole_shape.SetFilled(False)
        hole_shape.SetWidth(100000)

        return hole_shape

    def set_as_erase(self):
        self.hole_shape = self.create_hole_shape(mode="erase")

    def offset(self, offset_vec):
        self.position -= offset_vec
        self.hole_shape.SetPolyShape(offset_polygon(self.hole_shape.GetPolyShape(), offset_vec))
        pass
    
    # Use hole_shape to get points instead of creating polygon again
    def get_pads(self):
        annulus_point_lst = get_arc_points(self.position, self.annulus // 2, 0, 360)

        annulus_outline = pcbnew.SHAPE_LINE_CHAIN()

        for p in annulus_point_lst:
            annulus_outline.Append(p)

        polygon = pcbnew.SHAPE_POLY_SET()
        polygon.AddOutline(annulus_outline)


        return [PcbPad(None, self.position, "F.Cu", polygon, self.net_name), \
                    PcbPad(None, self.position, "B.Cu", polygon, self.net_name)]
        pass

    def plot(self, board):
        # shape = self.create_hole_shape(board)
        shape = self.hole_shape
        shape.SetLayer(pcbnew.Edge_Cuts)
        board.Add(shape)
        pass

    def __eq__(self, other):
        return (other != None) and (self.position == other.position) and (self.drill == other.drill)

class PcbBoard():
    def __init__(self, path=None):  
        self.is_valid = True
        
        if not path:
            board = pcbnew.GetBoard()
            # print("board in pcbboard:", board)
            if not board:
                self.is_valid = False
                return
        else:
            board = pcbnew.LoadBoard(path)
        self.board = board
        
        self.track_lst = []
        self.via_list = []

        for t in board.GetTracks():
            if type(t) == pcbnew.PCB_TRACK:
                self.track_lst.append(PcbTrack(t))
            elif type(t) == pcbnew.PCB_VIA:
                self.via_list.append(PcbVia(t))

        self.pad_lst = [PcbPad(pad) for pad in board.GetPads()]

        for via in self.via_list:
            self.pad_lst += via.get_pads()

        self.net_dict = dict()
        self.gnd_nets = []

        self.footprint_names = [(f.GetFPIDAsString(), f.GetPosition(), f) for f in board.GetFootprints()]
        self.offset_vec = pcbnew.VECTOR2I(0,0)

        self.holes = []
        self.edge_cut_shapes = None

        self.export_board = None
        self.disp_board = None

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

        self.path_dict = self.create_path_dict()

        self.add_holes()

        self.edge = EdgeCollection(self.edge_cut_shapes, self)
        self.edge.add_via_holes(self.via_list)

    def offset(self, offset):
        if offset == pcbnew.VECTOR2I(0,0):
            return
        
        self.offset_vec += offset
        for track in self.track_lst:
            track.offset(offset)
        for pad in self.pad_lst:
            pad.offset(offset)
        for via in self.via_list:
            via.offset(offset)

        self.edge_cut_shapes = [(name, start + offset, end + offset, edge) for (name, start, end, edge) in self.edge_cut_shapes]
        self.footprint_names = [(name, pos + offset, f) for (name, pos, f) in self.footprint_names]
        self.edge.offset(offset=offset)
        print("updated offsets and footprint positions")
        pass

    def reset_offset(self):
        self.offset(-self.offset_vec)

    def change_edge(self):
        new_edge = get_selection()

        if new_edge:
            self.edge = new_edge
            return new_edge.GetStart()
        
        return None

    def get_cu_layers(self):
        # Gets all copper layers and converts them to their readable names
        # layer_list = [self.board.GetLayerName(layer) for layer in self.board.GetEnabledLayers().Seq()]
        layer_list = [self.board.GetLayerName(layer) for layer in self.board.GetEnabledLayers().CuStack()]

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

    def get_corner(self, corner_name, edge_shape=None):
        if edge_shape:
            _, topleft, botright, edge = edge_shape
            # Trying to align with bounding box instead of othe rstuff
            bb = edge.GetBoundingBox()
            topleft = pcbnew.VECTOR2I(bb.GetLeft(), bb.GetTop()) + self.offset_vec
            botright = pcbnew.VECTOR2I(bb.GetRight(), bb.GetBottom()) + self.offset_vec
        else:
            topleft = self.edge.GetStart()
            botright = self.edge.GetEnd()

        corner = pcbnew.VECTOR2I(0,0)

        if "Top" in corner_name:
            corner[1] = topleft[1]
        else:
            corner[1] = botright[1]

        if "Left" in corner_name:
            corner[0] = topleft[0]
        else:
            corner[0] = botright[0]
        # print(corner_name, corner)
        return corner
        pass

    def add_holes(self):      
        # Getting all the shapes on the edge cuts layer
        drawings = list(filter(lambda x: x.GetLayer() == pcbnew.Edge_Cuts, self.board.GetDrawings()))
        self.edge_cut_shapes = [(d.GetShapeStr(), d.GetStart(), d.GetEnd(), d) for d in drawings]
        # However this includes the outer edge of the board
        # So let's remove the one that has the most area
        max_area = 0
        max_area_ind = 0

        for ind, d in enumerate(drawings):
            curr_area = d.GetBoundingBox().GetArea()
            if curr_area > max_area:
                max_area = curr_area
                max_area_ind = ind

        # if not self.edge:
        #     self.edge = drawings.pop(max_area_ind)

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
            if layer in net_dict:
                path_dict[layer] = NetCollection(net_list=net_dict[layer], layer=layer)
        
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
            if layer in old_path_dict:
                old_path = old_path_dict[layer]
                new_path = new_path_dict[layer]
                erase_path_dict[layer] = old_path.path_difference(new_path)
                write_path_dict[layer] = new_path.path_difference(old_path)

        return erase_path_dict, write_path_dict
        
    def compare_nets(self, old_board, selected_layers = None):
        write_net_dict = dict()
        erase_net_dict = dict()

        if not selected_layers:
            selected_layers = old_board.net_dict.keys()

        for layer in selected_layers:
            print("net layer comparing", layer)
            # Making sure changes to these lists don't affect the originals
            old_net_list = old_board.net_dict[layer].copy() if layer in old_board.net_dict else []
            write_net_dict[layer] = self.net_dict[layer].copy() if layer in self.net_dict else []
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

    def compare_edges(self, old_board):
        new_edges =  self.edge # EdgeCollection(self.edge_cut_shapes, self)
        old_edges = old_board.edge # EdgeCollection(old_board.edge_cut_shapes, old_board)

        erase_edges = old_edges.edge_difference(new_edges)
        write_edges = new_edges.edge_difference(old_edges)
        return erase_edges, write_edges
    
    def compare_vias(self, old_board):
        new_vias = self.via_list
        old_vias = old_board.via_list

        erase_vias = []
        write_vias = new_vias.copy()

        for old_via in old_vias:
            is_in_new = False
            
            for new_ind, new_via in enumerate(write_vias):
                if old_via == new_via:
                    is_in_new = True
                    write_vias.pop(new_ind)
                    break

            if not is_in_new:
                erase_vias.append(old_via)

        return erase_vias, write_vias
        

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

    def plot_via_holes(self, via_list, board):
        for via in via_list:
            via.plot(board)
        pass

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
    
    def export_drill(self, board, file_path):
        # https://gist.github.com/aster94/bd52972ab6dbf13a44fc046b4222f7e7
        drill_writer = pcbnew.EXCELLON_WRITER(board)

        DRILL_FILE = True
        MAP_FILE = False
        REPORTER = None # Not really sure what this is
        drill_writer.CreateDrillandMapFilesSet(file_path, DRILL_FILE, MAP_FILE, REPORTER)

        pass

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

    def plot_paths(self, path_dict, layer_dict, board, plot_board, mode, subtract_path_dict=None):
        for layer in path_dict:

            path = path_dict[layer]

            path.plot_in_kicad(plot_board, layer_dict[mode][layer])
            
            if subtract_path_dict and layer in subtract_path_dict:
                path = path_dict[layer].path_difference(subtract_path_dict[layer])

            path.export_path(board, os.path.join(self.comp_folder_path, f"{mode}_{layer}.svg"),
                             is_stencil=(mode=="erase"))

    def get_warnings(self, old_board):
        polgyon_dict = get_warnings(self.path_dict, self.edge, old_board.edge, self.via_list)
        return polgyon_dict
        pass

    def compare_and_plot(self, old_board, selected_layers= None, compare_paths="component"):
        print(f"start of comparing, method is {compare_paths}")
        erase_holes, write_holes = None, None

        # Assigning each erase and write layer to be exported to a user layer in the plot file
        user_layer_ind = 0
        for mode in layer_dict.keys():
            layer_dict[mode] = dict()

            for layer in selected_layers:
                layer_dict[mode][layer] = printable_layers[user_layer_ind]
                user_layer_ind += 1
        print("layer dict created")

        print(f"selected layers are {selected_layers}")

        if compare_paths == "line":
            erase_paths, write_paths = self.compare_paths(old_board=old_board, selected_layers=selected_layers)
            self.disp_board = self.create_board_copy("comparison")
            self.export_board = self.disp_board

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

        elif compare_paths == "hybrid":
            # print("hybrid")
            erase_nets, write_nets = self.compare_nets(old_board, selected_layers)
            self.disp_board = self.create_board_copy("comparison")
            self.export_board = self.disp_board
            print("net keys", self.net_dict.keys(), old_board.net_dict.keys())
            # Comparing those paths
            erase_paths, write_paths = self.compare_paths(old_board=old_board, selected_layers=selected_layers, \
                                                          new_net_dict=write_nets, old_net_dict=erase_nets)

        erase_vias, write_vias = self.compare_vias(old_board)
        for via in erase_vias:
            via.set_as_erase()
        # print(f"vias {erase_vias}")
        self.plot_via_holes(erase_vias, self.export_board)
        self.plot_via_holes(write_vias, self.export_board)
        
        self.edge.add_via_holes(erase_vias)

        self.plot_paths(path_dict=erase_paths, layer_dict=layer_dict, 
                            board=old_board, plot_board=self.disp_board, mode="erase")
            
        self.plot_paths(path_dict=write_paths, layer_dict=layer_dict, 
                            board=self,plot_board=self.disp_board, mode="write")

        if erase_holes:
            self.plot_holes(erase_holes, self.export_board, "erase")
            self.plot_holes(write_holes, self.export_board, "write")

        save_board(self.disp_board)
        save_board(self.export_board)

        erase_edges, write_edges = self.compare_edges(old_board)

        # adding vias to the write_edges:
        write_edges.add_via_holes(erase_vias)

        erase_edges.export_edge(old_board, os.path.join(self.comp_folder_path, "erase_Edge.Cuts.svg"))
        write_edges.export_edge(self, os.path.join(self.comp_folder_path, "write_Edge.Cuts.svg"))\
        
        self.edge.export_edge(self, os.path.join(self.comp_folder_path, "test.svg"))

        self.export_drill(self.export_board, self.comp_folder_path)

        self.export_overwrite(erase_paths, write_paths)

        self.plot_gerbers(self.export_board, self.comp_folder_path, [("Edge.Cuts", pcbnew.Edge_Cuts)])
        
        # print("Just checking the back layer is compared")
        # print(erase_paths.keys())

        return erase_paths, erase_edges, write_paths, write_edges

    def export_overwrite(self, erase_paths, write_paths):
        overwrite_dict = dict()

        new_path_dict = self.create_path_dict(selected_layers=write_paths.keys())

        print("\nOverwrite Calc\n")

        for layer in write_paths:
            if layer not in new_path_dict:
                continue
            n = new_path_dict[layer].polygonize_paths()
            e = erase_paths[layer].polygonize_paths()
            w = write_paths[layer].polygonize_paths()

            ow = e.intersection(n.difference(w))

            filename = os.path.join(self.comp_folder_path, f"overwrite_{layer}.svg")

            bb_width, bb_height, shape = convert_to_mm_coords(ow, self)

            with open(filename, "w") as svg_file:
                svg_text =  f'''<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {bb_width} {bb_height}\" width=\"{bb_width}mm\" height=\"{bb_height}mm\">
                    <g stroke-linecap=\"round\">
                        {shape.svg(scale_factor=0)} 
                    </g>
                    </svg>'''
                svg_file.write(svg_text)

        pass

    def open_disp_board(self):
        if self.disp_board:
            os.startfile(self.disp_board.GetFileName())

    def export_files(self, file_names=None, use_original=False):
        # Go through the layer dict and export each layer as a gerber

        # self.plot_gerbers(self.export_board, self.comp_folder_path, file_names)
        self.plot_svg(self.export_board, self.comp_folder_path)
        pass