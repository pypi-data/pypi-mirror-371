from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import MaterialX as mx

from .CompileError import CompileError
from .DataType import DataType, BOOLEAN, INTEGER, FLOAT, VECTOR2, VECTOR3, VECTOR4, COLOR3, COLOR4, STRING, FILENAME, \
    VOID
from .Keyword import Keyword
from .file_utils import pkg_path

"""
Pythonic wrappers around the generated MaterialX Python API.
"""

#
#   Type Definitions
#


type Uniform = bool | int | float | mx.VectorBase | str | Path
type Value = Node | Output | Uniform | None


#
#   Element
#


class Element:
    def __init__(self, source: mx.Element):
        self.__source = source

    @property
    def source(self) -> mx.Element:
        return self.__source

    @property
    def category(self) -> str:
        return self.source.getCategory()

    @property
    def name(self) -> str:
        return self.source.getName()

    @property
    def parent(self) -> Element:
        return Element(self.source.getParent())

    def create_valid_child_name(self, name: str) -> str:
        return self.source.createValidChildName(name)

    def get_child(self, name: str) -> Element:
        return Element(self.source.getChild(name))

    def remove(self) -> None:
        self.parent.source.removeChild(self.name)

    def get_attribute(self, name: str) -> str:
        return self.source.getAttribute(name)

    def set_attribute(self, name: str, value: str) -> None:
        self.source.setAttribute(name, value)

    def remove_attribute(self, name: str) -> None:
        self.source.removeAttribute(name)

    def __str__(self) -> str:
        return str(self.source)

    def __eq__(self, other: Element) -> bool:
        return self.source == other.source


#
#   Typed Element
#


class TypedElement(Element):
    def __init__(self, source: mx.InterfaceElement):
        super().__init__(source)

    @property
    def source(self) -> mx.TypedElement:
        return super().source

    @property
    def data_type(self) -> DataType:
        return DataType(self.source.getType())

    @data_type.setter
    def data_type(self, data_type: DataType | str) -> None:
        self.source.setType(str(data_type))

    @property
    def data_size(self) -> int:
        return self.data_type.size


#
#   Interface Element
#


class InterfaceElement(TypedElement):
    def __init__(self, source: mx.InterfaceElement):
        super().__init__(source)

    @property
    def source(self) -> mx.InterfaceElement:
        return super().source

    @property
    def has_inherit_string(self) -> bool:
        return self.source.hasInheritString()

    @property
    def inherits_from(self) -> InterfaceElement:
        return InterfaceElement(self.source.getInheritsFrom())

    @property
    def is_default_version(self) -> bool:
        if not self.source.hasVersionString():
            return True
        return self.source.getDefaultVersion()

    def has_input(self, name: str) -> bool:
        has_input = self.source.getInput(name) is not None
        if not has_input and self.has_inherit_string:
            return self.inherits_from.has_input(name)
        return has_input

    def add_input(self, name: str, value: Value = None, data_type: DataType = None) -> Input:
        assert not self.has_input(name)
        assert value is not None or data_type is not None
        if value is not None and data_type is not None:
            assert type_of(value) == data_type
        name = self.create_valid_child_name(name)
        data_type_str = str(data_type or type_of(value))
        input_ = Input(self.source.addInput(name, data_type_str))
        if value is not None:
            input_.value = value
        else:
            input_.value = data_type.default()
        return input_

    def get_input(self, name: str) -> Input:
        assert self.has_input(name), self.name
        input_ = Input(self.source.getInput(name))
        if input_ is None and self.has_inherit_string:
            return self.inherits_from.get_input(name)
        return input_

    @property
    def inputs(self) -> list[Input]:
        inputs = [Input(i) for i in self.source.getInputs()]
        inherited_inputs = self.inherits_from.inputs if self.has_inherit_string else []
        for inherited_input in inherited_inputs:
            if inherited_input.name not in [i.name for i in inputs]:
                inputs.append(inherited_input)
        return inputs

    @property
    def input_count(self) -> int:
        return len(self.inputs)

    def set_input(self, name: str, value: Value) -> Input:
        if self.has_input(name):
            input_ = self.get_input(name)
            input_.value = value
        else:
            assert value is not None
            input_ = self.add_input(name, value)
        return input_

    def remove_input(self, name: str) -> None:
        assert self.has_input(name)
        self.source.removeInput(name)

    def has_output(self, name: str) -> bool:
        has_output = self.source.getOutput(name) is not None
        if not has_output and self.has_inherit_string:
            return self.inherits_from.has_output(name)
        return has_output

    def add_output(self, name: str, value: Value = None, data_type: DataType = None) -> Output:
        assert not self.has_output(name)
        assert value is not None or data_type is not None
        if value is not None and data_type is not None:
            assert type_of(value) == data_type
        name = self.create_valid_child_name(name)
        data_type_str = str(data_type or type_of(value))
        output = Output(self.source.addOutput(name, data_type_str))
        if value is not None:
            output.value = value
        else:
            output.value = data_type.default()
        return output

    def get_output(self, name: str = None) -> Output:
        if name is None:
            if self.output_count == 1:
                return self.outputs[0]
            if self.has_output("out"):
                return self.get_output("out")
            raise AssertionError(self.name)
        assert self.has_output(name), self.name
        output = Output(self.source.getOutput(name))
        if output is None and self.has_inherit_string:
            return self.inherits_from.get_output(name)
        return output

    @property
    def output(self) -> Output:
        return self.get_output()

    @property
    def outputs(self) -> list[Output]:
        outputs = [Output(i) for i in self.source.getOutputs()]
        inherited_outputs = self.inherits_from.outputs if self.has_inherit_string else []
        for inherited_output in inherited_outputs:
            if inherited_output.name not in [i.name for i in outputs]:
                outputs.append(inherited_output)
        return outputs

    @property
    def output_count(self) -> int:
        return len(self.outputs)

    def set_output(self, name: str, value: Value) -> Output:
        if self.has_output(name):
            output = self.get_output(name)
            output.value = value
        else:
            assert value is not None
            output = self.add_output(name, value)
        return output

    def remove_output(self, name: str) -> None:
        assert self.has_output(name)
        self.source.removeOutput(name)


#
#   Graph Element
#


class GraphElement(InterfaceElement):
    def __init__(self, source: mx.GraphElement):
        super().__init__(source)

    @property
    def source(self) -> mx.GraphElement:
        return super().source

    def add_node(self, category: str, data_type: DataType | str) -> Node:
        return Node(self.source.addNode(category, "", str(data_type)))

    def remove_node(self, name: str) -> None:
        self.source.removeNode(name)

    def get_nodes(self, category="") -> list[Node]:
        return [Node(n) for n in self.source.getNodes(category)]

    def get_node(self, name: str) -> Node:
        return Node(self.source.getNode(name))


#
#   Port Element
#


class PortElement(TypedElement):
    def __init__(self, source: mx.PortElement):
        super().__init__(source)

    @property
    def source(self) -> mx.PortElement:
        return super().source

    @property
    def parent(self) -> InterfaceElement:
        return InterfaceElement(self.source.getParent())

    @property
    def is_output(self) -> bool:
        return isinstance(self.source, mx.Output)

    @property
    def connected_output(self) -> Output | None:
        return Output(self.source.getConnectedOutput())

    @property
    def connected_node(self) -> Node | None:
        return Node(self.source.getConnectedNode())

    @property
    def literal(self) -> Uniform | None:
        value = self.source.getValue()
        if self.data_type == FILENAME:
            return Path(value) if value is not None else None
        else:
            return value

    @property
    def has_literal(self) -> bool:
        return self.literal is not None

    @property
    def literal_string(self) -> str:
        return self.source.getValueString()

    @property
    def value(self) -> Value:
        return self.connected_output or self.connected_node or self.literal

    @value.setter
    def value(self, value: Value) -> None:
        self.clear_value()
        if value is None:
            self.remove()
        elif isinstance(value, Node):
            if value.is_null_node:
                self.remove()
                value.remove()
            else:
                self.source.setConnectedNode(value.source)
        elif isinstance(value, Output):
            self.source.setConnectedOutput(value.source)
        else:
            if isinstance(value, Path):
                value = str(value)
                if value == ".":
                    value = ""
                self.source.setValue(value, Keyword.FILENAME)
            else:
                self.source.setValue(value, str(self.data_type))

    @property
    def output_string(self) -> str | None:
        output = self.source.getOutputString()
        if output:
            return output
        else:
            return None

    @output_string.setter
    def output_string(self, output: str | None) -> None:
        if output is None:
            self.remove_attribute("output")
        else:
            assert self.literal is None
            assert self.interface_name is None
            self.source.setOutputString(output)

    @property
    def interface_name(self) -> str | None:
        name = self.source.getInterfaceName()
        if name:
            return name
        else:
            return None

    @interface_name.setter
    def interface_name(self, name: str | None) -> None:
        if name is None:
            self.remove_attribute("interfacename")
        else:
            assert not self.is_output
            self.clear_value()
            self.source.setInterfaceName(name)

    def clear_value(self) -> None:
        self.remove_attribute("value")
        self.remove_attribute("nodename")
        self.remove_attribute("output")
        self.remove_attribute("interfacename")
        self.remove_attribute("default")
        self.remove_attribute("nodegraph")


#
#   Document
#


class Document(GraphElement):
    def __init__(self, source: mx.Document | str | Path = None):
        if source is None:
            source = mx.createDocument()
        elif isinstance(source, str):
            doc = mx.createDocument()
            mx.readFromXmlString(doc, source)
            source = doc
        elif isinstance(source, Path):
            doc = mx.createDocument()
            mx.readFromXmlFile(doc, str(source))
            source = doc

        super().__init__(source)

    @property
    def source(self) -> mx.Document:
        return super().source

    def set_version_string(self, version: str) -> None:
        version = full_version(version)
        version = ".".join(version.split(".")[:2])
        self.source.setVersionString(version)

    def validate(self, version: str = None) -> tuple[bool, str]:
        version = full_version(version)
        if version == mx.getVersionString():
            tmp = Document(self.xml)
            tmp.set_version_string(version)
            tmp.load_standard_library(version)
            return tmp.source.validate()
        else:
            return True, ""

    def add_node_def(self, name: str, data_type: DataType, node_name: str) -> NodeDef:
        assert name.startswith("ND_")
        name = self.create_valid_child_name(name)
        node_def = NodeDef(self.source.addNodeDef(name, str(data_type), node_name))
        if data_type == VOID:
            node_def.remove_output("out")
        else:
            node_def.output.default = data_type.default()
        return node_def

    def add_node_graph_from_def(self, node_def: NodeDef) -> NodeGraph:
        name = node_def.name.replace("ND_", "NG_")
        node_graph = NodeGraph(self.source.addNodeGraph(name))
        node_graph.node_def = node_def
        return node_graph

    def get_node_def(self, name: str) -> NodeDef:
        return NodeDef(self.source.getNodeDef(name))

    @property
    def node_defs(self) -> list[NodeDef]:
        return [NodeDef(nd) for nd in self.source.getNodeDefs()]

    @property
    def node_graphs(self) -> list[NodeGraph]:
        return [NodeGraph(ng) for ng in self.source.getNodeGraphs()]

    @property
    def xml(self) -> str:
        return mx.writeToXmlString(self.source)

    def load_standard_library(self, version: str = None) -> None:
        version = full_version(version)
        libraries_dir = pkg_path(r"libraries")
        loaded = mx.loadLibraries([version], mx.FileSearchPath(str(libraries_dir)), self.source)
        if not loaded:
            raise CompileError(f"Unsupported MaterialX version: {version}.")

    def read_from_xml_file(self, xml_filepath: Path) -> None:
        mx.readFromXmlFile(self.source, str(xml_filepath))


#
#   Node
#


class Node(InterfaceElement):
    def __new__(cls, source: mx.Node):
        if source is None:
            return None
        else:
            return super().__new__(cls)

    def __init__(self, source: mx.Node):
        super().__init__(source)

    @property
    def source(self) -> mx.Node:
        return super().source

    @property
    def parent(self) -> GraphElement:
        return GraphElement(self.source.getParent())

    @property
    def name(self) -> str:
        return self.source.getName()

    @name.setter
    def name(self, name: str) -> None:
        if name != self.name:
            name = self.parent.create_valid_child_name(name)
            self.source.setName(name)

    @property
    def data_type(self) -> DataType:
        type_string = self.source.getType()
        if type_string == "multioutput":
            return VOID
        else:
            return DataType(type_string)

    @data_type.setter
    def data_type(self, data_type: DataType | str) -> None:
        self.source.setType(str(data_type))

    @property
    def is_null_node(self) -> bool:
        return self.category == Keyword.NULL

    @property
    def downstream_ports(self) -> list[PortElement]:
        return [PortElement(p) for p in self.source.getDownstreamPorts()]

    def add_interface_name(self, input_name: str, data_type: DataType, interface_name: str) -> Input:
        input_ = self.add_input(input_name, data_type=data_type)
        input_.interface_name = interface_name
        return input_

    def remove(self) -> None:
        self.parent.remove_node(self.name)

    def get_node_def(self) -> NodeDef:
        return NodeDef(self.source.getNodeDef())


#
#   Input
#


class Input(PortElement):
    def __new__(cls, source: mx.Input):
        if source is None:
            return None
        else:
            return super().__new__(cls)

    def __init__(self, source: mx.Input):
        super().__init__(source)

    def remove(self) -> None:
        self.parent.remove_input(self.name)


#
#   Output
#


class Output(PortElement):
    def __new__(cls, source: mx.Output):
        if source is None:
            return None
        else:
            return super().__new__(cls)

    def __init__(self, source: mx.Output):
        super().__init__(source)

    @property
    def default(self) -> str:
        return self.get_attribute("default")

    @default.setter
    def default(self, value: Uniform) -> None:
        self.clear_value()
        self.set_attribute("default", str(value))

    def remove(self) -> None:
        self.parent.remove_output(self.name)


#
#   NodeDef
#


class NodeDef(InterfaceElement):
    def __new__(cls, source: mx.NodeDef):
        if source is None:
            return None
        else:
            return super().__new__(cls)

    def __init__(self, source: mx.NodeDef):
        super().__init__(source)
        # nodedefs become "orphaned" unless there is an active pointer to their document
        # keep this pointer here stops it from becoming orphaned
        self.__ptr2parent = self.parent

    @property
    def source(self) -> mx.NodeDef:
        return super().source

    @property
    def parent(self) -> Document:
        return Document(self.source.getParent())

    @property
    def node_string(self) -> str:
        return self.source.getNodeString()

    def add_output(self, name: str, value: Value = None, data_type: DataType = None) -> Output:
        output = super().add_output(name, value, data_type)
        output.default = data_type.default()
        return output


#
#   NodeGraph
#


class NodeGraph(GraphElement):
    def __new__(cls, source: mx.NodeDef):
        if source is None:
            return None
        else:
            return super().__new__(cls)

    def __init__(self, source: mx.NodeGraph):
        super().__init__(source)

    @property
    def source(self) -> mx.NodeGraph:
        return super().source

    @property
    def parent(self) -> Document:
        return Document(self.source.getParent())

    @property
    def node_def(self) -> NodeDef:
        return NodeDef(self.source.getNodeDef())

    @node_def.setter
    def node_def(self, node_def: NodeDef) -> None:
        self.source.setNodeDef(node_def.source)


#
#   VectorBase Monkey Patch
#


def vector_mul(self: mx.VectorBase, other: Any) -> mx.VectorBase:
    if isinstance(other, float):
        other = self.__class__(other)
    assert isinstance(other, self.__class__)
    return self.__class__([
        a * b
        for a, b
        in zip(self.asTuple(), other.asTuple())
    ])


def vector_rmul(self: mx.VectorBase, other: Any) -> mx.VectorBase:
    return self * other


def vector_neg(self: mx.VectorBase) -> mx.VectorBase:
    return self.__class__(
        [-c for c in self.asTuple()]
    )


mx.VectorBase.__mul__ = vector_mul
mx.VectorBase.__rmul__ = vector_rmul
mx.VectorBase.__neg__ = vector_neg


#
#   util functions
#


def type_of(value: Value) -> DataType:
    if isinstance(value, TypedElement):
        return value.data_type
    if isinstance(value, bool):
        return BOOLEAN
    if isinstance(value, int):
        return INTEGER
    if isinstance(value, float):
        return FLOAT
    if isinstance(value, mx.Vector2):
        return VECTOR2
    if isinstance(value, mx.Vector3):
        return VECTOR3
    if isinstance(value, mx.Vector4):
        return VECTOR4
    if isinstance(value, mx.Color3):
        return COLOR3
    if isinstance(value, mx.Color4):
        return COLOR4
    if isinstance(value, str):
        return STRING
    if isinstance(value, Path):
        return FILENAME
    raise AssertionError


def full_version(version: str = None) -> str:
    if version is None:
        return mx.getVersionString()
    if re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", version):
        return version
    if re.match(r"^[0-9]+\.[0-9]+$", version):
        if version == "1.38":
            return "1.38.10"
        if version == "1.39":
            return "1.39.3"
        else:
            return version + ".0"
    else:
        raise CompileError(f"Unsupported MaterialX version: {version}.")