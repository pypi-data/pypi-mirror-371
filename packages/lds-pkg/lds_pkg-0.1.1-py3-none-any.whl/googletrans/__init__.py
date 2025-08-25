"""Free Google Translate API for Python. Translates totally free of charge."""
__all__ = ('Translator', 'AsyncTranslator'),
__version__ = '4.0.0-rc.1'


from .client import Translator
from .constants import LANGCODES, LANGUAGES  # noqa
from .async_client import Translator as AsyncTranslator