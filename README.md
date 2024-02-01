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
- [ 'python manage.py createsuperuser' mandatory since test employees were removed ]
- 'az login' if Azure connection is possible
- 'python manage.py runserver'

## Setup Notes 1 | User Management
Since test users were removed, a superuser has to be created manually.
From there onwards, this user needs to be given the groups 'Administrator' and 'Employee' to properly access the application.
Since the system was implemented in a hierarchical way, every active user needs the group 'Employee' to see all the necessary information, despite maybe being assigned to a higher group as well.
Administrators have access to user management, while Managers can modify every operational aspect (Orders, Customers, Tasks, Vehicles, ...).
Supervisor have the same access span as Managers, but read-only access and thereby cannot modify anything except their own tasks.
Employees can only see their own tasks and are not allowed to modify anything.

## Setup Notes 2 | Azure
The application works perfectly fine without Azure access, except for the file storage. No files can be uploaded if such storage location is not connected.
The deployed version on Azure is connected to a storage location and therefore works as intended.
A personal development setup requires access to such infrastructure, including credentials in the repository was not intended.

# Description 1 | General
TaskHub is a Django based MES for smaller businesses that do not want to / cannot pay large sums for complete ERP integrations.
It is designed to be a simple and easy to use tool for managing tasks and resources.
It is not intended to be a complete ERP system, but rather a tool for managing tasks and resources.
Many different aspects like employee management, vehicle management, task management, etc. are covered.

Django Rest Framework (DRF) is used for the API and the official frontend is built with Angular.
Incoming requests are serialized and validated with DRF serializers, before being processed by our business logic and saved to the database.
PostgreSQL is used as the database and Azure Blob Storage is used for file storage for task proofs or profile pictures.
An Azure deployment with several resources allows for fast communication between the frontend and backend/data storage.
This fact also makes the application very scalable, as the frontend and backend can be scaled independently of each other.

The module azure.py was written for this project (TaskHub) and simplifies the use of Azure BLOB storage by wrapping necessary commands behind the scenes.

# Description 2 | Features
- Employee Management
- Vehicle Management
- Task Management
- Customer Management
- Order Management
- File Storage
- User Management

The Task-Overview screen not only provides the possibility to filter by title (which is supported in all overviews),
but also enables the specifying of a relevant time span for the retrieval to prevent the download of unnecessary data.
The default requests a rather short term (1 week before and 4 after the current date), but can be changed to any desired time span.
If the new span exceeds the original one, a new, adapted request is sent to the backend to get the additional data.

###### Version 1.0.1 existing resources

- Group : Administrator, Manager, Supervisor, Employee
- EmployeeType : Office, Assembly, Printing, Sales, Contact
- TaskType : assembly, delivery, installation, repair, service
- TaskStatus : in progress, queued, done
- VehicleType : Sedan, Combi, Truck, Roof Storage, Business
- additionally various other resources
