<h1 align="center">Commerce</h1>

<p align="center">eBay-like e-commerce auction site that will allow users to post auction listings, place
bids on listings, comment on those listings, and add listings to a “watchlist.”</p>

<p align="center"><a href="#site">Check It Out!</a> 



[![vido_thumbnail]()](https://www.youtube.com/watch?v=LURyqW8zvcU)


## Prerequisites


```
django
django-crispy-forms
```

## Installation

```sh
> pip install -r requirements
> python manage.py makemigrations auctions
> python manage.py migrate
> python manage.py runserver
```

## Usage

- Users should be able to visit a page to create a new listing.
- The default route of the application let users view all
of the currently active auction listings.

- Clicking on a listing should take users to a page speci�c to that listing.
- Users who are signed in should be able to visit a Watchlist page, which should
display all of the listings that a user has added to their watchlist.

- Users should be able to visit a page that displays a list of all listing categories.
- Via the Django admin interface, a site administrator should be
able to view, add, edit, and delete any listings, comments, and bids made on the site.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Acknowledgements

-   [CS50 Web Development with python and javascript Course](https://cs50.harvard.edu/web/)
-   [yusufadell](linkedin.com/in/yusufadell/)
