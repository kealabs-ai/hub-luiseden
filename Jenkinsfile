pipeline {
    agent any

    environment {
        PROJETO        = 'hubluiseden'
        DEPLOY_PATH    = '/var/jenkins_home/apps/hubluiseden'
        GIT_REPO       = 'https://github.com/kealabs-ai/hub-luiseden.git'
        GIT_BRANCH     = 'master'
        DOCKER         = '/var/jenkins_home/docker'
    }

    stages {

        // ── 1. PREPARAR AMBIENTE ──────────────────────────────────────────
        stage('Prepare') {
            steps {
                sh '''
                    set -e
                    mkdir -p $DEPLOY_PATH
                    cd $DEPLOY_PATH

                    if [ -d ".git" ]; then
                        git fetch origin
                        git reset --hard origin/$GIT_BRANCH
                    else
                        git clone -b $GIT_BRANCH $GIT_REPO .
                    fi

                    echo "  ✔ Repositório atualizado em $DEPLOY_PATH"

                    cp -f $WORKSPACE/docker-compose.yml $DEPLOY_PATH/docker-compose.yml
                    cp -f $WORKSPACE/app/main.py $DEPLOY_PATH/app/main.py

                    for SVC in svc-auth svc-catalogo svc-vendas svc-financeiro svc-orcamentos svc-manutencao svc-fornecedores svc-usuarios; do
                        mkdir -p $DEPLOY_PATH/$SVC
                        cp -f $WORKSPACE/$SVC/main.py         $DEPLOY_PATH/$SVC/main.py
                        cp -f $WORKSPACE/$SVC/Dockerfile      $DEPLOY_PATH/$SVC/Dockerfile
                        cp -f $WORKSPACE/$SVC/requirements.txt $DEPLOY_PATH/$SVC/requirements.txt
                    done

                    echo "  ✔ Arquivos sincronizados do workspace"
                '''
            }
        }

        // ── 2. GARANTIR DOCKER BUILDX ─────────────────────────────────────
        stage('Ensure Buildx') {
            steps {
                sh '''
                    BUILDX_PATH="/var/jenkins_home/.docker/cli-plugins/docker-buildx"
                    if [ ! -f "$BUILDX_PATH" ]; then
                        echo "Instalando docker-buildx..."
                        mkdir -p /var/jenkins_home/.docker/cli-plugins
                        curl -fsSL "https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64" \
                             -o "$BUILDX_PATH"
                        chmod +x "$BUILDX_PATH"
                        echo "  ✔ buildx instalado"
                    else
                        echo "  ✔ buildx já presente"
                    fi
                '''
            }
        }

        // ── 3. BUILD E DEPLOY ─────────────────────────────────────────────
        stage('Deploy') {
            steps {
                sh '''
                    set -e
                    cd $DEPLOY_PATH

                    echo "▶ Garantindo rede eden-net..."
                    $DOCKER network inspect eden-net >/dev/null 2>&1 || \
                        $DOCKER network create eden-net

                    echo "▶ Garantindo rede easypanel..."
                    $DOCKER network inspect easypanel >/dev/null 2>&1 || \
                        $DOCKER network create easypanel

                    echo "▶ Derrubando stack anterior..."
                    $DOCKER compose -f docker-compose.yml -p $PROJETO down --remove-orphans 2>/dev/null || true

                    echo "▶ Build e subida dos containers..."
                    $DOCKER compose -f docker-compose.yml -p $PROJETO up -d --build

                    echo "✅ Deploy concluído"
                '''
            }
        }

        // ── 4. HEALTH CHECK ───────────────────────────────────────────────
        stage('Health Check') {
            steps {
                sh '''
                    echo "▶ Aguardando containers ficarem healthy..."

                    for CONTAINER in hubluiseden eden-svc-auth eden-svc-catalogo eden-svc-vendas eden-svc-financeiro eden-svc-orcamentos eden-svc-manutencao eden-svc-fornecedores eden-svc-usuarios; do
                        echo "  Verificando $CONTAINER..."
                        for i in 1 2 3 4 5 6 7 8 9 10; do
                            HEALTH_STATUS=$($DOCKER inspect --format="{{.State.Health.Status}}" $CONTAINER 2>/dev/null || echo "none")
                            echo "    Tentativa $i/10: $CONTAINER = $HEALTH_STATUS"
                            if [ "$HEALTH_STATUS" = "healthy" ]; then
                                echo "  ✔ $CONTAINER → HEALTHY"
                                break
                            fi
                            if [ $i -eq 10 ]; then
                                echo "  ✘ $CONTAINER não ficou healthy"
                                $DOCKER logs $CONTAINER | tail -20
                                exit 1
                            fi
                            sleep 3
                        done
                    done

                    echo "✅ Todos os containers healthy"
                '''
            }
        }

    }

    post {
        success {
            echo '✅ Deploy HubLuisEden realizado com sucesso!'
        }
        failure {
            echo '❌ Falha no deploy HubLuisEden!'
        }
        always {
            node('built-in') {
                sh '''
                    echo "▶ Estado final dos containers:"
                    /var/jenkins_home/docker ps --filter "name=hubluiseden" --filter "name=eden-svc-" || true
                '''
            }
        }
    }
}
