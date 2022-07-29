from src import scraping, ui
from src.warscroll import Warscroll
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


def parse_ws(ws):
    model_name = "hame"
    raw_tables = ws.find_all("table")
    raw_profile = ws.find("div", class_="ShowPitcheBattleProfile")
    raw_abilities = ws.find_all("div", class_="BreakInsideAvoid")


if __name__ == "__main__":
    M = Main()
    M.scrape_all()

    from bs4 import BeautifulSoup as BS
    soup = BS(M.raw_text['sbgl_ws'], "html.parser")
    ws_list = soup.find_all("div", class_="datasheet pagebreak")
    ws = ws_list[0]

    # Tables
    tables = ws.find_all("table")
    tab = tables[0]
    df = Warscroll.parse_ws_table(tab)

    # Combat Profile
    # profile = ws.find("div", class_="ShowPitchedBattleProfile")
    # pp = Warscroll.parse_ws_profile(profile)

    # Class-Based
    pws = Warscroll.from_html(ws)
