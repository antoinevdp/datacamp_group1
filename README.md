# datacamp

Datacamp project by Elliot Fesquet, Ethan Tomaso, Antoine Vandeplanque

## Information

Notre code est décomposé en plusieurs fichiers :

- scraper: Code utilisé pour scrapper SteamDB
- lambda: Code sur AWS lambda utilisé pour nettoyer les données scraper
- loaddb: Code utilisé pour chargé le dataset [Steam Review](https://www.kaggle.com/datasets/andrewmvd/steam-reviews) sur notre BDD mariadb
- models: Code utilisé pour entraîner les modèles + les modèles au format .pkl
- dataviz: Lien pour le tableau: [Ici](https://public.tableau.com/app/profile/elliot.fesquet/viz/Classeur2_17341021815550/STEAMDB_SCRAPED?publish=yes)

## Installation
### Selenium
```bash
pip install -r requirements.txt
```

Tor is required to run the scrapper. 
### Tor
Install Tor: Download and install Tor from Tor Project.

On Linux: 
```bash
sudo apt install tor
```
On macOS:
```zsh
brew install tor
```
On Windows: Download the [Tor Browser](https://www.torproject.org/) and start the Tor service.

## Usage

```bash
python scrapper/main.py
```
