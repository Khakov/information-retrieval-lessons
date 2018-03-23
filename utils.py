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
