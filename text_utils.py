import re

import nltk
from nltk.corpus import cmudict

import flesch_kincaid


cmu = cmudict.dict()

def reduce(word):
    return ''.join([x for x in word.lower() if re.match(r'\w', x)])


def syllable_count(word):
    reduced = reduce(word)
    if (not len(reduced)) or (not reduced in cmu):
        return 0
    return len([x for x in list(''.join(list(cmu[reduced])[-1])) if re.match(r'\d', x)])


def sentences(db, nick):
    all_sentences = list()
    for row in db.get_lines_by_nick(nick):
        text = row[0]
        all_sentences.extend(nltk.tokenize.sent_tokenize(text))

    return all_sentences


def reading_level(db, nick):
    all_sentences = sentences(db, nick)

    if len(all_sentences) == 0:
        return 0.0

    avg = 0
    for s in all_sentences:
        l = flesch_kincaid.grade_level(s)
        if l > 0.0:
            avg += l

    avg /= len(all_sentences)

    return avg
