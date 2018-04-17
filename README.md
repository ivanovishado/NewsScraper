# NewsScraper - Scrape any newspaper automatically
This is a simple python script for automatically scraping the most recent articles from any news-site.
Just add the websites you want to scrape to `NewsPapers.json` and the script will go through
and scrape each site listed in the file.

For more info read comments in `NewsScraper.py`.

# Usage
To run this project, you must create a virtual environment,
then install the packages in `requirements.txt` with:
```
pip install -r requirements.txt
```

Open a terminal, set the environment variable 'FLASK_APP' to `test.py` 

```
set FLASK_APP=test.py
```

In Linux:
```
export FLASK_APP=test.py
```

Then execute:
```
flask run
```

The app should be running on `localhost` on port `5000`

You also need to have a MongoDB server running in order to save the scraped articles.  

## Libraries
This script uses the following libraries:

https://github.com/codelucas/newspaper

https://github.com/kurtmckee/feedparser
