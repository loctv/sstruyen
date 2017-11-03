import requests
import click
import re
from bs4 import BeautifulSoup as bs
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
    return {
        'name': 'Tien nghich',
        'author': 'Nhi can',
        'number_page': 2302,
        'status': 'complete',
        'pages': [{
            'page_id': 1,
            'name': 'Mo dau',
            'link': 'http://...',
            'content': 'cong hoa x\nas\nxa\nsx\nsxa\nss\nxaxas'
        },{
            'page_id': 2,
            'name': 'Thanh vuc cuong gia',
            'link': 'http://...',
            'content': 'Page 2'
        },{
            'page_id': 3,
            'name': 'Du dau',
            'link': 'http://...',
            'content': 'Page 3'
        },{
            'page_id': 4,
            'name': 'O son tran',
            'link': 'http://...',
            'content': None
        }]
    }


def _download_content(link):
    return 'Page downloaded'


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
    click.secho('Library: %d books' % len(books), bold=True, bg='blue')
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
    click.secho('Chuong %r/%r: %s' % (page['page_id'], book['number_page'], page['name']), bg='blue', bold=True)
    click.secho(page_view)


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