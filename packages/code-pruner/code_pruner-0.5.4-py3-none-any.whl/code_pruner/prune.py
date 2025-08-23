from pathlib import Path
import libcst as cst

from .metadata.path_provider import NamedStructurePathProvider, UniqueStructurePathProvider
from .metadata.rules_provider import RemovalAllowedProvider
from .pruning.macher import NamedStructurePathMatcher, PathMatcher
from .pruning.transformers import RemoveTransformer

from .utils import print


def create_remove_list(root_node: cst.CSTNode, patterns) -> list[Path]:
    matcher: PathMatcher = NamedStructurePathMatcher(patterns)
    wrapper = cst.MetadataWrapper(root_node)
    node2named_structure_path = dict(wrapper.resolve(NamedStructurePathProvider))
    node2unique_structure_path = dict(wrapper.resolve(UniqueStructurePathProvider))
    node2unique_structure_path = dict(sorted(node2unique_structure_path.items(), key=lambda item: item[1], reverse=True))

    keep_map = dict()
    keep_path = Path()
    for node, unique_structure_path in node2unique_structure_path.items():
        named_path = node2named_structure_path[node]
        if not matcher.match(named_path):
            keep_path = unique_structure_path
            keep_map[unique_structure_path] = True
        else:
            if keep_path.is_relative_to(unique_structure_path):
                keep_map[unique_structure_path] = True
            else:
                keep_map[unique_structure_path] = False


    reversed_keep_map = dict(sorted(keep_map.items(), key=lambda item: item[0], reverse=False))
    unique_paths_to_remove = set()
    last_removed_path = None
    for unique_structure_path, should_keep in reversed_keep_map.items():
        should_remove = not should_keep
        if last_removed_path and unique_structure_path.is_relative_to(last_removed_path):
            continue
        elif should_remove:
            unique_paths_to_remove.add(unique_structure_path)
            last_removed_path = unique_structure_path
            

    remove_allowed_map = dict(wrapper.resolve(RemovalAllowedProvider))
    for node, (parent, attribute, removal_allowed, reason) in remove_allowed_map.items():
        unique_path = node2unique_structure_path[node]
        if unique_path in unique_paths_to_remove:
            print(f"{unique_path}: {removal_allowed}, Reason: {reason}")
            
    return list(unique_paths_to_remove)

def prune_code(code, patterns):
    root_node = cst.parse_module(code)
    wrapper = cst.MetadataWrapper(root_node)

    paths_to_remove = create_remove_list(root_node, patterns)
    transformer = RemoveTransformer(paths_to_remove)
    updated_node = wrapper.visit(transformer)
    return updated_node.code