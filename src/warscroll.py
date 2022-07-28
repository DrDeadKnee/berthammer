from bs4 import BeatifulSoup as BS


class Warscroll(object):

    def __init__(self):
        self.html = None
        self.name = None
        self.abilities = None
        self.weapon_profiles = None
        self.damage_tables = None
        self.keywords = None

    @classmethod
    def populate_from_html(cls, html):
        return ws

    @classmethod
    def populate_from_dataset(cls, name):
        return None
