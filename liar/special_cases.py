
# These URLs do not refer to meaningful statements and will not be included in the data set.
INVALID_URLS = (
    "http://www.politifact.com/oregon/statements/2011/nov/08/18-percent-american-public/test-share-facts-widget",
)

# These topics are too specific or localized (like to a special event). The statement itself
# may be valid but this topic should not affect the data.
FILTERED_TOPICS = (
#    ,
    "PolitiFact's Top Promises",
#    "This Week - ABC News",
    "The Colbert Report",
    "Tampa Bay 10 News",
    "Corrections and Updates",
    "After the Fact"
)

COLLAPSED_SUBJECTS = {
  "Florida Amendments" : "Florida",
  "Sotomayor Nomination" : "Supreme Court",
  "Kagan Nomination" : "Supreme Court",
  "New Hampshire 2012": "Elections",
  "Message Machine 2010": "Elections",
  "Message Machine 2012": "Elections",
  "Message Machine 2014": "Elections",
  "workers' compensation": "Workers",
  "State government spending": "State Budget",
  "Automatic Voter Registration": "Elections",
}