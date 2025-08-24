import ast

from nanodjango import hookimpl
from nanodjango.convert import Converter
from nanodjango.convert.converter import Resolver


@hookimpl
def convert_build_settings(
    converter: Converter, resolver: Resolver, settings_ast: ast.AST
):
    print("Hook: postgres")
    snippet = """
DATABASES = {
    "default": env.db_url(default="postgres://project:password@localhost:5432/project")
}
    """
    tree = ast.parse(snippet, mode="exec")
    settings_ast.body.append(tree)
