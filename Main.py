import cv2
import numpy as np
from db_connect import Base, engine, session
from db_config import API_BASEURI
from models import PhysicalObject, Configuration, PhysicalObjectConfiguration, Product, VirtualObject, VirtualObjectConfiguration
import requests
import socketio
import threading
import json
import queue
import asyncio

# Initialize a Socket.IO client
sio = socketio.Client()

physicalObjects = []
physicalObject_states = {}
currentConfig = None
currentProduct = None 

# Define the queue
task_queue = queue.Queue()
#db_lock = threading.Lock()



# Built-in connect event handler
@sio.event
def connect():
    print("Connected to the server")

# Built-in disconnect event handler
@sio.event
def disconnect():
    print("Disconnected from the server")

#Listens for incoming event when New Virtual Objects are created in unity and creates new Physical objects in Cache and in the DB
#The physical Objects created will later be assigned a marker_id when markers are detected
@sio.on("newVirtualObjectResponse")
def handle_new_virtual_object_response(data):
    # Your database operations here
    print("New virtual Object Created:", data)
    data = json.loads(data)
    #create new physical object, marker id 0, to be set later
    vObjID = int(data["virtual_object_id"])

    # Add the task to the queue instead of directly accessing the DB
    task_queue.put({
        "type": "create",
        "vObjID": vObjID,
        "name": f'Object{len(physicalObjects)+1}',
    })

#Listens for incoming event over WS when a New Virtual configuration is created. If this is the case, the virtual object
#in the virtual environment has changed its position, so the corresponding physical object should be moved to the same position
@sio.on("newVirtualConfigResponse")
def handle_new_virtual_config_response(data):
    print("New Virtual Configuration Detected", data)
    data = json.loads(data)
    movedVirtualObjectID = int(data["virtual_object_id"])
    x, y = int(data["x_coordinate"]), int(data["y_coordinate"])

    # Add the task to the queue to update the object
    task_queue.put({
        "type": "update_config",
        "vObjID": movedVirtualObjectID,
        "x": x,
        "y": y,
    })

    #set state of physical object to isMoving
    #if physicalObject_states[pObj] == 'stationary':
        #physicalObject_states[pObj] = 'moving'

    #create new configuration for this physical object in main thread TODO, dynamically add config name
    #new_PhysicalConfig = newConfiguration('physical', "NewConfiguration", sessionMain) 

    #create new physical object configuration in main thread, 
    #so that it creates the necessary foreign key relationships in main thread

    #new_PhysicalObjectConfig = newPhysicalObjectConfig(pObj.physical_object_id, new_PhysicalConfig.config_id, movedVirtualObjectX, movedVirtualObjectY, sessionMain)
    
    #Set new current config 
    #global currentConfig
    #currentConfig = new_PhysicalConfig

    # Update current configuration
    #urrentProduct.current_config = new_PhysicalConfig.config_id
    #move physical object to new location 
    #print(f"Moving physical object from to {movedVirtualObjectID, movedVirtualObjectY}")

    #set state of physical object to stationary


@sio.on('physical_configuration_change')
def handle_physicalConfigurationChange(data):
    print(f'received physical configuration update: {data}')

#def movePhysicalObject (physicalObj, newX, newY. session):
    #Get current position of physical object
    #Move X carve to current position
    #Activate the electromagnet over serial connection
    #Move X carve to new position


#finds the physical object from an array of physical objects with a certain virtual object id
def getPobjfromVobj(vObjID, physicalObjects):
    for pObj in physicalObjects:
        if pObj.virtual_object_id == vObjID:
            print(f"physical object found with virtual id: {vObjID}")
            return pObj     
    print(f"could not find physical object with virtual id: {vObjID}")
    
def calculate_Transform_Matrix (width, height, aruco_corners, aruco_ids):
    marker_dict = {1: None, 2: None, 3: None, 4: None}
    for i, marker_id in enumerate(aruco_ids):
     if marker_id in marker_dict:  # No need for marker_id[0] as marker_id is now a scalar
            marker_dict[marker_id] = aruco_corners[i][0]

    # Extract the four corner points from the detected ArUco markers
    # Assuming the marker corners are ordered as [top-left, top-right, bottom-right, bottom-left]
    src_points = np.array([
        marker_dict[1][0],  # Top-left corner of marker 1
        marker_dict[2][1],  # Top-right corner of marker 2
        marker_dict[3][2],  # Bottom-right corner of marker 3
        marker_dict[4][3]   # Bottom-left corner of marker 4
    ], dtype="float32")

    # Define the destination points (rectangle)
    dst_points = np.array([
        [0, 0],             # Top-left
        [width - 1, 0],     # Top-right
        [width - 1, height - 1],  # Bottom-right
        [0, height - 1]     # Bottom-left
    ], dtype="float32")

    # Get the perspective transform matrix
    M = cv2.getPerspectiveTransform(src_points, dst_points)
    return M


def filter_none_values(data):
    if isinstance(data, dict):
        return {k: filter_none_values(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [filter_none_values(item) for item in data]
    return data

def postRequest(obj, endpoint):
    try:
        url = f"{API_BASEURI}{endpoint}"
        print(url)

        # Use the object's to_dictionary method to get the dictionary representation
        json_data = filter_none_values(obj.to_dict())
        print("Sending JSON Data:", json_data)
        
        # Send the POST request with the JSON payload
        rspns = requests.post(url, json=json_data, timeout=10)
        print(rspns)
        
        # Check if the request was successful
        if rspns.status_code in (200, 201):
            print("Data sent successfully!")
            return rspns.json()  # Return the server's response as a dictionary
        else:
            print("Failed to send data:", rspns.status_code, rspns.text)
            return {"error": rspns.text}

    except Exception as e:
        print("An error occurred:", e)
        return {"error": str(e)}


def newConfiguration(type, name, session):
    # Create a new Configuration object with the provided type and name
    newConfig = Configuration(
        config_type=type,
        config_name=name
    )
    
    # Use the postRequest function to send the new configuration to the server
    #response = postRequest(newConfig,"configurations")
    #print(f"response: {response}")

    session.add(newConfig)
    session.flush()

    # Check if the response contains an error
    #if 'error' in response:
        #print("Error occurred:", response['error'])

    return newConfig  # Return the newly created configuration object
    
def newProduct(name, configuration, session):    
    # Create a new Product object with the provided name and the configuration ID
    newProduct = Product(
        product_name=name,
        current_config=configuration.config_id
    )
    # Use the postRequest function to send the new product to the server
    response = postRequest(newProduct, "products")

    #Commit after postrequest, to not send id + autoKeys to API, TODO, improve JSon to id and autoKeys
    session.add(newProduct)
    session.flush()
    print("Added new Product")  # Debugging line

    # Check if the response contains an error
    if 'error' in response:
        print("Error occurred:", response['error']) 

    return newProduct  # Return the new product object

def newPhysicalObject(vObjID, name, markerID, session):
    newPhysicalObject = PhysicalObject(
        virtual_object_id = vObjID,
        object_name = name,
        marker_id = markerID
    )

    session.add(newPhysicalObject)
    session.commit()
    print("Added new Physical Object")  # Debugging line

    return newPhysicalObject  # Return the new product object

def newPhysicalObjectConfig(pObjID,configID, x, y, session):
    newPhysicalObjectConfig = PhysicalObjectConfiguration(
        physical_object_id = pObjID,
        config_id = configID,
        x_coordinate = x,
        y_coordinate = y
    )
    # Send a Post request to the API
    #response = postRequest(newPhysicalObjectConfig, "physical_configurations")

    #Commit after postrequest, to not send id + autoKeys to API, TODO, improve JSon to id and autoKeys
    session.add(newPhysicalObjectConfig)
    session.commit()
    #session.flush()
    print(f"Added new Physical Object Config to DB with x,y {x,y}")  # Debugging line

    # Check if the response contains an error
    #if 'error' in response:
        #print("Error occurred:", response['error'])

    return newPhysicalObjectConfig  # Return the new product object
def main():
     # Start Socket.IO connection in a separate thread
    def start_socketio():
        try:
            sio.connect('http://127.0.0.1:5000')
        except Exception as e:
            print(f"Connection failed: {e}")
        
        #sio.wait()

    def mainCode():
        ### variable definition ###
        productName = "Marijns Product"
        frame_count = 0
        matrixHistory = []
        

        transformMatrix = np.ones((3,3))
        GlobalTransform_Matrix = np.ones((3,3))
        corner_ids = {1,2,3,4}
        this_aruco_dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        this_aruco_parameters = cv2.aruco.DetectorParameters()
        height = 850 #work area height in cm
        width = 850 #work area width in cm

        # Create tables in the database if they do not exist already
        Base.metadata.create_all(engine)

        #create initial configuration
        global currentConfig
        currentConfig = newConfiguration('physical', "Initial Physical Configuration", session)
        session.commit()
        
        # Insert a new product with the initial configuration
        global currentProduct
        currentProduct = newProduct(productName, currentConfig, session)
        session.commit()

        # Start videocapture (0 for integrated webcam, > 1 or 2 or 3 for external webcam)
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

        if not cap.isOpened():
            print("webcam couldnt open")

        # Main Frame Loop:
        while(True):
            # Capture frame-by-frame
            N = 100 
            # This method returns True/False as well
            # as the video frame.
            ret, frame = cap.read() 
            # Warp the perspective to create the new window
            warped_image = cv2.warpPerspective(frame, GlobalTransform_Matrix, (width, height)) 

            # Detect ArUco markers in the video frame
            (corners, ids, rejected) = cv2.aruco.detectMarkers(
            frame, this_aruco_dictionary, parameters=this_aruco_parameters)

            # Check that ArUco marker was detected
            if ids is not None and len(ids) > 0: 
                # Flatten the ArUco IDs list
                ids = ids.flatten() 
                if frame_count < N: # calculate transformation matrix
                    # check if all corners are detected
                    if corner_ids.issubset(ids):
                        
                        #calculate transformmatrix
                        transformMatrix = calculate_Transform_Matrix(width,height,corners,ids)

                        # Add the transformation matrix to the list
                        matrixHistory.append(transformMatrix)
                        
                        #calculate average matrix
                        avg_matrix = np.mean(np.array(matrixHistory), axis=0)

                        # Normalize the matrix from Homographic
                        #divide by the bottom-right element (to maintain scaling)
                        avg_matrix /= avg_matrix[2, 2]
                        GlobalTransform_Matrix = avg_matrix
                        print(frame_count)

                else: 
                    ids = ids.tolist()
                    filtered_corners = []
                    filtered_ids = []
                    new_physical_objects = []
                    new_configurations = []
                    updated_objects = []
                    threshold = int(width/100) #1% accuracy

                    # filter corner ids from ids
                    for marker_corner, marker_id in zip(corners, ids):
                        if marker_id not in list(corner_ids):
                            filtered_corners.append(marker_corner)
                            filtered_ids.append(marker_id)
                            
                    # Loop over the detected markers
                    for (marker_corner, marker_id) in zip(filtered_corners, filtered_ids):
                        # Extract the marker corners
                        corners = marker_corner.reshape((4, 2))
                        (top_left, top_right, bottom_right, bottom_left) = corners
                        
                        # Convert the (x,y) coordinate pairs to integers
                        top_right = (int(top_right[0]), int(top_right[1]))
                        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
                        bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
                        top_left = (int(top_left[0]), int(top_left[1]))
                    
                        # Draw the bounding box of the ArUco detection
                        cv2.line(frame, top_left, top_right, (0, 255, 0), 2)
                        cv2.line(frame, top_right, bottom_right, (0, 255, 0), 2)
                        cv2.line(frame, bottom_right, bottom_left, (0, 255, 0), 2)
                        cv2.line(frame, bottom_left, top_left, (0, 255, 0), 2)
                        
                        # Calculate and draw the center of the ArUco marker
                        center_x = int((top_left[0] + bottom_right[0]) / 2.0)
                        center_y = int((top_left[1] + bottom_right[1]) / 2.0)
                        originalCenterV = [[center_x], [center_y], [1]] #use homogenous coordinates

                        #calculate and draw the center of corrected Center of the ArUco marker
                        transformedCenterV = np.dot(transformMatrix, originalCenterV)
                        transformed_x = transformedCenterV[0] / transformedCenterV[2] # normalize tansformed x
                        transformed_y = transformedCenterV[1] / transformedCenterV[2] # normalize transformed y

                        transformedCenter = (int(transformed_x), int(transformed_y))
                        cv2.circle(warped_image, transformedCenter, 4, (0,0,255), -1)
                        
                        # Draw the ArUco marker ID on the video frame
                        # The ID is always located at the top_left of the ArUco marker
                        cv2.putText(frame, str(marker_id), 
                        (top_left[0], top_left[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)

                        # Draw the ArUco x, y location on the video frame
                        # The ID is always located at the top_left of the ArUco marker
                        cv2.putText(warped_image, str(transformedCenter), 
                        (transformedCenter[0], transformedCenter[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
                        
                        while not task_queue.empty():
                            task = task_queue.get()
                            
                            # Process each task based on its type
                            if task["type"] == "create":
                                # Assuming newPhysicalObject is defined elsewhere and returns a physical object
                                pObj = newPhysicalObject(task["vObjID"], task["name"], 0, session)

                                physicalObjects.append(pObj)  # Update your in-memory list
                                
                                task_queue.task_done()  # Mark task as done
                            
                            elif task["type"] == "update_config":
                                # Assuming getPobjfromVobj is defined to retrieve the physical object
                                pObj = getPobjfromVobj(task["vObjID"], physicalObjects)
                                if pObj:
                                    currentConfig
                                    currentProduct
                                    newPConfigFromVConfig = newConfiguration("physical","pConfigFromvConfig", session)
                                    newPObjConfigFromVObjConfig = newPhysicalObjectConfig(pObj.physical_object_id, newPConfigFromVConfig.config_id, task["x"], task["y"], session)  # Update the object in session
                                    

                                    currentConfig = newPConfigFromVConfig

                                    # Update current configuration
                                    currentProduct.current_config = newPConfigFromVConfig.config_id
                                    session.commit()
                                    #updated_objects.append((currentProduct))

                                    #set state of physical object to moving
                                    physicalObject_states[pObj.physical_object_id] = 'moving'

                                task_queue.task_done()  # Mark task as done


                  
                        for pObj in physicalObjects:
                            #assign marker id to physical objects 
                            if pObj.marker_id == 0:
                                #assign marker_id to physical object
                                pObj.marker_id = marker_id
                                new_physical_objects.append((pObj)) #Wrap physical object in a tuple

                            if len(pObj.configurations) == 0:
                                continue

                            #check position of marker against configuration to see if the object has moved, either manual or automatic    
                            configuration = pObj.configurations[len(pObj.configurations) -1] #last detected configuration
                            old_x = configuration.x_coordinate
                            old_y = configuration.y_coordinate
                            new_x = int(transformed_x)
                            new_y = int(transformed_y)
                            
                            # Check if the position error exceeds the threshold and if object is not moving
                            #TODO, add a buffer so that inconcistencies in the final position of a moved physical object do not create new configurations
                            if ((abs(new_x - old_x) > threshold or abs(new_y - old_y) > threshold)): #TODO, add stationary time check
                                print('physical object has moved or needs to be moved')
                                #Check if object needs to be moved automatically 
                                if physicalObject_states[pObj.physical_object_id] == 'moving':
                                    print("Moving physical object to new location")
                                    # move to location
                                    # Experimental function (send g code over serial), 
                                    # 
                                    
                                if physicalObject_states[pObj.physical_object_id] == 'stationary':
                                    print("Moved physical object by hand")
                                    #Physical object moved manually
                                    # Create new configuration for this object
                                    new_PhysicalConfig = newConfiguration('physical', "NewConfiguration", session) #TODO, dynamically add config name
                                    new_PhysicalObjectConfig = newPhysicalObjectConfig(
                                        pObj.physical_object_id, 
                                        new_PhysicalConfig.config_id,
                                        new_x,
                                        new_y, 
                                        session)
                                    
                                    #Set new current config 
                                    currentConfig = new_PhysicalConfig

                                    # Update current configuration
                                    currentProduct.current_config = new_PhysicalConfig.config_id
                                    updated_objects.append((new_PhysicalConfig, new_PhysicalObjectConfig, currentProduct))

                                    # Send Physical configuration change to Unity using WebSockets
                            else:
                                #set state to stationary if no change has been detected
                                physicalObject_states[pObj.physical_object_id] == 'stationary'
                    #Bulk save all new objects and configurations at once
                    if new_physical_objects:
                        session.bulk_save_objects(new_physical_objects)
                    if new_configurations:
                        session.bulk_save_objects(new_configurations)
                    if updated_objects:
                        # Add updated items to session in bulk
                        session.add_all([cfg for obj in updated_objects for cfg in obj])

                    # Final commit to save all changes
                    session.commit()

            if frame_count > N:
                #Show image
                cv2.imshow("warped window", warped_image)  

            # Display the resulting frame
            cv2.imshow('frame', frame)
            frame_count = frame_count + 1
            #print(f"frameCount: {frame_count}")
            #print("new frame")
            # If "q" is pressed on the keyboard, break the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break 

        # Close down the video stream
        cap.release()
        cv2.destroyAllWindows()
        session.close()

    start_socketio()
    mainCode()

if __name__ == '__main__':
  main()
  