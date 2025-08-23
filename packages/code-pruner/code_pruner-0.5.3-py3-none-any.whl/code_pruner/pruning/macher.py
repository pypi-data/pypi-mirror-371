from abc import abstractmethod
import re

from pathspec import PathSpec

class PathMatcher:
    """
    Abstract base class for path matchers.
    """
    @abstractmethod
    def match(self, path: str) -> bool:
        """
        Check if the path matches the specified patterns.
        """
        raise NotImplementedError("Subclasses must implement this method.")

class NamedStructurePathMatcher(PathMatcher):
    
    def __init__(self, patterns=None):
        processed_patterns = []
        for pattern in patterns or []:
            pattern = re.sub(r"FunctionDef(?!\(\w+\))", "FunctionDef(*", pattern)
            pattern = re.sub(r"ClassDef(?!\(\w+\))", "ClassDef(*", pattern)
            processed_patterns.append(pattern)
        self.patterns = PathSpec.from_lines('gitwildmatch', processed_patterns)
        
    def match(self, path: str) -> bool:
        """
        Check if the path matches any of the patterns.
        """
        return self.patterns.match_file(path)