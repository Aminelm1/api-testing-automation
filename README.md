# API Testing & Automation – DevOps CI/CD Project

Projet personnel de développement, test et automatisation d'une API REST avec mise en place d'une chaîne CI/CD complète.

L'objectif du projet est de mettre en pratique plusieurs technologies utilisées en QA Automation et DevOps :

- FastAPI
- PostgreSQL
- Pytest
- Selenium
- Docker / Docker Compose
- Jenkins
- Docker Hub
- Kubernetes
- Ansible
- Terraform
- Git / GitHub

---

## Architecture

```text
                         GitHub
                            |
                            v
                         Jenkins
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
      API Tests       Database Tests     Selenium Tests
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                       Docker Build
                            |
                            v
                       Docker Hub
                            |
                            v
                       Kubernetes
                    +-------+-------+
                    |               |
                    v               v
                 FastAPI        PostgreSQL
                    |               |
                    |              PVC
                    |
                    v
                Health Check

        Ansible                 Terraform
           |                       |
           v                       v
 Kubernetes Automation      Infrastructure as Code
```

---

## Fonctionnalités

L'application est une API REST de gestion de tâches.

Elle permet notamment :

- créer une tâche ;
- récupérer une tâche ;
- modifier son état ;
- supprimer une tâche ;
- vérifier l'état de l'API avec `/health`.

Exemple :

```http
GET /health
```

Réponse :

```json
{
  "status": "healthy"
}
```

---

## Technologies

| Technologie | Utilisation |
|---|---|
| Python | Développement et automatisation |
| FastAPI | API REST |
| PostgreSQL | Base de données |
| SQLAlchemy | Accès à PostgreSQL |
| Pytest | Tests automatisés |
| Selenium | Tests Web End-to-End |
| Docker | Conteneurisation |
| Docker Compose | Environnement local |
| Jenkins | Pipeline CI/CD |
| Docker Hub | Registry des images Docker |
| Kubernetes | Orchestration et déploiement |
| Ansible | Automatisation |
| Terraform | Infrastructure as Code |
| Git / GitHub | Versioning |

---

## Structure du projet

```text
api-testing-automation/
│
├── app/
│   ├── main.py
│   ├── database.py
│   └── static/
│       └── index.html
│
├── tests/
│   ├── test_api.py
│   ├── test_database.py
│   └── test_web.py
│
├── k8s/
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   └── postgres-pvc.yaml
│
├── ansible/
│   ├── inventory.ini
│   ├── playbook.yml
│   └── deploy.yml
│
├── terraform/
│   ├── main.tf
│   └── .terraform.lock.hcl
│
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
├── init.sql
├── requirements.txt
├── .gitignore
├── .dockerignore
└── README.md
```

---

# Tests automatisés

## Tests API

Les tests Pytest vérifient notamment :

- Health Check ;
- création d'une tâche ;
- lecture d'une tâche ;
- modification d'une tâche ;
- suppression d'une tâche ;
- erreurs `404` ;
- validation des données ;
- erreurs `422`.

Exécution :

```bash
pytest -v tests/test_api.py
```

---

## Tests PostgreSQL

Les tests Database vérifient que les données créées via l'API sont réellement présentes dans PostgreSQL.

```bash
pytest -v tests/test_database.py
```

Cela permet de tester la chaîne :

```text
API
 |
 v
PostgreSQL
```

---

## Tests Selenium

Selenium teste l'interface Web dans un véritable navigateur Chrome.

Le scénario automatisé :

```text
Ouverture de l'application
        |
        v
Saisie d'une tâche
        |
        v
Clic sur le bouton
        |
        v
Création via l'API
        |
        v
Vérification du résultat
```

Exécution :

```bash
pytest -v tests/test_web.py
```

---

# Docker

L'application, PostgreSQL et Selenium peuvent être démarrés avec Docker Compose.

```bash
docker compose up -d --build
```

Vérification :

```bash
docker compose ps
```

API :

```text
http://localhost:8000
```

Health Check :

```bash
curl http://localhost:8000/health
```

Arrêt :

```bash
docker compose down
```

---

# Pipeline Jenkins CI/CD

Le projet possède un pipeline Jenkins automatisé défini dans :

```text
Jenkinsfile
```

Pipeline :

```text
GitHub
   |
   v
Jenkins
   |
   v
Docker Compose
   |
   v
API Health Check
   |
   v
API + Database Tests
   |
   v
Selenium Web Test
   |
   v
Docker Hub Login
   |
   v
Docker Build
   |
   v
Docker Push
   |
   v
Kubernetes Deployment
   |
   v
Kubernetes Health Check
```

Chaque build Jenkins produit une image Docker versionnée avec le numéro du build.

Exemple :

```text
aminerayy1/api-testing-automation-api:11
```

Cela permet d'identifier précisément la version déployée.

---

# Docker Hub

Les images produites par Jenkins sont publiées dans Docker Hub sous :

```text
aminerayy1/api-testing-automation-api
```

Deux tags sont notamment générés :

```text
api-testing-automation-api:<BUILD_NUMBER>
api-testing-automation-api:latest
```

Les identifiants Docker Hub sont stockés dans les Credentials Jenkins et ne sont pas présents dans le repository Git.

---

# Kubernetes

L'API et PostgreSQL sont déployés sur Kubernetes.

Vérification :

```bash
kubectl get pods
```

Services :

```bash
kubectl get services
```

Déploiements :

```bash
kubectl get deployments
```

Le pipeline Jenkins met automatiquement à jour l'image de l'API :

```bash
kubectl set image deployment/task-api \
  task-api=aminerayy1/api-testing-automation-api:<BUILD_NUMBER>
```

Puis vérifie le déploiement :

```bash
kubectl rollout status deployment/task-api
```

---

## Persistance PostgreSQL

PostgreSQL utilise un PersistentVolumeClaim :

```text
postgres-pvc
```

Cela permet de conserver les données même lorsque le Pod PostgreSQL est recréé.

```text
PostgreSQL Pod
      |
      v
PersistentVolumeClaim
      |
      v
Persistent Storage
```

La persistance a été testée en créant une tâche, en redémarrant le Deployment PostgreSQL puis en vérifiant que la tâche était toujours disponible.

---

# Ansible

Ansible est utilisé pour automatiser les opérations de l'environnement DevOps.

Inventory :

```text
ansible/inventory.ini
```

Vérification de la connexion :

```bash
ansible all -i ansible/inventory.ini -m ping
```

Playbook de vérification :

```bash
ansible-playbook \
  -i ansible/inventory.ini \
  ansible/playbook.yml
```

Le playbook vérifie notamment :

- Docker ;
- kubectl ;
- Jenkins ;
- accès au cluster Kubernetes.

Un deuxième playbook permet d'automatiser le déploiement Kubernetes :

```bash
ansible-playbook \
  -i ansible/inventory.ini \
  ansible/deploy.yml
```

---

# Terraform

Terraform est utilisé pour démontrer l'Infrastructure as Code dans un environnement local.

Le provider Docker permet de créer une infrastructure Docker déclarativement.

Initialisation :

```bash
cd terraform
terraform init
```

Prévisualisation :

```bash
terraform plan
```

Création :

```bash
terraform apply
```

Inspection du state :

```bash
terraform state list
```

Destruction :

```bash
terraform destroy
```

Cette partie permet de démontrer le cycle Infrastructure as Code :

```text
Configuration
     |
     v
terraform plan
     |
     v
terraform apply
     |
     v
Infrastructure
     |
     v
terraform destroy
```

---

# Sécurité

Les informations sensibles ne sont pas stockées dans Git.

Les fichiers suivants sont notamment ignorés :

```text
.env
.venv/
__pycache__/
.pytest_cache/
terraform/.terraform/
*.tfstate
*.tfvars
```

Les secrets utilisés par Jenkins sont enregistrés dans Jenkins Credentials.

Les mots de passe Kubernetes sont stockés dans des Kubernetes Secrets et ne sont pas directement enregistrés dans les manifests Git.

---

# Exécution locale

Créer l'environnement Python :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Démarrer l'environnement Docker :

```bash
docker compose up -d --build
```

Tester l'API :

```bash
curl http://localhost:8000/health
```

---

# Compétences mises en pratique

Ce projet met en pratique :

- développement d'API REST ;
- automatisation de tests ;
- tests API ;
- tests de base de données ;
- tests Web End-to-End ;
- conteneurisation ;
- CI/CD ;
- gestion d'images Docker ;
- orchestration Kubernetes ;
- stockage persistant ;
- gestion de secrets ;
- automatisation Ansible ;
- Infrastructure as Code avec Terraform ;
- Git et GitHub.

---

## Auteur

Projet personnel réalisé dans le cadre d'un apprentissage pratique de :

**QA Automation / DevOps / CI/CD / Cloud & Infrastructure Automation**
