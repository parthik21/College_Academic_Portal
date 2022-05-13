pipeline {
  environment {
    imagename = "anubhavmohanty/college_academic_portal"
    registryCredential = 'anubhav_dockerhub'
    dockerImage = ''
  }
  agent any
  stages {
    stage('Cloning Git') {
      steps {
        git([url: 'https://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@github.com/parthik21/college_academic_portal.git'])

      }
    }
    stage('Python Build') {
      steps{
         sh "python3 manage.py migrate"
      }
    }
  stage("Api Testing"){
      steps{
        script {
          sh "python3 tests.py"
        }
      }
    }
    stage('Building image') {
        steps{
          script {
            dockerImage = docker.build imagename
          }
        }
      }
    stage('Deploy Image') {
      steps{
        script {
          docker.withRegistry( '', registryCredential ) {
             dockerImage.push('latest')
          }
        }
      }
    }
    stage('Remove Unused docker image') {
      steps{
         sh "docker rmi $imagename:latest"
      }
    }

    stage("Invoke ansible playbook") {
      steps{
      ansiblePlaybook(
      	credentialsId: "contnainer_access_key",
        inventory: "Inventory",
        installation: "ansible",
        limit: "",
        playbook: "docker_playbook.yaml",
        extras: ""
      )
    }
    }

  }
}
