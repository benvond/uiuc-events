from flask import Flask, render_template, request, abort
from event import Event
from generate_events import generate_events
from searcher import Searcher
from topic_modeler import TopicModeler

import metapy
import sys
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', events=app.sorted_events)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = app.searcher.make_search(query)
    return render_template('search.html', results=results, query=query)

@app.route('/event/<int:d_id>')
def event(d_id):
    if str(d_id) in app.mapping:
        event = app.mapping[str(d_id)]
        overview = re.split('\n|\r ', event.overview)
        events = app.model.get_similar_events(event)
        return render_template('event.html', event=event, overview=overview, events=events)
    else:
        abort(404)

def get_event(same_event):
    for event in app.events:
        if event == same_event:
            return event


if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print('Usage: server.py config.toml [--generate_events=false]')
        sys.exit(1)

    if len(sys.argv) == 2:
        print('Generating event data...')
        generate_events()

    cfg = sys.argv[1]
    app.idx = metapy.index.make_inverted_index(cfg)
    app.fidx = metapy.index.make_forward_index(cfg)
    app.events = []
    app.mapping = {}
    for d_id in range(0, app.idx.num_docs()):
        event = Event(app.idx, d_id)
        if event not in app.events:
            app.mapping[str(d_id)] = event
            app.events.append(event)
        else:
            app.mapping[str(d_id)] = get_event(event)
    app.sorted_events = sorted(list(app.events))
    app.searcher = Searcher(app.idx)
    app.model = TopicModeler(app.fidx, app.events)

    app.run(debug=True, use_reloader=False)
