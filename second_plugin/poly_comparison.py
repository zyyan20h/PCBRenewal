# from svgpathtools import svg2paths, wsvg, Line, Path, parse_path
from shapely import MultiPolygon, Polygon, union_all, buffer #  Go to Kicad Command prompt and type 'pip install shapely'
import pcbnew
# from .pcb_components import PcbTrack, PcbPad, rotate_point
import math

IU_PER_MM = pcbnew.PCB_IU_PER_MM

# SHAPE_POLY_SET class in pcbnew seems to have BooleanAdd, BooleanSubtract classes
# May be possible to remove the need for shapely library

# Eventually add to same file as rest, or find some other way to organise

def rotate_point(p: pcbnew.VECTOR2I, angle: float, centre: pcbnew.VECTOR2I = pcbnew.VECTOR2I(0,0)):
    centred_p = p - centre

    angle_rad = math.radians(angle)

    x = int((centred_p[0] * math.cos(angle_rad)) + (centred_p[1] * -math.sin(angle_rad)))
    y = int((centred_p[0] * math.sin(angle_rad)) + (centred_p[1] * math.cos(angle_rad)))

    return (pcbnew.VECTOR2I(x, y) + centre)

def iu_to_mm(p):   
    if type(p) == int:
        return p[0]/IU_PER_MM
    else:
        return (p[0]/IU_PER_MM, p[1]/IU_PER_MM)
    
def as_svg(shape, filename, dimensions=None, shape2 = None):
    
    with open(filename, "w") as svg_file:
        svg_text = \
            f"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {100} {100}\"> \
                {shape.svg(scale_factor=0.1, stroke_color='#ff0000')} {'' if not shape2 else shape2.svg(scale_factor=0.1, stroke_color='#00ff00')}</svg>"
        svg_file.write(svg_text)
        pass

class ComponentShape:
    # Decide if component_type is necessary
    # Maybe can use isinstance
    # but will have to import
    def __init__(self, component, type, drill_diameter=None):
        self.outline = None
        self.drill_diameter = drill_diameter

        if type == "pad":
            self.outline = self.get_pad_poly(component)
        else:
            self.outline = self.get_track_poly(component)

    def get_pad_poly(self, component):
        line_chain = component.polygon.Outline(0)
        point_lst = [ iu_to_mm(p) for p in line_chain.CPoints()]

        outline = Polygon(point_lst)
        return outline

    def get_track_poly(self, component, total_points = 50):
        start = component.start
        end = component.end
        radius = int(component.width / 2)
        point_lst = []

        # We find a vector to offset the start and end by
        vec = (start - end)
        vec = vec / vec.EuclideanNorm()
        offset_vec = rotate_point(vec, 90) * radius

        curr_angle = 0
        step = 360 / total_points
        while curr_angle <= 180:
            new_point = iu_to_mm(offset_vec + end)
            point_lst.append(new_point)
            offset_vec = rotate_point(offset_vec, step)
            curr_angle += step

        while curr_angle <= 360:
            new_point = iu_to_mm(offset_vec + start)
            point_lst.append(new_point)
            offset_vec = rotate_point(offset_vec, step)
            curr_angle += step

        outline = Polygon(point_lst)
        return outline

class NetShape:
    def __init__(self, net, offset=0.2):
        pad_shapes = [ComponentShape(pad, "pad").outline for pad in net.pad_lst]
        track_shapes = [ComponentShape(track, "track").outline for track in net.track_lst]

        self.outline = union_all(pad_shapes + track_shapes)
        # offset_shape = buffer(self.outline, offset)
        # self.offset_path = offset_shape.difference(self.outline)
        # a = int(1,2)
        # # Line tracing out the midle of the drill path
        print(type(self.outline))
        offset_path_shape = buffer(self.outline, offset/2)
        self.offset_path = None
        # Converting to a line instead of a polygon
        # It might be multiple polygons too
        if type(offset_path_shape) == MultiPolygon:
            self.offset_path = union_all([poly.exterior for poly in offset_path_shape.geoms])
        else:
            self.offset_path = offset_path_shape.exterior
        self.offset = offset

class ShapeCollection:
    def __init__(self, net_list, offset=0.2):
        self.combined_net_paths = None
        self.combined_outlines = None

        net_shapes = [NetShape(net)for net in net_list]
        path_lst = [shape.offset_path for shape in net_shapes]
        outline_lst = [shape.outline for shape in net_shapes]
        # # might be breaking because of somehting called pygeos and it not being the correct version
        # self.combined_net_paths = coverage_union_all(path_lst) 
        self.combined_net_paths = union_all(path_lst)
        self.combined_outlines = union_all(outline_lst)

    def path_difference(self, other):
        return self.combined_net_paths.difference(other.combined_net_paths)
    
    def plot_in_kicad(self, board, layer):
        pass



