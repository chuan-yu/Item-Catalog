# Item Catalog Web Application

## Introduction
This is a web application used to manage and display an item catalog. The main functionalities include:

1. Display items by category
2. Authorized users can create, edit and delete items and categories
3. User can sign in with a Google account
4. Include a RESTful API with which JSON data can be retrieved

The application is created using **Flask** framework and **SqlAlchemy**

## Technologies Used

1. Vagrant
2. Flask
3. SqlAlchemy
4. Google oauth2client library
5. PostgreSQL
6. Bootstrap


## Steps to Run the Pogramme
### Setp 1: Clone the application repository to the local machine

### Step 2: Start vagrant machine

- Start the Vagrant machine using command: `vagrant up`
- SSH to the Vagrant machine using command: `vagrant ssh`

### Step 3: Run the pogramme in Vagrant

- Initialize the database using command: `python database_setup.py`
- Start the programme using command: `python catalog.py`


