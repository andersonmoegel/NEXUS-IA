# NEXUS BING IA

Interface de chat desktop construída em **Python + CustomTkinter** que conecta com a API da **Groq** para executar modelos **LLM** de baixa latência.

O projeto simula um assistente chamado **NEXUS**, inspirado no estilo sarcástico do personagem **Chandler Bing** da série **Friends**.

A aplicação possui:

* Interface moderna estilo **Apple Dark UI**
* Histórico persistente de conversas
* Animação de digitação estilo chat
* Processamento assíncrono com threads
* Integração direta com modelos **Llama** via Groq

---

# Interface

Principais características da UI:

* Tema **Dark minimalista**
* Balões de conversa estilo mensageiro
* Scroll automático
* Campo de texto expansível
* Botão de novo chat
* Indicador de processamento da IA

---

# Arquitetura

Estrutura lógica do sistema:

```
NEXUS
│
├── Interface (CustomTkinter)
│
├── Gerenciamento de sessão
│   └── nexus_session.json
│
├── Cliente API
│   └── Groq API
│
└── Motor de chat
    └── Llama 3.1
```

Fluxo de execução:

```
Usuário envia mensagem
        ↓
Histórico é atualizado
        ↓
Thread envia request para Groq
        ↓
Modelo LLM gera resposta
        ↓
Resposta renderizada na UI
```

---

# Tecnologias Utilizadas

| Tecnologia    | Função                   |
| ------------- | ------------------------ |
| Python        | Linguagem principal      |
| CustomTkinter | Interface gráfica        |
| httpx         | Cliente HTTP             |
| threading     | Processamento assíncrono |
| Groq API      | Execução do modelo LLM   |
| JSON          | Persistência de sessão   |

---

# Modelo Utilizado

O sistema utiliza o modelo:

* **`llama-3.1-8b-instant`**

Executado via infraestrutura da **Groq**, conhecida por **inferência extremamente rápida para LLMs**.

---

# Instalação

### 1 — Clonar repositório

```bash
git clone https://github.com/seuusuario/nexus-bing-ia.git
cd nexus-bing-ia
```

---

### 2 — Criar ambiente virtual

```bash
python -m venv venv
```

Ativar:

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

---

### 3 — Instalar dependências

```bash
pip install customtkinter groq httpx
```

---

### 4 — Configurar API Key

Crie uma variável de ambiente:

Windows:

```powershell
setx GROQ_API_KEY "sua_api_key"
```

Linux / Mac:

```bash
export GROQ_API_KEY="sua_api_key"
```

Obtenha uma chave em:

[https://console.groq.com/](https://console.groq.com/)

---

# Executar

```bash
python app.py
```

A aplicação abrirá uma janela desktop com o chat.

---

# Estrutura do Projeto

```
nexus-bing-ia
│
├── app.py
├── nexus_session.json
└── README.md
```

---

# Recursos

### Sistema de histórico

As conversas são salvas automaticamente em:

```
nexus_session.json
```

Isso permite:

* restaurar sessões
* manter contexto
* continuar conversas após fechar o app

---

### Animação de digitação

A resposta da IA é renderizada **caractere por caractere**, simulando digitação humana.

Implementação:

```
Mensagem.digitar()
```

---

### Threading

Para evitar travamento da interface:

```
threading.Thread(target=self.processar)
```

Isso mantém a UI responsiva durante chamadas da API.

---

# Segurança

⚠️ **Nunca exponha sua API key diretamente no código.**

Use sempre:

```
os.getenv("GROQ_API_KEY")
```

Caso contrário qualquer pessoa que acessar o repositório poderá usar sua conta.

---

# Possíveis Melhorias

Algumas evoluções naturais do projeto:

* integração com **speech-to-text**
* suporte a **plugins/tools**
* busca na internet
* modo **voz**
* múltiplas conversas
* exportar chats
* suporte a **RAG (Retrieval Augmented Generation)**

---

# Roadmap

| Feature               | Status    |
| --------------------- | --------- |
| Interface Desktop     | ✔         |
| Integração Groq       | ✔         |
| Histórico             | ✔         |
| Animação de digitação | ✔         |
| Multi Chat            | Planejado |
| Plugins               | Planejado |
| Web version           | Planejado |

---

# Autor

**Anderson Moegel**

Desenvolvedor focado em:

* automação
* inteligência artificial
* ferramentas para produtividade
* análise de dados

LinkedIn
[https://linkedin.com/in/andersonmoegel](https://linkedin.com/in/andersonmoegel)
