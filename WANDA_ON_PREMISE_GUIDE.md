# Guia de Instalação On-Premise — Wanda Enterprise

**Versão:** 1.0.1
**Data:** 06 de Março de 2026

Este guia detalha o processo de instalação da plataforma Wanda em um ambiente corporativo (on-premise) utilizando Docker e Docker Compose. Esta opção está disponível exclusivamente para clientes do plano **Enterprise**.

---

## 1. Visão Geral da Arquitetura

A arquitetura on-premise do Wanda é composta por três contêineres Docker orquestrados pelo Docker Compose:

1.  **`wanda-app`**: O serviço principal da aplicação web, construído em Python (Flask).
2.  **`wanda-db`**: Um banco de dados PostgreSQL para armazenar os dados da aplicação (usuários, conexões, histórico de consultas).
3.  **`wanda-redis`**: (Opcional, recomendado para produção) Um servidor Redis para gerenciamento de sessões e cache.

```mermaid
graph TD
    subgraph Servidor Corporativo (Linux / Windows com WSL2)
        subgraph Docker Compose
            A[wanda-app] -- armazena dados em --> B(wanda-db:5432);
            A -- gerencia sessões em --> C(wanda-redis:6379);
        end
    end

    U(Usuário Corporativo) -- acessa via browser --> A;
    A -- conecta-se a --> D{Bancos de Dados Internos};

    style A fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff
    style B fill:#059669,stroke:#34d399,stroke-width:2px,color:#fff
    style C fill:#dc2626,stroke:#f87171,stroke-width:2px,color:#fff
    style D fill:#f59e0b,stroke:#facc15,stroke-width:2px,color:#000
```

## 2. Pré-requisitos

-   **Servidor:** Uma máquina virtual ou servidor físico com Linux (Ubuntu 22.04+ recomendado) ou Windows com WSL2.
    -   **Mínimo:** 2 vCPUs, 4 GB RAM, 20 GB de disco.
    -   **Recomendado:** 4 vCPUs, 8 GB RAM, 50 GB de disco.
-   **Software:**
    -   Docker Engine (versão 20.10+)
    -   Docker Compose (versão 2.5+)
-   **Acesso à Internet:** Necessário para baixar as imagens Docker e dependências iniciais.
-   **Chave da API Anthropic:** Uma chave de API válida do Claude para a funcionalidade NL2SQL.

## 3. Passos da Instalação

### Passo 3.1: Preparar o Ambiente

1.  **Clone o repositório do Wanda:**

    ```bash
    git clone https://github.com/Lsadagurschi/Wanda.git
    cd Wanda
    ```

2.  **Crie o arquivo de variáveis de ambiente:**

    Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env`.

    ```bash
    cp .env.example .env
    ```

### Passo 3.2: Configurar as Variáveis de Ambiente

Abra o arquivo `.env` em um editor de texto e configure as seguintes variáveis:

```ini
# Chave secreta para segurança da sessão Flask. Gere uma chave segura.
# Use `openssl rand -hex 32` no terminal para gerar uma.
SECRET_KEY=sua-chave-secreta-super-segura

# URL do banco de dados PostgreSQL interno do Docker Compose. NÃO ALTERE.
DATABASE_URL=postgresql://wanda:wanda@wanda-db:5432/wanda

# URL do Redis interno do Docker Compose. NÃO ALTERE.
REDIS_URL=redis://wanda-redis:6379/0

# Chave da API do Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui

# (Opcional) Modelo específico do Claude a ser usado
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Configurações do Flask. Mantenha como está para produção.
FLASK_APP=src.main
FLASK_ENV=production
FLASK_DEBUG=0
```

| Variável | Descrição | Ação Requerida |
| :--- | :--- | :--- |
| `SECRET_KEY` | Chave para criptografar sessões. | **Obrigatório.** Gere uma chave única e segura. |
| `DATABASE_URL` | Conexão com o banco de dados da aplicação. | Não alterar. O Docker Compose gerencia isso. |
| `REDIS_URL` | Conexão com o Redis. | Não alterar. O Docker Compose gerencia isso. |
| `ANTHROPIC_API_KEY` | Chave para a IA do Claude. | **Obrigatório.** Insira sua chave da API Anthropic. |

### Passo 3.3: Iniciar a Aplicação

Com o Docker e Docker Compose instalados e o arquivo `.env` configurado, inicie a aplicação em modo "detached" (background):

```bash
docker-compose up --build -d
```

-   `--build`: Força a reconstrução das imagens Docker na primeira vez.
-   `-d`: Executa os contêineres em background.

O processo pode levar alguns minutos na primeira execução, pois o Docker irá baixar as imagens base e construir a aplicação.

### Passo 3.4: Acessar a Plataforma

Após a conclusão do comando, a plataforma Wanda estará acessível no seu navegador no seguinte endereço:

**http://localhost:5000**

O primeiro passo é criar uma conta de administrador para começar a usar a plataforma.

## 4. Gerenciamento e Manutenção

-   **Verificar logs:** Para ver os logs da aplicação em tempo real:

    ```bash
    docker-compose logs -f wanda-app
    ```

-   **Parar a aplicação:** Para parar todos os serviços:

    ```bash
    docker-compose down
    ```

-   **Atualizar a aplicação:** Para atualizar para a versão mais recente do Wanda:

    ```bash
    # 1. Pare a aplicação atual
    docker-compose down

    # 2. Puxe as atualizações do repositório
    git pull origin main

    # 3. Reconstrua e inicie a aplicação
    docker-compose up --build -d
    ```

## 5. Considerações de Segurança

-   **Firewall:** Certifique-se de que apenas a porta `5000` (ou a porta que você configurar no `docker-compose.yml`) esteja exposta externamente no firewall do servidor.
-   **Backups:** O banco de dados `wanda-db` armazena todos os dados da aplicação. Implemente uma rotina de backup regular para o volume Docker `wanda_postgres_data` para evitar perda de dados.
-   **HTTPS:** Para produção, é altamente recomendável configurar um proxy reverso (como Nginx ou Traefik) na frente da aplicação para habilitar HTTPS (SSL/TLS).

---

Em caso de dúvidas ou necessidade de suporte avançado, entre em contato com seu gerente de conta Enterprise.
