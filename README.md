
# SST tool
This is simple command line tool to reading from [sstruyen.com](http://sstruyen.com)

_Status: In development_

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
