import json
import argparse

parser = argparse.ArgumentParser(
    description='Add news website to scraping list.')
parser.add_argument('website_name')
parser.add_argument('--link')
parser.add_argument('--rss')
parser.add_argument('--path', default='./resources/NewsPapers.json')

args = parser.parse_args()

if not args.link and not args.rss:
    print('You must at least provide a link to the newspaper or a rss.')
    exit(1)

newspaper_to_add = {
    args.website_name: {}
}

if args.link:
    newspaper_to_add[args.website_name]['link'] = args.link

if args.rss:
    newspaper_to_add[args.website_name]['rss'] = args.rss

with open(args.path) as f:
    data = json.load(f)

data.update(newspaper_to_add)

with open(args.path, 'w') as f:
    json.dump(data, f, indent=2)
