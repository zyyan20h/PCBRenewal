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

layer_dict = {
    "erase": {
        "front": ERASE_F_CU_LAYER,
        "back" : ERASE_B_CU_LAYER,
        "hole" : ERASE_HOLE_LAYER,
    },

    "write": {
        "front": WRITE_F_CU_LAYER,
        "back" : WRITE_B_CU_LAYER,
        "hole" : WRITE_HOLE_LAYER,
    }
}

class PcbTrack():    
    def __init__(self, start, end, width, direction, layer, net_name):

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


        self.width = width
        self.net_name = net_name

        # Scrapped below unit vector method because unit vector didn't seem to be what I expected it to be
        # When testing in the python shell
        """    
        # Unit vector pointing in the direction of it
        # Y component will always be positive as a convention
        self.direction = direction 
        """

        self.direction = direction

        # The layer it's on
        # e.g. front or back
        self.layer = layer
    
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

    def has_zero_length(self):
        return self.start == self.end
        #return False

    def __eq__(self, __value: object) -> bool:
        # print(__value.__dict__) if __value else __value
        # print(self.__dict__)
        # return __value == None or \
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
        
        self.hole_shape = None

        if pad.HasHole():
            # Creating my own polygon for a hole shape because I have to
            self.create_hole_shape(pad.GetEffectiveHoleShape(), pad.GetDrillShape())

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

        if shape_type == pcbnew.PAD_DRILL_SHAPE_CIRCLE:
            centre = eff_hole_shape.Centre()

            radius = eff_hole_shape.GetWidth() // 2

            point_lst = self.get_arc_points(centre, radius, 0, 360)

        elif shape_type == pcbnew.PAD_DRILL_SHAPE_OBLONG:
            # Use GetSeg() to get a seg (shocker)
            # This is basically a line segment, its points represented by A and B
            # You can construct the hole by crratign a rectangle and two half circls
            pass

        hole_outline = pcbnew.SHAPE_LINE_CHAIN()

        for p in point_lst:
            hole_outline.Append(p)

        self.hole_shape = pcbnew.SHAPE_POLY_SET()
        self.hole_shape.AddOutline(hole_outline)

        # self.polygon = self.hole_shape
        self.polygon.AddHole(hole_outline)

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
        
class PcbPadList():
    def __init__(self):
        self.front_pad_list = []
        self.back_pad_list = []

    def all(self):
        return self.front_pad_list + self.back_pad_list

    def add_to_list(self, board):
        pad_lst = board.GetPads()

        for pad in pad_lst:
            new_pad = PcbPad(pad)

            if new_pad.layer == "F.Cu":
                self.front_pad_list.append(new_pad)
            else:
                self.back_pad_list.append(new_pad)

    def compare_pads(self, old_pad_lst):
        erase_pad_lst = PcbPadList()    

        write_pad_lst = PcbPadList()
        write_pad_lst.front_pad_list = self.front_pad_list
        write_pad_lst.back_pad_list = self.back_pad_list

        for old_ind, old_pad in enumerate(old_pad_lst.front_pad_list):
            is_in_new = False

            for new_ind, new_pad in enumerate(self.front_pad_list):
                
                # print(f"old {str(old_pad)}\nnew {str(new_pad)}\n {old_pad == new_pad}\n")
                if old_pad == new_pad:
                    is_in_new = True
                    write_pad_lst.front_pad_list.pop(new_ind)
                    break

            if not is_in_new:
                erase_pad_lst.front_pad_list.append(old_pad)

        for old_ind, old_pad in enumerate(old_pad_lst.back_pad_list):
            is_in_new = False

            for new_ind, new_pad in enumerate(self.back_pad_list):

                if old_pad == new_pad:
                    is_in_new = True
                    write_pad_lst.back_pad_list.pop(new_ind)
                    break

            if not is_in_new:
                erase_pad_lst.back_pad_list.append(old_pad)
                
        return (erase_pad_lst, write_pad_lst)

    def plot_in_kicad(self, board, front_layer, back_layer):
        
        def get_new_pad(pad, side):
            new_pad = pcbnew.PCB_SHAPE(board)

            new_pad.SetShape(pcbnew.S_POLYGON)
            new_pad.SetPolyShape(pad.polygon)

            # new_pad.SetPosition(pad.position)

            # x_offset = int(pad.size[0] / 2)
            # y_offset = int(pad.size[1] / 2)

            # # start and end are the top left and bottom right corners of the rectangle
            # # This method only works with plain old rectangles until I can figure out how to work with other shapes
            # # When I tried getting the shape from a more rounded rectangular pad, it returned SH_SHAPE
            # # And when I tried to set
            # new_start = pcbnew.VECTOR2I(pad.position[0] - x_offset, pad.position[1] - y_offset)
            # new_end = pcbnew.VECTOR2I(pad.position[0] + x_offset, pad.position[1] + y_offset)

            # new_pad.SetStart(new_start)
            # new_pad.SetEnd(new_end)

            new_pad.SetFilled(True)
            new_pad.SetWidth
            # new_pad.Rotate(pad.position, pad.orientation)

            new_pad.SetLayer(front_layer if side == "front" else back_layer)
            

            return new_pad

        for pad in self.front_pad_list:
            board.Add(get_new_pad(pad, "front"))

        for pad in self.back_pad_list:
            board.Add(get_new_pad(pad, "back"))    

class PcbTrackList():    
    def __init__(self):
        self.front_track_list = []
        self.back_track_list = []
    
    # Clears the front and back list
    def clear_lists(self):
        self.front_track_list = []
        self.back_track_list = []

    def all(self):
        return self.front_track_list + self.back_track_list

    # Takes in board object and adds PcbTrack objects to the list
    def add_to_list(self, board):
        conn_lst = board.GetTracks()

        for conn in conn_lst:
            if type(conn) == pcbnew.PCB_TRACK:
                tr_st = conn.GetStart()
                tr_en = conn.GetEnd()
                tr_dr = (tr_st - tr_en) / (tr_st - tr_en).EuclideanNorm()
                
                tr_wd = conn.GetWidth()

                # We want the Y component to be positive
                # So I'm negating it if it's negative
                tr_dr = -tr_dr if tr_dr[1] < 0 else tr_dr

                tr_ly = conn.GetLayerName()

                new_track = PcbTrack(tr_st, tr_en, tr_wd, tr_dr, tr_ly, conn.GetNetname())

                if tr_ly == "F.Cu":
                    self.front_track_list.append(new_track)
                else:
                    self.back_track_list.append(new_track)

    fignum = 0

    #(erase, keep, write)
    # BIG PROBLEM, SOMETIMES A SINGLE LINE CAN BE 2 TRACKS, YOU NEED TO ACCOUNT FOR THAT
    # AND ALSO IF THERE ARE MULTIPLE NEW TRACKS ON A SINGLE OLD TRACK
    # POSSIBLE SOLUTION: RUN THE SAME OVERLAPPING ALGORITHM ON THE ERASE TRACKS AND KEEP TRACKS
    # THATS DUMB
    # Instead, update the old list with the subtracted tracks
    @staticmethod
    def overlaps(old_track, new_track):  

        def area_of_triangle(p1, p2, p3):
            return (p1.x * (p2.y - p3.y)) + (p2.x * (p3.y - p1.y)) + (p3.x * (p1.y - p2.y))

        def is_on_track(point, track):
            # TO DO: FIX THIS
            # Maybe to simplify this, we could make the end x always be greater than start x
            # by convention
            # Might not even need the first 4 lines
            return (track.start[0] <= point.x and point.x <= track.end[0] or \
                    track.end[0] <= point.x and point.x <= track.start[0] ) and \
                   (track.start[1] <= point.y and point.y <= track.end[1] or \
                    track.end[1] <= point.y and point.y <= track.start[1]) and \
                    area_of_triangle(point, track.start, track.end) == 0

        # Track to be erased, Track to be kept, Track to be written
        ret_tuple = (None, None, None)

        new_start_on_old = is_on_track(new_track.start, old_track)
        new_end_on_old = is_on_track(new_track.end, old_track)
        old_start_on_new = is_on_track(old_track.start, new_track)
        old_end_on_new = is_on_track(old_track.end, new_track)

            

        direction_vector = (new_track.start - new_track.end)

        # If the new track is completely within the old one
        if new_start_on_old and new_end_on_old:
            # pg.set_fig_name(f"Tracks {PcbTrackList.fignum}")
            # pg.plot_track(old_track.start, old_track.end, new_track.layer)
            # pg.plot_track(new_track.end, new_track.start, new_track.layer)
            # pg.show_plot()
            PcbTrackList.fignum += 1
            if direction_vector.Dot(new_track.start - old_track.end) > 0:
                # OE------NE NE------NS NS------OS
                
                ret_tuple = ([PcbTrack(old_track.end, new_track.end, new_track.width, new_track.direction, new_track.layer), \
                              PcbTrack(new_track.start, old_track.start,  new_track.width, new_track.direction, new_track.layer)], \
                              new_track, \
                              None)
            else:
                # OS------NE NE------NS NS------OE
                
                ret_tuple = ([PcbTrack(old_track.start, new_track.end, new_track.width, new_track.direction, new_track.layer), \
                              PcbTrack(new_track.start, old_track.end, new_track.width, new_track.direction, new_track.layer)], \
                              new_track, \
                              None)
                              
                
        # If the old track is completely withm the new one
        elif old_start_on_new and old_end_on_new:

            direction_vector = (old_track.start - old_track.end)
            if direction_vector.Dot(old_track.start - new_track.end) > 0:
                # NE------OE OE------OS OS------NS
                ret_tuple = (None, \
                             old_track, \
                             [PcbTrack(new_track.end, old_track.end, new_track.width, direction_vector, new_track.layer), \
                              PcbTrack(old_track.start, new_track.start, new_track.width, direction_vector, new_track.layer)])

            else:
                # NS------OE OE------OS OS------NE
                ret_tuple = (None, \
                             old_track, \
                             [PcbTrack(new_track.start, old_track.end, new_track.width, direction_vector, new_track.layer), \
                              PcbTrack(old_track.start, new_track.end, new_track.width, direction_vector, new_track.layer)])                



        # Following code can probably be combined and generalised
        
        # If the start of the new track overlaps the old one
        elif new_start_on_old:
            # Track to be erased, Track to be kept, Track to be written
        
            if old_start_on_new:
                # If the old track's start is on the new track
                ret_tuple = (PcbTrack(new_track.start, old_track.end, new_track.width, direction_vector, new_track.layer), \
                             PcbTrack(new_track.start, old_track.start, new_track.width, direction_vector, new_track.layer), \
                             PcbTrack(old_track.start, new_track.end, new_track.width, direction_vector, new_track.layer) )
            else:
                # If the old track's end is on the new track
                ret_tuple = (PcbTrack(new_track.start, old_track.start, new_track.width, direction_vector, new_track.layer), \
                             PcbTrack(new_track.start, old_track.end, new_track.width, direction_vector, new_track.layer), \
                             PcbTrack(old_track.end, new_track.end, new_track.width, direction_vector, new_track.layer) )
        

        #If the end of the new track overlaps the old one
        elif new_end_on_old:
            # Track to be erased, Track to be kept, Track to be written

            if old_start_on_new:
                # If the old track's start is on the new track
                # OE------NE NE------OS OS------NS  
                ret_tuple = (PcbTrack(old_track.end, new_track.end, new_track.width, direction_vector, new_track.layer), \
                             PcbTrack(new_track.end, old_track.start, new_track.width, direction_vector, new_track.layer), \
                             PcbTrack(old_track.start, new_track.start, new_track.width, direction_vector, new_track.layer) )
            else:
                # If the old track's end is on the new track
                # OS------NE NE------OE OE------NS  
                ret_tuple = (PcbTrack(old_track.start, new_track.end, new_track.width, direction_vector, new_track.layer), \
                             PcbTrack(new_track.end, old_track.start, new_track.width, direction_vector, new_track.layer), \
                             PcbTrack(old_track.end, new_track.start, new_track.width, direction_vector, new_track.layer) )
        
        return ret_tuple


    @staticmethod
    def track_subtract(old_lst, new_lst):
        erase_lst = []
        keep_lst = []
        write_lst = []

        old_overlap_lst = [False for i in range(len(old_lst))]
        new_overlap_lst = [False for i in range(len(new_lst))]

        for old_index, old_track in enumerate(old_lst):
            for new_index, new_track in enumerate(new_lst):

                if old_track.same_dir(new_track) :
                    # TO DO: MAKE THIS BIT LESS UGLY

                    

                    tracks_tuple = PcbTrackList.overlaps(old_track= old_track, new_track= new_track)

                    if tracks_tuple != (None, None, None):
                        old_overlap_lst[old_index] = True
                        new_overlap_lst[new_index] = True

                    if tracks_tuple[0] != None:
                        erase_lst = erase_lst + tracks_tuple[0] if type(tracks_tuple[0]) == list else erase_lst + [tracks_tuple[0]]

                    if tracks_tuple[1] != None:
                        keep_lst = keep_lst + tracks_tuple[1] if type(tracks_tuple[1]) == list else keep_lst + [tracks_tuple[1]]
                    
                    if tracks_tuple[2] != None:
                        write_lst = write_lst + tracks_tuple[2] if type(tracks_tuple[2]) == list else write_lst + [tracks_tuple[2]]
                
        
        for old_index, old_overlap in enumerate(old_overlap_lst):
            if not old_overlap:
                erase_lst.append(old_lst[old_index])

        for new_index, new_overlap in enumerate(new_overlap_lst):
            if not new_overlap:
                write_lst.append(new_lst[new_index])
                
        

        remove_bad_tracks = lambda a: not a.has_zero_length()

        return (filter(remove_bad_tracks, erase_lst), filter(remove_bad_tracks, keep_lst), filter(remove_bad_tracks, write_lst))


    # def compare_tracks(self, new_board_lst):
    #     old_flist = self.front_track_list
    #     old_blist = self.back_track_list

    #     new_flist = new_board_lst.front_track_list
    #     new_blist = new_board_lst.back_track_list

    #     erase_pcb_lst = PcbTrackList()
    #     keep_pcb_lst = PcbTrackList()
    #     write_pcb_lst = PcbTrackList()

    #     sub_tracks_tuple = PcbTrackList.track_subtract(old_lst=old_flist, new_lst=new_flist)

    #     erase_pcb_lst.front_track_list = sub_tracks_tuple[0]
    #     keep_pcb_lst.front_track_list = sub_tracks_tuple[1]
    #     write_pcb_lst.front_track_list = sub_tracks_tuple[2]

    #     sub_tracks_tuple = PcbTrackList.track_subtract(old_lst=old_blist, new_lst=new_blist)

    #     erase_pcb_lst.back_track_list = sub_tracks_tuple[0]
    #     keep_pcb_lst.back_track_list = sub_tracks_tuple[1]
    #     write_pcb_lst.back_track_list = sub_tracks_tuple[2]

    #     return (erase_pcb_lst, keep_pcb_lst, write_pcb_lst)

    def compare_tracks(self, old_track_lst):

        erase_track_lst = PcbTrackList()    

        write_track_lst = PcbTrackList()
        write_track_lst.front_track_list = self.front_track_list
        write_track_lst.back_track_list = self.back_track_list

        for old_ind, old_track in enumerate(old_track_lst.front_track_list):
            is_in_new = False

            for new_ind, new_track in enumerate(self.front_track_list):
                
                # print(f"old {str(old_track)}\nnew {str(new_track)}\n {old_track == new_track}\n")
                if old_track == new_track:
                    is_in_new = True
                    write_track_lst.front_track_list.pop(new_ind)
                    break

            if not is_in_new:
                erase_track_lst.front_track_list.append(old_track)

        for old_ind, old_track in enumerate(old_track_lst.back_track_list):
            is_in_new = False

            for new_ind, new_track in enumerate(self.back_track_list):

                if old_track == new_track:
                    is_in_new = True
                    write_track_lst.back_track_list.pop(new_ind)
                    break

            if not is_in_new:
                erase_track_lst.back_track_list.append(old_track)
                

        return (erase_track_lst, write_track_lst)

    def graph_lists(self, axes):
        for track in self.front_track_list:
            pg.plot_track(track.start, track.end, track.layer, axes= axes)

        for track in self.back_track_list:
            pg.plot_track(track.start, track.end, track.layer, axes= axes)

        #pg.show_plot()
            
    def plot_in_kicad(self, board, front_layer, back_layer):
        def get_new_wire(track, side):
            new_wire = pcbnew.PCB_SHAPE(board)

            new_wire.SetShape(pcbnew.SHAPE_T_SEGMENT)
            new_wire.SetLayer(front_layer if side == "front" else back_layer)
            new_wire.SetStart(track.start)
            new_wire.SetEnd(track.end)
            new_wire.SetWidth(track.width)

            return new_wire


        for track in self.front_track_list:
            board.Add(get_new_wire(track, "front"))

        for track in self.back_track_list:
            board.Add(get_new_wire(track, "back"))

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
            layer = layers["front" if track.layer == "F.Cu" else "back"]
            board.Add(track.as_drawing(board, layer))

        for pad in self.pad_lst:
            layer = layers["front" if pad.layer == "F.Cu" else "back"]
            board.Add(pad.as_drawing(board, layer))
            
            if pad.hole_shape:
                board.Add(pad.get_hole_drawing(board, layers["hole"]))


    # Inefficient, Might be better to write a __hash__ and compare sets instead
    def __eq__(self, other):
        if (len(self.track_lst) != len(other.track_lst)) or (len(self.pad_lst) != len(other.pad_lst)):
            return False
        
        return all([track in other.track_lst for track in self.track_lst]) and \
                    all([pad in other.pad_lst for pad in self.pad_lst])  

class PcbHole():
    def __init__(self, hole_shape):
        self.shape = hole_shape

    def plot(self, board, layers):
        self.shape.SetLayer(layers["hole"])
        board.Add(self.shape)

class PcbBoard():
    def __init__(self, board):
        self.board = board

        self.track_lst = PcbTrackList()
        
        self.track_lst.add_to_list(self.board)

        self.pad_lst = PcbPadList()
        self.pad_lst.add_to_list(self.board)

        self.net_dict = dict()
        self.gnd_nets = []

        self.holes = []

        self.add_to_dict(self.track_lst)
        self.add_to_dict(self.pad_lst)
        self.add_holes()

        print(print(self.net_dict))

    def add_to_dict(self, comp_list):
        for component in comp_list.all():

            if component.net_name == "GND":
                new_net = PcbNet()
                new_net.add(component)

                self.gnd_nets.append(new_net)

            else:
                if not (component.net_name in self.net_dict.keys()):
                    self.net_dict[component.net_name] = PcbNet()

                self.net_dict[component.net_name].add(component)

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



    # def compare_and_plot(self, old_board):

    #     erase_track_lst, write_track_lst = \
    #         self.track_lst.compare_tracks(old_board.track_lst)
        
    #     erase_pad_lst, write_pad_lst = \
    #         self.pad_lst.compare_pads(old_board.pad_lst)
        
    #     ERASE_FRONT = pcbnew.User_1
    #     ERASE_BACK =pcbnew.User_2

    #     WRITE_FRONT = pcbnew.User_3
    #     WRITE_BACK =pcbnew.User_4

    #     print(f"erase t {erase_track_lst}")
    #     print(f"erase p {erase_pad_lst}")

    #     erase_track_lst.plot_in_kicad(self.board, ERASE_FRONT, ERASE_BACK)
    #     erase_pad_lst.plot_in_kicad(self.board, ERASE_FRONT, ERASE_BACK)

    #     write_track_lst.plot_in_kicad(self.board, WRITE_FRONT, WRITE_BACK)
    #     write_pad_lst.plot_in_kicad(self.board, WRITE_FRONT, WRITE_BACK)

    def compare_nets(self, old_board):

        old_net_list = list(old_board.net_dict.values()) + old_board.gnd_nets

        erase_nets = []
        write_nets = list(self.net_dict.values()) + self.gnd_nets

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
            # TODO Figure out what to name them
            plot_ctrl.OpenPlotfile(pcbnew.LayerName(layer), pcbnew.PLOT_FORMAT_GERBER, title)
            plot_ctrl.PlotLayer()

        plot_ctrl.ClosePlot()

    def compare_and_plot(self, old_board):
        # self.plot_nets(list(self.net_dict.values())[1:2], self.board, pcbnew.User_3)

        erase_nets, write_nets = self.compare_nets(old_board)
        erase_holes, write_holes = self.compare_holes(old_board)

        parent_folder_path = pathlib.Path(self.board.GetFileName()).parent
        comp_folder_path = os.path.join(parent_folder_path, "compare_result")

        if not os.path.exists(comp_folder_path):
            os.mkdir(comp_folder_path)

        plot_board_path = os.path.join(comp_folder_path, "comparison.kicad_pcb")

        pcbnew.IO_MGR.Save(pcbnew.IO_MGR.KICAD_SEXP, plot_board_path, self.board)

        plot_board = pcbnew.IO_MGR.Load(pcbnew.IO_MGR.KICAD_SEXP, plot_board_path)

        # self.plot_nets(erase_nets, self.board, pcbnew.User_1)
        # self.plot_nets(write_nets, self.board, pcbnew.User_3)

        self.plot_nets(erase_nets, plot_board, "erase")
        self.plot_nets(write_nets, plot_board, "write")

        self.plot_holes(erase_holes, plot_board, "erase")
        self.plot_holes(write_holes, plot_board, "write")
        
        # Not working?? TODO: FIX
        # Setting unnecessary layers to hidden so I don't have to keep hiding them each time
        vis_layers = [pcbnew.User_1, pcbnew.User_2, pcbnew.User_3, \
                      pcbnew.User_4, pcbnew.User_5, pcbnew.User_6]

        vis_lset = pcbnew.LSET()

        for layer in vis_layers:
            vis_lset.addLayer(layer)

        plot_board.SetVisibleLayers(vis_lset)

        self.plot_gerbers(plot_board, comp_folder_path)

        pcbnew.IO_MGR.Save(pcbnew.IO_MGR.KICAD_SEXP, plot_board_path, plot_board)

        os.system(plot_board_path)
