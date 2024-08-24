#!/bin/bash

# Verzeichnis für die kategorisierten Pakete erstellen
rm -R /tmp/x-live/sections/
mkdir -p /tmp/x-live/sections

# Informationen zu allen verfügbaren Paketen abrufen
apt-cache dumpavail > /tmp/x-live/aptinfo

# Alle Pakete nach Sektionen sortieren und in Dateien speichern
awk '
    /^Package:/ { 
        pkg = $2 
    }
    /^Section:/ {
        section = $2
        sub(".*/", "", section)  # Nur die unterste Ebene der Sektion verwenden
        
        # Pakete auslassen, die mit -data oder -common enden
        if (pkg !~ /-data$/ && pkg !~ /-common$/) {
            print pkg >> "/tmp/x-live/sections/" section ".list"
        }
    }
' /tmp/x-live/aptinfo

# Jede .list Datei sortieren
for list in /tmp/x-live/sections/*.list; do
    sort "$list" -o "$list"
done

# Alle Listen in eine Datei zusammenführen und sortieren
cat /tmp/x-live/sections/*.list > /tmp/x-live/sections/all.list
sort /tmp/x-live/sections/all.list -o /tmp/x-live/sections/all.list

echo "Kategorisierung abgeschlossen. Paketlisten sind in /tmp/x-live/sections/"
