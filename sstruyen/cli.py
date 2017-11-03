import click
import commands

@click.group()
def cli():
    '''
        Sstruyen Reader Command Line Tool
    '''
    pass


@cli.command('l')
def library():
    '''
        List books
    '''
    commands.view_library()


@cli.command()
@click.option('--link', required=True, help='Need a link of book for crawl data')
def add(link):
    '''
        Add book to library
    '''
    commands.add_book_from_link(link)


@cli.command('r')
@click.option('--book', default='current', help='Book id to read other book, avoid it if you are reading')
def read(book):
    '''
        Read book
    '''
    commands.read_book(book)


@cli.command('i')
def index():
    '''
        Show index of book
    '''
    pass


@cli.command('n')
def next_page():
    '''
        Jump next page
    '''
    commands.next_page()


@cli.command('p')
def prev_page():
    '''
        Jump prev page
    '''
    commands.prev_page()

@cli.command('g')
@click.option('--page', default=-1, help='Page number you want go to')
def go_to_page(page):
    '''
        Go to page
    '''
    commands.go_to_page(page)
