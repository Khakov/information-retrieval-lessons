import collections
import xml.etree.ElementTree as Elem

import math
from string import punctuation

from pymystem3 import Mystem
from utils import get_words, get_articles


class TF_IDF:
    def __init__(self):
        self.word_map = {}
        self.word_map_title = {}
        self.word_map_annotate = {}
        self.keyword_result = {}
        self.articles = {}
        self.result_query = {}

    def get_keywords(self, articles_list):
        title_map = dict()
        annotate_map = dict()
        full_map = dict()
        keyword_str = ''
        for doc_num, article in enumerate(articles_list):
            annotate_map[doc_num] = [word.strip(punctuation) for word in article.find('title_mystem').text.split()]
            title_map[doc_num] = [word.strip(punctuation) for word in article.find('annotate_mystem').text.split()]
            full_map[doc_num] = set(annotate_map[doc_num] + title_map[doc_num])
            keyword_str += ' '.join(full_map[doc_num])
            keyword_str += ' '
            for word in title_map[doc_num]:
                if self.word_map_title.get(word, None) is not None:
                    self.word_map_title[word].append(doc_num)
                else:
                    self.word_map_title[word] = [doc_num]
            for word in annotate_map[doc_num]:
                if self.word_map_annotate.get(word, None) is not None:
                    self.word_map_annotate[word].append(doc_num)
                else:
                    self.word_map_annotate[word] = [doc_num]
            for word in full_map[doc_num]:
                if self.word_map.get(word, None) is not None:
                    self.word_map[word].append(doc_num)
                else:
                    self.word_map[word] = [doc_num]

        return set(keyword_str.split()), annotate_map, title_map

    def write_to_file(self, filename, is_query=False):
        if is_query:
            keys = self.result_query.items()
        else:
            keys = self.keyword_result.items()
        words = Elem.Element("tf_idf_words")
        words_dict = collections.OrderedDict(sorted(keys))
        for key, value in words_dict.items():
            word = Elem.SubElement(words, "word", attrib={'name': str(key)})
            documents = Elem.SubElement(word, "documents")
            for i, doc in value.items():
                document = Elem.SubElement(documents, "document", attrib={'number': str(i)})
                for j, val in doc.items():
                    Elem.SubElement(document, str(j)).text = str(val)
        tree = Elem.ElementTree(words)
        tree.write(filename, encoding='utf-8', xml_declaration=True)

    def calculate_tf_idf(self):
        keyword_result = dict()
        self.articles = get_articles('issue.xml')
        keyword_set, annotate_map, title_map = self.get_keywords(self.articles)
        doc_len = len(self.articles)
        for doc_num, article in enumerate(self.articles):
            article_list_len = len(annotate_map[doc_num])
            title_list_len = len(title_map[doc_num])
            sum_article_len = article_list_len + title_list_len
            for keyword in keyword_set:
                annotate_word_count = annotate_map[doc_num].count(keyword)
                title_word_count = title_map[doc_num].count(keyword)
                # calc tf
                tf_idf_title = title_word_count / title_list_len
                tf_idf_annotate = annotate_word_count / article_list_len
                tf_idf = (title_word_count + annotate_word_count) / sum_article_len
                # calc tf * idf
                if self.word_map_title.get(keyword, None) is not None:
                    tf_idf_title *= math.log(doc_len / len(self.word_map_title[keyword]))
                else:
                    tf_idf_title = 0
                if self.word_map_annotate.get(keyword, None) is not None:
                    tf_idf_annotate *= math.log(doc_len / len(self.word_map_annotate[keyword]))
                else:
                    tf_idf_annotate = 0
                if self.word_map.get(keyword, None) is not None:
                    tf_idf *= math.log(doc_len / len(self.word_map[keyword]))
                    tf_idf_full = 0.4 * tf_idf_annotate + 0.6 * tf_idf_title
                else:
                    tf_idf = 0
                if tf_idf > 0:
                    if keyword_result.get(keyword, None) is None:
                        keyword_result[keyword] = {}
                    keyword_result[keyword][doc_num] = {'tf_idf': tf_idf, 'tf_idf_full': tf_idf_full,
                                                        'tf_idf_title': tf_idf_title,
                                                        'tf_idf_annotate': tf_idf_annotate}
                self.keyword_result = keyword_result
        # write_to_file('tf_idf.xml', keyword_result)

    def calc_query_score(self, query):
        self.result_query[query] = {}
        result_docs = set(range(len(self.articles)))
        substr_list = set()
        query_1 = ''.join(Mystem().lemmatize(query)).strip()
        term = list()
        for word in query_1.split():
            if word[0] == '-':
                substr_list.update(set(self.word_map.get(word[1:], list())))
            elif self.word_map.get(word, None) is not None:
                term.append(word)
                result_docs.intersection_update(set(self.word_map.get(word)))
            else:
                result_docs = set()
                break
            result_docs.difference_update(substr_list)
        self.result_query[query] = {}
        for doc_num in result_docs:
            self.result_query[query][doc_num] = {}
            self.result_query[query][doc_num]['score'] = 0
            self.result_query[query][doc_num]['score_full'] = 0
            self.result_query[query][doc_num]['score_title'] = 0
            self.result_query[query][doc_num]['score_annotate'] = 0
            for word in term:
                self.add_tf_idf(query, word, doc_num, 'tf_idf', 'score')
                self.add_tf_idf(query, word, doc_num, 'tf_idf_full', 'score_full')
                self.add_tf_idf(query, word, doc_num, 'tf_idf_title', 'score_title')
                self.add_tf_idf(query, word, doc_num, 'tf_idf_annotate', 'score_annotate')

    def add_tf_idf(self, query, word, doc_num, tf_idf, score):
        self.result_query[query][doc_num][score] += self.keyword_result[word][doc_num][tf_idf]

    def print_result(self):
        print(self.result_query)


tf_idf = TF_IDF()
tf_idf.calculate_tf_idf()
tf_idf.write_to_file('tf_idf.xml')
tf_idf.calc_query_score('уравнения -алгебра')
tf_idf.calc_query_score('класс операторов')
tf_idf.calc_query_score('теоремы существования')
tf_idf.calc_query_score('пространстве')
tf_idf.calc_query_score('доказано')
tf_idf.calc_query_score('доказано -единице')
# tf_idf.write_to_file("task_05.xml", is_query=True)
f = open("task_05.txt", 'w')
f.write(str(tf_idf.result_query))
tf_idf.print_result()
