from collections import defaultdict
import dataclasses
from typing import get_origin, get_args
import typing
import libcst as cst
from functools import partial
from argumentize import argumentize
from libcst._nodes.internal import *
from libcst.metadata import ParentNodeProvider
from utils import print


class RemovalAllowedProvider(cst.VisitorMetadataProvider[tuple[cst.CSTNode, str, bool, str]]): # parent, attribute, is_removal_allowed, reason

    """
    For each node determines whether it can be removed.
    """

    def visit_required(self,
        parent: cst.CSTNode, fieldname: str, node: cst.CSTNode, visitor: cst.CSTVisitorT
    ) -> cst.CSTNode:
        print(f"Visiting {type(node).__name__} in {type(parent).__name__} attribute '{fieldname}'")
        self.restriction_map[parent][fieldname] = 'required'
        return node
    
    def visit_iterable(self,
        parent: cst.CSTNode, fieldname: str, children: typing.Iterable[cst.CSTNodeT], visitor: cst.CSTVisitorT
    ) -> typing.Iterable[cst.CSTNodeT]:
        print(f"Visiting iterable in {type(parent).__name__} attribute '{fieldname}'")
        self.restriction_map[parent][fieldname] = 'iterable'
        return children

    def visit_sequence(self,
        parent: cst.CSTNode, fieldname: str, children: typing.Sequence[cst.CSTNodeT], visitor: cst.CSTVisitorT
    ) -> typing.Sequence[cst.CSTNodeT]:
        print(f"Visiting sequence in {type(parent).__name__} attribute '{fieldname}'")
        self.restriction_map[parent][fieldname] = 'sequence'
        return children
    
    def visit_optional(self,
        parent: cst.CSTNode, fieldname: str, node: cst.CSTNode, visitor: cst.CSTVisitorT
    ) -> cst.CSTNode:
        print(f"Visiting optional in {type(parent).__name__} attribute '{fieldname}'")
        self.restriction_map[parent][fieldname] = 'optional'
        return node

    def visit_body_iterable(self,
        parent: cst.CSTNode, fieldname: str, children: typing.Iterable[cst.CSTNodeT], visitor: cst.CSTVisitorT
    ) -> typing.Iterable[cst.CSTNodeT]:
        print(f"Visiting body iterable in {type(parent).__name__} attribute '{fieldname}'")
        self.restriction_map[parent][fieldname] = 'body_iterable'
        return children

    def visit_body_sequence(self,
        parent: cst.CSTNode, fieldname: str, children: typing.Sequence[cst.CSTNodeT], visitor: cst.CSTVisitorT
    ) -> typing.Sequence[cst.CSTNodeT]:
        print(f"Visiting body sequence in {type(parent).__name__} attribute '{fieldname}'")
        self.restriction_map[parent][fieldname] = 'body_sequence'
        return children

    
    def __init__(self):
        self._visit_and_replace_children = None
        self.restriction_map = defaultdict(dict)
        self.parent_queue  = list()
        self.attribute_name_queue = list()

    def define_restriction_map(self, parent: cst.CSTNode) -> None:
        argumentize(parent._visit_and_replace_children.__func__)(
            parent,
            visitor=None,
            visit_required=self.visit_required,
            visit_iterable=self.visit_iterable,
            visit_sequence=self.visit_sequence,
            visit_optional=self.visit_optional,
            visit_body_iterable=self.visit_body_iterable,
            visit_body_sequence=self.visit_body_sequence
        )
        return self.restriction_map[parent]

        
    def on_visit_attribute(self, parent: cst.CSTNode, fieldname: str) -> None:
        self.parent_queue.append(parent)
        self.attribute_name_queue.append(fieldname)

    def on_leave_attribute(self, original_node, attribute):
        self.parent_queue.pop()
        self.attribute_name_queue.pop()
        
    @property
    def current_parent(self) -> cst.CSTNode | None:
        return self.parent_queue[-1] if self.parent_queue else None

    @property
    def current_attribute(self) -> str | None:
        return self.attribute_name_queue[-1] if self.attribute_name_queue else None

    def on_visit(self, node):
        if self.current_parent is None:
            self.set_metadata(node, (None, None, True, None))
            return True
        is_removal_allowed = False
        
        attribute_type = self.current_parent.__dataclass_fields__[self.current_attribute].type
        print('Attribute type', attribute_type)
        is_optional = False
        
        if get_origin(attribute_type) is typing.Union:
            is_optional = type(None) in get_args(attribute_type) or None in get_args(attribute_type)
            if is_optional:
                # make attribute type without None
                if len(get_args(attribute_type)) == 2:
                    attribute_type = next(t for t in get_args(attribute_type) if t is not type(None) and t is not None)
                else:
                    # If there are more than two types, we need to remove None from the Union
                    attribute_type = typing.Union[tuple(t for t in get_args(attribute_type) if t is not type(None) and t is not None)]
                
            # If the attribute is a Union, we need to check if it is a sequence type
        is_sequence_type = get_origin(attribute_type) != typing.Union and issubclass(get_origin(attribute_type) or attribute_type, typing.Sequence)
        
        default_value = self.current_parent.__dataclass_fields__[self.current_attribute].default
        if default_value == dataclasses._MISSING_TYPE and is_optional:
            default_value = None
        elif default_value == dataclasses._MISSING_TYPE and is_sequence_type:
            default_value = []
        else:
            default_value = None # try None if it is not allowed it will crash in try block

        value = getattr(self.current_parent, self.current_attribute)
        reason = None
        try:
            updated_parent: cst.CSTNode = self.current_parent
            if is_sequence_type:
                if len(value) > 1:
                    # just remove the node from the sequence
                    new_value = [v for v in value if v != node]
                else:
                    # Check if we can replace entire sequence with default value
                    new_value = default_value
            else:
                new_value = default_value
                
            updated_parent = updated_parent.with_changes(**{self.current_attribute: new_value})
            restriction_map = self.define_restriction_map(updated_parent)
            if restriction_map[self.current_attribute] == 'required':
                raise ValueError(f"Cannot remove {type(node).__name__} from {self.current_parent.__class__.__name__} attribute {self.current_attribute} because it is required")
            updated_parent._validate()
            
            is_removal_allowed = True

        except Exception as e:
            print('Provider: Removal not allowed for', type(node).__name__, 'in', self.current_parent.__class__.__name__, 'attribute', self.current_attribute, e)
            is_removal_allowed = False
            reason = str(e)
        self.set_metadata(node, (self.current_parent, self.current_attribute, is_removal_allowed, reason))

        return True
    
    def on_leave(self, node: cst.CSTNode) -> None:
        self._visit_and_replace_children = None