import logging

from pelican import signals

from .constants import __version__  # NOQA
from .initialize import check_settings, commonmark_version
from .reader import add_commonmark_reader, silence_builtin_reader_warning

# hide Markdown-IT logging (otherwise there's hundreds of lines...)
logging.getLogger("markdown_it").setLevel(logging.WARNING)


def register():
    """Register the plugin pieces with Pelican."""

    signals.initialized.connect(check_settings)
    signals.initialized.connect(commonmark_version)
    signals.readers_init.connect(add_commonmark_reader)
    signals.readers_init.connect(silence_builtin_reader_warning)
