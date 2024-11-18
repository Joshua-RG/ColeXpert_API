# Pasos para construir la imagen y contenedor de docker
En el directorio de estos archivos abre una terminal

Para construir la imagen 
`sudo docker build -t nginx-fastapi-colexpert-image .`

Para establecer conexiones entre contenedores

`sudo docker network create ColeXpertNetwork`
`sudo docker network connect ColeXpertNetwork ColeXpertDB`


Para construir el contenedor

`docker run --name ColeXpertAPI --network ColeXpertNetwork -p 8000:8000 -p 80:80 nginx-fastapi-colexpert-image`

# Pasos para instalar docker en ubuntu

Actualizar apt
`sudo apt update`

Instalar herramientas
`sudo apt install apt-transport-https ca-certificates curl software-properties-common`

Instalar docker
`curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg`

```echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null```

`sudo apt install docker-ce docker-ce-cli containerd.io -y`

Verificar la instalacion
`docker info`


