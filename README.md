# MNIST & Cassandra in docker
In this project, a application is built with docker that can recognize a uploaded image of the handwritten digit. <br/>

The user can use a Curl command to the designated address in the terminal or paste the URL in the website, the flask route will invoke a mnist model to predict the digit image, it will also save the file name, request time and the predict result into a cassandra database.<br/>

## Build Command
We need to build two docker containers, one for cassandra database, and the other for application.The two containers are connected by the Docker Network Bridge, which allows the communication between them.<br/>
To construct the Docker Network Bridge, execute the following command:
```
docker network create [bridge-name]
```

Pull the cassandra image from Docker Hub:
```
docker pull Cassandra
```

TConstruct the cassandra database container:
```
docker run --name cassandra --net=[bridge-name] -p 9042:9042 -d cassandra:latest
```

Build the application image with the Dockerfile:
```
docker build -t [imagename]:latest .
```

Construct the application container:
```
docker run --name [imagename] --net=[bridge-name] -d -p 8000:5000 [v]:latest
```
Using a curl command to submit a predict request.<br/>
Notice the size of image should be 28pix * 28pix.
```
curl -X POST -F image=@[path_to_the_image] '[url_to_the_service]'

```
Or you can using 0.0.0.0:8000 to view in the website, in this way you can submit the image from your folder, and you will receive the result in 0.0.0.0:8000/mnist

Checking the database with the following command:
```
docker exec -it cassandra cqlsh

```

