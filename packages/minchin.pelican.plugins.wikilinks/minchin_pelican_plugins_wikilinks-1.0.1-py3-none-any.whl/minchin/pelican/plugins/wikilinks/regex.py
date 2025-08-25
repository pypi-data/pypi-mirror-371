import re

_base_wikilink_regex = (
    r"\[\[\s*(?P<filename>[^|\]]+)(\|\s*(?P<linkname>[^|\]\n\r]+))?\]\]"
)
wikilink_regex = re.compile(_base_wikilink_regex)
wikilink_file_regex = re.compile(r"!" + _base_wikilink_regex)
