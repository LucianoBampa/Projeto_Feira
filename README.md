# Sistema de Feirantes - Projeto_Feira (Inova Tech)

## 1. Descrição do Projeto
O **Sistema de Feirantes** é uma plataforma web desenvolvida em Django para **conectar feirantes e consumidores**, permitindo que feirantes criem sua loja online, gerenciem produtos e participem de feiras locais, enquanto consumidores podem localizar feirantes, visualizar produtos e entrar em contato diretamente.

## 2. Principais funcionalidades:
  
  ## Para Feirantes:
    - Cadastro e login de feirantes.
    - Loja online exclusiva para cada feirante.
    - Sistema de avaliação de feirantes pelos consumidores.
    - Dashboard completo para feirantes:
      - Gerenciamento de produtos (criar, editar, deletar).
      - Visualização das feiras em que participa.
      - Edição de perfil.

  ## Para Consumidores:
    - Busca por produtos e feirantes.
    - Mapas interativos das feiras.
    - Visualizações de Detalhes das Feiras.
    - Máscaras de CPF, telefone e WhatsApp para melhor visualização.
    - Termos de Uso e Política de Privacidade (em conformidade com a LGPD):
    - Contato direto com feirantes via telefone, e-mail ou WhatsApp.

  ## Extras:
    - Integração com mapa interativo para localização de feiras
    - Páginas de Termos de Uso e Política de Privacidade (conforme LGPD)

## 3. Tecnologias Utilizadas
- **Backend:** Python 3.x, Django 4.x
- **Frontend:** HTML5, CSS3, Bootstrap 5, FontAwesome
- **Banco de Dados:** SQLite3 (atualmente; preparado para MySQL 9.0.1)
- **APIs/JS:** Leaflet.js (mapa interativo)
- **Outros:** validate-docbr (validação de CPF)

---

## 4. Estrutura de Diretórios Importante

feirantes/
├─ templates/
│ ├─ feirantes/
│ │ ├─ painel/
│ │ │ ├─ dashboard.html
│ │ │ ├─ minhas_feiras.html
│ │ │ ├─ produtos.html
│ │ │ ├─ produto_form.html
│ │ │ ├─ produto_confirm_delete.html
│ │ │ └─ editar_perfil.html
│ │ ├─ loja.html
│ │ ├─ lista.html
│ │ ├─ lista_feiras.html
│ │ ├─ mapa.html
│ │ ├─ mapa_feiras_feirante.html
│ │ ├─ mensagens.html
│ │ ├─ politica_privacidade.html
│ │ ├─ termos_uso.html
│ │ ├─ acesso_negado.html
│ │ ├─ avaliar_feirante.html
│ │ ├─ base.html
│ │ ├─ busca.html
│ │ └─ cadastro.html
├─ static/
├─ media/
├─ models.py
├─ views.py
├─ urls.py
└─ manage.py

## 5. Instalação e Setup

  ### Pré-requisitos
  Python >=3.10
  django-bootstrap-v5>=1.0.11
  django-widget-tweaks>=1.5.0

  # Framework principal
  Django>=4.2.23

  # Banco de dados MySQL
  mysqlclient==2.2.4

  # Biblioteca de imagens (para manipular uploads de fotos)
  Pillow==10.3.0

  # Validação de documentos brasileiros (CPF, CNPJ etc.)
  validate_docbr>=1.11.1

  # Variáveis de ambiente (opcional, caso use .env para senhas)
  python-decouple>=3.0,<3.9

  # Suporte a fusos horários
  tzdata==2024.1

  # Utilitário opcional para melhorar a compatibilidade no Windows
  colorama==0.4.6


## 6. Como Configurar e Rodar o Projeto

Siga os passos abaixo para configurar e iniciar o projeto localmente:

  ### 1 - Clone o repositório
  git clone https://github.com/LucianoBampa/Projeto_Feira.git
  cd Projeto_Feira

  ### 2 - Crie e ative o ambiente virtual
  python -m venv venv
  source venv/bin/activate      # Linux / macOS
  venv\Scripts\activate         # Windows

  ### 3 - Instale as dependências
  pip install -r requirements.txt

  ### 4 - Aplique as migrações
  python manage.py makemigrations
  python manage.py migrate

  ### 5 - Crie um superusuário para acessar o painel admin
  python manage.py createsuperuser

  ### 6 - Inicie o servidor de desenvolvimento
  python manage.py runserver

    Abra o navegador e acesse:
    http://127.0.0.1:8000/

  ### 7 - Para atualizações atraves do Github
  git pull origin main

# 7. Considerações

O banco de dados atual é SQLite3, adequado para desenvolvimento local. Para produção, recomenda-se migrar para MySQL ou PostgreSQL.
Termos de Uso e Política de Privacidade já estão implementados como páginas estáticas.
O sistema está preparado para futuras integrações, como pagamentos e notificações por e-mail.

# 8. Links Úteis

[Repositório GitHub](https://github.com/LucianoBampa/Projeto_Feira.git)

[Termos de Uso](feirantes/termos_uso.html)

[Política de Privacidade](feirantes/politica_privacidade.html)


# 9. Licença
Este é um **projeto acadêmico**, desenvolvido por **Luciano Bampa Vieira**.

O uso do código é permitido **exclusivamente para fins educacionais e não comerciais**.
A comercialização, redistribuição ou uso comercial por terceiros é proibida
sem autorização expressa do autor.

© 2025 – Todos os direitos reservados.
