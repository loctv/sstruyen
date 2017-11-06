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


@cli.command('a')
@click.argument('link', required=True, nargs=1)
def add(link):
    '''
        Add book to library
    '''
    commands.add_book_from_link(link)


@cli.command('r')
@click.argument('book', default='current', nargs=1)
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
    commands.view_index()


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
@click.argument('page', default=-1, nargs=1)
def go_to_page(page):
    '''
        Go to page
    '''
    commands.go_to_page(page)

@cli.command('d')
def download():
    '''
        Download content current book
    '''
    commands.download_current_book()
