from bs4 import BeautifulSoup as BS
from .utils import int_it
import os


class Warscroll(object):

    def __str__(self):
        return self.name

    def __init__(self):
        self.html = None
        self.name = None
        self.keywords = None

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
        self.raw_weaps = None
        self.damage_tables = None

        self.text_abilities = []
        self.magic = None
        self.rules = None
        self.abilities = None

    def display(self, output=False, show=True):
        """
        Print warscroll in human-readable form

        args:
            output (bool): Returns string that was built if true
            show (bool): Prints string that was built if true
        """
        # Name
        out = f"\n\n\n----\t----\t{self.name}\t----\t----\n"

        # Pitched battle profile
        out += f"\nProfile: \n\tpoints: {self.points} | "
        out += f"roles: {self.battlefield_role} | "
        out += f"base size: {self.base_size}"
        out += f"\n\tnotes: {self.notes}"

        # Card
        out += f"\n\nCard: \n\tmove: {self.movement}"
        out += f"\n\tsave: {self.save}"
        out += f"\n\twounds: {self.wounds}"
        out += f"\n\tbravery: {self.bravery}"

        # Weapon Tables Pretty Printing
        out += "\n\nWeapon Profiles:\n\t"
        basekeys = list(self.weapon_profiles[0].keys())
        pads = [
            max(
                [len("weapon_name")] +
                [len(i["weapon_name"]) for i in self.weapon_profiles]
            ) + 2
        ]
        pads += [len(i) + 2 for i in basekeys[1:]]

        for idx, key in enumerate(self.weapon_profiles[0].keys()):
            out += "\033[4m" + key.ljust(pads[idx]) + "\033[0m"

        for weapon in self.weapon_profiles:
            out += "\n\t"
            for idx, key in enumerate(weapon):
                out += str(weapon[key]).ljust(pads[idx])

        # Damage tables pretty printing
        if self.damage_tables is not None:
            out += "\n\nDamage Tables:\n\t"
            pads = [len(i) + 2 for i in self.damage_tables[0].keys()]
            for idx, key in enumerate(self.damage_tables[0].keys()):
                out += "\033[4m" + key.ljust(pads[idx]) + "\033[0m"

            for row in self.damage_tables:
                out += "\n\t"
                for idx, key in enumerate(row):
                    out += str(row[key]).ljust(pads[idx])

        # Text abilities
        if self.magic is not None:
            out += "\n\nMagic:"
            out += "\n".join([self._prettify_text(i) for i in self.magic])

        for section in self.text_abilities:
            out += "\n\n{}:".format(section.title())
            out += "\n".join([self._prettify_text(i) for i in getattr(self, section)])

        # Rules
        # Abilities
        # Kewords

        # Deal with options
        if show:
            print(out)

        if output:
            return out

    def _prettify_text(self, string, prefix="\n\t"):
        """
        Returns version of text which fits terminal width.
        """
        out = ""
        depth, width = os.popen("stty size", "r").read().split()
        width = int(width)
        if "\t" in prefix:
            width -= 8
        width += len(prefix.replace("\t", "").replace("\n", ""))

        strs = [string[i: i + width] for i in range(0, len(string), width)]

        for i in strs:
            out += f"{prefix}{i}"

        return out

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
        weapon_profiles = ws.parse_ws_table(wstables[0].find("table"))
        ws.raw_weaps = weapon_profiles
        ws.weapon_profiles = ws.cleanup_weapon_profiles(weapon_profiles)

        if len(wstables) > 1:
            ws.damage_tables = ws.parse_ws_table(wstables[1].find("table"))

        # Parse and store the pitched battle profile
        raw_profile = html.find("div", class_="ShowPitchedBattleProfile")
        profile = ws.parse_ws_profile(raw_profile)
        for key in profile:
            setattr(ws, key, profile[key])

        # Parse and store the top left card
        card = ws.parse_ws_card(html)
        for key in card:
            setattr(ws, key, int_it(card[key]))

        # Parse and store abilities
        try:
            rules_abilities = ws.parse_text(html)
            for key in rules_abilities:
                ws.text_abilities.append(key)
                setattr(ws, key, rules_abilities[key])
        except ValueError:
            ws.abilities = "Error"

        return ws

    @classmethod
    def populate_from_dataset(cls, name):
        return None

    @staticmethod
    def infer_name(html):
        """
        Infers unit name from bs4 element containing a wahapedia warscroll.

        args:
            html (bs4.element): Beautiful soup warscroll
        returns:
            name (string): Name from warscroll
        """
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
    def cleanup_weapon_profiles(weapon_profiles):
        """
        Cleans up weapon profiles for easy insertion into tables
        """
        new_profiles = []

        for profile in weapon_profiles:
            # Parse key categories
            if "MELEE WEAPONS" in profile:
                profile["weapon_name"] = profile["MELEE WEAPONS"]
                profile["attack_type"] = "melee"
                del profile["MELEE WEAPONS"]
            elif "MISSILE WEAPONS" in profile:
                profile["weapon_name"] = profile["MISSILE WEAPONS"]
                profile["attack_type"] = "missile"
                del profile["MISSILE WEAPONS"]

            # Rename keys
            new_keys = [
                i.strip().lower()
                 .replace("to wound to wnd", "to_wound")
                 .replace("damage dmg", "damage")
                 .replace(" ", "_")
                for i in profile
            ]

            # Pair keys with values and re-order, replace strings with ints
            temp_dict = dict(zip(new_keys, profile.values()))
            ordered = {
                "weapon_name": temp_dict["weapon_name"],
                "attack_type": temp_dict["attack_type"]
            }
            maybekeys = ["range", "attacks", "to_hit", "to_wound", "rend", "damage"]
            for i in maybekeys:
                if i in temp_dict:
                    val = str(temp_dict[i]).replace('"', "").replace("+", "")
                    try:
                        ordered[i] = int(val)
                    except ValueError:
                        ordered[i] = None
                else:
                    ordered[i] = None

            new_profiles.append(ordered)

        return new_profiles

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
            warscroll (bs4.element): beautiful soup html element containing
            the full warscroll.
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
            warscroll (bs4.element): Beautiful soup html element containing the
            full warscroll.
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
        Recursively searches some div elements containing rules and abilities of
        relevance to the warscroll. Parses and returns a dict of the relevant sections
        args:
            warscroll (bs4.element): Beautiful soup html element containing the
                                     full warscroll.
        returns:
            rulesetc (dict): Dictionary of ability sections and the entries of each section.
        """
        rulesetc = {}

        sections = warscroll.find_all("div", class_="wsAbilityHeader")
        sect_text = [i.text.strip() for i in sections]
        desc_idx = sect_text.index("DESCRIPTION")

        for i in range(desc_idx, len(sections)):
            title = sect_text[i].lower().replace(" ", "_")
            text = []
            n = sections[i].find_next("div", class_=["BreakInsideAvoid", "wsAbilityHeader"])
            while (sum([(j in n.text) for j in sect_text]) == 0):
                try:
                    cleanedish = (
                        n.text
                         .replace("   ", " ")
                         .replace("  ", " ")
                         .replace(" .", ".")
                         .replace(" ,", ",")
                    )
                    text.append(cleanedish)
                    n = n.find_next("div", class_=["BreakInsideAvoid", "wsAbilityHeader"])
                except (AttributeError, TypeError):
                    break

                if n is None:
                    break

            rulesetc[title] = text

        return rulesetc
