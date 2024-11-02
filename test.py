import requests
from models import Configuration, Product, PhysicalObject, PhysicalObjectConfiguration
from Main import filter_none_values

def main():
    newPhysicalObjectConfig = PhysicalObjectConfiguration(
        physical_object_id = 1,
        config_id = 90,
        x_coordinate = 1,
        y_coordinate = 1
    )
    print(newPhysicalObjectConfig.to_dict())

    json_data = filter_none_values(newPhysicalObjectConfig.to_dict())
    print(json_data)

    #json = {"config_type": "physical", "config_name":"TEST TEST"}
    response = requests.post("http://127.0.0.1:5000/physical_configurations", json= json_data, timeout=10)
    print(response.status_code)
    print(response.text)

if __name__ == '__main__':
  main()


