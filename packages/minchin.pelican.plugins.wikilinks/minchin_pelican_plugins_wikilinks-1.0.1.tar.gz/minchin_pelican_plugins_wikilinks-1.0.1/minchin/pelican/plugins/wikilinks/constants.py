__title__ = "minchin.pelican.plugins.wikilinks"
__version__ = "1.0.1"
__description__ = "Support Wikilinks when generating Pelican sites."
__author__ = "W. Minchin"
__email__ = "w_minchin@hotmail.com"
__url__ = "http://blog.minchin.ca/label/wikilinks-pelican/"
__license__ = "MIT License"

LOG_PREFIX = "[Wikilinks]"


SOURCE_EXTS = tuple(
    [
        ".md",
        ".markdown",
        ".mkd",
        ".mdown",
        ".rst",
        ".rest",
        ".htm",
        ".html",
    ]
)

IMAGE_EXTS = tuple(
    [
        ".gif",
        ".tif",
        ".tiff",
        ".webp",
        ".jpg",
        ".jpeg",
        ".png",
        # ".pdf",
        ".svg",
    ]
)
VIDEO_EXTS = tuple(
    [
        ".mp4",
    ]
)
AUDIO_EXTS = tuple(
    [
        ".mp3",
        ".flac",
    ]
)
_OTHER_STATIC_EXTS = tuple(
    [
        ".pdf",
    ]
)

STATIC_EXTS = IMAGE_EXTS + VIDEO_EXTS + AUDIO_EXTS + _OTHER_STATIC_EXTS

GENERATOR_PAGE_LISTS = [
    "articles",
    "translations",
    "hidden_articles",
    "hidden_translations",
    "drafts",
    "draft_translations",
    "pages",
    "hidden_pages",
    "draft_pages",
    "staticfiles",
]
