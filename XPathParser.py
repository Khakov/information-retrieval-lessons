from lxml import html
import requests
import dicttoxml


# Items name helper function
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
        href, = article.xpath('@href')
        issue['articles'].append({'url': str(site + href), 'title': title})

    for article in issue['articles']:
        dom_tree = get_site_content(article['url'])
        article['annotate'] = dom_tree.xpath("// b[contains(.,'Аннотация:')][1]")[0].tail.strip()
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
