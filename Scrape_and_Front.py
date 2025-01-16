import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# **Étape 1 : Récupérer les noms et URLs des champions**
def get_champions_data():
    # URL de la page des champions
    url = "https://leagueoflegends.fandom.com/wiki/League_of_Legends_Wiki"
    response = requests.get(url)
    response.raise_for_status()  # Vérifie si la requête a réussi

    # Parse le contenu de la page
    soup = BeautifulSoup(response.content, "html.parser")

    # Localiser la section contenant la liste des champions
    champion_grid = soup.find("div", {"id": "champion-grid"})
    champion_list = champion_grid.find_all("li")

    # Liste pour stocker les informations des champions
    champions_data = []

    # Parcourir chaque champion
    for champion in champion_list:
        champion_name = champion.find("span")["data-champion"]
        champion_page_url = "https://leagueoflegends.fandom.com" + champion.find("a")["href"]
        champions_data.append({"Name": champion_name, "Page URL": champion_page_url})

    return pd.DataFrame(champions_data)


# **Étape 2 : Scraper les données des pages des champions**
def scrape_champion_details(df):
    results = []

    for index, row in df.iterrows():
        try:
            # URL de la page du champion
            page_url = row['Page URL']
            response = requests.get(page_url)
            response.raise_for_status()  # Vérifie si la requête a réussi

            # Parse le contenu de la page avec BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. Extraction de la position
            div_position = soup.find('div', class_='pi-item pi-data pi-item-spacing pi-border-color', attrs={'data-source': 'position'})
            if div_position:
                spans = div_position.find_all('span', class_='glossary')
                positions = [a.text.strip() for span in spans for a in span.find_all('a') if a.text.strip()]
                champion_position = ', '.join(positions) if positions else 'NULL'
            else:
                champion_position = 'NULL'

            # 2. Extraction des types (Legacy)
            div_legacy = soup.find('div', class_='pi-item pi-data pi-item-spacing pi-border-color', attrs={'data-source': 'legacy'})

            if div_legacy:
                spans = div_legacy.find_all('span', class_='glossary')
                champion_types = [a.text.strip() for span in spans for a in span.find_all('a') if a.text.strip()]
                champion_type = ', '.join(champion_types) if champion_types else 'NULL'
            else:
                champion_type = 'NULL'

            # 3. Extraction de la classe
            div_role = soup.find('div', class_='pi-item pi-data pi-item-spacing pi-border-color', attrs={'data-source': 'role'})

            if div_role:
                spans = div_role.find_all('span', class_='glossary')
                classes = [a.text.strip() for span in spans for a in span.find_all('a') if a.text.strip()]
                champion_class = ', '.join(classes) if classes else 'NULL'
            else:
                champion_class = 'NULL'

            # 4. Extraction du Movement Speed
            movement_speed_span = soup.find('span', id=re.compile(r'MovementSpeed_\w+'))
            movement_speed = movement_speed_span.text.strip() if movement_speed_span else 'NULL'

            # 5. Extraction de l'Attack Range
            attack_range_span = soup.find('span', id=re.compile(r'AttackRange_\w+'))
            attack_range = attack_range_span.text.strip() if attack_range_span else 'NULL'

            # 6. Recherche de l'URL de l'image
            image_url_tag = soup.find('figure', class_='pi-item pi-image')
            image_url = image_url_tag.find('a')['href'] if image_url_tag else 'NULL'

            # Ajouter les résultats dans la liste
            results.append({
                'name': row['Name'],
                'type': champion_type,
                'position': champion_position,
                'class': champion_class,
                'movement_speed': movement_speed,
                'attack_range': attack_range,
                'url': image_url  # URL de l'image en dernière colonne
            })

        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de l'accès à {row['Page URL']}: {e}")
            results.append({
                'name': row['Name'],
                'type': 'Erreur d\'accès',
                'position': 'Erreur d\'accès',
                'class': 'Erreur d\'accès',
                'movement_speed': 'Erreur d\'accès',
                'attack_range': 'Erreur d\'accès',
                'url': 'Erreur d\'accès'  # URL de l'image en cas d'erreur
            })

    return pd.DataFrame(results)


# **Étape 3 : Génération du fichier HTML directement avec les données scrappées**
def generate_html_from_scraping():
    print('Données en cours de scrapping ! Veuillez patienter quelques instants ... !!!')
    # Récupérer les noms et URLs des champions
    champions_df = get_champions_data()

    # Scraper les détails des champions
    champions_details_df = scrape_champion_details(champions_df)

    print('La page HTML est en cours de génération... !!!')
    # Générer le fichier HTML avec du CSS inclus dans le même fichier
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Liste des Champions de League of Legends</title>
        <style>
            /* styles.css intégrés directement dans le fichier HTML */
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column; /* Permet d'empiler les éléments */
                justify-content: flex-start; /* Aligne les éléments en haut */
                align-items: center;
                height: 100vh;
                text-align: center;
            }

            h1 {
                color: #333;
                font-size: 2em; /* Réduction de la taille du titre */
                margin-top: 20px; /* Espacement du haut */
                margin-bottom: 20px; /* Espacement sous le titre */
                width: 100%;
            }

            .champion-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
                padding: 20px;
                width: 90%;
                max-width: 1200px;
            }

            .champion {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                text-align: center;
            }

            .champion img {
                width: 100%;
                max-height: 200px;
                object-fit: contain;
                border-radius: 10px;
            }

            .champion h2 {
                color: #2c3e50;
                font-size: 1.5em;
                margin: 10px 0;
            }

            .champion p {
                color: #7f8c8d;
                font-size: 1.1em;
            }

            .champion p strong {
                color: #34495e;
            }
        </style>
    </head>
    <body>
        <h1>Liste des Champions</h1>
        <div class="champion-list">
    """

    # Ajouter les champions au contenu HTML
    for index, row in champions_details_df.iterrows():
        html_content += f"""
        <div class="champion">
            <img src="{row['url']}" alt="{row['name']}">
            <h2>{row['name']}</h2>
            <p><strong>Type:</strong> {row['type']}</p>
            <p><strong>Position:</strong> {row['position']}</p>
            <p><strong>Class:</strong> {row['class']}</p>
            <p><strong>Movement Speed:</strong> {row['movement_speed']}</p>
            <p><strong>Attack Range:</strong> {row['attack_range']}</p>
        </div>
        """

    # Fermer la balise champion-list et HTML
    html_content += """
        </div>
    </body>
    </html>
    """

    # Sauvegarder le fichier HTML
    output_html = 'champions_liste.html'
    with open(output_html, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"Fichier HTML généré avec succès dans {output_html}.")

# **Appel de la fonction principale**
if __name__ == "__main__":
    generate_html_from_scraping()
