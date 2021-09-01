# Django template in docker with docker-compose

### Features of the template:

### How to use:

#### Clone the repo:

    git clone https://github.com/Mikhail-Gorelov/infotechs_task.git ./project_name

authentification information for user

    SUPERUSER_EMAIL=test@test.com
    SUPERUSER_PASSWORD=tester26

#### Run the local develop server:

    docker-compose up -d --build
    docker-compose logs -f
    
##### Server will bind 8010 port. You can get access to server by browser [http://localhost:8010](http://localhost:8010)


#### Configuration for develop stage at 9000 port:
    docker-compose -f prod.yml -f prod.dev.yml up -d --build

##### The same configuration could be for stage and prod:
    docker-compose -f prod.yml -f prod.stage.yml up -d --build
    docker-compose -f prod.yml -f prod.prod.yml up -d --build
