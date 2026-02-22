# ⏱️ Discord WoS Rally Team-Timer Bot

Ein Discord-Bot zur Koordination von Rally-Teams mit Live-Countdowns, Gruppenverwaltung und interaktiven Buttons.

## 1. Hauptfunktionen
*   **Gruppen-Management:** Erstelle verschiedene Gruppen (z. B. Rally-Teams) mit individuellen Zeitmarken für jeden Spieler.
*   **Live-Countdown:** Ein grafisches Embed aktualisiert sich jede Sekunde und zeigt den Status ("Wartend", "JETZT", "Erledigt") an.
*   **Automatischer Ablauf:** Der Timer startet mit einem 3s-Delay.
*   **Interaktive Steuerung:** Nutze Buttons direkt unter der Timer-Box, um den Countdown abzubrechen oder sofort neu zu starten (alte Boxen werden automatisch entfernt).
*   **Silent-Mode:** Benachrichtigungen erfolgen direkt im Live-Embed, um Chat-Spam zu vermeiden.

---

## 2. Erforderliche Konfiguration

Damit der Bot einwandfrei funktioniert, müssen im [Discord Developer Portal](https://discord.com) folgende Einstellungen aktiv sein:

### Privileged Gateway Intents
*   `Message Content Intent`: **AN** (Erforderlich für Slash-Command Parameter).
*   `Server Members Intent`: **AN** (Für die Team-Verwaltung).

### OAuth2 Scopes & Permissions
Beim Erstellen des Einladungs-Links müssen folgende Haken gesetzt sein:
*   **Scopes:** `bot`, `applications.commands`
*   **Permissions:** `Send Messages`, `Embed Links`, `Read Message History`, `Manage Messages` (für das Löschen alter Boxen).

---

## 3. Befehlsübersicht

Der Bot nutzt moderne Slash-Commands. Tippe `/timer`, um das Menü aufzurufen:


| Befehl | Parameter | Beschreibung |
| :--- | :--- | :--- |
| `/timer add` | `user`, `zeit`, `[gruppe]` | Fügt einen Spieler mit Zeitmarke hinzu. |
| `/timer update` | `user`, `akt_gruppe`, `[zeit]`, `[ziel_gruppe]` | Ändert Daten oder verschiebt Spieler zwischen Gruppen. |
| `/timer list` | - | Zeigt alle Gruppen und gespeicherten Zeiten an. |
| `/timer start` | `[gruppe]` | Startet den Live-Timer für die gewählte Gruppe. |
| `/timer delay` | `gruppe`, `zahl` | Ändert die Startverzögerung (Standard: 3s). |
| `/timer delete` | `[gruppe]`| Löscht alle gruppen oder eine angegebene. |

### Button-Steuerung
*   **🔄 Neustart:** Löscht die aktuelle Nachricht und postet eine neue, frische Timer-Box am Ende des Kanals.
*   **🛑 Stopp:** Bricht den laufenden Hintergrund-Prozess sofort ab.

---

## 4. Installation & Start

### Voraussetzungen
*   Python 3.8 oder höher
*   Ein Discord Bot-Token

### Schritt-für-Schritt
1.  **Abhängigkeiten installieren:**
    ```bash
    pip install discord.py python-dotenv
    ```
2.  **Umgebungsvariablen:**
    Erstelle eine Datei namens `.env` im Hauptverzeichnis:
    ```env
    DISCORD_TOKEN=DEIN_GEHEIMER_TOKEN_HIER
    ```
3.  **Bot starten:**
    ```bash
    python main.py
    ```

---

## 5. Troubleshooting
*   **"Interaction failed":** Stelle sicher, dass der Bot in dem Kanal Schreibrechte und die Berechtigung "Nachrichten verwalten" hat.
