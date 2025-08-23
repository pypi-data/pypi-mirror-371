from typing_extensions import override
from anyio import Path
import libcst as cst
from libcst.metadata import PositionProvider    

class StructurePathProvider(cst.VisitorMetadataProvider[Path]):
    """
    A class to provide paths for metadata files based on a hierarchical structure.
    """
    
    METADATA_DEPENDENCIES = (PositionProvider,)


    def __init__(self):
        self.path = Path()
        
    def node_name(self, node: cst.CSTNode) -> str:
        """
        Returns the name of the node class.
        """
        return node.__class__.__name__
    

    def on_visit(self, node: cst.CSTNode) -> bool:
        self.path = self.path / self.node_name(node)
        self.set_metadata(node, self.path)
        return True

        
    def on_leave(self, node: cst.CSTNode) -> None:
        self.path = self.path.parent
        
class NamedStructurePathProvider(StructurePathProvider):
    """
    A class to provide named paths for metadata files.
    """

    def node_name(self, node: cst.CSTNode) -> str:
        """
        Returns the name of the node class with its name if available.
        """
        if hasattr(node, 'name'):
            return f"{node.__class__.__name__}({node.name.value})"
        return super().node_name(node)
        
        
class UniqueStructurePathProvider(StructurePathProvider):
    """
    A class to provide unique paths for metadata files.
    """

    @override
    def node_name(self, node: cst.CSTNode) -> str:
        """
        Returns the name of the node class with a unique identifier.
        """
        pos = self.get_metadata(PositionProvider, node, None)
        return f"{node.__class__.__name__}({pos.start.line}:{pos.start.column})"