PYTHON      ?= python3
PIP         ?= $(PYTHON) -m pip
VENV_DIR    ?= .venv
VENV_BIN    := $(VENV_DIR)/bin
ACTIVATE    := . $(VENV_BIN)/activate

PROJECT_NAME := db-admin-ville-marseille

DOCKER_COMPOSE ?= docker-compose

.PHONY: help setup venv install simulate-data init-db run-all test lint fmt clean \
        compose-up compose-down compose-logs check-env

help:
	@echo ""
	@echo "Cibles principales :"
	@echo "  setup         - Crée le venv et installe les dépendances"
	@echo "  compose-up    - Démarre les conteneurs SGBD (Postgres, MySQL, MSSQL)"
	@echo "  compose-down  - Arrête les conteneurs"
	@echo "  simulate-data - Génère les données /data (sources + generated)"
	@echo "  init-db       - Applique les DDL/DML Postgres et charge les données"
	@echo "  run-all       - simulate-data + init-db"
	@echo "  test          - Lance les tests unitaires"
	@echo "  lint          - Lint du code Python (flake8)"
	@echo "  fmt           - Formatage du code Python (black)"
	@echo "  clean         - Nettoie artefacts Python et fichiers générés"
	@echo ""

setup: venv install

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Création de l'environnement virtuel dans $(VENV_DIR)"; \
		$(PYTHON) -m venv $(VENV_DIR); \
	else \
		echo "Environnement virtuel déjà présent dans $(VENV_DIR)"; \
	fi

install: check-env
	@echo "Installation des dépendances Python"
	@$(ACTIVATE) && $(PIP) install --upgrade pip
	@$(ACTIVATE) && $(PIP) install -r requirements.txt

check-env:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Environnement virtuel absent. Lancer 'make setup' d'abord."; \
		exit 1; \
	fi

compose-up:
	@echo "Démarrage des services Docker (Postgres / MySQL / MSSQL)"
	@$(DOCKER_COMPOSE) up -d

compose-down:
	@echo "Arrêt des services Docker"
	@$(DOCKER_COMPOSE) down

compose-logs:
	@$(DOCKER_COMPOSE) logs -f

simulate-data: check-env
	@echo "Génération des données de démonstration (data/sources et data/generated)"
	@$(ACTIVATE) && $(PYTHON) scripts/python/simulate_data.py

init-db: check-env
	@echo "Déploiement des schémas et chargement des données dans PostgreSQL"
	@$(ACTIVATE) && $(PYTHON) scripts/python/manage_schemas.py

run-all: simulate-data init-db

test: check-env
	@echo "Exécution des tests unitaires"
	@$(ACTIVATE) && pytest tests

lint: check-env
	@echo "Lint du code Python (flake8)"
	@$(ACTIVATE) && flake8 scripts tests

fmt: check-env
	@echo "Formatage du code Python (black)"
	@$(ACTIVATE) && black scripts tests monitoring security

clean:
	@echo "Nettoyage des fichiers temporaires et artefacts"
	find . -name "__pycache__" -type d -exec rm -rf {} + || true
	find . -name "*.pyc" -delete || true
	find . -name "*.pyo" -delete || true
	rm -rf .pytest_cache || true
	rm -rf .mypy_cache || true
	rm -rf .venv || true
	rm -rf monitoring/status/*.json 2>/dev/null || true
	rm -rf monitoring/metrics/*.csv 2>/dev/null || true
	rm -rf monitoring/reports/*.md 2>/dev/null || true
	rm -rf security/audit_results/*.csv 2>/dev/null || true
	rm -rf data/generated/* 2>/dev/null || true
