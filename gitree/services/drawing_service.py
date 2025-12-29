from ..objects.tree_item import TreeItem, Folder, File
from ..constants.constant import (BRANCH, LAST, VERT, SPACE,
                                  EMPTY_DIR_EMOJI, NORMAL_DIR_EMOJI, 
                                  FILE_EMOJI,
                                  RESET, GREY, BLUE, CYAN)


class DrawingService:
    """
    Service responsible for drawing tree items.
    """

    def __init__(self, enable_emoji: bool=False, enable_color: bool=False):
        """
        Initializer for setting vars.
        """
        self.add_emoji = enable_emoji
        self.add_color = enable_color


    def draw(self, item: TreeItem, is_last: bool=False) -> str:
        """
        Returns a string representation of the drawing of the given tree item.
        """

        if isinstance(item, Folder):
            return self._draw_folder(item, is_last)
        
        elif isinstance(item, File):
            return self._draw_file(item, is_last)
        
        else:
            raise TypeError("Unsupported TreeItem type passed to draw method.")


    def _draw_folder(self, folder: Folder, is_last: bool) -> str:
        """
        Draws a folder.
        """
        prefix = ""
        if folder.depth > 0:    # No prefix needed if root
            prefix = LAST if is_last else BRANCH

        emoji = ""
        if self.add_emoji:
            emoji = NORMAL_DIR_EMOJI if len(folder.children) > 0 else EMPTY_DIR_EMOJI

        color = ""
        if self.add_color:
            color = CYAN if folder.hidden else BLUE

        result = (((folder.depth-1) * SPACE) + prefix + emoji + 
                  color + folder.name + "/" + RESET)

        return result


    def _draw_file(self, file: File, is_last: bool) -> str:
        """
        Draws a file.
        """
        prefix = ""
        if file.depth > 0:    # No prefix needed if root
            prefix = LAST if is_last else BRANCH

        emoji = ""
        if self.add_emoji:
            emoji = FILE_EMOJI

        color = GREY if file.hidden and self.add_color else ""

        result = ((file.depth-1) * SPACE) + prefix + emoji + color + file.name + file.ext + RESET

        return result
    