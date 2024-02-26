# Import necessary modules
from flask import Flask, render_template, request, jsonify
from pulp import LpVariable, LpProblem, lpSum, LpMinimize, LpStatus, value, LpContinuous
import requests

# Create a Flask app instance
app = Flask(__name__)

# My Google API key
GOOGLE_API_KEY = 'AIzaSyD5Ya8Xz_6YDCeMrBIoZqkWmd1ycLkEvHA'

# Function to get coordinates for a given address using Google Maps API
def get_coordinates(address):
    # Construct the URL for Google Maps API to get coordinates
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_API_KEY}'
    
    # Make a GET request to the API
    response = requests.get(url)
    
    # Print the full JSON response to the Flask console
    print
    print(f"Full GET_COORDINATES JSON Response for {address}: {response.json()}")

    # Parse the JSON response
    data = response.json()

    # Check if the required information is present in the response
    if 'results' in data and data['results']:
        location = data['results'][0]['geometry']['location']
        coordinates = location['lat'], location['lng']
        print(f"Coordinates for {address}: {coordinates}")
        print
        return coordinates
    else:
        print(f"Unable to find coordinates for address: {address}")
        return None

# Function to get driving distance in miles between two sets of coordinates using Google Maps API
def get_driving_distance_in_miles(origin, destination):
    # Construct the URL for Google Maps API to get driving distance
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin[0]},{origin[1]}&destination={destination[0]},{destination[1]}&key={GOOGLE_API_KEY}"
    # Make a GET request to the API
    response = requests.get(url)
    # Parse the JSON response
    data = response.json()
    # Check if the required information is present in the response
    if 'routes' in data and data['routes'] and 'legs' in data['routes'][0] and data['routes'][0]['legs']:
        # Extract distance in miles
        return data['routes'][0]['legs'][0]['distance']['value'] * 0.000621371
    else:
        print("Unable to retrieve driving distance.")
        return None

# Function to get driving duration between two sets of coordinates using Google Maps API
def get_driving_duration(origin, destination):
    # Construct the URL for Google Maps API to get driving duration
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin[0]},{origin[1]}&destination={destination[0]},{destination[1]}&key={GOOGLE_API_KEY}"
    # Make a GET request to the API
    response = requests.get(url)
    # Parse the JSON response
    data = response.json()
    # Check if the required information is present in the response
    if 'routes' in data and data['routes'] and 'legs' in data['routes'][0] and data['routes'][0]['legs']:
        # Extract duration in seconds
        return data['routes'][0]['legs'][0]['duration']['value']
    else:
        print("Unable to retrieve driving duration.")
        return None

# Function to generate Google Maps URL based on the ordered path
def generate_map_url(ordered_path):
    waypoints = []
    for address, _ in ordered_path:
        coords = get_coordinates(address)
        if coords:
            waypoints.append(f"{coords[0]},{coords[1]}")

    origin = waypoints[0]
    waypoints_str = "|".join(waypoints[1:])
    api_key = 'AIzaSyD5Ya8Xz_6YDCeMrBIoZqkWmd1ycLkEvHA'  # Use Variable?
    url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={origin}&destination={origin}&waypoints={waypoints_str}&mode=driving"
    print(f"Generated Map URL: {url}")
    return url

# Define the default route to render the index.html template
@app.route('/')
def index():
    return render_template('index.html')

# Define the route to handle the optimization problem
@app.route('/solve', methods=['POST'])
def solve():
    # Get form data from the request
    minimize_choice = request.form['minimizeChoice']
    starting_address = request.form['startingAddress']
    addresses = {key: request.form[f'address{key}'] for key in range(2, 10) if request.form.get(f'address{key}')}

    # Convert addresses to coordinates for processing
    coords = {1: (starting_address, get_coordinates(starting_address))}
    coords.update({key: (address, get_coordinates(address)) for key, address in addresses.items()})

    # Create binary variables for each pair of coordinates
    x = LpVariable.dicts("x", [(i, j) for i in coords for j in coords if i != j], cat="Binary")

    # Add print statements
    for var in x:
        print(f"x[{var}] = {x[var]}")

    # Create the Linear Programming problem
    prob = LpProblem("ShortestPath", LpMinimize)
    print(prob)
    
    distance = LpVariable('distance',cat=LpContinuous)
    duration = LpVariable('duration',cat=LpContinuous)
    
    duration = lpSum([get_driving_duration(coords[i][1], coords[j][1]) * x[i, j] for i in coords for j in coords if i != j])
    distance = lpSum([get_driving_distance_in_miles(coords[i][1], coords[j][1]) * x[i, j] for i in coords for j in coords if i != j])

    # Objective function: minimize total driving time or distance
    if minimize_choice == 'time':
        prob += duration
    elif minimize_choice == 'distance':
        prob += distance

    # Constraints for outgoing and incoming edges
    for j in coords:
        # Constraints for outgoing edges
        outgoing_sum = 0
        for i in coords:
            if i != j:
                outgoing_sum += x[i, j]
        prob += outgoing_sum == 1  # Sum of outgoing edges must be equal to 1

        # Constraints for incoming edges
        incoming_sum = 0
        for i in coords:
            if i != j:
                incoming_sum += x[j, i]
        prob += incoming_sum == 1  # Sum of incoming edges must be equal to 1

    # Subtour elimination constraints
    n = len(coords)
    u = LpVariable.dicts("u", [i for i in coords], lowBound=1, upBound=n, cat="Integer")
    for i in coords:
        for j in coords:
            if i != j and (i != 1 and j != 1):  # Avoid the starting point
                prob += u[i] - u[j] + n * x[i, j] <= n - 1

    # Solve the Linear Programming problem
    prob.solve()

    # Extract the ordered path from the solution
    current_node = 1
    ordered_path = []
    while True:
        next_node = [j for j in coords if j != current_node and x[current_node, j].value() == 1][0]
        ordered_path.append((coords[current_node][0], coords[next_node][0]))
        current_node = next_node
        if current_node == 1:
            break

    # Get the Google Maps URL for displaying the route
    map_url = generate_map_url(ordered_path)

    # Prepare the result as a JSON object
    result = {
        "status": LpStatus[prob.status],
        "total_distance": round(distance.value(), 2),
        "total_duration": round(duration.value() / 3600, 2),  # convert seconds to hours
        "ordered_path": ordered_path,
        "map_url": map_url,
    }
    
    print(result)

    # Return the result as JSON
    return jsonify(result)

# Run the Flask app if this script is executed
if __name__ == '__main__':
    app.run(debug=False, port=5003)

