# Koparka OPXEN - Automatyczny Minter XEN na Optimism

Automatyczny skrypt do mintowania XEN NFT na sieci Optimism z funkcją ciągłego działania.

## Wymagania

- Python 3.8 lub nowszy
- Dostęp do internetu
- Klucz prywatny portfela Ethereum/Optimism
- ETH na Optimism do pokrycia gas fees

## Instalacja na VPS/VM

### Krok 1: Zainstaluj Python i Git
Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

CentOS/RHEL
sudo yum install -y python3 python3-pip git

### Krok 2: Sklonuj repozytorium
git clone https://github.com/pkonieczny007/Koparka-OPXEN.git
cd Koparka-OPXEN

### Krok 3: Utwórz środowisko wirtualne
python3 -m venv venv
source venv/bin/activate # Linux/Mac

lub
venv\Scripts\activate # Windows

### Krok 4: Zainstaluj zależności
pip install -r requirements.txt


### Krok 5: Skonfiguruj zmienne środowiskowe
cp .env.example .env
nano .env # lub vim .env

Uzupełnij plik `.env` swoimi danymi:
- `PRIVATE_KEY` - Twój klucz prywatny (z 0x na początku)
- `FROM_ADDRESS` - Adres Twojego portfela
- Pozostałe wartości możesz zostawić domyślne

**⚠️ UWAGA: Nigdy nie commituj pliku .env do GitHuba!**

### Krok 6: Uruchom mintera

#### Pojedyncze uruchomienie:
python minter.py --count 120 --term 507 --repeat 1


#### Ciągłe mintowanie (z looperem):
python looper.py


## Parametry minter.py

- `--count` - Liczba VMU na NFT (domyślnie: 120)
- `--term` - Liczba dni (domyślnie: 507)
- `--repeat` - Ile NFT mintować pod rząd (domyślnie: 1)
- `--delay` - Opóźnienie między transakcjami w sekundach (domyślnie: 3)
- `--maxFee` - maxFeePerGas w gwei (domyślnie: 0.000001)
- `--maxPrio` - maxPriorityFeePerGas w gwei (domyślnie: 0.000001)
- `--gasLimit` - Ręczny gasLimit (opcjonalne)
- `--rpc` - Własny RPC URL (opcjonalne)

## Przykłady użycia
Mint 5 NFT pod rząd z 120 VMU i 507 dniami
python minter.py --count 120 --term 507 --repeat 5 --delay 5

Mint z własnym gas fee
python minter.py --count 120 --term 507 --maxFee 0.00001 --maxPrio 0.00001

Użyj własnego RPC
python minter.py --count 120 --term 507 --rpc https://twoj-rpc-url.com

## Uruchomienie w tle (screen/tmux)

### Opcja 1: Screen

screen -S minter
python looper.py
Naciśnij Ctrl+A, potem D aby odłączyć
Powrót: screen -r minter

### Opcja 2: Tmux

tmux new -s minter
python looper.py
Naciśnij Ctrl+B, potem D aby odłączyć
Powrót: tmux attach -t minter

### Opcja 3: Systemd Service (zalecane dla VPS)

sudo nano /etc/systemd/system/koparka-opxen.service

Zawartość pliku:

[Unit]
Description=Koparka OPXEN Minter
After=network.target
[Service]
Type=simple
User=twoj_user
WorkingDirectory=/sciezka/do/Koparka-OPXEN
Environment="PATH=/sciezka/do/Koparka-OPXEN/venv/bin"
ExecStart=/sciezka/do/Koparka-OPXEN/venv/bin/python looper.py
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target

Aktywacja:

sudo systemctl daemon-reload
sudo systemctl enable koparka-opxen
sudo systemctl start koparka-opxen
sudo systemctl status koparka-opxen

## Baza danych

Wszystkie minty są zapisywane w bazie SQLite `mints.db` z następującymi informacjami:
- Hash transakcji
- Token ID
- Adres portfela
- Parametry mintu (count, term)
- Timestamp UTC

## Troubleshooting

### Błąd: "replacement transaction underpriced"
Zwiększ `--maxFee` i `--maxPrio`:

python minter.py --maxFee 0.00005 --maxPrio 0.00005

### Błąd: "insufficient funds"
Upewnij się, że masz wystarczająco ETH na Optimism.

### Błąd importu web3

pip install --upgrade web3

## Bezpieczeństwo

- Nigdy nie udostępniaj swojego klucza prywatnego
- Plik `.env` jest w `.gitignore` - nie zostanie wysłany na GitHub
- Regularnie sprawdzaj salda i transakcje
- Używaj dedykowanego portfela tylko do mintowania

## Licencja

MIT

## Kontakt

GitHub: [@pkonieczny007](https://github.com/pkonieczny007)

Zmodyfikowany minter.py (z obsługą .env)
Na początku pliku dodaj:
import argparse
import time
from datetime import datetime
import os
from web3 import Web3
from db import create_table, insert_mint
from dotenv import load_dotenv

# Załaduj zmienne z .env
load_dotenv()

RPC_URL = os.getenv("RPC_URL", "https://mainnet.optimism.io")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
FROM_ADDRESS = Web3.to_checksum_address(os.getenv("FROM_ADDRESS"))
CHAIN_ID = int(os.getenv("CHAIN_ID", "10"))
DEFAULT_MAX_FEE_GWEI = 0.000001
DEFAULT_MAX_PRIO_GWEI = 0.000001

# Reszta kodu bez zmian...

Szybka instalacja - jedna komenda
Dodaj do README sekcję:
## Szybka instalacja (advanced)


curl -fsSL https://raw.githubusercontent.com/pkonieczny007/Koparka-OPXEN/main/install.sh | bash

Następnie utwórz plik install.sh:
#!/bin/bash
echo "🚀 Instalacja Koparka-OPXEN..."

# Sprawdź czy git jest zainstalowany
if ! command -v git &> /dev/null; then
    echo "❌ Git nie jest zainstalowany. Instaluję..."
    sudo apt update && sudo apt install -y git
fi

# Sprawdź czy python3 jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nie jest zainstalowany. Instaluję..."
    sudo apt update && sudo apt install -y python3 python3-pip python3-venv
fi

# Sklonuj repo
git clone https://github.com/pkonieczny007/Koparka-OPXEN.git
cd Koparka-OPXEN

# Utwórz venv
python3 -m venv venv
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Skopiuj .env.example
cp .env.example .env

echo "✅ Instalacja zakończona!"
echo "📝 Teraz edytuj plik .env i uzupełnij swoje dane:"
echo "   nano .env"
echo ""
echo "🚀 Następnie uruchom mintera:"
echo "   python looper.py"

Co umieścić na GitHub
1.	Wszystkie pliki oprócz .env i mints.db (będą zignorowane przez .gitignore)
2.	Usuń klucz prywatny z minter.py przed commitowaniem
3.	Komenda do pierwszego commita:
git init
git add .
git commit -m "Initial commit - OPXEN Minter"
git branch -M main
git remote add origin https://github.com/pkonieczny007/Koparka-OPXEN.git
git push -u origin main

