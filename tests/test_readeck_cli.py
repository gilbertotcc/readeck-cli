from typing import TYPE_CHECKING

from readeck_cli import main


if TYPE_CHECKING:
    import pytest


def test_main_prints_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    main()

    captured = capsys.readouterr()
    assert captured.out == "Hello from readeck-cli!\n"
