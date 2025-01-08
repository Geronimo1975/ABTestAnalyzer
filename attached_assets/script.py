import os

# Define the base directory for the project
base_path = "/home/dci-student/Projects/InventoryManagemntSystem"

# Define the updated structure of the project
project_structure = {
    "InventoryManagementSystem": {
        "__init__.py": None,
        "asgi.py": None,
        "settings.py": None,
        "urls.py": None,
        "wsgi.py": None,
    },
    "inventory": {
        "__init__.py": None,
        "admin.py": None,
        "apps.py": None,
        "forms.py": None,
        "models.py": None,
        "tests.py": None,
        "urls.py": None,
        "views.py": None,
        "migrations": {
            "__init__.py": None,
        },
    },
    "templates": {
        "inventory": {
            "home.html": None,
            "product_list.html": None,
            "product_detail.html": None,
            "cart.html": None,
            "checkout.html": None,
        },
    },
    "static": {
        "css": {},
        "js": {},
    },
    "tests": {
        "__init__.py": None,
        "test_inventory_manager.py": None,
    },
    "db.sqlite3": None,
    "LICENSE": None,
    "README.md": None,
    "requirements.txt": None,
    "manage.py": None,
}

def create_project_structure(base_path, structure):
    for name, contents in structure.items():
        current_path = os.path.join(base_path, name)
        if contents is None:
            # Create a file
            if not os.path.exists(current_path):
                open(current_path, 'w').close()
                print(f"File created: {current_path}")
            else:
                print(f"File already exists: {current_path}")
        elif isinstance(contents, dict):
            # Create a folder
            os.makedirs(current_path, exist_ok=True)
            print(f"Directory created: {current_path}")
            create_project_structure(current_path, contents)

# Create the project structure
create_project_structure(base_path, project_structure)

# Add example requirements
requirements = """
Django==4.2.6
stripe==5.1.0
django-crispy-forms==1.14.0
Pillow==9.3.0
"""
with open(os.path.join(base_path, "requirements.txt"), 'w') as req_file:
    req_file.write(requirements)

print("Project structure created successfully!")
