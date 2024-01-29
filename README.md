# Taskhub
TaskHub is an MES for smaller businesses that do not want to / cannot pay large sums for complete ERP integrations.

# Setup
- PyCharm for easy development recommended
- install Python 3.11.x
- setup venv with this version
- load all packages from requirements.txt
- 'python create_secretkey'
- 'python manage.py makemigrations'
- 'python manage.py migrate'
- [ 'python manage.py createsuperuser' optional ]
- 'az login' if Azure connection is possible
- 'python manage.py runserver'

###### Version 1.0.0

- Group : Administrator, Manager, Supervisor, Employee
- EmployeeType : Office, Assembly, Printing, Sales, Contact
- TaskType : assembly, delivery, installation, repair, service
- TaskStatus : in progress, queued, done
- VehicleType : Sedan, Combi, Truck, Roof Storage, Business
- additionally various employees and other resources
- passwords for test users: 'securepassword'