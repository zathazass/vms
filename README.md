# Vendor Management System

## System Software Specifications

- python-3.9.x
- django-4.2.11
- djangorestframework-3.15.1

## Installation guides

Clone the project using `https://github.com/zathazass/vms.git` , 
then navigate to the project directory.

1. create a virtual environment using `virtualenv` and activate it
```bash
virtualenv ../env

# linux
source ../env/bin/activate

# windows
..\env\Scripts\activate
```

2. install required packages
```bash
pip install -r requirements.txt
```

3. to run test suite
```bash
# base command
pytest -W ignore::DeprecationWarning

# run parallely with n {4} workers
pytest -W ignore::DeprecationWarning -n 4
```

4. to run the developement server
```bash
python manage.py runserver
```

## Documentation Details

To explore and interact with the live API documentation, 
visit `localhost:8000/swagger/` and give it a try.

## Test File Details

Tests are categorized by api and models.

```text
vendors/
|--tests/
|----api_tests.py
|----model_tests.py
```

## Details on using the API endpoints

NOTE: Every endpoint requires user access token

1. Vendor list, create

- `GET /api/vendors/` to get list of vendors
- `POST /api/vendors/` to create a new vendor

2. Vendor retrieve, update, and delete

- `GET vendors/<int:vendor_id>/` to retrieve a particular vendor details
- `PUT vendors/<int:vendor_id>/` to update a particular vendor
- `DELETE vendors/<int:vendor_id>/` to delete a particular vendor

3. Purchase Order list, create

- `GET /api/purchase_orders/` to get list of vendors
- `POST /api/purchase_orders/` to create a new vendor

4. Purchase Order retrieve, update, and delete

- `GET purchase_orders/<int:po_id>/` to retrieve a particular vendor details
- `PUT purchase_orders/<int:po_id>/` to update a particular vendor
- `DELETE purchase_orders/<int:po_id>/` to delete a particular vendor

5. Update Purchase Order Acknowledgment by vendor

- `PUT purchase_orders/<int:po_id>/acknowledge`

6. To retrieve a vendor performance details

- `GET vendors/<int:vendor_id>/performance`

7. To get vendor performance historical data

- `GET vendors/<int:vendor_id>/performance/logs`