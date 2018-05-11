# UIUC Events
UIUC Events is a hub for all sorts events happening within the Urbana-Champaign area. A problem that I have encountered
is that there are so many great events happening around UIUC, but the information about them is very fragmented. UIUC Events
is a Flask web app that gathers event data from a variety of sources and uses the [MeTA toolkit](https://meta-toolkit.org/) to search and group events. When the server is first run, the app scrapes event data from a wide selection of sources and 
assembles the necessary MeTA data files. It then creates forward and inverted indexes in order to allow searching with an
Okampi BM25 ranking function, as well as running a latent Dirichlet allocation (LDA) generative model to group events into topics, regardless of their source. Users can browse upcoming events, search for a specific event, and see similar events to 
ones that they've found.

Event data is pulled from:
* [UIUC General Events](https://calendars.illinois.edu/list/7)
* [Visit Champaign County](https://www.visitchampaigncounty.org/events)
* [Canopy Club](http://canopyclub.com/calendar)
* [Krannert Center](https://krannertcenter.com/calendar)
* [Champaign Parks](https://champaignparks.com/events/)
* [CampusTowns](https://campustowns.com/events/)

The Flask routes/URLs are as follows:
* '/' - The main homepage. Shows all upcoming events sorted by their date.
* '/about' - Just some simple information about the service.
* '/search' - A page that shows search results after using the search bar at any page.
* '/event/{id}' - Each event's page that gives their overview, link to the source, and shows all similar modeled events.

## Setup Locally
When setting up the project locally, create a virtual environment to run the server.
```bash
pip install --upgrade pip
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
In order to leave the virtual environment, simply close your terminal or type
`deactivate`.

To run the server,
```bash
python server.py config.toml
```
This will generate the necessary event data and save it to MeTA compatible files. If you have run the 
server previously and want to use the same data, simply run
```bash
python server.py config.toml --generate_events=false
```
From there, simply go to localhost:5000 in your browser to use the app!

