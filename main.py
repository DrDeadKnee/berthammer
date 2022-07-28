from src import scraping, ui
from tqdm import tqdm
import yaml


class Main():

    def __init__(self, config="config.yml"):

        with open(config, "r") as fin:
            self.config = yaml.safe_load(fin)

        self.parsed_text = {}
        self.raw_text = {}

    def scrape_all(self):
        pages = self.config["page_ids"]

        print("Scraping data...")
        for page in tqdm(pages):
            pageid = page["id"]
            raw_text = scraping.fetch_html(page["url"], pageid)
            self.raw_text[pageid] = raw_text
            parsed_text = scraping.extract_sentences(raw_text, pageid)
            self.parsed_text[pageid] = parsed_text

        return self.parsed_text

    def inspect(self, parsed=True, lines=10):
        if parsed:
            doc_id = ui.choose(
                "Which page to inspect?",
                list(self.parsed_text.keys())
            )
            corpus = self.parsed_text[doc_id]
        else:
            doc_id = ui.choose(
                "Which page to inspect?",
                list(self.raw_text.keys())
            )
            corpus = self.raw_text[doc_id]

        for i in range(len(corpus)):
            print(corpus[i])
            if (i % lines == 0) and i > 0:
                ui.keepon(f"\nany key for the next {lines} lines\n>")


def parse_ws_table(table):
    mytable = []
    for row in table.find_all("tr", class_=["wsHeaderRow", "wsDataRow"]):
        new_row = []
        for column in row.find_all("td"):
            txt = column.text.strip()
            new_row.append(txt)
        if len(new_row) > 3:
            mytable.append(new_row)

    return mytable


def parse_ws_table2(table):
    mytable = []

    for row in table.find_all("tr", class_=["wsHeaderRow", "wsDataRow"]):
        print("\n\n------\n")
        print(row)
        if "wsHeaderRow" in row.attrs["class"]:
            headers = [str(i.text).strip() for i in row.find_all("td")]
            print("\nt1\n")
        elif (("wsDataRow" in row.attrs["class"]) and
              ("wsDataCell_short" not in row.attrs["class"])):

            print("\nt2\n")
            new_row = {}
            raw_elements = row.find_all("td", class_=["wsDataCell", "wsLastDataCell"])

            print(" - ".join([str(i) for i in raw_elements]))
            for i in range(len(raw_elements)):
                new_row[headers[i]] = str(raw_elements[i].text).strip()
            mytable.append(new_row)

        print(f"\n{mytable}\n")

    return mytable


def encode_ws_table(table):
    df = pd.DataFrame()
    columns = [
        "weapon_name",
        "range",
        "attacks",
        "to_hit",
        "to_wound",
        "rend",
        "damage"
    ]
    badrows = []

    missile = False
    for row in table:
        if row[0] == "MISSILE WEAPONS":
            missile = True
        elif row[0] == "MELEE WEAPONS":
            missile = False
        else:
            try:
                newrow = dict(zip(columns, row))
            except IndexError:
                badrows.append(row)

            newrow["weapon_type"] = {False: "melee", True: "missile"}[missile]
            df = df.append(newrow, ignore_index=True)

    return df, badrows


if __name__ == "__main__":
    M = Main()
    M.scrape_all()

    from bs4 import BeautifulSoup as BS
    import pandas as pd
    soup = BS(M.raw_text['sbgl_ws'], "html.parser")
    ws_list = soup.find_all("div", class_="datasheet pagebreak")
    ws = ws_list[0]
    tables = ws.find_all("table")
    tab = tables[0]
    df = parse_ws_table2(tab)
    # df = parse_ws_table(tab)
    # df2, badrows = encode_ws_table(df)
