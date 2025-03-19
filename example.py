from gdeltdoc import GdeltDoc, Filters

f = Filters(
    keyword="climate change", start_date="2020-05-10", end_date="2020-05-11", tone=">5"
)

print(f.query_string)

gd = GdeltDoc()

# Search for articles matching the filters
articles = gd.article_search(f)
print(articles)
