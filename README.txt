Overview
--------
I created this project in order to assist in demonstrating the possibilities of Cisco IOx. This IOx app provides a user interface through a web browser to a battery powered ride-on. 

Components used in the project
> Cisco IR829 router
> Cisco IP Camera (for video) 
> Arduino Uno R3
> Some 12V batteries ;-)

-- controller_app   (IOx app source)
-- electronics      (customer electronics scematics)
    |
    --Enclosure     (enclosure .stl for 3D printing
-- firmware         (arduino sketch)
-- overview         (project overview)


This was my first IOx app and was hacked together in a fairly short amount of time. It is meant exclusively as a proof of concept, there are some significant issues with security and require re-engineering to get rid of the websocket as a start.

The custom electronics was based on basic arduino microprocessor and relay's. This was the components I had lying around and can be much improved on. I had fun creating the proof of concept and hope you find it a useful example.

package_config.ini file contains configurable options including IP Camera settings and default user name and password for the app. (admin/password)

## Compiling and activating the app from ioxclient(IOx sandbox). Of course ioxclient profile must be configured to interact with router.

cd carcontrol/
ls
source ~/.virtualenvs/carcontrol/bin/activate

# interacting with the app
ioxclient app console carcontrol
ioxclient app stop carcontrol
ioxclient app start carcontrol

# packaging app and upgrading app
ioxclient package .
ioxclient app stop carcontrol
ioxclient app deactivate carcontrol
ioxclient app carcontrol package.tar 
ioxclient app upgrade carcontrol package.tar 


