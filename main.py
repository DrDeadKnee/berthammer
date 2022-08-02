from src import scraping, ui
from src.warscroll import Warscroll
from bs4 import BeautifulSoup as BS
from tqdm import tqdm
import yaml


class Main():

    def __init__(self, config="config.yml"):

        with open(config, "r") as fin:
            self.config = yaml.safe_load(fin)

        self.parsed_text = {}
        self.raw_text = {}
        self.warscrolls = {}

    def scrape_all(self):
        pages = self.config["page_ids"]

        for page in tqdm(pages, desc="Downloading pages"):
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

    def load_warscrolls(self, page_id):
        self.warscrolls[page_id] = scraping.ingest_warscrolls(self.raw_text[page_id])


if __name__ == "__main__":
    M = Main()
    M.scrape_all()
    M.load_warscrolls("sbgl_ws")
    M.load_warscrolls("sce_ws")
