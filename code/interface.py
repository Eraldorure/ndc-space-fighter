"""The file containing all the ui elements (such as buttons)."""

import pyxel as px
import code.functions as fn


class Hitbox:
    """A class representing a hitbox.
    The class is used by all objects that can be interacted with."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.w = width
        self.h = height

    def __bool__(self):
        """Returns either True if the hitbox is valid (aka if both its width and height are strictly positive) or False."""
        return self.w > 0 and self.h > 0

    def __contains__(self, co: tuple[int, int]):
        """Similar to the 'contains' method, with the exception that this one is used like : `(x, y) in hitbox`."""
        return self.contains(*co)

    def __and__(self, other):
        """Returns the overlapping area between two hitboxes.
        To be used as follows : `hitbox1 & hitbox2`."""
        if not (self and other):
            return Hitbox(0, 0, 0, 0)
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        w = min(self.x + self.w, other.x + other.w) - x
        h = min(self.y + self.h, other.y + other.h) - y
        return Hitbox(x, y, w, h)

    def contains(self, x: int, y: int) -> bool:
        """Indicates if two coordinates x and y are situated inside the hitbox."""
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def draw(self, col: int):
        """Method to draw the hitbox. To be used for debugging purposes."""
        px.rect(self.x, self.y, self.w, self.h, col)


class Text:
    """A class representing a text object.
    The text represented by this object is static, meaning its position will stay the same when any modification are
    made. Consequently, the appropriate way to modify anything is to recreate a whole new instance."""

    class Line:
        """A class representing a line of text."""

        def __init__(self, x: int, y: int, text: str, h_align: str):
            self.w = len(text) * 4 - 1
            self.h = 5
            if h_align == "left":
                self.x = x
            elif h_align == "center":
                self.x = x - self.w // 2
            else:
                self.x = x - self.w
            self.y = y
            self.txt = text
            self.hb = Hitbox(self.x, self.y, self.w, self.h + 1)

        def draw(self, color: int):
            """Draws the line of text."""
            px.text(self.x, self.y, self.txt, color)

        def draw_underline(self, color: int):
            """Draws a line under the text."""
            px.line(self.x, y := self.y + self.h + 1, self.x + self.w - 1, y, color)

    def __init__(self, x: int, y: int, text: str, max_width: int = None,
                 *, h_align: str = "left", v_align: str = "top"):
        if h_align not in ("left", "center", "right"):
            raise ValueError("invalid horizontal alignment, choose between 'left', 'center' and 'right'")
        if v_align not in ("top", "center", "bottom"):
            raise ValueError("invalid vertical alignment, choose between 'top', 'center' and 'bottom'")

        if max_width is not None:
            lines = fn.cut_max_text_width(text, (max_width + 1) // 4)
        else:
            lines = text.splitlines()
        self._txt = text
        self.w = 0
        self.h = len(lines) * 6 - 1

        self.x = x
        self.y = y
        if v_align == "center":
            self.y -= self.h // 2
        elif v_align == "bottom":
            self.y -= self.h

        self.lines = []
        for i in range(len(lines)):
            line = self.Line(x, self.y + i * 6, lines[i], h_align)
            self.lines.append(line)
            if line.w > self.w:
                self.x = line.x
                self.w = line.w

    def __str__(self):
        return self._txt

    def draw(self, color: int = 7):
        """Draws the text. The default color is white."""
        for line in self.lines:
            line.draw(color)


class Button:
    """A class representing a button that you can interact with."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.txt = Text(x + width // 2, y + height // 2, text.upper(), width - 1, h_align="center", v_align="center")
        self.hb = Hitbox(x, y, width, height)

    def is_pressed(self, btn: int = px.MOUSE_BUTTON_LEFT) -> bool:
        """Indicates whether the mouse is inside the button and the given key (left click by default) is pressed.
        If it's the case, the button is considered as pressed."""
        return px.btnp(btn) and self.mouse_over()

    def mouse_over(self) -> bool:
        """Returns either True if the mouse hovers over the button or False."""
        return self.hb.contains(px.mouse_x, px.mouse_y)

    def draw(self):
        """Draws the button."""
        if self.mouse_over():
            px.rectb(self.x - 1, self.y - 1, self.w + 2, self.h + 2, 2)
            px.rect(self.x, self.y, self.w, self.h, 10)
        else:
            px.rectb(self.x, self.y, self.w, self.h, 1)
            px.rect(self.x + 1, self.y + 1, self.w - 2, self.h - 2, 9)
        self.txt.draw(1)


class ClickableText(Text):
    """A class representing a clickable text.
    It could be considered as text reacting the exact same way a button would."""

    __str__ = object.__str__
    is_pressed = Button.is_pressed

    @property
    def txt(self):
        return super().__str__()

    def mouse_over(self) -> bool:
        """Returns either True if the mouse hovers over the text or False."""
        return any(line.hb.contains(px.mouse_x, px.mouse_y) for line in self.lines)

    def draw(self, color: int = 7):
        """Writes the text. When the mouse hovers over the text, it underlines it."""
        if self.mouse_over():
            super().draw(1)
            self.lines[-1].draw_underline(5)
        else:
            super().draw(color)
