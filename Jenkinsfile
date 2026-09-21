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

                        docker compose down || true
                        docker compose up -d --build
                    '''
                }
            }
        }

        stage('Check Containers') {
            steps {
                sh 'docker compose ps'
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

                    echo "L'API n'a pas démarré."
                    docker compose logs
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'Docker + PostgreSQL + API fonctionnent dans Jenkins !'
        }

        failure {
            echo 'Pipeline en échec.'
        }
    }
}
