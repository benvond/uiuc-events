# UIUC Events
UIUC Events is a hub for all sorts events happening within the Urbana-Champaign area. 
Built with Flask and the [MeTA toolkit](https://meta-toolkit.org/), this app uses an Okampi BM25 ranking function 
and latent Dirichlet allocation (LDA) generative model to categorize and search through a wide collection of events.

Event data is pulled from:
* [UIUC General Events](https://calendars.illinois.edu/list/7)
* [Visit Champaign County](https://www.visitchampaigncounty.org/events)
* [Canopy Club](http://canopyclub.com/calendar)
* [Krannert Center](https://krannertcenter.com/calendar)
* [Champaign Parks](https://champaignparks.com/events/)
* [CampusTowns](https://campustowns.com/events/)

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


