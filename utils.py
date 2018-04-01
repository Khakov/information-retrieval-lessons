import xml.etree.ElementTree as Elem


def get_words(filename):
    porter_index = Elem.parse(filename)
    porter = porter_index.getroot()
    porter_word_map = dict()
    for word in porter.find('words').findall('word'):
        word_name = word.attrib['name']
        word_docs = [int(doc.text) for doc in word.find('documents').findall('document')]
        porter_word_map[word_name] = word_docs
    return porter_word_map


def get_articles(filename):
    tree = Elem.parse(filename)
    root = tree.getroot()
    articles = root.find('articles')
    return articles.findall('article')


def get_articles_mystem(filename):
    articles = get_articles(filename)
    annotate_map = dict()
    for doc_num, article in enumerate(articles):
        annotate_map[doc_num] = article.find('title_mystem').text.split() + article.find('annotate_mystem').text.split()
    return annotate_map
