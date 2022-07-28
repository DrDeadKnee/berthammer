from bs4 import BeautifulSoup as BS
from bs4 import Tag as BSTag


class Warscroll(object):

    def __str__(self):
        return self.name

    def __init__(self):
        self.html = None
        self.name = None

        self.unit_size = None
        self.points = None
        self.battlefield_role = None
        self.base_size = None
        self.notes = None

        self.weapon_profiles = None
        self.damage_tables = None

        self.abilities = None
        self.keywords = None

    @classmethod
    def from_html(cls, html):
        ws = Warscroll()

        if not isinstance(html, BSTag):
            html = BeautifulSoup(html, "html.parser")

        ws.html = html
        ws.name = ws.infer_name(html)

        wstables = html.find_all("div", "wsTable")
        ws.weapon_profiles = ws.parse_ws_table(wstables[0].find("table"))
        if len(wstables) > 1:
            ws.damage_tables = ws.parse_ws_table(wstables[1].find("table"))

        raw_profile = html.find("div", class_="ShowPitchedBattleProfile")
        profile = ws.parse_ws_profile(raw_profile)
        ws.unit_size = int(profile["Unit Size"])
        ws.points = int(profile["Points"])
        ws.battlefield_role = profile["Battlefield Role"]
        ws.base_size = profile["Base size"]
        ws.notes = profile["Notes"]

        return ws

    @classmethod
    def populate_from_dataset(cls, name):
        return None

    @staticmethod
    def infer_name(html):
        raw_name = html.find("h3", class_="wsHeader")
        name = str(raw_name.text).replace(".", "").strip()
        return name

    @staticmethod
    def parse_ws_table(table):
        """
        Parses an html warscroll table from wahapedia and returns
        a list where each element corresponds to a row from the original
        table, parsed into column: value pairs.

        args:
            table (bs4.element): Beautiful Soup html table.

        returns:
            parsedtable (list[dict]): List of rows, where each element is
                                      a dict of column name: value pairs.
        """
        mytable = []

        for row in table.find_all("tr", class_=["wsHeaderRow", "wsDataRow"]):
            if "wsHeaderRow" in row.attrs["class"]:
                headers = [str(i.text).strip() for i in row.find_all("td")]
            elif (("wsDataRow" in row.attrs["class"]) and
                  ("wsDataCell_short" not in row.attrs["class"])):

                new_row = {}
                raw_elements = row.find_all("td", class_=["wsDataCell", "wsLastDataCell"])

                for i in range(len(raw_elements)):
                    new_row[headers[i]] = str(raw_elements[i].text).strip()
                mytable.append(new_row)

        return mytable

    @staticmethod
    def parse_ws_profile(profile):
        """
        Parses the combat profile from a ws table.

        args:
            profile (bs4.element): Beautiful soup HTML element contatining battle frofile
        returns:
            parsed (dict): Dictionary-based encoding of combat profile.
        """
        elements = str(profile).split('class="redfont"')
        parsed = {}

        for i in elements:
            sane = str(BS(i, features="lxml").text)
            keyval = sane.replace(">", "").replace(".", "").split(":")

            if len(keyval) > 1:
                parsed[keyval[0].strip()] = keyval[1].strip()

        return parsed
