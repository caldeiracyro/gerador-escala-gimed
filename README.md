
# Gerador de Escalas de Inspetores – ANVISA (GIMED/GGFIS)

Este é um sistema web desenvolvido em Flask para gerar automaticamente escalas de inspetores com base em planilhas Excel de:

- Disponibilidade semanal
- Inspetores cadastrados
- Preferências de dupla
- Estrutura da escala padrão

---

## 🔧 Tecnologias utilizadas

- Python + Flask
- Pandas
- Jinja2 (templates)
- Bootstrap 5
- Chart.js (opcional – pode ser substituído por tabela)

---

## 🗂 Estrutura do Projeto

```
.
├── app_flask.py           # Backend principal Flask
├── utils.py               # Funções de geração da escala e estatísticas
├── requirements.txt       # Dependências do projeto
├── templates/
│   └── index.html         # Página web com formulário e resultado
├── static/
│   └── Escala_Final_Otimizada.xlsx (gerado no runtime)
└── uploads/
    └── arquivos temporários enviados (não vão para o GitHub)
```

---

## 🚀 Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/gerador-escala-anvisa.git
cd gerador-escala-anvisa
```

### 2. Crie um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Crie um arquivo `.env` com as senhas de login (criptografadas com werkzeug)

```env
ADMIN_PASSWORD=<hash da senha do admin>
USER_PASSWORD=<hash da senha do user>
```

Para gerar os hashes:

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('sua_senha'))"
```

### 5. Rode o servidor

```bash
python app_flask.py
```

Abra no navegador: `http://localhost:5000`

---

## 📄 Upload necessário

Na interface, você deve carregar:

- `escala.xlsx` – estrutura da escala semanal
- `disponibilidade.xlsx` – disponibilidade por semana/inspetor
- `inspetores.xlsx` – lista de inspetores e liderança
- `preferencias.xlsx` – mapeamento de preferências entre inspetores

---

## ✅ Resultado

- Arquivo `Escala_Final_Otimizada.xlsx` gerado automaticamente
- Tabela com estatísticas de escalas por inspetor

---

## 🌐 Deploy gratuito

Você pode fazer o deploy no [Render](https://render.com):

- Instale `gunicorn` no `requirements.txt`
- Use `Start Command`: `gunicorn app_flask:app`

---

## 👨‍💼 Desenvolvido por

Este sistema foi criado para fins administrativos e operacionais no contexto da ANVISA (GIMED/GGFIS), com o objetivo de otimizar a geração de escalas de inspeções sanitárias.
