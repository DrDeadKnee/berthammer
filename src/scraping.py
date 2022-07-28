import os
import requests
from bs4 import BeautifulSoup as BS


def fetch_html(url, dataname="unknown"):
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

    returns:
        raw_content (string): Long string of minimally processed html
    """
    # Prep paths to write
    rawout = os.path.join("data", "raw")
    if not os.path.isdir(rawout):
        os.makedirs(rawout)

    # Scrape and minimaly reformat
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
    )
    with open(os.path.join(rawout, dataname) + ".html", "w") as fout:
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
