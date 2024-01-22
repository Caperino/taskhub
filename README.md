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
- 'python manage.py createsuperuser'
- 'az login'
- 'python manage.py runserver'

###### Version 0.1.0

#### Common Start Types for proper Actions
#### check https://docs.djangoproject.com/en/5.0/topics/migrations/#data-migrations for reference

- Group : Administrator, Manager, Supervisor, Employee
- EmployeeType : Office, Assembly, Printing, Sales, Contact
- TaskType : assembly, delivery, installation, repair, service
- TaskStatus : in progress, queued, done
- VehicleType : Sedan, Combi, Truck, Roof Storage, Business