pipeline {
    agent any

    environment {
        PYTHON_MODULE_NAME = 'hydra_notebook'
    }

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
                    if [ -d "dist" ]; then
                        rm -r dist
                    fi
                deactivate'''
            }
        }

        stage('Test') {
            steps {
                sh '''. ./env/bin/activate
                    pytest --verbose --junit-xml test-reports/results.xml
                deactivate'''
            }
            post {
                always {
                    // Archive unit tests for the future
                    junit allowEmptyResults: true, testResults: 'test-reports/results.xml'
                }
            }
        }

        stage('Static code metrics') {
            steps {
                echo "Code Coverage"
                sh  ''' . ./env/bin/activate
                        coverage run --source='.' manage.py test ${env.PYTHON_MODULE_NAME}
                        python -m coverage xml -o ./test-reports/coverage.xml

                    '''
                echo "PEP8 style check"
                sh  ''' . ./env/bin/activate
                        pylint --disable=C ${env.PYTHON_MODULE_NAME} || true
                    '''
            }

            post{
                always{
                    step([$class: 'CoberturaPublisher',
                                   autoUpdateHealth: false,
                                   autoUpdateStability: false,
                                   coberturaReportFile: 'test-reports/coverage.xml',
                                   failNoReports: false,
                                   failUnhealthy: false,
                                   failUnstable: false,
                                   maxNumberOfBuilds: 10,
                                   onlyStable: false,
                                   sourceEncoding: 'ASCII',
                                   zoomCoverageChart: false])
                }
            }
        }

        stage('Update version') {
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                sh '''. ./env/bin/activate
                    BUMPED_VERSION=$(cat ${env.PYTHON_MODULE_NAME}/version.py | grep "__version__ = " | sed 's/__version__ =//' | tr -d "'")
                    echo "$BUMPED_VERSION"
                    bumpversion --allow-dirty --message 'Jenkins Build {$BUILD_NUMBER} bump version of hydra-notebook: {current_version} -> {new_version}' --commit --tag --tag-name 'v{new_version}' --current-version $BUMPED_VERSION patch ${PYTHON_MODULE_NAME}/version.py
                deactivate'''

                sh '''git push origin master'''
            }
        }

        stage('Build') {
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                sh '''. ./env/bin/activate
                    python setup.py sdist develop
                deactivate'''
            }
        }

        stage('Deploy staging') {
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                sh '''. ./env/bin/activate
                    python setup.py sdist install
                deactivate'''
            }
        }

        stage('Distribute') {
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
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

                    slackSend color: "warning", channel: "#jenkins", message: "Build #${env.BUILD_NUMBER} Deployment Completed - ${env.JOB_NAME} (<https://jenkins.cherubits.hu/blue/organizations/jenkins/hydra-notebook/detail/master/${env.BUILD_NUMBER}/pipeline|Open>, <https://pypi.cherubits.hu/packages/|Show>)"
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