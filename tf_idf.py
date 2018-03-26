import collections
import xml.etree.ElementTree as Elem

import math
from pymystem3 import Mystem
from utils import get_words


def get_keywords(articles_list):
    title_map = dict()
    annotate_map = dict()
    keyword_str = ''
    for doc_num, article in enumerate(articles_list):
        keyword_str += ' '.join([keyword.text for keyword in article.find('keywords').findall('keyword')])
        keyword_str += ' '
        annotate_map[doc_num] = article.find('title_mystem').text.split()
        title_map[doc_num] = article.find('annotate_mystem').text.split()
    return set(
        [word.strip() for word in Mystem().lemmatize(keyword_str) if len(word.strip()) > 2]), annotate_map, title_map


def write_to_file(filename, keyword_result):
    words = Elem.Element("tf_idf_words")
    words_dict = collections.OrderedDict(sorted(keyword_result.items()))
    for key, value in words_dict.items():
        word = Elem.SubElement(words, "word", attrib={'name': str(key)})
        documents = Elem.SubElement(word, "documents")
        for i, doc in value.items():
            document = Elem.SubElement(documents, "document", attrib={'number': str(i)})
            for j, val in doc.items():
                Elem.SubElement(document, str(j)).text = str(val)
    tree = Elem.ElementTree(words)
    tree.write(filename, encoding='utf-8', xml_declaration=True)


def calculate_tf_idf():
    word_map = get_words('index_mystem.xml')
    word_map_title = get_words('index_mystem_title.xml')
    word_map_annotate = get_words('index_mystem_annotate.xml')
    tree = Elem.parse('issue.xml')
    root = tree.getroot()
    articles = root.find('articles')
    keyword_result = dict()
    keyword_set, annotate_map, title_map = get_keywords(articles.findall('article'))
    doc_len = len(articles.findall('article'))
    for doc_num, article in enumerate(articles.findall('article')):
        article_list_len = len(annotate_map[doc_num])
        title_list_len = len(title_map[doc_num])
        sum_article_len = article_list_len + title_list_len
        for keyword in keyword_set:
            annotate_word_count = annotate_map[doc_num].count(keyword)
            title_word_count = title_map[doc_num].count(keyword)
            tf_idf_title = title_word_count / title_list_len
            tf_idf_annotate = annotate_word_count / article_list_len
            tf_idf = (title_word_count + annotate_word_count) / sum_article_len
            if word_map_title.get(keyword, None) is not None:
                tf_idf_title *= math.log(doc_len / len(word_map_title[keyword]))
            if word_map_annotate.get(keyword, None) is not None:
                tf_idf_annotate *= math.log(doc_len / len(word_map_annotate[keyword]))
            if word_map.get(keyword, None) is not None:
                tf_idf *= math.log(doc_len / len(word_map[keyword]))
                tf_idf_full = 0.4 * tf_idf_annotate + 0.6 * tf_idf_title
            if tf_idf > 0:
                if keyword_result.get(keyword, None) is None:
                    keyword_result[keyword] = {}
                keyword_result[keyword][doc_num] = {'tf_idf': tf_idf, 'tf_idf_full': tf_idf_full,
                                                    'tf_idf_title': tf_idf_title,
                                                    'tf_idf_annotate': tf_idf_annotate}
    write_to_file('tf_idf.xml', keyword_result)


calculate_tf_idf()
