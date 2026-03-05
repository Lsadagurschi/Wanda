# 🔮 Plano de Negócios: Wanda

**Data:** 05 de Março de 2026

## 1. Sumário Executivo

Wanda é uma plataforma SaaS (Software as a Service) projetada para democratizar o acesso a dados. Utilizando inteligência artificial de ponta (Anthropic Claude), a Wanda traduz perguntas em linguagem natural (português) para consultas SQL complexas, permitindo que usuários não-técnicos explorem bancos de dados de forma intuitiva. O modelo de negócio é baseado em assinaturas mensais (freemium), com planos que escalam conforme a necessidade do cliente, desde startups e pequenas empresas até grandes corporações.

O mercado-alvo são empresas que coletam grandes volumes de dados mas carecem de equipes de análise dedicadas ou cujas equipes de negócios dependem de gargalos técnicos para obter insights. A Wanda visa preencher essa lacuna, oferecendo uma ferramenta poderosa, acessível e de rápida implementação.

---

## 2. Análise de Mercado

### 2.1. O Problema

- **Dependência Técnica:** Analistas de negócios, gerentes de produto e executivos precisam de dados para tomar decisões, mas geralmente não sabem escrever SQL. Isso cria uma dependência constante de engenheiros de dados ou analistas de BI.
- **Lentidão:** O ciclo de "pedir dados → esperar na fila → receber relatório" é lento e ineficiente, atrasando decisões críticas.
- **Custo Elevado:** Contratar analistas de dados dedicados é caro, especialmente para pequenas e médias empresas (PMEs).
- **Subutilização de Dados:** Muitas empresas coletam dados valiosos que ficam "presos" em bancos de dados, sem gerar valor por falta de ferramentas acessíveis para explorá-los.

### 2.2. O Público-Alvo

- **Primário:** Pequenas e Médias Empresas (PMEs) em setores como e-commerce, marketing digital, fintechs e startups de tecnologia. Essas empresas possuem dados, mas recursos limitados para análise.
- **Secundário:** Departamentos dentro de grandes corporações (Marketing, Vendas, Produto) que desejam autonomia para realizar suas próprias análises sem sobrecarregar a equipe de TI/BI.
- **Terciário:** Profissionais autônomos e freelancers que gerenciam dados de clientes (ex: gestores de tráfego, consultores de marketing).

### 2.3. Concorrência

| Concorrente | Pontos Fortes | Pontos Fracos |
|---|---|---|
| **Ferramentas de BI Tradicionais** (Tableau, Power BI) | Extremamente poderosas, visualizações avançadas. | Curva de aprendizado íngreme, caras, ainda exigem conhecimento técnico para modelagem de dados. |
| **Concorrentes Diretos NL2SQL** (ex: `ThoughtSpot`, `Tellius`) | Focados no mesmo problema. | Geralmente focados no mercado enterprise, preços muito elevados, implementação complexa, interface em inglês. |
| **Equipes Internas de BI** | Conhecimento profundo do negócio. | Custo de pessoal, gargalo de produtividade, lentidão para responder a novas perguntas. |

**Diferencial da Wanda:** Foco no mercado de língua portuguesa, simplicidade de uso, modelo de preço acessível para PMEs e uma experiência de usuário fluida e intuitiva, transformando a análise de dados em uma conversa.

---

## 3. Estratégia de Marketing e Vendas

### 3.1. Aquisição de Clientes

- **Marketing de Conteúdo:** Criar artigos de blog, tutoriais em vídeo e webinars sobre temas como "Como analisar dados de vendas sem saber programar", "Perguntas que toda startup deveria fazer aos seus dados", etc. Otimização para SEO com foco em palavras-chave como "analise de dados para leigos", "sql em portugues", "dashboard para ecommerce".
- **Modelo Freemium:** O plano gratuito é a principal ferramenta de aquisição, permitindo que os usuários experimentem o valor da Wanda com baixo atrito. O objetivo é converter usuários gratuitos em pagantes à medida que suas necessidades crescem.
- **Parcerias:** Colaborar com consultorias de negócios, agências de marketing digital e plataformas de e-commerce (ex: Shopify, Nuvemshop) para oferecer a Wanda como uma ferramenta complementar.
- **Mídia Paga:** Campanhas direcionadas no LinkedIn e Google Ads focadas em cargos como "Gerente de Marketing", "CEO de Startup", "Analista de Negócios".

### 3.2. Estratégia de Preços

O modelo de preços foi projetado para ser acessível e escalável.

| Plano | Preço (Mensal) | Público-Alvo | Proposta de Valor |
|---|---|---|---|
| **Gratuito** | R$ 0 | Freelancers, estudantes, teste | Experimente o poder da Wanda com limitações generosas. |
| **Starter** | R$ 97 | Pequenas empresas, startups | Ferramentas essenciais para começar a tomar decisões baseadas em dados. |
| **Pro** | R$ 297 | Empresas em crescimento | Funcionalidades avançadas para equipes que dependem de dados diariamente. |
| **Enterprise** | Sob Consulta | Grandes corporações | Solução completa com segurança, suporte e implantação personalizados. |

---

## 4. Projeções Financeiras (Simplificadas - Ano 1)

### 4.1. Premissas

- **Taxa de Conversão (Gratuito → Starter):** 3%
- **Taxa de Conversão (Starter → Pro):** 15%
- **Custo de Aquisição de Cliente (CAC):** R$ 50 (via mídia paga e conteúdo)
- **Custo Operacional Mensal (Servidores, APIs):** R$ 10 por usuário pagante (estimativa inicial)

### 4.2. Metas de Aquisição (Ano 1)

- **Mês 1-3:** Foco em aquisição de 1.000 usuários gratuitos através de lançamento inicial e conteúdo.
- **Mês 4-6:** Atingir 30 clientes pagantes (plano Starter).
- **Mês 7-9:** Atingir 100 clientes pagantes (90 Starter, 10 Pro).
- **Mês 10-12:** Atingir 250 clientes pagantes (220 Starter, 30 Pro).

### 4.3. Receita Anual Estimada (Ano 1)

- **Receita do Plano Starter:** (220 usuários * R$ 97/mês) * 3 meses (média) ≈ R$ 64.020
- **Receita do Plano Pro:** (30 usuários * R$ 297/mês) * 3 meses (média) ≈ R$ 26.730
- **Receita Total Anual (Estimada):** **~R$ 90.750**

*Nota: Esta é uma projeção conservadora e simplificada. A receita real dependerá da velocidade de aquisição e das taxas de conversão.* 

---

## 5. Roadmap do Produto

- **Q2 2026 (Lançamento):** Funcionalidades atuais (NL2SQL, dashboards, exportação, conexões básicas).
- **Q3 2026:**
  - Integração com mais fontes de dados (Google Sheets, arquivos CSV).
  - Alertas programados (ex: "me avise quando as vendas caírem 10%").
  - Melhorias na IA com base no feedback dos usuários.
- **Q4 2026:**
  - Compartilhamento de dashboards com links públicos.
  - API pública para que outras aplicações possam usar o motor da Wanda.
- **2027:**
  - Versão on-premise para clientes Enterprise.
  - Análise preditiva (ex: "projete as vendas para o próximo trimestre").

