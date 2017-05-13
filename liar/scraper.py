import string
import re
from concurrent.futures import ThreadPoolExecutor

# TODO: Figure out why I can't use flask.current_app (I get an error about the context)

import datetime
import logging
import datefinder
import requests

from pymongo import IndexModel, ASCENDING, DESCENDING
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose

from liar.extensions import mongo
from .special_cases import *

PAGECOUNT_REGEX = re.compile(r"\s*Page \d+ of (?P<pages>\d+)")
PUBLISHED_REGEX = re.compile(r"\s*Published:")
SUBJECTS_REGEX = re.compile(r"\s*Subjects:")
STATEMENTS_PAGE = "http://www.politifact.com/truth-o-meter/statements/?page={0}"
STRIPPED_CHARS = string.whitespace + "\"\'"
BASEURL = "http://www.politifact.com{0}"
RULING_TYPES = ["Pants on Fire!", "False", "Mostly False", "Half-True", "Mostly True", "True"]


def get_page(number):
    response = requests.get(STATEMENTS_PAGE.format(number))
    # TODO: Handle case where this fails

    soup = BeautifulSoup(response.text, 'lxml')
    # TODO: Handle failure

    return soup


def get_num_pages():
    page1 = get_page(1)
    tag = page1.find("span", class_="step-links__current") # TODO: Handle failure
    match = PAGECOUNT_REGEX.match(tag.text) # TODO: Handle failure
    return int(match.group("pages"))


def get_all_pages(num_pages):

    urls = tuple(STATEMENTS_PAGE.format(i) for i in range(1, num_pages + 1))

    with ThreadPoolExecutor() as executor:
        pages = tuple(data for data in executor.map(requests.get, urls))

        return pages


def get_all_article_urls(pages):
    urls = set()
    for page in pages:
        soup = BeautifulSoup(page.text, 'lxml') # TODO: Handle failure
        links = soup.select(".statement__text a.link") # TODO: Handle failure
        full_links = tuple(map(lambda p: BASEURL.format(p['href']), links))
        urls.update(full_links) # TODO: Handle failure

    return urls


# These functions are here so that we don't dynamically instantiate lambdas
def identity(x):
    return x


def match_published(t):
    return PUBLISHED_REGEX.match(t.text)


def match_subjects(t):
    return SUBJECTS_REGEX.match(t.text)


def get_and_scrape_article(url: str):
    # TODO: Massage the URL in case it's invalid

    try:
        response = requests.get(url)
        response.raise_for_status()

        article = BeautifulSoup(response.text, 'lxml')

        statement = article.find("div", class_='statement')

        aside = article.select_one(".widget_about-article .widget__content")

        statement_meta = statement.find("p", class_="statement__meta")

        data = {"_id": url}

        if url in INVALID_URLS:
            # If this is one of the URLs that are known to be meaningless articles...
            return None

        ruling = statement.find("img", class_="statement-detail")
        data["ruling"] = ruling["alt"].strip(STRIPPED_CHARS)

        if data["ruling"] not in RULING_TYPES:
            # If this isn't a fact-check article... (no flip-flops allowed)
            return None

        statement_text = statement.select_one(".statement__text")
        data["statement"] = statement_text.text.strip(STRIPPED_CHARS)

        personality = statement_meta.find("a")
        data["personality"] = {
            "url": BASEURL.format(personality['href'].strip(STRIPPED_CHARS)),
            "name": personality.text.strip(STRIPPED_CHARS)
        }

        remark_date = tuple(datefinder.find_dates(tuple(statement_meta.strings)[-1]))
        if remark_date:
            data["remark_date"] = remark_date[0]
            # TODO: Some articles return the published date as 2017
            # ex: http://www.politifact.com/florida/statements/2012/mar/22/arthenia-joyner/democratic-senator-says-there-warnings-stand-your-/

        published_text = aside.find_all(match_published)[0]
        data["published_date"] = tuple(datefinder.find_dates(published_text.text))[0]

        subjects = aside.find_all(match_subjects)[0]
        subject_set = set()
        for s in subjects.find_all('a'):
            text = s.text.strip()
            if text in COLLAPSED_SUBJECTS:
                # If this is one of the subjects that we've merged together...
                text = COLLAPSED_SUBJECTS[text]

            if text not in FILTERED_TOPICS:
                subject_set.add(text)

        data["subjects"] = sorted(subject_set)

        sources = aside.find('div')
        data["sources"] = tuple(i for i in filter(identity, sources.text.splitlines())) # TODO: Fix

        return data
    except Exception as e:
        print("{0}: {1}".format(type(e).__name__, e))
        return None


def scrape():
    print("Starting the scraper")

    db = mongo.db
    statements = db.statements

    num_pages = get_num_pages()
    print("{0} pages found".format(num_pages))
    print("Getting list of articles")
    pages = get_all_pages(num_pages)
    print("Got all {0} pages, looking for articles".format(num_pages))

    urls = get_all_article_urls(pages)

    existing_urls = statements.distinct('_id')
    print("{0} articles found, and {1} are already in the database".format(len(urls), len(existing_urls)))

    urls.difference_update(existing_urls)

    print("Scraping data")
    scraped_statements = []
    with ThreadPoolExecutor() as executor:
        for data in executor.map(get_and_scrape_article, urls):
            if data is not None:
                scraped_statements.append(data)

        print("Inserting {0} statements into the database".format(len(data)))
        if scraped_statements:
            statements.insert_many(scraped_statements, False)

    print("Creating indexes")
    statements.create_index([("subjects", ASCENDING)], background=True)
    statements.create_index([("ruling", ASCENDING)], background=True)
    print("Created indexes")
    print("Done")
