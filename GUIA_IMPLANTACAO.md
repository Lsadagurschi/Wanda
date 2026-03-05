# 🚀 Guia de Implantação Rápida da Wanda

Este guia foi criado para ajudar usuários com pouca ou nenhuma experiência técnica a implantar a plataforma Wanda online. O método recomendado utiliza o **Render.com**, que oferece um processo simplificado e um plano gratuito.

**Tempo estimado:** 15-20 minutos.

---

### 📋 Pré-requisitos

Antes de começar, você precisará de:

1.  **Conta no GitHub:** Essencial para gerenciar o código. [Crie uma conta aqui](https://github.com/join).
2.  **Conta no Render:** Plataforma onde a Wanda será hospedada. [Crie uma conta aqui](https://dashboard.render.com/register).
3.  **Conta no Railway:** Para hospedar o banco de dados MySQL gratuitamente. [Crie uma conta aqui](https://railway.app/login).
4.  **Chave da API Anthropic (Claude):** Necessária para a funcionalidade de IA. Obtenha a sua no [console da Anthropic](https://console.anthropic.com/).

---

### Passo 1: Fazer um "Fork" do Repositório no GitHub

"Fork" é como fazer uma cópia pessoal do projeto para a sua conta do GitHub. O Render usará essa cópia para implantar a aplicação.

1.  Vá para o repositório da Wanda: [https://github.com/Lsadagurschi/Wanda](https://github.com/Lsadagurschi/Wanda)
2.  No canto superior direito da página, clique no botão **Fork**.
3.  Na tela seguinte, apenas confirme clicando em **Create fork**.

Pronto! Agora você tem uma cópia do projeto na sua conta.

---

### Passo 2: Criar o Banco de Dados no Railway

A Wanda precisa de um banco de dados para armazenar informações de usuários, conexões e consultas. Usaremos o Railway para isso.

1.  Acesse seu [Dashboard no Railway](https://railway.app/dashboard).
2.  Clique em **New Project**.
3.  Na lista que aparece, selecione **Provision MySQL**.
4.  Aguarde alguns segundos enquanto o banco de dados é criado.
5.  Com o banco criado, vá para a aba **Variables**. Você verá todas as credenciais de que precisa (`MYSQLHOST`, `MYSQLPORT`, `MYSQLDATABASE`, `MYSQLUSER`, `MYSQLPASSWORD`).

**Importante:** Mantenha essa página aberta. Você precisará dessas informações no próximo passo.

---

### Passo 3: Implantar a Aplicação no Render

Agora vamos conectar tudo no Render para colocar a Wanda no ar.

1.  Acesse seu [Dashboard no Render](https://dashboard.render.com).
2.  Clique em **New +** e selecione **Web Service**.
3.  Na seção "Connect a repository", clique em **Configure account** para conectar sua conta do GitHub. Autorize o acesso a todos os repositórios ou apenas ao fork da Wanda que você criou.
4.  Após conectar, o repositório `SeuUsuario/Wanda` deve aparecer na lista. Clique em **Connect** ao lado dele.
5.  Na tela de configuração, preencha os seguintes campos:
    *   **Name:** `wanda-app` (ou o nome que preferir).
    *   **Region:** Escolha a mais próxima de você (ex: `US East (N. Virginia)`).
    *   **Branch:** `main`.
    *   **Build Command:** `pip install -r requirements.txt` (geralmente já vem preenchido).
    *   **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 src.main:app` (geralmente já vem preenchido).
    *   **Instance Type:** `Free`.

6.  Role para baixo até a seção **Environment Variables**. Aqui é a parte mais importante. Clique em **Add Environment Variable** e adicione as seguintes chaves e valores, uma por uma, usando as informações do Railway e da Anthropic:

| Chave (Key) | Valor (Value) |
|---|---|
| `SECRET_KEY` | *Clique em `Generate` ao lado do campo de valor para criar uma chave segura automaticamente.* |
| `ANTHROPIC_API_KEY` | Sua chave da API Claude (começa com `sk-ant-...`) |
| `DB_HOST` | O valor de `MYSQLHOST` do Railway |
| `DB_PORT` | O valor de `MYSQLPORT` do Railway (geralmente `3306`) |
| `DB_NAME` | O valor de `MYSQLDATABASE` do Railway (geralmente `railway`) |
| `DB_USERNAME` | O valor de `MYSQLUSER` do Railway (geralmente `root`) |
| `DB_PASSWORD` | O valor de `MYSQLPASSWORD` do Railway |
| `FLASK_DEBUG` | `false` |

7.  Após adicionar todas as variáveis, role até o final da página e clique em **Create Web Service**.

---

### Passo 4: Acessar a Wanda

O Render começará o processo de implantação. Você pode acompanhar o progresso na aba **Events** ou **Logs**.

*   A primeira implantação pode levar de 5 a 10 minutos.
*   Quando o status mudar para **Live**, significa que a Wanda está no ar!

No topo da página do seu serviço no Render, você verá a URL da sua aplicação (algo como `https://wanda-app.onrender.com`).

**Clique nessa URL e comece a usar a Wanda!**

---

### ❓ Solução de Problemas

*   **Erro no Deploy:** Verifique a aba **Logs** no Render. A causa mais comum são variáveis de ambiente incorretas. Confira se você copiou e colou os valores do Railway e da Anthropic sem espaços extras.
*   **Aplicação não carrega:** Se o log mostrar um erro de `connection timeout` com o banco de dados, verifique se o seu provedor de banco (Railway) está online e se as credenciais de `DB_HOST` e `DB_PORT` estão corretas.
*   **Erro de API:** Se a conversão de pergunta para SQL não funcionar, verifique se a `ANTHROPIC_API_KEY` está correta e se sua conta Anthropic tem créditos.

