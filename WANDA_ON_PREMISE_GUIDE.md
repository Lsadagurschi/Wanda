# Guia de Instalação On-Premise — Wanda Enterprise

**Versão:** 1.0.1
**Data:** 06 de Março de 2026

Este guia detalha o processo de instalação da plataforma Wanda em um ambiente corporativo (on-premise) utilizando Docker e Docker Compose. Esta opção está disponível exclusivamente para clientes do plano **Enterprise**.

---

## 1. Visão Geral da Arquitetura

A arquitetura on-premise do Wanda é composta por três contêineres Docker orquestrados pelo Docker Compose:

1. **`wanda-app`** — O serviço principal da aplicação web, construído em Python (Flask).
2. **`wanda-db`** — Um banco de dados PostgreSQL para armazenar os dados da aplicação (usuários, conexões, histórico de consultas).
3. **`wanda-redis`** — (Opcional, recomendado para produção) Um servidor Redis para gerenciamento de sessões e cache.

```mermaid
graph TD
    subgraph Servidor Corporativo
        subgraph Docker Compose
            A[wanda-app] -- armazena dados em --> B[(wanda-db 5432)]
            A -- gerencia sessoes em --> C[(wanda-redis 6379)]
        end
    end

    U[Usuario Corporativo] -- HTTPS --> A
    A -- SSL/TLS --> D[(Bancos Internos da Empresa)]

    style A fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff
    style B fill:#059669,stroke:#34d399,stroke-width:2px,color:#fff
    style C fill:#dc2626,stroke:#f87171,stroke-width:2px,color:#fff
    style D fill:#f59e0b,stroke:#facc15,stroke-width:2px,color:#000
```

| Componente | Tecnologia | Descrição |
| :--- | :--- | :--- |
| **wanda-app** | Python Flask + Gunicorn | Aplicação principal: interface web, lógica de negócio e orquestração de serviços. |
| **wanda-db** | PostgreSQL | Banco de dados gerenciado que armazena usuários, conexões e histórico de consultas. |
| **wanda-redis** | Redis | Gerenciamento de sessões e cache de resultados (recomendado para produção). |
| **Bancos do Cliente** | PostgreSQL, MySQL, etc. | Bancos externos da empresa, acessados em modo somente leitura pela Wanda. |

---

## 2. Pré-requisitos

**Servidor:**

Uma máquina virtual ou servidor físico com Linux (Ubuntu 22.04+ recomendado) ou Windows com WSL2.

| Configuração | Mínimo | Recomendado |
| :--- | :--- | :--- |
| vCPUs | 2 | 4 |
| RAM | 4 GB | 8 GB |
| Disco | 20 GB | 50 GB |

**Software necessário:**

- Docker Engine (versão 20.10+)
- Docker Compose (versão 2.5+)
- Acesso à internet (para baixar imagens e dependências na primeira execução)

**Credenciais:**

- Chave de API válida do Claude (Anthropic) para a funcionalidade NL2SQL.

---

## 3. Passos da Instalação

### Passo 3.1 — Preparar o Ambiente

Clone o repositório oficial da Wanda no servidor:

```bash
git clone https://github.com/Lsadagurschi/Wanda.git
cd Wanda
```

Em seguida, crie o arquivo de variáveis de ambiente a partir do modelo:

```bash
cp .env.example .env
```

### Passo 3.2 — Configurar as Variáveis de Ambiente

Abra o arquivo `.env` em um editor de texto e configure as variáveis conforme a tabela abaixo:

```ini
# Chave secreta para segurança da sessão Flask.
# Gere uma chave segura com: openssl rand -hex 32
SECRET_KEY=sua-chave-secreta-super-segura

# URL do banco de dados PostgreSQL interno do Docker Compose. NÃO ALTERE.
DATABASE_URL=postgresql://wanda:wanda@wanda-db:5432/wanda

# URL do Redis interno do Docker Compose. NÃO ALTERE.
REDIS_URL=redis://wanda-redis:6379/0

# Chave da API do Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui

# Configurações do Flask. Mantenha como está para produção.
FLASK_APP=src.main
FLASK_ENV=production
FLASK_DEBUG=0
```

| Variável | Descrição | Ação Requerida |
| :--- | :--- | :--- |
| `SECRET_KEY` | Chave para criptografar sessões. | **Obrigatório.** Gere uma chave única e segura. |
| `DATABASE_URL` | Conexão com o banco de dados da aplicação. | Não alterar — o Docker Compose gerencia isso. |
| `REDIS_URL` | Conexão com o Redis. | Não alterar — o Docker Compose gerencia isso. |
| `ANTHROPIC_API_KEY` | Chave para a IA do Claude. | **Obrigatório.** Insira sua chave da API Anthropic. |

### Passo 3.3 — Iniciar a Aplicação

Com o Docker e Docker Compose instalados e o arquivo `.env` configurado, inicie a aplicação em modo background:

```bash
docker-compose up --build -d
```

O parâmetro `--build` força a reconstrução das imagens Docker na primeira execução. O processo pode levar alguns minutos enquanto o Docker baixa as imagens base e constrói a aplicação.

### Passo 3.4 — Acessar a Plataforma

Após a conclusão do comando, a plataforma Wanda estará acessível no navegador:

**http://localhost:5000**

O primeiro passo é criar uma conta de administrador para começar a usar a plataforma.

---

## 4. Gerenciamento e Manutenção

**Verificar logs em tempo real:**

```bash
docker-compose logs -f wanda-app
```

**Parar todos os serviços:**

```bash
docker-compose down
```

**Atualizar para a versão mais recente:**

```bash
# 1. Pare a aplicação atual
docker-compose down

# 2. Puxe as atualizações do repositório
git pull origin main

# 3. Reconstrua e inicie a aplicação
docker-compose up --build -d
```

---

## 5. Considerações de Segurança

**Firewall:** Certifique-se de que apenas a porta `5000` (ou a porta configurada no `docker-compose.yml`) esteja exposta externamente no firewall do servidor.

**Backups:** O banco de dados `wanda-db` armazena todos os dados da aplicação. Implemente uma rotina de backup regular para o volume Docker `wanda_postgres_data` para evitar perda de dados.

**HTTPS:** Para produção, é altamente recomendável configurar um proxy reverso (Nginx ou Traefik) na frente da aplicação para habilitar HTTPS (SSL/TLS) com um certificado válido.

---

Em caso de dúvidas ou necessidade de suporte avançado, entre em contato com seu gerente de conta Enterprise.
