Project Objective

The objective of this project (tentatively named “Mercury” for the Roman God of speed) is to build a web-based travel route optimizer that takes a provided list of addresses and returns the optimum route of travel (along with other helpful information) back to the user.  It will utilize the Google Maps API to get longitude/latitude coordinates and route distance/times as well as the Python Pulp linear optimizer to determine and generate the optimum travel route.
Features
•	Utilizes Flask for creating a web application.
•	Retrieves coordinates using Google Maps API based on user-input addresses.
•	Calculates driving distance and duration between coordinates.
•	Calculates estimated travel costs based on a user supplied vehicle MPG rating and a current average gas price estimate.
•	Utilizes a linear programming model to determine the optimal route.
•	Provides real-time optimization results, including total distance, total duration, an ordered destination path, turn-by-turn directions (I hope), and an embedded interactive Google map of the route.
•	Gives users the ability to save a PDF of their travel report for future reference.

Target Audience

The application is designed for any travelers who need to generate optimized routes for multiple waypoints, such as delivery drivers, field service personnel, vacation planners or anyone requiring an efficient path between various locations.  It is currently restricted to driving but this could potentially be expanded as Google supports various modes of transportation (walk, bike, bus, train, etc)

Resources Used

•	Utilizes Flask for web application structure.
•	Incorporates Google Maps API for geocoding, directions, and embedding maps.
•	Applies linear programming using the PuLP library for optimization.
•	The HTML interface will feature a user-friendly form with dynamic address input fields.
•	CSS styling will enhance the visual presentation of the form and the displayed result.
•	JavaScript will manage the dynamic form elements, initiate optimization, and update the UI.
