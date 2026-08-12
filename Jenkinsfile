pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"C:\\Users\\Gaming\\AppData\\Local\\Programs\\Python\\Python39\\python.exe" -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat '"C:\\Users\\Gaming\\AppData\\Local\\Programs\\Python\\Python39\\python.exe" -m py_compile ml_app.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t penguin-species-app .'
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-hub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    bat 'echo %DOCKER_PASSWORD% | docker login -u %DOCKER_USERNAME% --password-stdin'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                bat 'docker tag penguin-species-app palanikumaran/penguin_species_predictor:latest'
                bat 'docker push palanikumaran/penguin_species_predictor:latest'
            }
        }

        stage('Run Docker Container') {
            steps {
                bat 'docker stop penguin-species-container || exit 0'
                bat 'docker rm penguin-species-container || exit 0'
                bat 'docker run -d -p 8501:8501 --name penguin-species-container penguin-species-app'
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}
