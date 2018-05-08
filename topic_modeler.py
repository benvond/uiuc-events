import metapy

def multinomial_to_list(mn):
    """
    Convert a MeTA Multinomial object to a python list.
    """
    str_mn = metapy.stats.Multinomial.__repr__(mn)
    list_mn = str_mn.split()
    num_list = []
    for num in list_mn:
        if '0.' in num:
            num = num.replace(',', '')
            num = num.replace('}>', '')
            num_list.append(float(num))
    return num_list

class TopicModeler:
    """
    Wraps the MeTA topic model
    """
    def __init__(self, fidx, events):
        """
        Creates a LDA topic model given a forward index.
        """
        self.fidx = fidx
        dset = metapy.learn.Dataset(self.fidx)
        lda_inf = metapy.topics.LDACollapsedVB(dset, num_topics=8, alpha=1.0, beta=0.01)
        lda_inf.run(num_iters=1000000)
        lda_inf.save('lda-cvb0')
        self.model = model = metapy.topics.TopicModel('lda-cvb0')
        self.scorer = metapy.topics.BLTermScorer(model)

        self.mapping = {}
        self.groups = []
        for x in range(0, 8):
            self.groups.append([])
        for event in events:
            mn = self.model.topic_distribution(event.d_id)
            dl = multinomial_to_list(mn)
            self.mapping[event.link] = (dl.index(max(dl)), max(dl))
            self.groups[dl.index(max(dl))].append(event)

    def get_similar_events(self, event):
        """
        Returns a list of Event objects that are found to be in the same topic.
        """
        events = self.groups[self.mapping[event.link][0]]
        group = []
        for event in events:
            group.append((event, self.mapping[event.link][1]))
        return sorted(group, key=lambda x : x[1], reverse=True)
