from typing_extensions import Self


class P(list[str]):
    
    def __call__(self, **kwargs) -> Self:
        result = [pattern.replace(k, f"{k}({v})") for pattern in self for k, v in kwargs.items()]
        return P(result)


class Patterns:
    """
    Use only positive patterns to match nodes
    Negative patterns are not allowed here

    For negative patterns use ExceptPatterns
    """
    ALL = P(r"**")
    IMPORT = P([r"**/Import", r"**/ImportFrom"])
    COMMENT = P([r"**/Comment"])
    STRING_LITERAL = P([r"**/Expr/SimpleString"])
    ANN_ASSIGN = P([r"**/AnnAssign/Annotation"])
    PARAM_ANNOTATION = P([r"**/FunctionDef/**/Param/Annotation"])
    EMPTY = P([r"**/EmptyLine"])
    DECORATOR = P([r"**/Decorator"])
    CLASS_DEF = P([r"**/ClassDef"])
    CLASS_BODY = P([r"**/ClassDef/**/IndentedBlock/**"])
    CLASS_DOCSTRING = P([r"**/ClassDef/**/Expr/SimpleString"])
    FUNCTION_DEF = P([r"**/FunctionDef", r"**/AsyncFunctionDef"])
    FUNCTION_BODY = P([r"**/FunctionDef/**/IndentedBlock/**"])
    FUNCTION_DOCSTRING = P([r"**/FunctionDef/**/Expr/SimpleString"])


class ExceptPatternMeta(type):
    
    def __getattribute__(self, name):
        if name.startswith("_"):
            return super().__getattribute__(name)
        pattern_list = super().__getattribute__(name)
        if not isinstance(pattern_list, P):
            return pattern_list
        return P(f"!{pattern}" for pattern in pattern_list)
    
class ExceptPatterns(Patterns, metaclass=ExceptPatternMeta):
    pass
