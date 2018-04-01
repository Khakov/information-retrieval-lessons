from string import punctuation

from pymystem3 import Mystem

from utils import get_articles_mystem
import numpy as np


class LSI(object):
    def __init__(self, docs, is_tf_idf=False, k=2):
        # инициализируем документы
        self.docs = self._prepare_docs(docs)
        # инициализируем  слова
        self.words = self._get_words()
        # указываем размерность для обрезания матрицы
        self.k = k
        # нужно ли вычислять методом tf_idf
        self.is_tf_idf = is_tf_idf
        #  строим матрицу
        self.A = self._build_matrix()

    # достаем слова из всех документов
    def _get_words(self):
        words = set()
        for doc_num, doc in self.docs.items():
            words = words | set(doc.split())
        return sorted(words)

    # строим матрицу
    def _build_matrix(self):
        matrix = np.zeros((len(self.words), len(self.docs)), dtype=int)
        for i, word in enumerate(self.words):
            for j, doc in self.docs.items():
                matrix[i, j] = doc.count(word)
        # если используем tf_idf
        if self.is_tf_idf:
            docs_count = len(self.docs)
            model = np.zeros((len(self.words), len(self.docs)), dtype=float)
            for i, word in enumerate(self.words):
                for j, doc in enumerate(self.docs):
                    tf = matrix[i, j] / len(doc)
                    if matrix[i, j] != 0:
                        idf = np.log(docs_count / sum(matrix[i] > 0))
                    else:
                        idf = 0
                    model[i, j] = tf * idf
        return matrix

    # сингулярно разлогаем и выделяем нужное колисетво столбцов
    def _svd_with_approximation(self):
        u, s, v = np.linalg.svd(self.A)
        s = np.diag(s)
        k = self.k
        return u[:, :k], s[:k, :k], v[:k, :]

    # нормализуем запрос
    def _prepare_query(self, query):
        result = np.zeros(len(self.words))
        i = 0
        for word in sorted(self._parse_query(query)):
            while word > self.words[i]:
                i += 1
            if word == self.words[i]:
                result[i] += 1
        return result

    # нормализуем запрос
    def _parse_query(self, query):
        return [word.strip() for word in Mystem().lemmatize(self._prepare_text(query.split())) if len(word) > 0]

    # приводим текст к нормальному виду
    def _prepare_text(self, text):
        return " ".join(word.lower().strip(punctuation) for word in text)

    # подготавливаем документы
    def _prepare_docs(self, docs):
        result = {}
        for doc_num, doc in docs.items():
            result[doc_num] = self._prepare_text(doc)
        return result

    # вычисляем косинусную меру для двух векторов ( запроса и документа)
    def _similarity(self, x, y):
        return (x @ y) / (np.linalg.norm(x) * np.linalg.norm(y))

    # вычисляем резльтат
    def calc(self, query):
        _query = self._prepare_query(query)
        u_k, s_k, v_k = self._svd_with_approximation()
        query_coordinates = _query.T @ u_k @ np.linalg.pinv(s_k)  # вычисляем q = q_T * u_k * s_k ^-1
        doc_coordinates = self.A.T @ u_k @ np.linalg.pinv(s_k)  # вычисляем A = A_T * u_k * s_k ^-1
        result = np.apply_along_axis(  # берем срез вектора вдоль главной оси и вычисляем косинусную меру
            lambda row: self._similarity(query_coordinates, row),  # для каждого документа считаем его косинусную меру
            axis=1,
            arr=doc_coordinates
        )
        ranking = np.argsort(-result)
        return ranking


articles = get_articles_mystem('issue.xml')
query = "риманово многообразие"
lsi = LSI(articles)
print(lsi.calc(query))
# [1 4 8 3 5 6 7 0 2] - контактный метрический
# [6 1 2 0 8 7 5 3 4] - риманово многообразие
