# SFDC Field Creator

This application aims to simlpify the generation a Salesforce data model by taking an excel template and converting it into a package xml file and subsiquently deploying the package to Salesforce. This can allow for a data model to be designed and agreed on before creating anything in Salesforce itself.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Installing

To run this app you will first need to install the dependancies using:

```
pip install -r requirements.txt
```

### Usage

To use you will need to complete the config/congig.json file and the enviroment.json with the relevant data. After this you can run the program from the command line using `python package_create`. You can pass in the directory path to the `config.json` if it is not contained within the the `./config` directory.

## Todo

* Create a project structure
* Test classes
* Include options to retrieve metadata and output as Excel file
* Include Excel utilities to covert Profile information into metadata (potentially even other metadata types)
* Split out the config file into multiple files
* Including the object sharing table into Salesforce deployment
* Adding something like pipenv to ensure the versions of packages that are used in the project
* Document the solution
