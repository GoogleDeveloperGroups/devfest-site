### DevFest Web Site ###
This is the code for the devfest.info site and the local microsites.

### Basics ###
It is programmed in python 2.7 running on AppEngine, using webapp2 as its
framework. For templates jinja2 is used, and from django it imports code
for JSON encode / decode as well as serialization code for caching.

Forms are generated and validated using WTForms.

### Directories ###
Basic supportive code can be found in the directory lib, including
base classes for pages, caching, db definitions, etc.

In the directory pages you find the definitions for the pages,
which then take the templates using jinja2.

### Data Storage ###
The data is stored in standard AppEngine data base, and there is an input
support using Google Spreadsheets.

