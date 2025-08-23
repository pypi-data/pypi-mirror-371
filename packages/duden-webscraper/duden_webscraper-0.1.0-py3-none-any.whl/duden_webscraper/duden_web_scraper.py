import re
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from .endpoint import Endpoint
from .word_info_error import WordInfoError
from .word_not_found_error import WordNotFoundError

class DudenWebScraper:
    MIN_ATTEMPTS = 1

    def __init__(self):
        self.number_attempts = self.MIN_ATTEMPTS

    def get_word_info(self, word: str) -> dict:
        word = self.__convert(word)

        response = self.__get(Endpoint.ORTHOGRAPHY + "/" + word)

        if response is None:
            raise WordNotFoundError(f"the word {word} was not found")

        main = response.find('article')
        tuples_items = main.find_all(class_='tuple')
        tuples_items_contents = tuples_items[0].find(class_="tuple__val").text

        frequency = 0
        word_usage = None

        second_tuple_item = tuples_items[1].find(class_="tuple__key").text


        is_frequency = second_tuple_item.find("Häufigkeit") == 0
        frequency_position = 1 if is_frequency else 2

        if frequency_position == 2:
            word_usage = second_tuple_item.find(class_="tuple__val").text

        frequency_tuples = tuples_items[frequency_position].find(class_="tuple__val").find(class_="shaft__full")

        if len(frequency_tuples) > 0:
            frequency = frequency_tuples.text

        tuples_contents_pieces = tuples_items_contents.split(", ")
        word_gender = None

        if len(tuples_contents_pieces) > 1:
            word_gender = tuples_contents_pieces[1] if tuples_contents_pieces[1] is not None else None

        lemma = word
        determiner = main.find(class_="lemma__determiner")
        lemma_determiner = determiner.text if len(determiner) > 0 else None

        spelling_items = main.select("#rechtschreibung .tuple")
        spelling = self.__parse_spelling(spelling_items)

        meaning_items = main.select("#bedeutungen ol li")
        meaning = self.__parse_meanings(meaning_items)

        return {
            "lemma": lemma,
            "lemma_determiner": lemma_determiner,
            "word_type": tuples_contents_pieces[0],
            "word_usage": word_usage,
            "word_gender": word_gender,
            "frequency": frequency,
            "spelling": spelling,
            "meaning": meaning,
        }

    def __parse_meaning_kernel_tuples(self, tuples) -> list[dict]:
        results = []

        for note in tuples:
            results.append({
                "title": note.find(class_="tuple__key").text,
                "items": [
                    note.find(class_="tuple__val").text,
                ],
            })

        return results

    def __parse_meaning_kernel_notes(self, notes) -> list[dict]:
        results = []

        for note in notes:
            items = []

            for item in note.select(".note__list li"):
                items.append(item.text)
                results.append({
                    "title": note.find(class_="note__title").text,
                    "items": items,
                })

        return results

    def __parse_meaning_kernel(self, item) -> dict:
        parsedFigured = None
        figure = None
        enumeration_text = None
        notes = []
        tuples = []

        if not isinstance(item, NavigableString) and item.select("dl.note"):
            notes = item.select("dl.note")
        if not isinstance(item, NavigableString) and item.select("dl.tuple"):
            tuples = item.select("dl.tuple")
        if not isinstance(item, NavigableString) and item.find("figure"):
            figure = item.find("figure")
        if not isinstance(item, NavigableString) and item.find(class_="enumeration__text"):
            enumeration_text = item.find(class_="enumeration__text")
            enumeration_text = enumeration_text.text if len(enumeration_text) > 0 else None

        notes_list = []

        if len(notes) > 1:
            notes_list = self.__parse_meaning_kernel_notes(notes)
        else:
            notes_list = self.__parse_meaning_kernel_tuples(tuples)

        if figure:
            parsedFigured = {
                "link": figure.find("a")["href"],
                "caption": figure.find(class_="depiction__caption").text,
            }

        return {
            "text": enumeration_text,
            "figure": parsedFigured,
            "notes": notes_list,
        }

    def __parse_meanings(self, meanings) -> list:
        results = []

        for item in meanings:
            items = []
            sublists = item.find(class_="enumeration__sub-item")

            if sublists is None:
                continue

            if len(sublists) < 1:
                items.append(self.__parse_meaning_kernel(item))
                continue
            else:
                for sublist in sublists:
                    items.append(self.__parse_meaning_kernel(sublist))

            results.append(items)

        return results

    def __parse_spelling(self, spelling) -> (Tag | NavigableString | None):
        result = []

        for item in spelling:
            title = item.find(class_="tuple__key").text
            value = item.find(class_="tuple__val")
            result.append({
                "title": title,
                "value": value.text if title != "Verwandte Form" else value.find("a").text,
            })

        return result

    def __get(self, endpoint: str):
        response = requests.get(Endpoint.BASE + endpoint)

        if response.status_code != 200:
            raise WordInfoError("failed to get word info")

        soup = BeautifulSoup(response.content, "html.parser")
        return soup.find('body')

    def __convert(self, word: str) -> str:
        patterns = {
            '/ä/': 'ae',
            '/ö/': 'oe',
            '/ü/': 'ue',
            '/ß/': 'sz',
        }

        for pattern, replacement in patterns.items():
            word = re.sub(pattern, replacement, word)

        return word
