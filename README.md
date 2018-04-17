# NewsScraper - Scrape any newspaper automatically
This is a simple python script for automatically scraping the most recent articles from any news-site.
Just add the websites you want to scrape to `NewsPapers.json` and the script will go through
and scrape each site listed in the file.

For more info read comments in `NewsScraper.py`.

# Usage
To run this project, you must create a virtual environment,
installing the packages in `requirements.txt` - coming soon!

You also need to have a MongoDB server running in order to save the scraped articles.  

## Libraries
This script uses the following libraries:

https://github.com/codelucas/newspaper

https://github.com/kurtmckee/feedparser
