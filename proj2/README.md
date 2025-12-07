# Backend Instructions
1) Add your unique values for ```my_host```, ```my_user```, and ```my_password``` in the ```get_database()``` function in ```database.py```, if necessary.
2) Run ```database.py``` (to create databases and/or database tables)
3) Run ```load_database.py``` (to load dummy data into tables)
4) Edit ```app.py``` with your unique ```user```, ```password```, and ```host``` strings for ```MYSQL``` in the ```get_app()``` function, if necessary.
5) Run your model's ```.py``` file (i.e., ```drivers.py```)

### NOTES
* Only run the ```load_database.py``` when first creating the database or after dropping all tables to avoid errors due to duplicate entries.
* ```database.py``` makes three different databases: one for **testing**, **development** (*default*), and **production**. 
* Functions ```drop_table(database, table)``` and ```drop_all_tables(database)``` are included in ```database.py``` for your convenience/if needed.  
* Change ```db_name``` to ```movie_munchers_test``` in ```load_database.py``` to load dummy data into test database before performing api/unit tests.
* A local ```.env.example``` file can be used to store your personal ```MYSQL``` data for reference.
* Recommended to make sub-branches from backend for each model (i.e., ```backend-drivers```).
* Review ```models.py``` to confirm model structure and data types.

### Helpful Functions
- ```db.session.add()``` (adding instance of model to session)
- ```db.session.commit()``` (committing all session changes to database)
