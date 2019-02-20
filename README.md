## Welcome to News Parser project

Currently project supports parsing of two following 
websites:

* https://tsn.ua
* https://www.ukr.net

In the following sections you will see a few examples and short information about the project.

## Structure

The project contains following application:

* [`parser`](./parser) — The News Parser representation

Parser application is explained in its directory.

## Quick start

#### Search
On the main page of the app you fan find:
 1. dropdown list of the categories
 2. search form
 
 Click on dropdown list and select those categories by which you want to make the search.<br />
 By default all categories are selected.<br />
 You can also use the button (`select all \ unselect all`) in dropdown list to select \ unselect
 all categories.<br />
 <br />
 In search form write tags by which you want to make the search. You can separate tags
 by any non alphanumeric symbol.<br >
 If you will not enter any tag the search will be made only by categories. <br />
 <br />
  
 After all desired categories and tags are entered, press the search button and check the results.
 
#### Results

Results of the search are ordered by news time.<br />
Every news consist of its category, time, link to original news and title.
Picture and text of the news are optional and depend on whether the
resource has provided it.<br />
By clicking on link, title or picture you will be redirected (in the new tab)
to the original news.<br />

Navigate through page py scrolling it up or down.<br />
You also can scroll the text of the news if it exists and overflows the size of news container.<br />
There are only 10 results by page. Use `first `, `previous `, `next`, `last` buttons (at the bottom of the page)
to navigate through the results.
You can also find the current page and total amount of the pages at the bottom of the each page.



