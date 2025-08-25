from .loader import lib  # Import the library first
from .audio_processing import AudioProcessor
from ._version import __version__, version_info

__all__ = ['AudioProcessor', '__version__', 'version_info', 'lib']