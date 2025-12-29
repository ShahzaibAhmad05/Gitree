"""
Represents tree items such as files and folders.
"""
import os


class TreeItem:
    """
    Represents a generic item in the tree structure.
    """

    def __init__(self, rel_path: str, depth: str, ignore: bool=False, 
                 hidden: bool=False) -> None:
        
        self.name = os.path.basename(rel_path)
        self.depth = depth
        self.ignore = ignore
        self.hidden = hidden


class File(TreeItem):
    """
    Represents a file in the tree structure.
    """

    def __init__(self, rel_path: str, depth: str, ignore: bool=False, 
                 hidden: bool=False, add_contents: bool=True) -> None:
        
        super().__init__(rel_path, depth, ignore, hidden)

        # Update name and extension in case of files (handles multiple dots)
        self.name = ".".join(os.path.splitext(rel_path)[:-1])
        self.ext = os.path.splitext(rel_path)[-1]
        self.add_contents = add_contents


class Folder(TreeItem):
    """
    Represents a folder in the tree structure.
    """

    def __init__(self, rel_path: str, depth: str, ignore: bool=False, 
                 hidden: bool=False) -> None:
        
        super().__init__(rel_path, depth, ignore, hidden)

        self.children = []

    
    def add_child(self, child: TreeItem):
        self.children.append(child)


class Truncated(TreeItem):
    """
    Represents a truncated list of items.
    """

    def __init__(self, items: list[TreeItem], rel_path, depth, ignore = False, hidden = False):
        super().__init__(rel_path, depth, ignore, hidden)

        self.items = items
        self.name = f"... and {len(items)} more items"
