from src import scraping
from tqdm import tqdm
import yaml


class Main():

    def __init__(self, config="config.yml"):

        with open(config, "r") as fin:
            self.config = yaml.safe_load(fin)

        self.parsed_text = []

    def scrape_all(self):
        pages = self.config["page_ids"]

        for page in tqdm(pages):
            raw_text = scraping.fetch_html(page["url"], page["id"])
            parsed_text = scraping.extract_sentences(raw_text, page["id"])
            self.parsed_text.append(parsed_text)

        return self.parsed_text

    def inspect(self, text=None, lines=10):

        if text is None:
            text = self.parsed_text[0]


if __name__ == "__main__":
    M = Main()
    M.scrape_all()
