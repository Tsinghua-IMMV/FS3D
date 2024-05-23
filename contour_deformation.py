# Author: Di Huang

import matplotlib.pyplot as plt
from svgpathtools import svg2paths


def draw(output, paths, ax, fig, color=None):
    for path in paths:
        x_data = [segment.start.real for segment in path] + [path[-1].end.real]
        y_data = [-segment.start.imag for segment in path] + [-path[-1].end.imag]
        if not color:
            ax.plot(x_data, y_data)
        else:
            ax.plot(x_data, y_data, color=color)

    ax.axis('off')
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout(pad=0)

    plt.savefig(output, format='svg', bbox_inches='tight', pad_inches=0)


def contour_deformation(input, output, output_color=None, scale=1, length=100, randomness=4):
    # scale: The amplitude of the wiggle perpendicular to the source line (affects the jitter amplitude of the strokes).
    # length: The length of the wiggle along the line (affects the divergence of strokes).
    # randomness: The scale factor by which the length is shrunken or expanded (affects the jitter amplitude of the strokes).

    paths, attributes = svg2paths(input)

    with plt.xkcd(scale=scale, length=length, randomness=randomness):
        x_data_ = []
        y_data_ = []
        for path in paths:
            for line in path:
                x_data_.extend([line.start.real, line.end.real])
                y_data_.extend([-line.start.imag, -line.end.imag])
        x_min, x_max, y_min, y_max = min(x_data_), max(x_data_), min(y_data_), max(y_data_)
        radio = (x_max - x_min) / (y_max - y_min)

        fig_width = 5 * radio
        fig_height = 5
        dpi_value = 100
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi_value)

        draw(output, paths, ax, fig, color="black")

        if output_color:
            ax.cla()
            draw(output_color, paths, ax, fig)


if __name__ == "__main__":
    input = r'samples/sample.svg'
    output = r'samples/deformation.svg'
    output_color = r'samples/deformation_color.svg'
    contour_deformation(input, output, output_color=output_color, scale=1, length=100, randomness=5)

