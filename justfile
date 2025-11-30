alias r := run
alias s := stop
alias d := down
alias m := migrate
alias mm := makemigrations
alias mmm := makemigrations_and_migrate 

CHROME := env_var("CHROME_EXECUTION")

DB_HOST := env_var("POSTGRES_HOST")
DB_PORT := env_var("POSTGRES_PORT")
POSTGRES_USER := env_var("POSTGRES_USER")
POSTGRES_PASSWORD := env_var("POSTGRES_PASSWORD")
POSTGRES_DB := env_var("POSTGRES_DB")

run:
   docker compose up -d postgres
   ./manage.py runserver

up *args:
   docker compose up {{args}}

down: 
   docker compose down

stop:
    docker stop $(docker ps -aq)

rebuild:
   docker compose up --build

makemigrations *args:
   ./manage.py makemigrations {{args}}
    
migrate *args:
   ./manage.py migrate {{args}}

makemigrations_and_migrate:
   ./manage.py makemigrations && ./manage.py migrate 

