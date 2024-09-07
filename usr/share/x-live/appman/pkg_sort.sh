#!/bin/bash

# Verzeichnis für die kategorisierten Pakete erstellen
rm -rf /tmp/x-live/sections/
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

# Jede .list Datei sortieren und doppelte Einträge entfernen
for list in /tmp/x-live/sections/*.list; do
    sort -u "$list" -o "$list"  # `-u` entfernt Duplikate und speichert direkt in der Datei
done

# Alle Listen in eine Datei zusammenführen, sortieren und doppelte Einträge entfernen
sort -u /tmp/x-live/sections/*.list -o /tmp/x-live/sections/all.list

echo "Kategorisierung abgeschlossen. Paketlisten sind in /tmp/x-live/sections/"
