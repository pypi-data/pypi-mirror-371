from pathlib import Path
import libcst as cst

from metadata.path_provider import NamedStructurePathProvider, UniqueStructurePathProvider
from metadata.rules_provider import RemovalAllowedProvider
from pruning.macher import NamedStructurePathMatcher, PathMatcher
from utils import print

class RemoveTransformer(cst.CSTTransformer):
    
    METADATA_DEPENDENCIES = (UniqueStructurePathProvider, RemovalAllowedProvider)
    
    def __init__(self, paths_to_remove: list[Path]):
        self.paths_to_remove = paths_to_remove
        
    def on_leave(self, original_node, updated_node):
        unique_path = self.get_metadata(UniqueStructurePathProvider, original_node, None)
        if unique_path in self.paths_to_remove:
            parent, attribute, removal_allowed, reason = self.get_metadata(RemovalAllowedProvider, original_node, True)
            if not removal_allowed:
                print(f"Removal not allowed for {unique_path}. Parent {type(parent).__name__} does not allow removal of attribute '{attribute}'.")
                return updated_node
            print(f"Removing node with path {unique_path}. Parent {type(parent).__name__}. Attribute '{attribute}'.")
            return cst.RemoveFromParent()
        else:
            return updated_node