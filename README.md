# Finance Flow 💜

App de controle financeiro pessoal em **Python + Streamlit**, com **Firebase Authentication** (contas) e **Cloud Firestore** (dados). Cada usuário vê apenas as próprias movimentações.

**Recursos:** cadastro/login/logout/recuperação de senha · indicadores Receita, Despesas e Saldo · listagem com busca e filtros (tipo, categoria, período) · botão circular **+** · criar, editar e excluir (com confirmação) · gráfico Plotly · exportação CSV · valores em centavos inteiros.

## Estrutura
```text
app.py                    # entrada e roteamento (login / dashboard / formulário)
database/firebase.py      # único módulo que lê credenciais e conecta ao Firestore
services/transactions.py  # regras de negócio + Firestore (checa o dono em TODA operação)
services/auth.py          # Firebase Auth (REST) + validação de token no servidor
services/export.py        # CSV
components/               # cards, lista, botão +
views/                    # auth, dashboard, formulário
styles/main.css           # tema escuro Finance Flow
tests/                    # pytest (Firebase simulado em memória)
firestore.rules           # regras: bloqueia acesso direto de clientes
.streamlit/secrets.toml.example
```

## A. Pré-requisitos
Python 3.10+, uma conta Google, acesso a https://console.firebase.google.com/ e este projeto baixado.

## B. Criando o projeto Firebase
1. Acesse o [Console do Firebase](https://console.firebase.google.com/) e crie (ou escolha) um projeto.
2. Menu **Build > Firestore Database > Criar banco de dados**.
3. Escolha uma localização próxima (ex.: `southamerica-east1`, São Paulo). Ela não pode ser alterada depois.
4. Em **Regras**, cole o conteúdo de `firestore.rules` e publique. Elas bloqueiam acesso direto de navegadores; o app acessa tudo pelo servidor (Admin SDK). **Não deixe o Firestore em modo de teste** (aberto) além de poucos minutos.

## C. Criando as credenciais
1. **Configurações do projeto (engrenagem) > Contas de serviço > Gerar nova chave privada**. Baixa um `.json`.
2. Guarde em local seguro. **Nunca** envie ao GitHub nem compartilhe.
3. ⚠️ A conta de serviço do Admin SDK tem **permissões privilegiadas**: a chave deve existir só no ambiente confiável do servidor, nunca no navegador ou em HTML.
4. **Configurações do projeto > Geral > Seus apps**: registre um app **Web** (`</>`) e copie a **Chave de API da Web**. Ela é pública e **não** é senha administrativa.

## D. Autenticação por e-mail/senha
1. Console > **Authentication > Começar**.
2. Aba **Sign-in method > E-mail/senha > Ativar > Salvar**.
3. (Opcional) Em **Modelos de e-mail**, personalize a mensagem de redefinição de senha.

## E. Configurando localmente
Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha:
```toml
[firebase]            # campos idênticos aos do JSON da conta de serviço
type = "service_account"
project_id = "SEU_PROJECT_ID"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@SEU_PROJECT_ID.iam.gserviceaccount.com"
client_id = "..."
token_uri = "https://oauth2.googleapis.com/token"

[firebase_web]
api_key = "SUA_WEB_API_KEY"
```
Os nomes dos campos devem ser exatamente esses (o código lê `st.secrets["firebase"]` e `st.secrets["firebase_web"]["api_key"]`). Mantenha os `\n` da chave como estão no JSON. O `.gitignore` já exclui `secrets.toml`, `.env`, `*.json` e ambientes virtuais.

## F. Instalando e executando
```bash
python -m venv .venv
```
Windows: `.venv\Scripts\Activate.ps1` · Linux/macOS: `source .venv/bin/activate`
```bash
pip install -r requirements.txt
streamlit run app.py
```
Se a conexão falhar, o app mostra **"Firebase não configurado: …"** com o motivo (credenciais ausentes, campos faltando, chave malformada). Ele **nunca** troca para outro banco nem simula sucesso.

## G. Primeiro uso e verificação
1. Clique em **Criar minha conta**, preencha nome, e-mail e senha (mín. 6 caracteres). Confira em **Authentication > Users** e em **Firestore > users/{uid}**.
2. Clique no **+**, cadastre uma **receita** de R$ 2.000,00 e salve. Veja o documento em **Firestore > transactions** (`amount_cents: 200000`, `type: income`, `user_id`).
3. Cadastre uma **despesa** de R$ 350,00: Receita R$ 2.000,00 · Despesas R$ 350,00 · Saldo R$ 1.650,00.
4. Menu 👤 > **Sair da conta**. O dashboard deixa de ser acessível. Atualizar a página também exige novo login (a sessão vive só na memória do servidor).
5. **Esqueci minha senha:** informe o e-mail; o Firebase envia o link. A mensagem é a mesma exista ou não a conta.

## H. Segurança e isolamento
- Senhas são tratadas **somente** pelo Firebase Auth: não vão ao Firestore, disco ou `session_state` (os campos de senha somem quando a tela é trocada).
- A cada interação, o ID token é **verificado no servidor** (Admin SDK) e renovado com o refresh token quando expira. O `uid` das operações vem desse token, nunca de formulário/navegador. Um booleano `logged_in` não é usado.
- O Admin SDK **ignora** as regras do Firestore, então `services/transactions.py` confere `user_id` em toda leitura, edição, exclusão e totais. Por isso as regras bloqueiam clientes diretos.
- **Testar isolamento manualmente:** crie duas contas (A e B) em navegadores/janelas anônimas. Cadastre movimentações em A; em B a lista e os totais devem estar vazios. Copie o ID de um documento de A e tente (via testes) editar/excluir com B: retorna "não encontrada". Automatizado em `tests/test_auth.py` e `tests/test_transactions.py`.
- Cadastro parcial: se o perfil no Firestore falhar após criar a conta, a conta do Authentication é removida.
- Limitação: filtros e totais são calculados em Python sobre os documentos do usuário (evita índices compostos). Para milhares de lançamentos, considere paginação/agregações no Firestore.

## I. Testes
```bash
pytest
```
Usam Firestore e Firebase Auth **simulados em memória** (nenhum dado ou conta real é tocado) e `AppTest` do Streamlit para o fluxo completo (+ → formulário → salvar → listagem e totais).

## J. Publicação (Streamlit Community Cloud)
1. Suba o código para um repositório GitHub **sem** `secrets.toml`.
2. Em https://share.streamlit.io, crie o app apontando para `app.py`.
3. **Settings > Secrets**: cole o conteúdo do seu `secrets.toml`.
4. Revise antes de divulgar: regras do Firestore publicadas (`firestore.rules`), conta de serviço com permissões mínimas (papel *Cloud Datastore User* / *Firebase Authentication Admin* é suficiente), e domínios autorizados em Authentication > Settings.
5. Considere restringir a Chave de API da Web no Google Cloud Console (APIs habilitadas: Identity Toolkit/Secure Token).

## K. Solução de problemas
| Sintoma | O que fazer |
|---|---|
| "Credenciais do Firebase não encontradas" | Crie `.streamlit/secrets.toml` (rode o app a partir da pasta do projeto). |
| "Chave privada malformada" | Copie `private_key` do JSON sem alterar; mantenha os `\n`. |
| "Chave de API inválida" / projeto incorreto | Confira `project_id` e `api_key` do **mesmo** projeto. |
| "Login por e-mail/senha não está ativado" | Seção D (ativar provedor). |
| `PERMISSION_DENIED` / "Erro de permissão" | Conta de serviço sem papel adequado ou de outro projeto. |
| "Database (default) not found" | Crie o Firestore (seção B). |
| `ModuleNotFoundError` | Ative o venv e rode `pip install -r requirements.txt`. |
| Falha de conexão | Verifique internet/proxy e tente novamente. |
