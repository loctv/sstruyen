
# SST tool
This is simple command line tool to read book from [sstruyen.com](http://sstruyen.com)

_Status: In development_

#### Install:

```bash
> git clone https://github.com/loctv/sstruyen.git
> cd sstruyen
> pip install .
> sst --help
```

*In first time launch command 'sst', it will create a file store at ~/.sst/db.json. You must create folder ~/.sst by hand if error occured.*

#### Use:

```bash
> sst --help 

Usage: sst [OPTIONS] COMMAND [ARGS]

Options:
  --help  Show this message and exit.

Commands:
  a  Add book to library
  d  Download content current book
  g  Go to page
  i  Show index of book
  l  List books
  n  Jump next page
  p  Jump prev page
  r  Read book
```

#### How to get link book to add:
-   Choose a book in [sstruyen.com](http://sstruyen.com)
-   Go to [Danh sach chuong]
-   Click a page in chap list, copy this url as a link book
-   Use command for add book is: sst a LINK
