pipeline {
    agent any

    environment {
        POSTGRES_DB = 'taskdb'
        POSTGRES_USER = 'api_tester'
        DOCKER_IMAGE = 'aminerayy1/api-testing-automation-api'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Code récupéré depuis GitHub'
            }
        }

        stage('Docker Build') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'postgres-password',
                        variable: 'POSTGRES_PASSWORD'
                    )
                ]) {
                    sh '''
                        export DATABASE_URL="postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}"

                        echo "Démarrage de Docker Compose..."

                        docker compose down || true
                        docker compose up -d --build
                    '''
                }
            }
        }

        stage('Check Containers') {
            steps {
                sh '''
                    echo "Conteneurs Docker :"
                    docker compose ps
                '''
            }
        }

        stage('API Health Check') {
            steps {
                sh '''
                    echo "Attente du démarrage de l'API..."

                    for i in $(seq 1 30); do

                        if curl --fail http://127.0.0.1:8000/health; then
                            echo ""
                            echo "API disponible !"
                            exit 0
                        fi

                        echo "API pas encore disponible..."
                        sleep 2

                    done

                    echo "ERREUR : l'API n'a pas démarré."
                    docker compose logs
                    exit 1
                '''
            }
        }

        stage('API & Database Tests') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'postgres-password',
                        variable: 'POSTGRES_PASSWORD'
                    )
                ]) {
                    sh '''
                        export TEST_DATABASE_URL="postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:5433/${POSTGRES_DB}"

                        echo "Création de l'environnement Python..."

                        rm -rf .venv-jenkins
                        python3 -m venv .venv-jenkins

                        echo "Installation des dépendances..."
                        .venv-jenkins/bin/pip install -r requirements.txt

                        echo "Lancement des tests API et Database..."

                        .venv-jenkins/bin/pytest -v \
                            tests/test_api.py \
                            tests/test_database.py
                    '''
                }
            }
        }

        stage('Selenium Web Test') {
            steps {
                sh '''
                    echo "Attente de Selenium..."

                    for i in $(seq 1 30); do

                        if curl --fail http://127.0.0.1:4444/status; then
                            echo ""
                            echo "Selenium disponible !"
                            break
                        fi

                        echo "Selenium pas encore disponible..."
                        sleep 2

                    done

                    echo "Lancement du test Web Selenium..."

                    .venv-jenkins/bin/pytest -v tests/test_web.py
                '''
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login \
                            -u "$DOCKERHUB_USERNAME" \
                            --password-stdin

                        echo "Connexion Docker Hub réussie."
                    '''
                }
            }
        }

        stage('Docker Build & Push') {
            steps {
                sh '''
                    echo "Construction de l'image Docker..."

                    docker build \
                        -t ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                        -t ${DOCKER_IMAGE}:latest \
                        .

                    echo "Push de l'image ${BUILD_NUMBER}..."

                    docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}

                    echo "Push de l'image latest..."

                    docker push ${DOCKER_IMAGE}:latest

                    echo "Images publiées sur Docker Hub."
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    echo "Déploiement Kubernetes..."

                    echo "Image : ${DOCKER_IMAGE}:${BUILD_NUMBER}"

                    kubectl set image deployment/task-api \
                        task-api=${DOCKER_IMAGE}:${BUILD_NUMBER}

                    echo "Attente du rollout Kubernetes..."

                    kubectl rollout status deployment/task-api \
                        --timeout=120s

                    echo "Déploiement Kubernetes réussi."

                    echo "Pods actuellement déployés :"
                    kubectl get pods

                    echo "Image actuellement utilisée :"

                    kubectl get deployment task-api \
                        -o=jsonpath='{.spec.template.spec.containers[0].image}'

                    echo ""
                '''
            }
        }

        stage('Kubernetes Health Check') {
            steps {
                sh '''
                    echo "Vérification de l'API dans Kubernetes..."

                    kubectl port-forward service/task-api 8001:8000 \
                        > /tmp/task-api-port-forward.log 2>&1 &

                    PF_PID=$!

                    cleanup() {
                        kill $PF_PID 2>/dev/null || true
                    }

                    trap cleanup EXIT

                    echo "Attente du port-forward..."

                    for i in $(seq 1 15); do

                        if curl --fail http://127.0.0.1:8001/health; then
                            echo ""
                            echo "API Kubernetes disponible !"
                            exit 0
                        fi

                        echo "API Kubernetes pas encore disponible..."
                        sleep 2
                    done

                    echo "ERREUR : API Kubernetes inaccessible."

                    echo "===== Port-forward logs ====="
                    cat /tmp/task-api-port-forward.log || true

                    echo "===== Pods ====="
                    kubectl get pods || true

                    exit 1
                '''
            }
        }
    }

    post {

        success {
            echo '========================================'
            echo 'PIPELINE CI/CD TERMINE AVEC SUCCES'
            echo 'API Tests          : OK'
            echo 'Database Tests     : OK'
            echo 'Selenium Tests     : OK'
            echo 'Docker Hub Login   : OK'
            echo 'Docker Build/Push  : OK'
            echo 'Kubernetes Deploy  : OK'
            echo 'Kubernetes Health  : OK'
            echo '========================================'
        }

        failure {
            echo 'Pipeline CI/CD en échec.'

            sh '''
                echo "===== Docker containers ====="
                docker compose ps || true

                echo "===== Docker logs ====="
                docker compose logs || true

                echo "===== Kubernetes pods ====="
                kubectl get pods || true

                echo "===== Kubernetes deployment ====="
                kubectl get deployment task-api || true
            '''
        }

        always {
            echo 'Nettoyage des conteneurs Docker Compose...'

            sh '''
                docker compose down || true
            '''
        }
    }
}
