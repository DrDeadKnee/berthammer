from src import scraping, ui
from src.warscroll import Warscroll
from bs4 import BeautifulSoup as BS
from tqdm import tqdm
import yaml


class Main():

    def __init__(self, config="config.yml"):

        with open(config, "r") as fin:
            self.config = yaml.safe_load(fin)

        self.text = {}
        self.raw_text = {}

        self.warscroll = {}
        self.raw_warscroll = {}

    def scrape_all(self):
        pages = self.config["text_pages"]
        ws_pages = self.config["warscroll_pages"]

        for page in tqdm(pages, desc="Downloading text"):
            pageid = page["id"]
            raw_text = scraping.fetch_html(page["url"], pageid)
            self.raw_text[pageid] = raw_text
            parsed_text = scraping.extract_sentences(raw_text, pageid)
            self.text[pageid] = parsed_text

        for wss in tqdm(ws_pages, desc="Downloading and parsing ws"):
            wsid = wss["id"]
            raw_text = scraping.fetch_html(wss["url"], wsid)
            self.raw_warscroll[pageid] = raw_text
            parsed_ws = scraping.ingest_warscrolls(raw_text)
            self.warscroll[wsid] = parsed_ws

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


if __name__ == "__main__":
    M = Main()
    M.scrape_all()
    k = M.warscroll["sce"]["Knight-Draconis"]
    v = M.warscroll["sbgl"]["Vampire Lord on Zombie Dragon"]
    k.display()
    v.display()
