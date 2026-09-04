import importlib
import pkgutil

from readeck_cli.infrastructure import readeck_client


def test_all_generated_submodules_import_cleanly() -> None:
    module_names = [
        module.name for module in pkgutil.walk_packages(readeck_client.__path__, readeck_client.__name__ + ".")
    ]

    assert module_names

    for module_name in module_names:
        importlib.import_module(module_name)
