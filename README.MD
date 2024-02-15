# Basic Queue System
This project is a web application developed with Flask, a lightweight Python framework, designed to manage user reservations in a facility, such as a cafeteria or a public restroom. The application keeps track of user names, their destinations, and the time spent outside the facility.

Unfortunately, as of right now, logging and documentation is entirely in Italian.

Key Features:

User Registration: Users can register by entering their name and desired destination, such as the bar or restroom.

Reservation Management: Users are added to a reservation list and can request to exit and return to the facility.

Activity Logging: A log of user activities, such as registrations, exits, and returns, is recorded to keep track of operations performed. You can also print in the log the MVP (person with most time outside the facility) and the LVP (person with least time outside the facility)

Login system: A login system is available to access the activity log, ensuring the security and privacy of information. Default password is password1234. It is accessible via the '/log' page

Usage:
The application is intended to be used by owners or managers of facilities that require a system to manage user reservations and monitor activities within the facility.

Credits:
getcssscan.com for css button style.
GitHub user ZachSaucier for css page layout
