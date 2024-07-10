## Criando a Tabela de Agendamentos

Para armazenar os agendamentos no banco de dados, você pode criar a seguinte tabela SQL:
---
```sql
create table schedules (
	id SERIAL PRIMARY KEY,
	text varchar(200),
	schedule_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
	sessionName varchar(20)
);
```
### Configurando o Ambiente
---
O sistema utiliza Flask como framework web, Schedule para agendamento em Python e psycopg2 para comunicação com o banco de dados PostgreSQL. Aqui está um guia passo a passo para configurar o ambiente:

### Clonar o Repositório:
---
Clone o repositório do projeto para o seu ambiente local.

#### Ambiente Virtual:
---
Crie um ambiente virtual Python para isolar as dependências do projeto. Você pode usar venv ou virtualenv.

#### Instalação de Dependências:
---
Navegue até o diretório do projeto e instale as dependências listadas no arquivo requirements.txt. Você pode fazer isso executando o seguinte comando:

```bash
pip install -r requirements.txt
```

### Configuração do Banco de Dados:
---
Certifique-se de ter um servidor PostgreSQL em execução. Crie um banco de dados e configure as credenciais de acesso no arquivo .env. Certifique-se de que as credenciais correspondam às suas configurações do PostgreSQL.

### Execução do Aplicativo:
---
Após configurar o ambiente e o banco de dados, você pode iniciar o aplicativo Flask. Navegue até o diretório raiz do projeto e execute o seguinte comando:

```bash
flask run
```
### Acesso ao Aplicativo:
---
Após iniciar o aplicativo, você poderá acessá-lo em http://localhost:5000.