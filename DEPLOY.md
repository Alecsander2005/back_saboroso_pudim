# Hospedar na Render com banco Supabase

## 1. Criar o banco no Supabase

1. Crie um projeto no [Supabase](https://supabase.com/dashboard) e guarde a
   senha do banco definida na criação.
2. No projeto, abra **Connect** e escolha **Session pooler**. Copie a URI de
   conexão PostgreSQL; ela terá este formato:
   `postgresql://postgres.<PROJECT_REF>:<PASSWORD>@<POOLER_HOST>:5432/postgres`.
3. Use a URI completa como `DATABASE_URL` na Render. Substitua o marcador de
   senha pela senha do banco. Se ela tiver caracteres como `@`, `#`, `?`, `/`
   ou espaços, faça o percent-encoding desses caracteres antes de salvar a URI.

O Session pooler é apropriado para este servidor web persistente e funciona em
redes IPv4. Não use a chave/API URL do Supabase: este projeto se conecta
diretamente ao PostgreSQL. As tabelas são criadas pelas migrações Django no
primeiro deploy; não é necessário executar SQL manualmente.

## 2. Criar o serviço web na Render

1. Envie o repositório ao GitHub e, no painel da [Render](https://dashboard.render.com),
   escolha **New > Web Service** e conecte o repositório.
2. Preencha:

   | Campo na Render | Valor |
   | --- | --- |
   | Language / Runtime | Python 3 |
   | Root Directory | deixe em branco (raiz do repositório) |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `bash start.sh` |
   | Region | escolha uma região próxima à do projeto Supabase |

3. Em **Environment**, crie as variáveis da tabela abaixo. Salve os valores
   sensíveis como secrets e não os coloque no Git.
4. Crie o serviço. O `start.sh` aplica as migrações (adotando migrações iniciais
   quando as tabelas correspondentes já existem), cria o administrador inicial,
   coleta os arquivos estáticos e inicia o Gunicorn.

## 3. Variáveis de ambiente da Render

| Nome | Valor a colocar |
| --- | --- |
| `DATABASE_URL` | URI PostgreSQL **Session pooler** copiada do Supabase. |
| `SECRET_KEY` | Gere uma chave exclusiva; comando abaixo. |
| `DEBUG` | `False` |
| `EMAIL_ENCRYPTION_KEY` | Gere uma chave Fernet; comando abaixo. |
| `INITIAL_ADMIN_EMAIL` | E-mail que será usado para entrar no painel administrativo. |
| `INITIAL_ADMIN_PASSWORD` | Senha forte para esse administrador. |
| `INITIAL_ADMIN_NAME` | Nome exibido para o administrador; por exemplo, `Administrador da loja`. |
| `ALLOWED_HOSTS` | Domínio da API sem `https://`, por exemplo `saboroso-api.onrender.com`. Se usar domínio próprio, separe os domínios por vírgula. A Render também informa automaticamente o hostname `.onrender.com` do serviço. |
| `CORS_ALLOWED_ORIGINS` | URL(s) completa(s) do frontend, por exemplo `https://saboroso-pudim.onrender.com`. Separe várias URLs por vírgula e não coloque `/` no final. |
| `CSRF_TRUSTED_ORIGINS` | Origem(ens) HTTPS autorizada(s), normalmente a URL do frontend; separadas por vírgula. Exemplo: `https://saboroso-pudim.onrender.com`. |

Gere `SECRET_KEY` e `EMAIL_ENCRYPTION_KEY` localmente, com as dependências do
projeto instaladas:

```sh
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Use cada saída na variável correspondente. **Guarde ambas em local seguro e não
as regenere entre deploys**: perder `EMAIL_ENCRYPTION_KEY` impede a leitura dos
e-mails já criptografados no banco; perder `SECRET_KEY` invalida tokens e
sessões existentes.

Configure as duas chaves antes do primeiro deploy: a inicialização aplica
migrações e cria o administrador, operações que dependem de
`EMAIL_ENCRYPTION_KEY`.

`INITIAL_ADMIN_EMAIL` e `INITIAL_ADMIN_PASSWORD` são obrigatórios porque o
comando de inicialização cria essa conta (ou preserva a existente) a cada
inicialização. Se o e-mail já pertencer a uma conta não administradora, o
serviço interrompe a inicialização em vez de alterar essa conta.

Atualizar `INITIAL_ADMIN_PASSWORD` na Render não altera a senha já salva no
banco. Para sincronizar a conta existente após mudar a variável, abra o Shell do
serviço Render e execute:

```sh
python manage.py ensure_admin --reset-password
```

O comando exige a senha configurada no ambiente, valida sua força e atualiza o
hash no banco. A inicialização normal continua preservando a senha existente.

## 4. Conferir o deploy

- Veja **Events** e **Logs** no serviço da Render. O primeiro deploy deve
  terminar as migrações e informar que o administrador foi criado.
- Abra a URL `.onrender.com` do serviço. O painel fica na raiz; a API usa os
  caminhos `/api/...`.
- Para trocar a origem do frontend, atualize `CORS_ALLOWED_ORIGINS` e faça um
  novo deploy. Configure também `CSRF_TRUSTED_ORIGINS` caso o frontend faça
  requisições protegidas por CSRF.

## Atenção a dados existentes e imagens

As migrações criam as tabelas no Supabase, mas **não copiam** os registros do
`db.sqlite3` local. Se precisar manter esses dados, planeje uma migração de
dados antes de apontar o serviço para o banco novo.

O banco guarda os caminhos das imagens, mas os arquivos de `media/` ficam no
disco local do serviço Render, que é efêmero. Portanto, imagens enviadas pelo
painel podem desaparecer em um novo deploy ou reinicialização. Para mantê-las,
configure armazenamento persistente (por exemplo, Supabase Storage) antes de
usar uploads em produção; conectar o PostgreSQL, sozinho, não persiste esses
arquivos.

## Desenvolvimento local

Instale as dependências com `pip install -r requirements.txt`, defina
`DEBUG=True`, configure `EMAIL_ENCRYPTION_KEY` e `SECRET_KEY` no ambiente (ou
em um `.env` local ignorado pelo Git) e rode `python manage.py migrate` e
`python manage.py runserver`. Sem `DATABASE_URL`, o projeto usa SQLite local.

Referências: [deploy de Django na Render](https://render.com/docs/deploy-django)
e [métodos de conexão PostgreSQL do Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres).
