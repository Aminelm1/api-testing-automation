pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Code récupéré depuis GitHub'
            }
        }

        stage('Environment') {
            steps {
                sh 'python3 --version'
                sh 'docker --version'
                sh 'docker compose version'
            }
        }

        stage('Tests') {
            steps {
                echo 'Les tests automatisés seront lancés ici'
            }
        }
    }

    post {
        success {
            echo 'Pipeline terminé avec succès !'
        }

        failure {
            echo 'Pipeline en échec.'
        }
    }
}
