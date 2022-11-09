# unionLabs

##Introduction

• Cloud computing enables deployment of computing
resources on demand with substantially less
overhead costs. In combination with modern web
technologies it provides immense opportunities to
conduct and engage in research remotely.
• The primary objective behind this project is to
implement a scalable solution for remotely
accessing the servers hosted by an organisation
behind a NAT firewall.
• The secondary objective is to use this system to
enable remote access to an IoT lab using which
students can conduct experiments without being
physically present. The proposed solution enables
cross platform browser based remote access that
doesn’t require installation of any third party
software applications by the user

##Methodology

• The first step in configuring the system is to set up
a reverse proxy to forward certain ports in the
server that will be used for granting remote access
to the machine.
• FRP is an open source fast reverse proxy for port
forwarding a server behind a NAT firewall to a
remote server under our control.


![frp](https://user-images.githubusercontent.com/36897394/200740504-5a1b209b-5207-4839-8d54-b506cde0cf57.jpg)

• The next step is to use a Virtual Network
Computing (VNC) application that will be used to
serve the graphical user interface of the desktop
over a socket connection.
• For the proposed solution, we are using
TightVNC ,a free and open-source remote desktop
software server application for Linux and Windows
servers.
• VNC servers will be run on the ports which were
exposed by FRP. This solves the issue of remotely
accessing a server that is behind a firewall.
• NoVNC is an open source VNC client application
that serves VNC as a web server.
• We can instantiate separate environments with
noVNC installed ,to provide isolated client
machines for every user.


![vnc](https://user-images.githubusercontent.com/36897394/200740584-fc48e1d4-c1e1-4bb8-83ff-466a876ee255.jpg)

• Users can connect to their respective instance with
VNC client process running , thorough their
browsers to access their unique Graphical User
Interface (GUI) of the remote server.
• Separate VNC client machines’ creation and
termination after use, can be automated in the
background by a parallel computing resource on
the cloud such as AWS SQS and AWS Lambda .

##Detailed Architecture


![Architecture](https://user-images.githubusercontent.com/36897394/200740675-75962f01-d9a0-445b-9c15-39ecd3a8caf7.jpg)
• An authentication server is used to authenticate
and authorise users for remote server access.
• Once authentication is successful, an EC2
instance is dynamically created using Boto3 python
scripts that is run inside a lambda function.
• The instance is created using a pre configured
AWS machine image that has VNC client installed.
• To avoid delay in accessing the application, a
number of instances are kept running in a buffer so
that when a user logs in he/she can already be
assigned a free instance in this buffer without
having to wait for its creation.
• The assigned instance is replaced by spawning a
new instance in the background that will be added
to the buffer.
• The number of simultaneous EC2 instances that
are run and the buffer size decides the cost of
maintaining the system.
• When a user logs out , the corresponding instance
is queued for termination.

##Results and Challenges


• With our current design , multiple users obtain
separate desktop GUI to a remote machine with
only their web browser.
• Access to the user EC2 instance is granted after
authentication and whitelisting the IP of the user in
the instance firewall settings.
• To avoid security breaches using stolen
passwords, a two factor authentication system
can be implemented at the application level.
• TLS encryption should be used for all network
traffic in the system passing through the public
internet.
• The cost of maintaining the EC2 servers can be
significantly reduced by using only containers and
serverless computing resources .

##Conclusion

• With the designed system we are able to authenticate
and authorise multiple users to remotely access a GUI
to a machine behind a NAT firewall.
