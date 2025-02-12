from shapely import MultiPolygon, Polygon, LineString, MultiLineString, Point, box, union_all, transform #  Go to Kicad Command prompt and type 'pip install shapely'
import pcbnew
import math

IU_PER_MM = pcbnew.PCB_IU_PER_MM

DEFAULT_OFFSET = 0.4

OFFSET_BY_LAYER = {"F.Cu" : 0.2, "B.Cu": 0.4}

# SHAPE_POLY_SET class in pcbnew seems to have BooleanAdd, BooleanSubtract classes
# May be possible to remove the need for shapely library

# Eventually add to same file as rest, or find some other way to organise

def rotate_point(p: pcbnew.VECTOR2I, angle: float, centre: pcbnew.VECTOR2I = pcbnew.VECTOR2I(0,0)):
    centred_p = p - centre

    angle_rad = math.radians(angle)

    x = int((centred_p[0] * math.cos(angle_rad)) + (centred_p[1] * -math.sin(angle_rad)))
    y = int((centred_p[0] * math.sin(angle_rad)) + (centred_p[1] * math.cos(angle_rad)))

    return (pcbnew.VECTOR2I(x, y) + centre)

def get_arc_points(centre, radius=None, start_angle=None, end_angle=None, start=None, end=None, angle=None, step= 5):
        if not angle:
            point = pcbnew.VECTOR2I(centre[0] + radius, centre[1])
            point_lst = []

            angle = start_angle

            while angle < end_angle:
                point_lst.append(rotate_point(point, angle, centre))

                angle += step
        else:
            point_lst = [start]
            point = start
            while angle > (0 + step):
                point = rotate_point(point, step, centre)
                point_lst.append(point)
                angle -= step

            point_lst.append(end)

        return point_lst

debug = False

def iu_to_mm(p):  

    if type(p) == int:
        return p[0]/IU_PER_MM
    else:
        return (p[0]/IU_PER_MM, p[1]/IU_PER_MM)
    
def convert_to_mm_coords(shape, board):
    board_bb = board.board.GetBoundingBox()
    bb_width = board_bb.GetWidth() / IU_PER_MM
    bb_height = board_bb.GetHeight() / IU_PER_MM
    board_topleft = pcbnew.VECTOR2I(board_bb.GetLeft(), board_bb.GetTop())

    # Move the board edge to 0,0
    shape = transform(shape,lambda x: x - list(board_topleft))
    shape = transform(shape, lambda x: x / IU_PER_MM)

    return bb_width, bb_height, shape

def get_warnings(path_dict, new_edge, old_edge, via_list):
    polygon_dict = dict()
    no_warnings = True
    def via_to_poly(via):
        shape = via.hole_shape
        points = shape.GetPolyShape().Outline(0).CPoints()
        poly = Polygon([p for p in points])
        return poly

    for layer in path_dict:
        polygon_dict[layer] = None
        net_poly = path_dict[layer].combined_outlines
        
        for via in via_list:
            poly = via_to_poly(via)
            net_poly = net_poly.difference(poly)
            pass

        p1 = net_poly.difference(new_edge.edge_polygon)
        p2 = net_poly.difference(old_edge.edge_polygon)
        p = p1.union(p2)

        if not p.is_empty:
            no_warnings = False

        if type(p) == Polygon:
            p = [p]
        else:
            p = p.geoms
        polygon_dict[layer] = p


    if no_warnings:
        polygon_dict = None

    return polygon_dict

class ComponentShape:
    # Decide if component_type is necessary
    # Maybe can use isinstance
    # but will have to import
    def __init__(self, component, type, offset=DEFAULT_OFFSET):
        self.outline = None

        if type == "pad":
            self.outline = self.get_pad_poly(component)
        else:
            self.outline = self.get_track_poly(component)

        # self.offset_shape = self.outline.buffer(offset)

    def get_pad_poly(self, component):
        line_chain = component.polygon.Outline(0)
        # point_lst = [ iu_to_mm(p) for p in line_chain.CPoints()]
        point_lst = [ p for p in line_chain.CPoints()]
        outline = Polygon(point_lst)
        return outline

    def get_track_poly(self, component, total_points = 50):
        start = component.start
        end = component.end
        radius = int(component.width / 2)
        point_lst = []
        
        line = LineString([tuple(start), tuple(end)]) # Casting to tuple might be unnecessary
        return line.buffer(radius)

class NetShape:
    def __init__(self, net, offset=DEFAULT_OFFSET):
        pad_shapes = [ComponentShape(pad, "pad", offset).outline for pad in net.pad_lst]
        track_shapes = [ComponentShape(track, "track", offset).outline for track in net.track_lst]
        component_shapes = pad_shapes + track_shapes
        self.outline = union_all(component_shapes)

        # offset_path_shape = buffer(self.outline, offset/2)
        offset_path_shape = union_all([p.buffer((offset/2) * IU_PER_MM) for p in component_shapes])
        # print("shape offset", offset)

        self.offset_path = None
        # Converting to a line instead of a polygon
        # It might be multiple polygons too
        if type(offset_path_shape) == MultiPolygon:
            self.offset_path = union_all([poly.exterior for poly in offset_path_shape.geoms])
        else:
            self.offset_path = offset_path_shape.exterior
        self.offset = offset

class NetCollection:
    def __init__(self, net_list=None, offset=DEFAULT_OFFSET, layer=None, shape_collection=None):
        self.combined_net_paths = None
        self.offset = offset
        self.combined_outlines = None

        if layer:
            self.offset = OFFSET_BY_LAYER[layer]
            # print("Offset", layer, self.offset)

        if shape_collection:
            # For when you already have shapely objects and you just want to store them in this class
            self.combined_net_paths = shape_collection

        elif net_list:
            net_shapes = [NetShape(net, self.offset)for net in net_list]
            path_lst = [shape.offset_path for shape in net_shapes]
            outline_lst = [shape.outline for shape in net_shapes]

            self.combined_net_paths = union_all(path_lst)
            self.combined_outlines = union_all(outline_lst)
        
        else:
            self.combined_net_paths = MultiLineString()

        self.net_path_polygon = None

    def path_difference(self, other):
        diff = self.combined_net_paths.difference(other.combined_net_paths)
        return NetCollection(shape_collection=diff, offset=self.offset)

    def export_path(self, board, filename, add_edge_cut=True, is_stencil=False):
        # shape = self.combined_net_paths
        shape = self.polygonize_paths()

        board_bb = board.board.GetBoundingBox()
        bb_width = board_bb.GetWidth() / IU_PER_MM
        bb_height = board_bb.GetHeight() / IU_PER_MM
        board_topleft = pcbnew.VECTOR2I(board_bb.GetLeft(), board_bb.GetTop())

        # Doesn't seem to be actually moving it to 0,0
        # Move the board edge to 0,0
        print(" board offset", board.offset_vec)
        shape = transform(shape,lambda x: x - list(board_topleft) - board.offset_vec)
        shape = transform(shape, lambda x: x / IU_PER_MM)
        # edge_cut_d_string = f"M 0,0 L 0,{height} L {width},{height} L {width},0"

        edge_svg_text = ""
        # Adding edge sgapes
        for shape_name, start, end, shape_ref in board.edge_cut_shapes:
            if shape_name == "Rect":
                width = (end[0] - start[0]) / IU_PER_MM
                height = (end[1] - start[1]) / IU_PER_MM
                x, y = iu_to_mm((start - board.offset_vec - board_topleft))
                edge_svg_text += f'<rect width=\"{width}\" height=\"{height}\" x=\"{x}\" y=\"{y}\" stroke-width=\"{0.1}\" fill="none" stroke=\"black\"/>'
            
            elif shape_name == "Circle":
                radius = (end - start).EuclideanNorm() / IU_PER_MM
                x, y = iu_to_mm((start - board.offset_vec - board_topleft))
                edge_svg_text += f'<circle r=\"{radius}\" cx=\"{x}\" cy=\"{y}\" stroke-width=\"{0.1}\" fill="none" stroke=\"black\"/>'
            
            elif shape_name == "Arc":
                radius = shape_ref.GetRadius() / IU_PER_MM
                start = iu_to_mm((start - board.offset_vec - board_topleft)) 
                end = iu_to_mm((end - board.offset_vec - board_topleft))
                angle = shape_ref.GetArcAngle().AsDegrees()
                large_arc_factor = 1 if angle > 180 else 0
                edge_svg_text += f'<path d=\"M {start[0]} {start[1]} A {radius} {radius} 0 {large_arc_factor} 1 {end[0]} {end[1]}\" stroke-width=\"{0.1}\" fill="none" stroke=\"black\"/>'

            elif shape_name == "Line":
                start = iu_to_mm((start - board.offset_vec - board_topleft))
                end = iu_to_mm((end - board.offset_vec - board_topleft))
                edge_svg_text += f'<line x1=\"{start[0]}\" y1=\"{start[1]}\" x2=\"{end[0]}\" y2=\"{end[1]}\" stroke-width=\"{0.1}\" fill="none" stroke=\"black\"/>'
            pass

        with open(filename, "w") as svg_file:
            svg_text =  f'''<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {bb_width} {bb_height}\" width=\"{bb_width}mm\" height=\"{bb_height}mm\">
                    <g stroke-linecap=\"round\" fill-rule=\"{"evenodd" if is_stencil else "nonzero"}\">
                        {shape.svg(scale_factor=0, opacity=1)}
                        {edge_svg_text}
                    </g>
                    </svg>'''
            svg_file.write(svg_text)

    def polygonize_paths(self):
        if not self.net_path_polygon:
            self.net_path_polygon = self.combined_net_paths.buffer((self.offset/2 ) * IU_PER_MM)
        
        return self.net_path_polygon

    def get_area_mm(self):
        return self.polygonize_paths().area / (IU_PER_MM * IU_PER_MM)

    def get_length_mm(self):
        return self.combined_net_paths.length / IU_PER_MM

    # Returns list of polygons created out of paths
    def get_poly_list(self):
        if not self.net_path_polygon:
            # self.net_path_polygon = self.combined_net_paths.buffer((self.offset/2 ) * IU_PER_MM)
            self.polygonize_paths()
        
        if type(self.net_path_polygon) == MultiPolygon:
            poly_list = self.net_path_polygon.geoms
        else:
            poly_list = [self.net_path_polygon]

        return poly_list

    def plot_in_kicad(self, board, layer):
        if type(self.combined_net_paths) == MultiLineString:
            shape_list = self.combined_net_paths.geoms
        else:
            shape_list = [self.combined_net_paths]

        line_width = int(self.offset * IU_PER_MM)
        # print(line_width)
        for shape in shape_list:
            ind = 0
            points = shape.coords
            num_points = len(points)
            
            while ind < num_points - 1:
                line = pcbnew.PCB_SHAPE(board)
                line.SetShape(pcbnew.SHAPE_T_SEGMENT)
                line.SetLayer(layer)

                # Have to convert the coordinates to integers
                start = pcbnew.VECTOR2I(int(points[ind][0]), int(points[ind][1]))
                end = pcbnew.VECTOR2I(int(points[ind + 1][0]), int(points[ind + 1][1]))
                line.SetStart(start)
                line.SetEnd(end)

                line.SetWidth(line_width)

                board.Add(line)

                ind += 1
        pass

class EdgeCollection:
    def __init__(self, edge_cut_shapes=None, board=None, shape=None, cut_length=0):
        self.board = board
        self.cut_length = cut_length
        
        if edge_cut_shapes:
            self.edge_polygon = self.create_edge_polygon(edge_cut_shapes)
        else:
            self.edge_polygon = shape

    def create_edge_polygon(self, edge_cut_shapes):
        polygons = []
        # print(edge_cut_shapes)

        for name, start, end, shape in edge_cut_shapes:
            board_offset = pcbnew.VECTOR2I(0,0)
            if self.board:
                board_offset = self.board.offset_vec

            width = shape.GetWidth()
            
            if name == "Rect":
                start = shape.GetStart() + board_offset
                end = shape.GetEnd() + board_offset
                p = box(*start, *end)
                p = p.exterior.buffer(width)
                polygons.append(p)

            elif name == "Circle":
                radius = (start - end).EuclideanNorm()
                center = Point(start)
                p = center.buffer(radius)
                p = p.exterior.buffer(width)
                polygons.append(p)
        
            elif name == "Line":
                p = LineString([start,end]).buffer(width)
                polygons.append(p)

            elif name == "Arc":
                center = shape.GetCenter() + board_offset
                p = LineString(get_arc_points(center, start=start, end=end, angle=shape.GetArcAngle().AsDegrees()))
                p = p.buffer(width)
                polygons.append(p)

        combined =  union_all(polygons)
        polygons = []
        if type(combined) == Polygon:
            polygons = [Polygon(ls) for ls in combined.interiors]
        else:
            for p in combined.geoms:
                polygons += [Polygon(ls) for ls in p.interiors]
        
        polygons.sort(key=lambda x: x.area, reverse=True)

        combined = polygons[0]
        polygons = polygons[1:]
        
        for p in polygons:
            if combined.contains(p):
                combined = combined.difference(p)
            else:
                combined = combined.union(p)

        return combined
    
    def add_via_holes(self, via_list):
        def via_to_poly(via):
            shape = via.hole_shape
            points = shape.GetPolyShape().Outline(0).CPoints()
            poly = Polygon([p for p in points])
            return poly
            
        for via in via_list:
            poly = via_to_poly(via)
            self.cut_length += poly.length
            self.edge_polygon = self.edge_polygon.difference(poly)
            pass
    
    def offset(self, offset):
        self.edge_polygon = transform(self.edge_polygon, lambda x: x + offset)

    def get_outline(self):
        outline = None
        if type(self.edge_polygon) == Polygon:
            outline = self.edge_polygon.exterior
        else:
            outline = union_all([s.exterior for s in self.edge_polygon.geoms])
        return outline

    def edge_difference(self, other_edge):
        diff = self.edge_polygon.difference(other_edge.edge_polygon)
        #The line that would be cut to make an edge into another edge
        cut_length = (other_edge.get_outline().difference(self.get_outline())).length / IU_PER_MM
        return EdgeCollection(shape=diff, cut_length=cut_length)
    
    def get_area_mm(self):
        return self.edge_polygon.area / (IU_PER_MM * IU_PER_MM)
    
    def get_length_mm(self):
        return self.edge_polygon.length / IU_PER_MM
    
    def get_poly_points(self):
        if type(self.edge_polygon) == Polygon:
            return [self.edge_polygon.exterior.coords]
        
        else:
            return [p.exterior.coords for p in self.edge_polygon.geoms]
        
    def export_edge(self, board, filename):
        shape = self.edge_polygon

        board_bb = board.board.GetBoundingBox()
        bb_width = board_bb.GetWidth() / IU_PER_MM
        bb_height = board_bb.GetHeight() / IU_PER_MM
        board_topleft = pcbnew.VECTOR2I(board_bb.GetLeft(), board_bb.GetTop())

        # Move the board edge to 0,0
        shape = transform(shape,lambda x: x - list(board_topleft))
        shape = transform(shape, lambda x: x / IU_PER_MM)

        with open(filename, "w") as svg_file:
            svg_text =  f'''<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {bb_width} {bb_height}\" width=\"{bb_width}mm\" height=\"{bb_height}mm\">
                    <g stroke-linecap=\"round\">
                        {shape.svg(scale_factor=0)}
                    </g>
                    </svg>'''
            svg_file.write(svg_text)
        pass
