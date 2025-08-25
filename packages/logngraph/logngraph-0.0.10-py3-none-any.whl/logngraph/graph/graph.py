import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from warnings import deprecated
from logngraph.errors import *
from typing import Callable

__all__ = [
    "Window",
]

class Window:
    def __init__(self, title: str = "Window", width: int = 800, height: int = 600, resizable: bool = True) -> None:
        pygame.init()
        pygame.font.init()

        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE if resizable else 0)
        pygame.display.set_caption(title)

        self.running = True
        self.key_bindings: dict[int, Callable] = {}

    def fill(self, color: tuple[int, int, int] | str) -> None:
        """
        Fill the window with given color.

        :param color: Color to fill the window with.
        :return:
        """
        self.screen.fill(color)

    def update(self) -> None:
        """
        Updates the window.

        :return:
        """
        if self.running:
            pygame.display.flip()

    def stop(self) -> None:
        """
        Stops the window.

        :return:
        """
        self.running = False

    @deprecated("Use Window.handle_events()!")
    def handle_quit(self) -> None:
        """
        DEPRECATED: USE Window.handle_events()!
        :return:
        """
        self.handle_events()

    def handle_events(self) -> None:
        """
        Handles event (quit, keypresses, etc.)

        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in self.key_bindings:
                    self.key_bindings[event.key]()

    def screenshot(self, filename: str) -> None:
        """
        Save a screenshot of the window to a file.

        :param filename: Path to the file to save the screenshot to.
        :return:
        """
        pygame.image.save(self.screen, filename)

    def rect(self, left_top: tuple[float, float], width_height: tuple[float, float], color="#ffffff") -> None:
        """
        Draw a rectangle with given width and height and at given coordinates.

        :param left_top: Leftmost top coordinates of the rectangle.
        :param width_height: Width and height of the rectangle.
        :param color: Fill color of the rectangle.
        :return:
        """
        pygame.draw.rect(self.screen, color, (*left_top, *width_height))

    def ellipse(self, left_top: tuple[float, float], width_height: tuple[float, float], color="#ffffff") -> None:
        """
        Draw an ellipse enclosed in a rectangle of given width and height and at given coordinates.

        :param left_top: Leftmost top coordinates of the rectangle.
        :param width_height: Width and height of the rectangle.
        :param color: Fill color of the ellipse.
        :return:
        """
        pygame.draw.ellipse(self.screen, color, (*left_top, *width_height))

    def circle(self, center: tuple[float, float], radius: float, color="#ffffff") -> None:
        """
        Create circle with center at center and radius=radius.

        :param center: Center position of the circle.
        :param radius: Radius of the circle.
        :param color: Fill color of the circle.
        :return:
        """
        pygame.draw.circle(self.screen, color, center, radius)

    def line(self, start_pos: tuple[float, float], end_pos: tuple[float, float], color="#ffffff", width: int = 1) -> None:
        """
        Draw a line from start_pos to end_pos with width=width and color=color.

        :param start_pos: Starting position of the line.
        :param end_pos: Ending position of the line.
        :param color: Color of the line.
        :param width: Width of the line.
        :return:
        """
        pygame.draw.line(self.screen, color, start_pos, end_pos, width=width)

    def polygon(self, *args: float | tuple[float, float], color="#ffffff") -> None:
        """
        Draw a polygon with given position arguments.

        :param args: x, y pairs of coordinates of the vertices of the polygon. E.g. `(0, 0), (15, 60), (123, 624)`, or `0, 0, 15, 60, 123, 624`.
        :param color: Fill color of the polygon.
        :return:
        """
        try:
            if len(args) % 2 == 0:
                points = []
                for i in range(0, len(args), 2):
                    points.append((args[i], args[i + 1]))
            else:
                points = list(args)
        except Exception as e:
            raise InvalidArgsError(f"Could not unpack args: {args}") from e
        pygame.draw.polygon(self.screen, color, points)

    def write(self, center: tuple[int, int], text: str = "", color="#ffffff", bg_color="#000000", antialias: bool = True, font: pygame.font.Font | str = "Arial", size: int = 16) -> None:
        """
        Write given text to the screen.

        :param center: Center position of the text.
        :param text: Text to write.
        :param color: Color of the text.
        :param bg_color: Background color of the text.
        :param antialias: Enable antialiasing of the text.
        :param font: Font of the text.
        :param size: Font size of the text.
        :return:
        """
        if type(font) is str:
            try:
                font = pygame.font.Font(font, size)
            except FileNotFoundError:
                font = pygame.font.SysFont(font, size)
        text = font.render(text, antialias, color, bg_color)
        textRect = text.get_rect()
        textRect.center = center
        self.screen.blit(text, textRect)

    def bind_key(self, key: str, function: Callable) -> None:
        """
        Bind given keypress to given function.
        Function will be called when the key is pressed.

        :param key: Key press. Must be a valid pygame key name (e.g., 'a', 'space', 'enter').
        :param function: Function to call when the key is pressed.
        :return:
        """
        try:
            key_constant = pygame.key.key_code(key)
            self.key_bindings[key_constant] = function
        except ValueError:
            raise InvalidKeyError(f"Invalid key name: {key}")
