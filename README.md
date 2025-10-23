# Koparka OPXEN

Automatyczny minter XEN na Optimism.

## Instalacja

git clone https://github.com/pkonieczny007/Koparka-OPXEN.git

cd Koparka-OPXEN

pip install -r requirements.txt


## Konfiguracja

Otwórz `minter.py` i zmień w linii 7-9:
- `PRIVATE_KEY` - twój klucz prywatny
- `FROM_ADDRESS` - twój adres portfela

## Uruchomienie

Pojedyncze:
python minter.py

Ciągłe:
python looper.py
