from pathlib import Path
from typing import Sequence

from . import state
from .CompileError import CompileError
from .Interactive.ShaderInterface import ShaderInterface
from .Interactive.mx_interactive_types import Value
from .Preprocessor.macros import undefine_all_macros, Macro, define_macro
from .compile import compile_
from .document import new_document, get_document
from .file_utils import handle_input_path, handle_output_path
from .mx_wrapper import Uniform
from .post_process import post_process


def compile_file(mxsl_path: str | Path,
                 mtlx_path: str | Path = None,
                 *,
                 mtlx_version: str = None,
                 globals: dict[str, Uniform] = None,
                 main_func: str = None,
                 main_args: Sequence[Uniform] = None,
                 add_include_dirs: Sequence[Path] = None,
                 add_macros: Sequence[str | Macro] = None,
                 validate=False) -> None:
    globals = globals or {}
    main_args = main_args or []
    add_include_dirs = add_include_dirs or []
    add_macros = add_macros or []

    mxsl_filepaths = handle_input_path(mxsl_path)

    for mxsl_filepath in mxsl_filepaths:
        mtlx_filepath = handle_output_path(mtlx_path, mxsl_filepath)

        new_document()

        state.clear()
        state.add_globals(globals)

        include_dirs = add_include_dirs + [mxsl_filepath.parent, Path(".")]

        undefine_all_macros()
        for macro in add_macros:
            define_macro(macro)

        mtlx_version = compile_(mxsl_filepath, mtlx_version, include_dirs, is_main=True)
        _call_main(mxsl_filepath, main_func, main_args)
        post_process()

        if validate:
            success, message = get_document().validate(mtlx_version)
            if not success:
                message += "\n" + get_document().xml
                raise CompileError(message)

        with open(mtlx_filepath, "w") as file:
            file.write(get_document().xml)

        print(f"{mxsl_filepath.name} compiled successfully.")


def _call_main(file: Path, name: str | None, args: Sequence[Value]) -> None:
    shader = ShaderInterface()
    if name is None:
        if "main" in shader and shader.main.file == file:
            shader.main(*args)
    else:
        shader[name](*args)
