"""
Adds line plots to EmberGraphs.
"""
from embermaker.graphbase import Element, CanPos, Axis, draw_xaxis, draw_vaxis


class LinePlot(Element):
    """
    A simple x-y line plot that can be drawn with the same vertical axis as ember.
    """
    parent_type = "GraphLine"

    def __init__(self, egr=None, xaxis_name="", title=""):
        super().__init__()
        if egr:
            egr.add(self)
        self.xaxis_name = xaxis_name
        self.withvgrid = False
        self.title = title

    def set_cx(self, base_x):
        gp = self.egr.gp
        # left margin (may include an axis)
        mar_x = self.has_vaxis * (self.has_axis_name * self.egr.gp["haz_name_x"] + self.egr.gp["scale_x"])
        # x-interval of the dataset (all lines)
        axmin = min(el.xsmin() for el in self.elements)
        axmax = max(el.xsmax() for el in self.elements)
        # Create x coordinate system
        self.cx.cp = CanPos(base_x, mar_x, gp["be_y"] * 0.6, 0)
        self.cx.ax = Axis(bottom=axmin, top=axmax)
        # Propagate this coordinate to the lines
        for el in self.elements:
            el.cx = self.cx

        return self.cx.b1  # Right end of this element => left of the following one

    def draw(self):
        # Axis
        draw_xaxis(self.egr, self.cx, self.cy, name=self.xaxis_name)
        draw_vaxis(self)
        egr = self.egr
        c = egr.c

        # Group title
        if self.title:
            self.egr.c.paragraph(self.cx.c0, self.cy.c1 + egr.gp['be_top_y'] * 0.6, self.title, valign='center',
                                 width=self.cx.c, font=("Helvetica", egr.gp['gr_fnt_size']))

        # "clip" the viewable area to the rectangle within the axis
        c.clip((self.cx.c0, self.cy.c0, self.cx.c, self.cy.c))
        # Draw content
        super().draw()
        c.clip(None)


class Line(Element):
    _elementary = True
    parent_type = "LinePlot"

    def __init__(self, xs=None, ys=None, color=None):
        """
        A line in a x-y lineplot
        :param xs:
        :param ys:
        :param color:
        """
        super().__init__()
        if xs is not None and ys is not None and len(xs) != len(ys):
            raise ValueError("xs and ys must contain the same number of values.")
        self.xs = xs
        self.ys = ys
        self.color = color

    def xsmin(self):
        return min(self.xs)

    def xsmax(self):
        return max(self.xs)

    def draw(self):
        egr = self.egr
        points = []
        for xv, yv in zip(self.xs, self.ys):
            xp = self.cx.tocan(xv)
            yp = self.cy.tocan(yv)
            points.append((xp, yp))
        egr.c.polyline(points, stroke=self.color)
