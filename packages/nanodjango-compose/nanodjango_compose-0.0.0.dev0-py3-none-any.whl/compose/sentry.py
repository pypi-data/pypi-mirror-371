import ast

from nanodjango import hookimpl
from nanodjango.convert import Converter
from nanodjango.convert.converter import Resolver


@hookimpl
def convert_build_settings(
    converter: Converter, resolver: Resolver, settings_ast: ast.AST
):
    print("Hook: sentry")
    snippet = """    
if DSN := env.str("DJANGO_SENTRY_DSN", default=""):
    import sentry_sdk

    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(  # type: ignore
        DSN,
        integrations=[
            DjangoIntegration(),
        ],
        auto_session_tracking=False,
        traces_sample_rate=0,
        environment="production",
    )
    """
    tree = ast.parse(snippet, mode="exec")
    settings_ast.body.append(tree)
