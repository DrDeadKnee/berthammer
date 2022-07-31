from bs4 import BeautifulSoup as BS
from .utils import int_it


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

        self.movement = None
        self.save = None
        self.wounds = None
        self.bravery = None

        self.weapon_profiles = None
        self.damage_tables = None

        self.magic = None
        self.rules = None
        self.abilities = None
        self.keywords = None

    @classmethod
    def from_html(cls, html):
        # Initialize Warscroll
        ws = Warscroll()

        # Establish html, name, keywords
        ws.html = BS(
            str(html).replace('<img src="/aos3/img/asterix.png"/>', " * "),
            "html.parser"
        )
        ws.name = ws.infer_name(html)
        ws.keywords = ws.extract_keywords(html)

        # Loop over tables and extract info
        wstables = html.find_all("div", "wsTable")
        ws.weapon_profiles = ws.parse_ws_table(wstables[0].find("table"))
        if len(wstables) > 1:
            ws.damage_tables = ws.parse_ws_table(wstables[1].find("table"))

        # Parse and store the pitched battle profile
        raw_profile = html.find("div", class_="ShowPitchedBattleProfile")
        profile = ws.parse_ws_profile(raw_profile)
        for key in profile:
            setattr(ws, key, profile[key])

        # ws.unit_size = int(profile["Unit Size"])
        # ws.points = int(profile["Points"])
        # ws.battlefield_role = profile["Battlefield Role"]
        # ws.base_size = profile["Base size"]
        # ws.notes = profile["Notes"]

        # Parse and store the top left card
        card = ws.parse_ws_card(html)
        for key in card:
            setattr(ws, key, int_it(card[key]))

        # Parse and store abilities
        try:
            rules_abilities = ws.parse_text(html)
            for key in rules_abilities:
                setattr(ws, key, rules_abilities[key])
        except ValueError:
            ws.abilities = "Error"

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
                key = keyval[0].strip().lower().replace(" ", "_")
                parsed[key] = keyval[1].strip()

        return parsed

    @staticmethod
    def parse_ws_card(warscroll):
        """
        Parses the unit card (movement, wounds, etc.) into a dict.

        args:
            warscroll (bs4.element): beautiful soup html element containing the full warscroll.
        returns:
            parsed (dict): Dictionary of warscroll card (movement, save, wounds, bravery)
        """
        return {
            "movement": warscroll.find("div", class_=["wsMoveCt", "wsMove"]).text,
            "save": warscroll.find("div", class_="wsSave").text,
            "wounds": warscroll.find("div", class_="wsWounds").text,
            "bravery": warscroll.find("div", class_="wsBravery").text
        }

    @staticmethod
    def extract_keywords(warscroll):
        """
        Finds keywords and returns as list

        args:
            warscroll (bs4.element): Beautiful soup html element containing the full warscroll.
        returns:
            keywords (list[string]): List of Keywords in the warscroll.
        """
        kw_line = warscroll.find("td", class_="wsKeywordLine")
        keywords = [i.strip() for i in kw_line.text.split(",")]
        return keywords

    # TODO parse individual abilities
    @staticmethod
    def parse_text(warscroll):
        """
        Recursively searches some div elements containing rules and abilities of relevance to the
        warscroll. Parses and returns a dict of the relevant sections
        args:
            warscroll (bs4.element): Beautiful soup html element containing the full warscroll.
        returns:
            rulesetc (dict): Dictionary of ability sections and the entries of each section.
        """
        rulesetc = {}

        sections = warscroll.find_all("div", class_="wsAbilityHeader")
        sect_text = [i.text.strip() for i in sections]
        desc_idx = sect_text.index("DESCRIPTION")
        print(desc_idx)

        for i in range(desc_idx, len(sections)):
            title = sect_text[i].lower().replace(" ", "_")
            text = []
            n = sections[i].find_next("div", class_=["BreakInsideAvoid", "wsAbilityHeader"])
            while (sum([(j in n.text) for j in sect_text]) == 0):
                try:
                    text.append(n.text)
                    n = n.find_next("div", class_=["BreakInsideAvoid", "wsAbilityHeader"])
                except (AttributeError, TypeError):
                    break

                if n is None:
                    break

            rulesetc[title] = text

        return rulesetc
