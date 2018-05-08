from event import Event
import metapy
import sys

class Searcher:
    """
    Wraps the MeTA search engine.
    """
    def __init__(self, idx):
        """
        Save inverted index and create BM25 ranker for searches.
        """
        self.idx = idx
        self.ranker = metapy.index.OkapiBM25()

    def make_search(self, query_text):
        """
        Peform a search given a query and return all results as Event objects.
        """
        query = metapy.index.Document()
        query.content(query_text)
        top_docs = self.ranker.score(self.idx, query, num_results=100)
        events = []
        for num, (d_id, _) in enumerate(top_docs):
            events.append(Event(self.idx, d_id))
        return events
