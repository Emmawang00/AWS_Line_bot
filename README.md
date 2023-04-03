# Personal Assistant Line Bot using AWS 

## Goal of the Project

The project aims to design an interactive Line Bot that can help track the to-do list. Line is a message platform where people in Taiwan, Japan and Korea use in their daily life.

* First, AWS Lambda Function was built to connect dynamoDB and Line (using the `line-sdk`.
* Second, you will need to set up two environmental variables: `ACCESS_TOKEN` and `SECRET` from Line in the Lambda Function.
* Create a table in dynamoDB with the key being `LineID`.
* Connect the Lambda Function with AWS Gateway using the REST API, which would allow the messages sent from Line users to store in dynamoDB, and allow the information to be pulled out from dynamoDB.

## How the Line Bot looks like 

