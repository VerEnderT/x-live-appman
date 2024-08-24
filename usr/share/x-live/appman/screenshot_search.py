import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_image_urls(package_name):
    # Basis-URL und URL der Galerie-Seite
    base_url = 'https://screenshots.debian.net/'
    gallery_url = f'{base_url}package/{package_name}#gallery'
    
    # Abrufen der Webseite
    response = requests.get(gallery_url)
    if response.status_code != 200:
        print(f"Fehler beim Abrufen der Seite: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Finden der Links zu den größeren Bildern
    links = soup.find_all('a', class_='black')

    # Extrahieren und Ausgeben der vollständigen Bild-URLs
    image_urls = []
    for link in links:
        relative_url = link.get('href')
        full_url = urljoin(base_url, relative_url)
        image_urls.append(full_url)

    return image_urls

if __name__ == "__main__":
    package_name = input("Gib den Paketnamen ein: ")
    image_urls = fetch_image_urls(package_name)
    
    if image_urls:
        for url in image_urls:
            print(url)
