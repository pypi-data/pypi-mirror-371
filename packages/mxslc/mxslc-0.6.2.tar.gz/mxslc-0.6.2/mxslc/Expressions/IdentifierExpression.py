from . import Expression
from .. import state, node_utils
from ..DataType import DataType
from ..Token import Token
from ..mx_wrapper import Node, Uniform


class IdentifierExpression(Expression):
    def __init__(self, identifier: Token):
        super().__init__(identifier)
        self.__identifier = identifier

    @property
    def identifier(self) -> Token:
        return self.__identifier

    @property
    def _value(self) -> Uniform | None:
        node = state.get_node(self.__identifier)
        while node.category in ["dot", "constant"]:
            input_name = "in" if node.category == "dot" else "value"
            input_ = node.get_input(input_name)
            if input_.has_literal:
                return input_.literal
            node = input_.connected_node
            if node is None:
                return None
        return None

    def instantiate_templated_types(self, template_type: DataType) -> Expression:
        return IdentifierExpression(self.__identifier)

    def _init(self, valid_types: set[DataType]) -> None:
        # raises exception if node is not found
        _ = state.get_node(self.__identifier)

    @property
    def _data_type(self) -> DataType:
        node = state.get_node(self.__identifier)
        return node.data_type

    def _evaluate(self) -> Node:
        old_node = state.get_node(self.__identifier)
        new_node = node_utils.dot(old_node)
        return new_node

    def __str__(self) -> str:
        return str(self.__identifier)
