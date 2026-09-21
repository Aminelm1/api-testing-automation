pipeline {
    agent any

    environment {
        POSTGRES_DB = 'taskdb'
        POSTGRES_USER = 'api_tester'
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
    }

    post {

        success {
            echo '========================================'
            echo 'Pipeline CI terminé avec succès !'
            echo 'API Tests      : OK'
            echo 'Database Tests : OK'
            echo 'Selenium Tests : OK'
            echo '========================================'
        }

        failure {
            echo 'Pipeline CI en échec.'

            sh '''
                echo "===== Docker containers ====="
                docker compose ps || true

                echo "===== Docker logs ====="
                docker compose logs || true
            '''
        }

        always {
            echo 'Nettoyage des conteneurs...'
            sh 'docker compose down || true'
        }
    }
}
