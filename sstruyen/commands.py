import requests
import click
import re
from pyquery import PyQuery
from tinydb import TinyDB, Query

db = TinyDB('db.json')
db_books = db.table('books')
db_pages = db.table('pages')
db_current = db.table('current')
q = Query()


def _parse_ss_id(link):
    '''
        Parse link to get ss_id 
    '''
    ss_id = re.findall('/\d+/', link)
    if ss_id:
        ss_id = ss_id[0][1:-1]
    else:
        ss_id = None
    return ss_id    


def _crawl_book_info(link):
    '''
        Crawl book info
    '''
    data = {}
    __sstruyen = 'http://sstruyen.com'

    web_list_pages = requests.get(link).text
    jq = PyQuery(web_list_pages)

    # find info
    data['name'] = jq('h1.title a')[0].text
    data['author'] = jq('span[itemprop="name"]')[0].text
    
    # after a while
    data['status'] = ''
    data['number_page'] = 0
    data['pages'] = []

    # find index
    nav_div = jq('.page-split')[0]
    min_page = 1
    first_page = __sstruyen + nav_div[0].attrib['href']
    max_page = int(nav_div[-1].text)
    link_right = first_page.split('/page-')[-1]
    left = first_page[0:-len(link_right)]
    links_web_list_page = [left+str(i)+'.html#chaplist' for i in range(0, max_page)]
    
    page_ids = []
    for link in links_web_list_page:
        web = requests.get(link).text
        jq = PyQuery(web)
        div_list = jq('.chuongmoi div a')
        for div in div_list:
            page_id = int(div.findall('div')[0].text[0:-1])
            
            if page_id not in page_ids:
                page_ids.append(page_id)
                data['number_page'] += 1
                name = div.attrib['title']
                href = div.attrib['href']
                text_href = 'http://cf.sstruyen.com/doc-truyen/index.php?ajax=ct&id=' \
                        + href.split('/')[-1][0:-5] + '&t=00000000000000'
                data['pages'].append({
                    'page_id': int(page_id),
                    'name': name,
                    'link': text_href,
                    'content': None
                })

    return data


def _download_content(link):
    return requests.get(link).text[27:-6].replace('<p>', '').replace('</p>', '\n')


def _get_history(book_id=None):
    '''
        Retriev last page with book_id or current book reading
    '''
    if book_id:
        try:
            return db_current.search(q.book_id == book_id)[0]
        except IndexError:
            new = {'book_id': book_id, 'page_id': 1, 'opening': False}
            db_current.insert(new)
            return new
    else:
        try:
            return db_current.search(q.opening == True)[0]
        except IndexError:
            return {}

def _set_history(book_id, page_id):
    '''
        Save last book_id, page_id reading
    '''
    current = db_current.search(q.opening == True)
    if current: 
        opening = current[0]
    else: 
        opening = None

    if opening and opening['book_id'] != book_id:
        db_current.update({'opening': False}, q.book_id == opening['book_id'])
    
    if not db_current.search(q.book_id == book_id):
        db_current.insert({'book_id': book_id, 'page_id': page_id, 'opening': True})
    else:
        db_current.update({'page_id': page_id, 'opening': True}, q.book_id == book_id)


def add_book_from_link(link):
    '''
        Collect book from sstruyen with link Danh sach chuong
    '''
    print 'Add book from: %s' % link
    ss_id = _parse_ss_id(link)
    if not ss_id:
        raise 'Link invalid!'
   
    info = _crawl_book_info(link)
    if not db_books.search(q.book_id == ss_id):
        db_books.insert({
            'book_id': ss_id,
            'link': link,
            'name': info['name'],
            'author': info['author'],
            'number_page': info['number_page'],
            'status': info['status']
        })

        pages = info['pages']

        for page in pages:
            downloaded = page['content'] != None
            db_pages.insert({
                'book_id': ss_id,
                'page_id': page['page_id'],
                'name': page['name'],
                'link': page['link'],
                'content': page['content'],
                'downloaded': downloaded
            })
        print '%s added.' % info['name'] 
    else:
        print 'Book already in library'

def view_library():
    '''
        List books:
    '''
    books = db_books.all()
    click.secho('Library: %d books.' % len(books), bold=True, bg='blue')
    reading = _get_history()

    for index, book in enumerate(books):
        if reading and book['book_id'] == reading['book_id']:
            click.secho('%d: %s <reading>' % (book.doc_id, book['name']), fg='red') 
        else:
            click.secho('%d: %s' % (book.doc_id, book['name'])) 


def read_book(doc_id):
    if doc_id == 'current':
        reading = _get_history()
        if reading:
            read_page(reading['book_id'], reading['page_id'])
        else:
            print 'You have not read any book previous, please choose a book to read'
    else:
        book_id = db_books.get(doc_id=int(doc_id))['book_id']
        reading = _get_history(book_id)
        _set_history(book_id, reading['page_id'])
        read_page(reading['book_id'], 1)


def read_page(book_id, page_id):
    page = db_pages.search((q.book_id == book_id) & (q.page_id == page_id))[0]
    book = db_books.search(q.book_id == book_id)[0]
    page_view = page['content']
    if not page['downloaded']:
        content = _download_content(page['link'])
        if content:
            db_pages.update({'content': content, 'downloaded': True}, (q.book_id == book_id) & (q.page_id == page_id))
            page_view = content
    header = click.style('%s: Chuong %r/%r: %s' % (book['name'], page['page_id'], book['number_page'], page['name']), bg='blue', bold=True)
    click.echo(header)
    click.echo_via_pager(header + '\n' + page_view)

def go_to_page(page_id):
    reading = _get_history()
    if page_id < 0:
        page_id = reading['page_id']
    read_page(reading['book_id'], page_id)
    _set_history(reading['book_id'], page_id)
    # TODO: validate page

def next_page():
    page_id = _get_history()['page_id']
    go_to_page(page_id + 1)
    # TODO: validate page

def prev_page():
    page_id = _get_history()['page_id']
    go_to_page(page_id - 1)
    # TODO: validate page

def view_index():
    reading = _get_history()
    if not reading:
        print 'Please read to open book before view index'
    else:
        book_id, page_id = reading['book_id'], reading['page_id']
        book = db_books.search(q.book_id == book_id)[0]
        header = click.style(
            '\n'
            '%s\n\n'
            'author: %s\n'
            'number pages: %d\n---'
            % (book['name'], book['author'], book['number_page']), bold=True, bg='blue')
        pages = sorted(db_pages.search(q.book_id == book_id), key=lambda x: x['page_id'], reverse=False)
        page_view = header + '\n'
        for page in pages:
            if page['page_id'] == page_id:
                page_view += click.style('%d: %s <reading>\n' % (page['page_id'], page['name']), fg='red')
            else:
                page_view += click.style('%d: %s\n' % (page['page_id'], page['name']))
        click.echo_via_pager(page_view)
