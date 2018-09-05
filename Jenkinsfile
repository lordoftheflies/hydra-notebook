pipeline {
    agent any
    stages {
        stage('SCM') {
            steps {
                slackSend channel: "#jenkins", message: "Build #${env.BUILD_NUMBER} Started - ${env.JOB_NAME} (<${env.BUILD_URL}|Open>)"

                git(url: 'git@github.com:lordoftheflies/hydra-notebook.git', branch: 'master', changelog: true, credentialsId: 'credentials-github-lordoftheflies-ssh', poll: true)
            }
        }

        stage('Install virtual environment') {
            steps {
                sh '''if [ ! -d "env" ]; then
                    virtualenv --no-site-packages -p /usr/bin/python3.6 env
                fi'''
            }
        }



        stage('Setup') {
            steps {
                sh '''. ./env/bin/activate
                    pip install -r requirements.txt --extra-index-url=https://pypi.cherubits.hu
                    python manage.py collectstatic --noinput
                    python manage.py migrate
                deactivate'''
            }
        }

        stage('Cleanup') {
            steps {
                sh '''. ./env/bin/activate
                    if [ -d "portalcrawler/dist" ]; then
                        rm -r portalcrawler/dist
                    fi
                deactivate'''
            }
        }

        stage('Test') {
            steps {
                sh '''. ./env/bin/activate
                    python manage.py test
                deactivate'''
            }
        }

        stage('Update version') {
            steps {
                sh '''. ./env/bin/activate
                    BUMPED_VERSION=$(cat hydra_datastore/version.py | grep "__version__ = " | sed 's/__version__ =//' | tr -d "'")
                    echo "$BUMPED_VERSION"
                    bumpversion --allow-dirty --message 'Jenkins Build {$BUILD_NUMBER} bump version of portalcrawler: {current_version} -> {new_version}' --commit --tag --tag-name 'v{new_version}' --current-version $BUMPED_VERSION patch hydra_datastore/version.py
                deactivate'''

                sh '''git push origin master'''
            }
        }

        stage('Build') {
            steps {
                sh '''. ./env/bin/activate
                    python setup.py sdist develop
                deactivate'''
            }
        }

        stage('Deploy staging') {
            steps {
                sh '''. ./env/bin/activate
                    python setup.py sdist install
                deactivate'''
            }
        }

        stage('Distribute') {
            steps {
                script {
                    try {
                        sh '''. ./env/bin/activate
                            twine upload -r local dist/*
                        deactivate'''
                    } catch(error) {
                        echo 'Deploy failed.'
                        echo 'Exception in distribution: ${error}.'
                        echo currentBuild.result
                    }

                    slackSend color: "warning", channel: "#jenkins", message: "Build #${env.BUILD_NUMBER} Deployment Completed - ${env.JOB_NAME} (<https://jenkins.cherubits.hu/blue/organizations/jenkins/gargantula-frontend/detail/master/${env.BUILD_NUMBER}/pipeline|Open>, <https://pypi.cherubits.hu/packages/|Show>)"
                }
            }
        }

    }

    post {
        success {
            slackSend color: "good", channel: "#jenkins", message: "Build #${env.BUILD_NUMBER} Succeed - ${env.JOB_NAME} (<https://jenkins.cherubits.hu/blue/organizations/jenkins/gargantula-frontend/detail/master/${env.BUILD_NUMBER}/pipeline|Open>)"
        }

        failure {
            slackSend color: "danger", channel: "#jenkins", message: "Build #${env.BUILD_NUMBER} Failed - ${env.JOB_NAME} (<https://jenkins.cherubits.hu/blue/organizations/jenkins/gargantula-frontend/detail/master/${env.BUILD_NUMBER}/pipeline|Open>)"
        }
    }
}