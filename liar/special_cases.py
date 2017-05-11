
# These URLs do not refer to meaningful statements and will not be included in the data set.
INVALID_URLS = (
    "http://www.politifact.com/oregon/statements/2011/nov/08/18-percent-american-public/test-share-facts-widget",
)

# These topics are too specific or localized (like to a special event). The statement itself
# may be valid but this topic should not affect the data.
FILTERED_TOPICS = (
    "Message Machine 2010",
    "Message Machine 2012",
    "Message Machine 2014",
    "New Hampshire 2012",
    "PolitiFact's Top Promises",
    "This Week - ABC News",
    "The Colbert Report",
    "Tampa Bay 10 News",
)