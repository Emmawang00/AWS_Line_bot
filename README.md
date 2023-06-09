# Personal Assistant Line Bot using AWS 

## Goal of the Project

The project aims to design an interactive Line Bot that can help track the to-do list. Line is a message platform where people in Taiwan, Japan and Korea use in their daily life.

## Project Flow

![Project4](https://user-images.githubusercontent.com/112578755/229415976-97aae94c-f5f3-474c-94ff-14f4ed1817d5.jpg)

* First, AWS Lambda Function was built to connect dynamoDB (using `boto3`) and Line (using the `line-bot-sdk`).
* To import the line package, you'll need to zip the package using EC2, and save it as a Lambda Layer.
* Second, you will need to set up two Environmental variables in configuration: `ACCESS_TOKEN` and `SECRET` generated from Line in the Lambda Function.
* Create a table in dynamoDB with the key being `LineID`.

<img width="595" alt="DynamoDB" src="https://user-images.githubusercontent.com/112578755/229414771-b26828bb-6c26-45d9-a8d6-029f80908546.png">

* Connect the Lambda Function with AWS Gateway using the REST API, which would allow the messages sent from Line users to store in dynamoDB, and allow the information to be pulled out from dynamoDB.

<img width="505" alt="apigateway" src="https://user-images.githubusercontent.com/112578755/229415077-8badc31e-75e1-49b5-a123-aa6d6e1940d9.png">


## How the Line Bot looks like 

![IMG_7473](https://user-images.githubusercontent.com/112578755/230182981-7155b16c-9100-421d-bd48-0aca14c21351.jpg)

