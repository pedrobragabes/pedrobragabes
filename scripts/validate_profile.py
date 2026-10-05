"""Validate the profile's local assets without requiring external services."""
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
readme = (root / 'README.md').read_text(encoding='utf-8')
assert readme.strip(), 'README must not be empty'
assert not re.search(r'github\.com/yourusername|example\.com', readme), 'Replace placeholder links'


class ProfileImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.local_images = 0

    def handle_starttag(self, tag, attrs):
        if tag != 'img':
            return
        attrs = dict(attrs)
        assert attrs.get('alt', '').strip(), 'Profile images need an alternative description'
        assert attrs.get('src', '').strip(), 'Image source must not be empty'
        source = urlsplit(attrs['src'])
        if source.scheme or source.netloc:
            assert source.scheme == 'https', 'Remote profile images must use HTTPS'
            return
        image = (root / unquote(source.path)).resolve()
        assert image.is_relative_to(root), 'Local image must stay inside the repository'
        assert image.is_file() and image.stat().st_size, f'Missing or empty image: {source.path}'
        if image.suffix.lower() == '.svg':
            assert ET.parse(image).getroot().tag == '{http://www.w3.org/2000/svg}svg', 'Invalid SVG image'
        self.local_images += 1


images = ProfileImages()
images.feed(readme)
assert images.local_images, 'Keep a local profile image available without external card services'
print('Profile README and local image references are valid')
