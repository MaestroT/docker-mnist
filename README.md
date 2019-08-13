# Dockerized MNIST & Cassandra
In this project, a journaling application that can recognize a user-uploaded image of the handwritten digit was constructed by two docker Containers: an Application Docker Container and a Database Docker Container. <br/>

While the user submits a Curl command to the designated address, the Flask Router first makes a safety check to both the command and the image file it contains. The Router then saves the image and requests the prediction from the MNIST TensorFlow model. After the result returns, the Router forwards the result to the user and submits all four data to the Cassandra Database Container through the Docker Network Bridge.<br/>

The Cassandra Database records the user IP address, the service request time, the predicted result, and the path to the uploaded image. Finally, the application currently uses a MNIST model trained by 10000 steps and provides the prediction service with an accuracy of 0.92.  

## Network Preparation
The two Docker Containers, Cassandra Database Container, and Application Container, are connected by the Docker Network Bridge, which allows the communication between them.<br/>
To construct the Docker Network Bridge, execute the following command:
```
docker network create [bridge-name]
```

## Cassandra Container Preparation
A standard Cassandra Database image published on the Docker Hub. <br/>
Thus the administrator can simply pull the image from Docker Hub by the following command:
```
docker pull Cassandra
```

To construct the Docker Container:
```
docker run --name cassandra --net=[bridge-name] --net-alias=cassandra -p 9042:9042 -d cassandra:latest
```

## Application Container Preparation
Since the application image is not available on the Docker Hub, the administrator needs to build the image from the Dockerfile, with the following command:
```
docker build -t [MNIST-Name]:latest .
```

To construct the Docker Container:
```
docker run --name [APP-Name] --net=[bridge-name] --net-alias=[APP-Name] -d -p 8000:5000 [APP-Name]:latest
```

## Submit Prediction
Using following curl command to submit prediction to Application Docker Container.<br/>
The size of testing image should be exactly 28pix * 28pix.
```
curl -X POST -F image=@[path_to_the_image] '[url_to_the_service]'

```

## Local Testing
By attaching to the Application Docker Container, a testing file "1.png" is provide, which could be used by changing [path_to_the_image] to "1.png". <br/>
The default URL to the service is "http://localhost:5000/mnist". <br/>
If testing out of the Docker Container, the port should be changed to 8000. (Defined in Application Container Preparation)# docker-mnist
