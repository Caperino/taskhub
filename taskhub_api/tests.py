from django.test import TestCase, Client
from . import models, serializers
from django.urls import reverse

# Create your tests here.
class TaskHubBaseTestCase(TestCase):
    def setUp(self):
        """
        This method is called before each test.
        Fills database with test data.
        :return:
        """
        self.client = Client()
        self.customers = [
            {
                "name": "Customer 1",
                "address": "Address 1",
                "phone": "Phone 1",
                "is_company": True
            },
            {
                "name": "Customer 2",
                "address": "Address 2",
                "phone": "Phone 2",
                "is_company": False
            }
        ]
        self.created_customers = [models.Customer.objects.create(**customer) for customer in self.customers]

        self.orders = [
            {
                "order_nr": 1,
                "title": "Order 1",
                "customer": self.created_customers[0],
                "order_date": "2019-01-01",
                "is_completed": False
            },
            {
                "order_nr": 2,
                "title": "Order 2",
                "customer": self.created_customers[1],
                "order_date": "2019-01-02",
                "is_completed": True
            }
        ]
        self.created_orders = [models.Order.objects.create(**order) for order in self.orders]

        self.employee_types = [
            {
                "title": "Employee Type 1",
                "description": "Description 1"
            },
            {
                "title": "Employee Type 2",
                "description": "Description 2"
            }
        ]
        self.created_employee_types = [models.EmployeeType.objects.create(**employee_type) for employee_type in self.employee_types]

        self.employees = [
            {
                "first_name": "Employee 1",
                "last_name": "Employee 1",
                "employee_type": self.created_employee_types[0],
                "phone": "Phone 1",
                "email": "Email 1",
                "is_active": True
            },
            {
                "first_name": "Employee 2",
                "last_name": "Employee 2",
                "employee_type": self.created_employee_types[1],
                "phone": "Phone 2",
                "email": "Email 2",
                "is_active": True
            }
        ]
        self.emp_1 = models.Employee.objects.create(first_name="Employee 1", last_name="Employee 1", employee_type=self.created_employee_types[0], phone="Phone 1", email="Email 1", is_active=True, username="emp1", password="12345")
        self.emp_2 = models.Employee.objects.create(first_name="Employee 2", last_name="Employee 2",
                                                    employee_type=self.created_employee_types[1], phone="Phone 2",
                                                    email="Email 2", is_active=True, username="emp2", password="12345")
        self.created_employees = [self.emp_1, self.emp_2]

        self.task_types = [
            {
                "title": "as",
            },
            {
                "title": "ins",
            }
        ]
        self.created_task_types = [models.TaskType.objects.create(**task_type) for task_type in self.task_types]

        self.task_statuses = [
            {
                "title": "Task Status 1",
            },
            {
                "title": "Task Status 2",
            }
        ]
        self.created_task_statuses = [models.TaskStatus.objects.create(**task_status) for task_status in self.task_statuses]

        self.tasks = [
            {
                "order": self.created_orders[0],
                "title": "Task 1",
                "task_type": self.created_task_types[0],
                "task_status": self.created_task_statuses[0],
                "scheduled_from": "2019-01-03 08:00:00",
                "from_shift": "am",
                "scheduled_to": "2019-01-04 12:00:00",
                "to_shift": "am"
            },
            {
                "order": self.created_orders[1],
                "title": "Task 2",
                "task_type": self.created_task_types[1],
                "task_status": self.created_task_statuses[1],
                "scheduled_from": "2019-01-02 08:00:00",
                "from_shift": "am",
                "scheduled_to": "2019-01-04 17:00:00",
                "to_shift": "pm"
            }
        ]
        self.created_tasks = [models.Task.objects.create(**task) for task in self.tasks]

        self.azure_images = [
            {
                "image_name": "Azure Image 1",
            },
            {
                "image_name": "Azure Image 2",
            }
        ]
        self.created_azure_images = [models.AzureImage.objects.create(**azure_image) for azure_image in self.azure_images]

        self.vehicle_types = [
            {
                "title": "Vehicle Type 1",
                "description": "Description 1"
            },
            {
                "title": "Vehicle Type 2",
                "description": "Description 2"
            }
        ]
        self.created_vehicle_types = [models.VehicleType.objects.create(**vehicle_type) for vehicle_type in self.vehicle_types]

        self.vehicles = [
            {
                "title": "Vehicle 1",
                #"vehicle_type": self.created_vehicle_types[0],
                "max_load_length": 6,
                "max_load_weight": 2,
            },
            {
                "title": "Vehicle 2",
                #"vehicle_type": self.created_vehicle_types[1],
                "max_load_length": 8,
                "max_load_weight": 3,
            }
        ]
        self.created_vehicles = [models.Vehicle.objects.create(**vehicle) for vehicle in self.vehicles]
        ct = 0
        for vehicle in self.created_vehicles:
            vehicle.vehicle_type.add(self.created_vehicle_types[ct])
            ct += 1

        self.created_tasks[0].vehicles.add(self.created_vehicles[0])
        self.created_tasks[1].vehicles.add(self.created_vehicles[1])

        self.created_tasks[0].employees.add(self.created_employees[0])
        self.created_tasks[1].employees.add(self.created_employees[1])

        self.created_tasks[0].images.add(self.created_azure_images[0])
        self.created_tasks[1].images.add(self.created_azure_images[1])

        self.created_tasks[0].save()
        self.created_tasks[1].save()

        self.created_vehicles[0].save()
        self.created_vehicles[1].save()



    def test_check_setup(self):
        """
        This method checks if the setup is correct.
        :return:
        """
        print("Checking setup...")
        self.assertEqual(len(self.created_customers), len(self.customers))
        self.assertEqual(len(self.created_orders), len(self.orders))
        self.assertEqual(len(self.created_employee_types), len(self.employee_types))
        self.assertEqual(len(self.created_employees), len(self.employees))
        self.assertEqual(len(self.created_task_types), len(self.task_types))
        self.assertEqual(len(self.created_task_statuses), len(self.task_statuses))
        self.assertEqual(len(self.created_tasks), len(self.tasks))
        self.assertEqual(len(self.created_azure_images), len(self.azure_images))
        self.assertEqual(len(self.created_vehicle_types), len(self.vehicle_types))
        self.assertEqual(len(self.created_vehicles), len(self.vehicles))
        print("Setup is correct.")

    def test_get_customers(self):
        """
        This method tests the get_customers method.
        :return:
        """
        url = reverse("customers")
        response = self.client.get(url)
        ser = serializers.CustomerSerializer(data=response.data, many=True)
        self.assertEqual(ser.is_valid(), True)
        print(ser.validated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.created_customers))

    def test_get_customer_not_company(self):
        """
        This method tests the customers endpoint with queries
        :return:
        """
        url = reverse("customers")
        response = self.client.get(url + "?company=false")
        ser = serializers.CustomerSerializer(data=response.data, many=True)
        self.assertEqual(ser.is_valid(), True)
        print(ser.validated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_customer_company(self):
        """
        This method tests the customers endpoint with queries
        :return:
        """
        url = reverse("customers")
        response = self.client.get(url + "?company=true")
        ser = serializers.CustomerSerializer(data=response.data, many=True)
        self.assertEqual(ser.is_valid(), True)
        print(ser.validated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_customer_with_query(self):
        """
        This method tests the customers endpoint with queries
        :return:
        """
        url = reverse("customers")
        response = self.client.get(url + "?query=Customer 1")
        ser = serializers.CustomerSerializer(data=response.data, many=True)
        self.assertEqual(ser.is_valid(), True)
        print(ser.validated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_customer_with_query_not_company(self):
        """
        This method tests the customers endpoint with queries
        :return:
        """
        url = reverse("customers")
        response = self.client.get(url + "?query=Customer 1&company=true")
        ser = serializers.CustomerSerializer(data=response.data, many=True)
        self.assertEqual(ser.is_valid(), True)
        print(ser.validated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_customer_with_query_company(self):
        """
        This method tests the customers endpoint with queries
        :return:
        """
        url = reverse("customers")
        response = self.client.get(url + "?query=omer&company=false")
        ser = serializers.CustomerSerializer(data=response.data, many=True)
        self.assertEqual(ser.is_valid(), True)
        print(ser.validated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_customer_correct(self):
        """
        This method tests the create_customer method.
        :return:
        """
        url = reverse("customers")
        data = {
            "name": "Customer 3",
            "address": "Address 3",
            "phone": "Phone 3",
            "is_company": True
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        ser = serializers.CustomerSerializer(data=response.data)
        self.assertEqual(ser.is_valid(), True)
        print(ser.validated_data)
        self.assertEqual(models.Customer.objects.count(), len(self.created_customers) + 1)
        self.assertEqual(models.Customer.objects.last().name, data["name"])

    def test_create_customer_incorrect(self):
        """
        This method tests the create_customer method.
        :return:
        """
        url = reverse("customers")
        data = {
            "name": "Customer 3",
            "address": "Address 3",
            "is_company": True
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(models.Customer.objects.count(), len(self.created_customers))
        self.assertNotEqual(models.Customer.objects.last().name, data["name"])
        data = {
            "name": "Customer 3",
            "address": "Address 3",
            "phone": "Phone 3",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Customer.objects.count(), len(self.created_customers)+1)

    def test_get_single_customer(self):
        """
        This method tests the get_single_customer method.
        :return:
        """
        url = reverse("direct_customer", args=[self.created_customers[0].pk])
        response = self.client.get(url)
        ser = serializers.CustomerSerializer(data=response.data)
        self.assertEqual(ser.is_valid(), True)
        print(ser.validated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.created_customers[0].name)

    def test_get_single_customer_not_found(self):
        """
        This method tests the get_single_customer method.
        :return:
        """
        url = reverse("direct_customer", args=[self.created_customers[0].pk+100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_update_customer(self):
        """
        This method tests the update_customer method.
        :return:
        """
        url = reverse("direct_customer", args=[self.created_customers[0].pk])
        data = {
            "name": "Customer 1",
            "address": "Address 1",
            "phone": "Phone 3",
            "is_company": False
        }
        response = self.client.put(url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        ser = serializers.CustomerSerializer(data=response.data)
        self.assertEqual(ser.is_valid(), True)
        print(ser.validated_data)
        self.assertEqual(models.Customer.objects.count(), len(self.created_customers))
        self.assertEqual(models.Customer.objects.get(pk=1).name, data["name"])
        self.assertEqual(models.Customer.objects.get(pk=1).is_company, data["is_company"])

    def test_update_customer_not_found(self):
        """
        This method tests the update_customer method.
        :return:
        """
        url = reverse("direct_customer", args=[self.created_customers[0].pk+100])
        data = {
            "name": "Customer 1",
            "address": "Address 1",
            "phone": "Phone 3",
            "is_company": False
        }
        response = self.client.put(url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(models.Customer.objects.count(), len(self.created_customers))
        self.assertNotEqual(models.Customer.objects.get(pk=1).phone, data["phone"])

    def test_delete_customer(self):
        """
        This method tests the delete_customer method.
        :return:
        """
        url = reverse("direct_customer", args=[self.created_customers[0].pk])
        response = self.client.delete(url)
        print(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(models.Customer.objects.count(), len(self.created_customers))
        # delete referenced order and task (in following order --> first task, then order, then customer) first
        self.created_tasks[0].delete()
        self.created_orders[0].delete()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(models.Customer.objects.count(), len(self.created_customers)-1)
