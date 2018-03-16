import xml.etree.ElementTree as Elem


porter_index = Elem.parse('index_porter.xml')
tree = Elem.parse('issue.xml')
root = tree.getroot()
articles = root.find('articles').findall('article')
porter = porter_index.getroot()
porter_word_map = dict()
for word in porter.find('words').findall('word'):
    word_name = word.attrib['name']
    word_docs = [int(doc.text) for doc in word.find('documents').findall('document')]
    porter_word_map[word_name] = word_docs

result_docs = set(range(len(articles)))
substr_list = set()

query = input("add query:").split()
# from russian_stemmer import Porter
# query = Porter.stem(query).strip().split()
for word in query:
    if word[0] == '-':
        substr_list.update(set(porter_word_map.get(word[1:], list())))
    elif porter_word_map.get(word, None) is not None:
        result_docs.intersection_update(set(porter_word_map.get(word)))
    else:
        result_docs = set()
        break
    result_docs.difference_update(substr_list)
print(result_docs)
