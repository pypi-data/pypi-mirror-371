"""Entrypoint for cryptozaurus package."""

from importlib.metadata import PackageNotFoundError, version

from .main import is_timestamp_valid

__all__: list[str] = [
    "is_timestamp_valid",
]

try:
    __version__: str = version("cryptozaurus")
except PackageNotFoundError:
    __version__: str = "0.0.0"


def main() -> None:
    print("cryptozaurus", __version__)  # noqa: T201
