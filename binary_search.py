import xml.etree.ElementTree as Elem

from pymystem3 import Mystem

from utils import get_words

tree = Elem.parse('issue.xml')
root = tree.getroot()
articles = root.find('articles').findall('article')
result_docs = set(range(len(articles)))
substr_list = set()
porter_word_map = get_words('index_mystem.xml')
query = input("add query:")
query = ''.join(Mystem().lemmatize(query)).strip()
for word in query.split():
    if word[0] == '-':
        substr_list.update(set(porter_word_map.get(word[1:], list())))
    elif porter_word_map.get(word, None) is not None:
        result_docs.intersection_update(set(porter_word_map.get(word)))
    else:
        result_docs = set()
        break
    result_docs.difference_update(substr_list)
print(result_docs)
