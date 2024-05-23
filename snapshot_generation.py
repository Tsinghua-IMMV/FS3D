# Author: Di Huang

from OCC.Display.SimpleGui import init_display
from OCC.Extend.DataExchange import read_step_file


def generate_snapshot(input, output, direction, up, eye, scale, img_size=(2160, 1344)):
    shape = read_step_file(input)
    display, _, _, _ = init_display(size=img_size, display_triedron=False, background_gradient_color1=[255,255,255], background_gradient_color2=[255,255,255])
    display.DisplayShape(shape, update=True)
    display.EnableAntiAliasing()
    display.FitAll()
    display.Context.UpdateCurrentViewer()

    view = display.View
    view.SetEye(eye[0], eye[1], eye[2])
    view.SetAt(eye[0] + direction[0], eye[1] + direction[1], eye[2] + direction[2])
    view.SetUp(up[0], up[1], up[2])
    view.SetScale(scale)
    view.FitAll()
    display.FitAll()
    display.Context.UpdateCurrentViewer()
    view.Dump(output)


if __name__ == "__main__":
    direction = (-0.57735,0.57735,-0.57735)
    up = (-0.408248,0.408248,0.816497)
    eye = (263.519,-174.052,173.519)
    scale = 284.998
    generate_snapshot(r'samples/sample.step', r'samples/snapshot.png', direction, up, eye, scale)

