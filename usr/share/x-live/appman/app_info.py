import subprocess
import re

def get_package_info(package_name):
    try:
        # Führe den Befehl apt show aus und hole die Ausgabe
        result = subprocess.run(['apt', 'show', '-a', package_name], capture_output=True, text=True, check=True)
        data = result.stdout

        # Extrahiere die gesamte Beschreibung ab der Zeile Description:
        description_match = re.search(r'^Description: (.*)', data, re.MULTILINE | re.DOTALL)
        if description_match:
            # Gesamte Beschreibung
            long_description = description_match.group(1).strip()

            # Kurze Beschreibung ist die erste Zeile der gesamten Beschreibung
            short_description = long_description.split('\n', 1)[0].strip()

            # Lange Beschreibung ist der Rest der Beschreibung
            long_description = '\n'.join(long_description.split('\n')[1:]).strip()
        else:
            short_description = 'Nicht gefunden'
            long_description = ''

        # Extrahiere weitere Informationen
        installed_size = re.search(r'^Installed-Size: (\d+)', data, re.MULTILINE)
        depends = re.search(r'^Depends: (.*?)(?:\n|$)', data, re.MULTILINE | re.DOTALL)
        maintainer = re.search(r'^Maintainer: (.*?)(?:\n|$)', data, re.MULTILINE)
        homepage = re.search(r'^Homepage: (.*?)(?:\n|$)', data, re.MULTILINE)
        version = re.search(r'^Version: (.*?)(?:\n|$)', data, re.MULTILINE)
        status = re.search(r'Installed: (.*?)(?:\n|$)', data, re.MULTILINE)

        # Überprüfe den Installationsstatus mit which
        #status = 'Nicht installiert'
        #if subprocess.run(['apt', 'list', '--installed', '2>>/dev/null', '|grep', package_name], capture_output=True, text=True).stdout.strip():
        #    status = 'Installiert'

        # Zusammenstellen der Informationen in einem Wörterbuch
        info = {
            'Short Description': short_description,
            'Long Description': long_description if long_description else 'Nicht gefunden',
            'Installed-Size': installed_size.group(1) if installed_size else 'Nicht gefunden',
            'Depends': depends.group(1).strip() if depends else 'Nicht gefunden',
            'Maintainer': maintainer.group(1).strip() if maintainer else 'Nicht gefunden',
            'Homepage': homepage.group(1).strip() if homepage else 'Nicht gefunden',
            'Version': version.group(1).strip() if version else 'Nicht gefunden',
            'Status': status.group(1).strip() if status else 'Nicht gefunden'
        }
        return info
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Abrufen der Paketinformationen: {e}")
        return None

# Beispiel
#package_info = get_package_info('python3-pyqt5')
#print(package_info)
