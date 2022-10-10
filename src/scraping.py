import os
import requests
from bs4 import BeautifulSoup as BS
from .warscroll import Warscroll


def fetch_html(url, dataname="unknown", cache_fetched=True, use_cached=True):
    """
    Function to fetch and store html as 'raw' data, although
    some string replacement is done beforehand to allow bs4 text
    rendering to work properly.

    args:
        url (string):       The site to scrape. This code assumes
                            a standard 3-column wahapedia page.
        dataname (string):  A short string representing the desired
                            output name. Files with that name will be
                            stored under the data directory.
        cache_fetched (bool): If true, will cache any new data that was
                              downloaded
        use_cached (bool): If true, will load any data on disk matching
                           a path determined by dataname if available,
                           rather than fetching remotely.

    returns:
        raw_content (string): Long string of minimally processed html
    """
    # State variables
    new_bolus = False

    # Prep paths to write
    rawout = os.path.join("data", "raw")
    filename = os.path.join(rawout, dataname) + ".html"
    if not os.path.isdir(rawout):
        os.makedirs(rawout)

    # Load locally if appropriate
    if use_cached and os.path.exists(filename):
        rawish_content = open(filename).read()

    # Scrape and minimaly reformat
    else:
        new_bolus = True
        raw_content = requests.get(url).text
        rawish_content = (
            raw_content
                .replace("</h1>", ". </h1>")
                .replace("</h2>", ". </h2>")
                .replace("</h3>", ". </h3>")
                .replace("</h4>", ". </h4>")
                .replace("</a>", " </a>")
                .replace("</b>", " </b>")
                .replace("<br>", ". <br>")
                .replace("</div>", " </div>")
                .replace("</li>", " </li>")
                .replace("</p>", " </p>")
                .replace("</td>", " </td>")
                .replace("</span>", " </span>")
                .replace('<img src="/aos3/img/asterix.png"/>', " * ")
        )

    if cache_fetched and new_bolus:
        with open(filename, "w") as fout:
            fout.write(rawish_content)
        fout.close()

    return rawish_content


def extract_sentences(raw_content, dataname="unknown"):
    """
    Parse raw html into dataset-freindly sentences using bs4
    text extraction. Then loops through all text to infer sentence chunks,
    and writes each sentence seperately to a processed text file.

    args:
        raw_content (string): A long string containing the web page's
                              content as 'raw' html.
        dataname (string):  A short string representing the desired
                            output name. Files with that name will be
                            stored under the data directory.

    returns:
        allrules (list[string]): List of all sentences from original code
    """

    # Prep paths to write
    textout = os.path.join("data", "text")
    if not os.path.isdir(textout):
        os.makedirs(textout)

    # Parse html with beautifulsoup
    soup = BS(raw_content, "html.parser")
    content = soup.find_all("div", class_=[
        "Columns1", "Columns2", "Columns3", "datasheet pagebreak"
    ])

    # Loop over sections, inferring sentence ends
    allrules = []
    for section in content:
        allrules += get_sentences(section.text)

    with open(os.path.join(textout, dataname) + ".txt", "w") as fout:
        for sentence in allrules:
            fout.write(sentence + "\n")
    fout.close()

    return allrules


def get_sentences(textblock):
    """
    Takes a block of text and infers sentence ends, assuming
    any '.' character without a digit to either side constitutes
    a sentence end.

    args:
        textblock (string): Block of text to be parsed.

    returns:
        sentences (list[string]): List where each element is a sentence.
    """
    sentences = []

    sentence_start, i = 0, 1
    while i < len(textblock) - 1:
        if textblock[i] in [".", "!", "?"]:
            c1 = textblock[i - 1].isdigit()
            c2 = textblock[i + 1].isdigit()
            if not (c1 and c2):
                sentences.append(textblock[sentence_start: i])
                sentence_start = i + 1
        i += 1
    return sentences


def ingest_warscrolls(ws_html, faction, grand_alliance):
    """
    Extracts warscrolls from wahapedia warscroll page,
    and loads them into a name: Warscroll dictionary where
    Warscroll is a special class containing the extracted
    data.

    args:
        ws_html (string): A long string containing a wahapedia
            warscroll page's html.
    returns:
        ws_parse (dict[string: Warscroll]): A dictionary with the
            warscroll names pointing to a parsed Warscroll object.
    """
    soup = BS(ws_html, "html.parser")
    ws_list = soup.find_all("div", class_="datasheet pagebreak")
    ws_parsed = {}

    for i in ws_list:
        if i.find("div", class_="nails-header").text.lower().strip() == "warscroll":
            ws_parsed[Warscroll.infer_name(i)] = Warscroll.from_html(i, faction, grand_alliance)

    return ws_parsed
