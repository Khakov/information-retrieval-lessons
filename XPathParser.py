from string import punctuation

from lxml import html
import requests
import dicttoxml

# Items name helper function
from pymystem3 import Mystem

from russian_stemmer import Porter


def item_func(parent):
    if parent == 'articles':
        return 'article'
    elif parent == 'keywords':
        return 'keyword'
    else:
        return 'item'


# Get page content
def get_site_content(path):
    page_url = path
    page = requests.get(page_url)
    page.encoding = 'windows-1251'
    return html.fromstring(page.content)


# Parse page
def parse_site(site, path):
    page_url = site + path
    issue = {'url': page_url, 'articles': []}

    dom_tree = get_site_content(page_url)
    for article in dom_tree.xpath('//td[@width="90%"]/a[@class="SLink"]'):
        title = ''.join(article.xpath('text()'))
        title_porter = ' '.join([Porter.stem(word.strip(punctuation)) for word in title.split()])
        title_mystem = ''.join(Mystem().lemmatize(title)).strip()
        href, = article.xpath('@href')
        issue['articles'].append({'url': str(site + href), 'title_original': title, 'title_porter': title_porter,
                                  'title_mystem': title_mystem})

    for article in issue['articles']:
        dom_tree = get_site_content(article['url'])
        original_annotate = ''.join(dom_tree.xpath("//b[contains(.,'Аннотация:')]/following-sibling::node()"
                                                   "[following-sibling::br[1] and following-sibling::"
                                                   "b[contains(.,'Ключевые слова:')]]/descendant-or-self::text()")) \
            .strip()
        article['annotate_original'] = original_annotate
        article['annotate_porter'] = ' '.join(
            [Porter.stem(word.strip(punctuation)) for word in original_annotate.split()])
        article['annotate_mystem'] = ''.join(Mystem().lemmatize(original_annotate)).strip(punctuation)
        article['keywords'] = str(dom_tree.xpath("// b[contains(.,'Ключевые слова:')] / following-sibling::i")[0].text)[
                              :-1].split(', ')
    return issue


site = 'http://www.mathnet.ru'
path = '/php/archive.phtml?jrnid=ivm&wshow=issue&year=2014&volume=&volume_alt=&issue=10&issue_alt=&option_lang=rus'
issue = parse_site(site, path)

# Save issue into XML
with open('issue.xml', 'wb') as f:
    xml = dicttoxml.dicttoxml(issue, attr_type=False, custom_root='issue', item_func=item_func)
    f.write(xml)
