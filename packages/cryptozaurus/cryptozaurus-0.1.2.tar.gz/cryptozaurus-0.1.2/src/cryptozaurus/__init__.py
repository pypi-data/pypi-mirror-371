from importlib.metadata import version, PackageNotFoundError

from .main import is_timestamp_valid

__all__ = [
    "is_timestamp_valid",
]

try:
    __version__ = version("cryptozaurus")
except PackageNotFoundError:
    __version__ = "0.0.0"


def main() -> None:
    print("cryptozaurus", __version__)
