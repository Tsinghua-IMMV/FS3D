# Author: Di Huang

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Extend.TopologyUtils import TopologyExplorer, get_sorted_hlr_edges
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_QuasiUniformDeflection
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Trsf, gp_Ax3, gp_Vec
from OCC.Core.HLRAlgo import HLRAlgo_Projector
from OCC.Core.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCC.Core.TopoDS import TopoDS_Shape

from typing import List, Optional, Tuple
import xml.etree.ElementTree as ET


def get_sorted_hlr_edges(
    topods_shape: TopoDS_Shape,
    direction: Optional[gp_Dir] = gp_Dir(),
    up: Optional[gp_Dir] = gp_Dir(),
    position: Optional[gp_Pnt] = gp_Pnt(),
    at: Optional[gp_Pnt] = gp_Pnt(),
    scale = 1.0,
    export_hidden_edges: Optional[bool] = False,
) -> Tuple[List, List]:

    aBackDir = direction.Reversed()
    aXpers = gp_Vec(up).Crossed(gp_Vec(aBackDir))
    aCenter = at
    anAx3 = gp_Ax3(aCenter, aBackDir, gp_Dir(aXpers))
    aTrsf = gp_Trsf()
    aTrsf.SetTransformation(anAx3)
    projector = HLRAlgo_Projector(aTrsf, False, scale)
    
    # Initialize the HLR algorithm with the shape and the projector
    hlr = HLRBRep_Algo()
    hlr.Add(topods_shape)
    hlr.Projector(projector)
    hlr.Update()
    hlr.Hide()

    # Process the shapes from HLR algorithm
    hlr_shapes = HLRBRep_HLRToShape(hlr)

    # Extract visible edges
    visible = []
    if visible_sharp_edges_as_compound := hlr_shapes.VCompound():
        visible += list(TopologyExplorer(visible_sharp_edges_as_compound).edges())
    if visible_smooth_edges_as_compound := hlr_shapes.Rg1LineVCompound():
        visible += list(TopologyExplorer(visible_smooth_edges_as_compound).edges())
    if visible_contour_edges_as_compound := hlr_shapes.OutLineVCompound():
        visible += list(TopologyExplorer(visible_contour_edges_as_compound).edges())

    # Extract hidden edges if requested
    if export_hidden_edges:
        hidden = []
        if hidden_sharp_edges_as_compound := hlr_shapes.HCompound():
            hidden += list(TopologyExplorer(hidden_sharp_edges_as_compound).edges())
        if hidden_contour_edges_as_compound := hlr_shapes.OutLineHCompound():
            hidden += list(TopologyExplorer(hidden_contour_edges_as_compound).edges())
        return visible, hidden
    return visible


def points2svg(points, out_path, line_width):
    tmp = []
    for stroke in points:
        for coord in stroke:
            x, y = coord
            y = -y
            tmp.append((x, y))
    x_values, y_values = zip(*tmp)
    min_x, max_x = min(x_values) - 5, max(x_values) + 5
    min_y, max_y = min(y_values) - 5, max(y_values) + 5

    svg_root = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1",
                        width="100%", height="100%", viewBox=f"{min_x} {min_y} {max_x - min_x} {max_y - min_y}")

    for stroke in points:
        current_path = []
        for coord in stroke:
            x, y = coord
            y = -y
            current_path.append(f"{x},{y}")
        polyline = ET.SubElement(svg_root, 'polyline', points=" ".join(current_path), style=f"fill:none;stroke:black;stroke-width:{line_width}%")

    tree = ET.ElementTree(svg_root)
    tree.write(out_path)


def generate_contour(input, output, direction, up, position=(0,0,0), at=(0,0,0), scale=1.0, line_width=0.8):
    x, y, z = direction
    direction = gp_Dir(x, y, z)
    x, y, z = up
    up = gp_Dir(x, y, z)
    x, y, z = position
    position = gp_Pnt(x, y, z)
    x, y, z = at
    at = gp_Pnt(x, y, z)

    step_reader = STEPControl_Reader()
    step_reader.ReadFile(input)
    step_reader.TransferRoot()
    shape = step_reader.Shape()

    vis_edges = get_sorted_hlr_edges(shape, direction=direction, up=up, position=position, at=at, scale=scale, export_hidden_edges=False)

    points = []
    for ve in vis_edges:
        stroke = []
        adaptor = BRepAdaptor_Curve(ve)

        deflection = GCPnts_QuasiUniformDeflection(adaptor, 0.01)
        for j in range(1, deflection.NbPoints() + 1):
            pnt = deflection.Value(j)
            stroke.append((pnt.X(), pnt.Y()))

        points.append(stroke)
    
    min_x = min(x for sublist in points for x, y in sublist)
    min_y = min(y for sublist in points for x, y in sublist)

    delta_x = 5 - min_x
    delta_y = 5 - min_y

    points = [[(x + delta_x, y + delta_y) for x, y in sublist] for sublist in points]
    
    points2svg(points, output, line_width)


if __name__ == "__main__":
    direction = (-0.57735,0.57735,-0.57735)
    up = (-0.408248,0.408248,0.816497)
    generate_contour(r'samples/sample.step', r'samples/sample.svg', direction, up)

