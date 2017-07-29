# Item Catalog - Craigslist knock-off
The purpose of this project is to demonstrate how you can use flask and sqlalchemy to build a comprehensive catalog app with full CRUD functionality. It also makes use of Google and Facebook OAuth APIs for secure login.

## Installation
* Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* Install [Vagrant](https://www.vagrantup.com/downloads.html)
* Clone this project onto your machine
* Inside the project there should be a folder named `vagrant`
* In terminal, cd into the `vagrant` folder and run `vagrant up`
* Wait for installationt to complete

## Setup

### Google API
* Go to the [Google API page](https://console.developers.google.com/apis/) and create a new project named `gregslist`
* Make sure the project is selected, then go to `Credentials`, `Create credentials`, `OAuth Client ID`
* On the resulting screen click `Configure consent screen` and under `Product name` put `gregslist` and save
* On the next screen select `Web application`
* Under `Authorized JavaScript origins` put `http://localhost:5000`
* Under `Authorized redirect URIs` put `http://localhost:5000` and `http://localhost:5000/login`
* Click save then click the download icon on the right side of the screen under `Web client 1`
* Rename it `client_secret.json` and move it to `/vagrant/gregslist/`
* From inside the `vagrant` folder, run `vagrant up`, `vagrant ssh`

### Facebook API
* Go to the [Facebook app API page](https://developers.facebook.com/apps), click `Add a New App`, name it `gregslist` and click `Create App ID`
* Under `Settings`, `Basic` click `Add Platform` then select `Website`
* Under `Site URL` put `http://localhost:5000`
* Leave the Facebook app settings page open, go to the `/vagrant/gregslist/` folder, create a new file named `fb_client_secrets.json` and paste the following code into it:
```
{
  "web": {
    "app_id": "PASTE_YOUR_APP_ID_HERE",
    "app_secret": "PASTE_YOUR_CLIENT_SECRET_HERE"
  }
}
```
* Back at the Facebook app settings page, use the `App ID` and `App Secret` to fill in the above code.

### Database and dummy data
* Inside the `vagrant` folder run `vagrant up`, `vagrant ssh`
* Once vagrant has launched, cd into this project folder (`cd \vagrant\gregslist`)
* Run `python database_setup.py` then `python dummy_data.py` to add some data to the database

## Use
* Follow the first two steps in the 'Setup' above
* Launch the server by running `python main.py`
* In a browser, go to `http://localhost:5000/` and you should see the homepage
* The page should be relativily intuative. Each category links to a page listing the posts associated with them. There's a login/logout button, a button for posting a new item.

## JSON response
* The main, category, and post pages each have a json version that can be seen by appending `JSON` to the url

