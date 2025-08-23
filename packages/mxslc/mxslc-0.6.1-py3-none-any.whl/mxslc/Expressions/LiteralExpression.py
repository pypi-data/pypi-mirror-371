from . import Expression
from .. import node_utils
from ..CompileError import CompileError
from ..DataType import DataType, BOOLEAN, INTEGER, FLOAT, STRING, FILENAME
from ..Keyword import Keyword
from ..Token import Token
from ..mx_wrapper import Node, Uniform
from ..token_types import INT_LITERAL, FLOAT_LITERAL, STRING_LITERAL


class LiteralExpression(Expression):
    def __init__(self, literal: Token):
        super().__init__(literal)
        self.__literal = literal
        self.__null_type: DataType | None = None

    @property
    def _value(self) -> Uniform | None:
        return self.__literal.value

    def instantiate_templated_types(self, template_type: DataType) -> Expression:
        return LiteralExpression(self.token)

    def _init(self, valid_types: set[DataType]) -> None:
        if self.__literal == Keyword.NULL and len(valid_types) > 1:
            raise CompileError(f"null type is ambiguous.", self.token)
        self.__null_type = list(valid_types)[0]

    @property
    def _data_type(self) -> DataType:
        return {
            Keyword.TRUE: BOOLEAN,
            Keyword.FALSE: BOOLEAN,
            INT_LITERAL: INTEGER,
            FLOAT_LITERAL: FLOAT,
            STRING_LITERAL: STRING,
            Keyword.NULL: self.__null_type
        }[self.__literal]

    def _evaluate(self) -> Node:
        if self.__literal == Keyword.NULL:
            return node_utils.null(self.__null_type)
        else:
            return node_utils.constant(self.__literal.value)

    def __str__(self) -> str:
        return str(self.__literal)


class NullExpression(LiteralExpression):
    def __init__(self):
        super().__init__(Token(Keyword.NULL))
