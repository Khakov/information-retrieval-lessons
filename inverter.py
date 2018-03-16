import xml.etree.ElementTree as Elem
from string import punctuation
import collections


# create index dict for set of words
def create_index_for_doc(index_dict, words_set, doc_num):
    for word in words_set:
        if word not in index_dict:
            index_dict[word] = {}
            index_dict[word]['documents_count'] = 1
            index_dict[word]['documents'] = [doc_num]
        else:
            index_dict[word]['documents'].append(doc_num)
            index_dict[word]['documents_count'] += 1


# Save issue into XML
def write_to_file(filename, index_dict):
    root = Elem.Element("inverter_index")
    words = Elem.SubElement(root, "words")
    index_dict = collections.OrderedDict(sorted(index_dict.items()))
    for key, value in index_dict.items():
        word = Elem.SubElement(words, "word", attrib={'name': str(key), 'count': str(value['documents_count'])})
        documents = Elem.SubElement(word, "documents")
        for i, doc in enumerate(value['documents']):
            Elem.SubElement(documents, "document").text = str(doc)
    tree = Elem.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)


# get document
def get_index():
    tree = Elem.parse('issue.xml')
    root = tree.getroot()
    mystem_index = {}
    porter_index = {}
    articles = root.find('articles')
    for doc_num, article in enumerate(articles.findall('article')):
        article_mystem_set = set(
            [w.strip(punctuation).replace('$', '') for w in
             article.find('title_mystem').text.split() + article.find('annotate_mystem').text.split()
             if w.strip()[0] != '$' and w.strip()[-1] != '$'])
        article_porter_set = set(
            [w.strip(punctuation).replace('$', '') for w in
             (article.find('title_porter').text.split() + article.find('annotate_porter').text.split())
             if w.strip()[0] != '$' and w.strip()[-1] != '$'])
        create_index_for_doc(porter_index, article_porter_set, doc_num)
        create_index_for_doc(mystem_index, article_mystem_set, doc_num)
    write_to_file('index_mystem.xml', mystem_index)
    write_to_file('index_porter.xml', porter_index)


get_index()
