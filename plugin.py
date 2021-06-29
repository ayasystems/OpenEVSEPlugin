# OpenEVSE domoticz plugin
#
# Author: EA4GKQ Ángel
# https://github.com/OpenEVSE/ESP8266_WiFi_v2.x/blob/master/Developers_Guides/Developers%20Guide_MQTT.pdf
# 
# 06/07/2020
# Se mejora reconexión a MQTT cuando esta se corta
# 26/05/2020
# Se captura conexión / desconexión de mqtt dando error por consola
# 25/05/2020
# Se añade Switch EcoMode
# 23/03/2021
# Se añade Switch Plugged para saber si el coche está o no enchufado al cargador
# 29/06/2021
# Se añade Switch Manual Override
# Adaptado a funcionar en V4 ESP32
"""
<plugin key="BasePlug" name="OpenEVSE mqtt plugin" author="EA4GKQ Ángel" version="1.0.6" wikilink="https://github.com/ayasystems/OpenEVSEPlugin" externallink="https://www.openevse.com/">
     <description>
        <h2>OpenEVSE MQTT Plugin</h2><br/>
        
        <h3>by @ea4gkq</h3>
        Visita https://domotuto.com/integracion-domoticz-openevse-mqtt/
    </description>
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Username" label="Username" width="300px"/>
        <param field="Password" label="Password" width="300px" default="" password="true"/>
        <param field="Mode1" label="Topic" width="125px" default="openevse"/>

        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>


    </params>
</plugin>
"""
errmsg = ""
subval = ""
amperios = 0
try:
 import Domoticz
except Exception as e:
 errmsg += "Domoticz core start error: "+str(e)
try:
 import json
except Exception as e:
 errmsg += " Json import error: "+str(e)
try:
 import time
except Exception as e:
 errmsg += " time import error: "+str(e)
try:
 import re
except Exception as e:
 errmsg += " re import error: "+str(e)
try:
 from mqtt import MqttClientSH2
except Exception as e:
 errmsg += " MQTT client import error: "+str(e)

class BasePlugin:
    enabled = False
    mqttConn = None
    counter = 0
    mqttClient = None
    errmsg = ""
    subval = ""
    response = ""
    plugged = "0"
    ManualOverride = "0"
    amperios = 0	
    read_time = time.time()
    elapsed_time = 0
    def __init__(self):
        return

    def onStart(self):
     global errmsg
     if errmsg =="":
      try:
        Domoticz.Heartbeat(10)
        if Parameters["Mode6"] != "0":
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()
        self.base_topic = Parameters["Mode1"].strip() # hardwired
        self.mqttserveraddress = Parameters["Address"].strip()
        self.mqttserverport = Parameters["Port"].strip()
        self.mqttClient = MqttClientSH2(self.mqttserveraddress, self.mqttserverport, "", self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)
      except Exception as e:
        Domoticz.Error("MQTT client start error: "+str(e))
        self.mqttClient = None
     else:
        Domoticz.Error("Your Domoticz Python environment is not functional! "+errmsg)
        self.mqttClient = None
    def onMQTTConnected(self):
       Domoticz.Debug("onMQTTConnected")	
       if self.mqttClient is not None:
        self.mqttClient.subscribe([self.base_topic + '/#'])
        #Domoticz.Debug([self.base_topic + '/#'])	
    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTSubscribed(self):
        Domoticz.Debug("onMQTTSubscribed")
    def onMQTTPublish(self, topic, message): # process incoming MQTT statuses
        global amperios
        subval = ""
        if "/announce" in topic: # announce did not contain any information for us
         return False
        try:
         topic = str(topic)
         message = str(message)
        except:
         Domoticz.Debug("MQTT message is not a valid string!") #if message is not a real string, drop it
         return False
        Domoticz.Debug("MQTT message: " + topic + " " + str(message))
        if(str(message)=="connected"):
            Domoticz.Error("mqtt connected")
        elif(str(message)=="disconnected"):         
            Domoticz.Error("mqtt disconnected")
        else:
            mqttpath = topic.split('/')
            if (mqttpath[0] == self.base_topic):
              Domoticz.Debug("mqttpath[1]: "+mqttpath[1])
              if (mqttpath[1] == "temp"):
                unitname="Temp"
                subval="temp"
              if (mqttpath[1] == "pilot"):
                unitname="Pilot"
                subval="pilot"
              if (mqttpath[1] == "state"):
                unitname="Status"
                subval="state"
              if (mqttpath[1] == "amp"):
                unitname="Amps"
                subval="amp"
                amperios = float(str(message).strip()) 			
              if (mqttpath[1] == "wh"):
                unitname="Energy"
                subval="wh"
              if (mqttpath[1] == "divertmode"):
                unitname="EcoMode"
                subval="divertmode"
              if (mqttpath[1] == "vehicle"): 
                response = str(message)
                if(response=="1"):
                  plugged = "1"                
                  unitname="Plugged"
                  subval="Plugged"
                if(response=="0"):
                  plugged = "0"             
                  unitname="Plugged"
                  subval="Plugged"     
              if (mqttpath[1] == "manual_override"): 
                response = str(message)
                if(response=="1"):
                  ManualOverride = "1"                
                  unitname="ManualOverride"
                  subval="ManualOverride"
                if(response=="0"):
                  ManualOverride = "0"             
                  unitname="ManualOverride"
                  subval="ManualOverride"                    
              iUnit = -1
              for Device in Devices:
               try:
                if (Devices[Device].DeviceID.strip() == unitname):
                 iUnit = Device
                 break
               except:
                pass
              if iUnit<0: # if device does not exists in Domoticz, than create it
                try:
                 iUnit = 0
                 for x in range(1,256):
                  if x not in Devices:
                   iUnit=x
                   break
                 if iUnit==0:
                  iUnit=len(Devices)+1
                 if subval=="temp":
                  Domoticz.Debug("Creamos temp.")#Domoticz.Device(Name=unitname, Unit=iUnit,TypeName="Switch",Used=1,DeviceID=unitname).Create()
                  Domoticz.Device(Name=unitname, Unit=iUnit,TypeName="Temperature",Used=1,DeviceID=unitname).Create()
                 elif subval=="amp":
                  Domoticz.Debug("Creamos amp.")#Domoticz.Device(Name=unitname, Unit=iUnit,TypeName="Switch",Used=1,DeviceID=unitname).Create()
                  Domoticz.Device(Name=unitname, Unit=iUnit,TypeName="Current (Single)",Used=1,DeviceID=unitname).Create()
                 elif subval=="pilot":
                  Domoticz.Device(Name=unitname, Unit=iUnit,TypeName="Current (Single)",Used=1,DeviceID=unitname).Create()   
                  Domoticz.Device(Name="PilotSet", Unit=20,Type=242,Subtype=1,Used=1,DeviceID="PilotSet").Create() 				  
                  Domoticz.Debug("MQTT connected pilot.")#Domoticz.Device(Name=unitname, Unit=iUnit,Type=243,Subtype=8,Used=1,DeviceID=unitname).Create()
                 elif subval=="state":
                  Options =   {   "LevelActions"  :"||||||" , 
                                  "LevelNames"    :"Disable|Disconnected|Connected|Charging|Error|Timer|WatingEv" ,
                                  "LevelOffHidden":"false",
                                  "SelectorStyle" :"1"
                  }			  
                  Domoticz.Device(Name=unitname,  Unit=iUnit, TypeName="Selector Switch", Switchtype=18, Image=12, Options=Options, Used=1,DeviceID=unitname).Create()
                  iUnit=iUnit+1
                  Domoticz.Device(Name="Toggle", Unit=iUnit,TypeName="Switch", Switchtype=9,Used=1,DeviceID="Toggle").Create()
                  iUnit=iUnit+1
                  Domoticz.Device(Name="Start", Unit=iUnit,TypeName="Switch", Switchtype=9,Used=1,DeviceID="Start").Create()
                  iUnit=iUnit+1
                  Domoticz.Device(Name="Stop", Unit=iUnit,TypeName="Switch", Switchtype=9,Used=1,DeviceID="Stop").Create()	
                  iUnit=iUnit+1
                  Domoticz.Device(Name="EcoMode", Unit=iUnit,TypeName="Switch", Switchtype=0,Used=1,DeviceID="EcoMode").Create()    
                 elif subval=="Plugged":   
                  Domoticz.Device(Name="Plugged", Unit=iUnit,TypeName="Switch", Switchtype=0,Used=1,DeviceID="Plugged").Create()                   
                 elif subval=="ManualOverride":   
                  Domoticz.Device(Name="ManualOverride", Unit=iUnit,TypeName="Switch", Switchtype=0,Used=1,DeviceID="ManualOverride").Create()                   
                 elif subval=="wh":
                  Domoticz.Device(Name=unitname, Unit=iUnit,Type=243,Subtype=29,Switchtype=0,Used=1,DeviceID=unitname).Create()
                  Domoticz.Debug("MQTT connected wh.")
                except Exception as e:
                 Domoticz.Debug(str(e))
                 return False



              if subval=="temp":
               self.read_time = time.time()
               try:
                mval = float(str(message).strip())/10
               except:
                mval = str(message).strip()
               try:
                Devices[iUnit].Update(nValue=0,sValue=str(mval),TimedOut=0)
               except Exception as e:
                Domoticz.Debug(str(e))
                return False
              elif subval=="pilot":
               self.read_time = time.time()
               try:
                mval = float(str(message).strip())
               except:
                mval = str(message).strip()
               try:
                Devices[iUnit].Update(nValue=0,sValue=str(mval),TimedOut=0)
               except Exception as e:
                Domoticz.Debug(str(e))
                return False


               try:
                mval = float(str(message).strip())
               except:
                mval = str(message).strip()
               try:
                Devices[20].Update(nValue=0,sValue=str(mval),TimedOut=0)
               except Exception as e:
                Domoticz.Debug(str(e))
                return False

               pilot = float(str(message).strip())
               Domoticz.Debug("pilot: "+str(pilot))  
               return False		
              elif subval=="amp":
               self.read_time = time.time()
               try:
                mval = float(str(message).strip())/1000
               except:
                mval = str(message).strip()
               try:
                Devices[iUnit].Update(nValue=0,sValue=str(mval),TimedOut=0)
               except Exception as e:
                Domoticz.Debug(str(e))
                return False
               amperios = float(str(message).strip())/1000
               Domoticz.Debug("Amp: "+str(amperios))  
               return False		   
              elif subval=="state":
               self.read_time = time.time()
               try:
                mval = str(message).strip()
               except:
                mval = str(message).strip()
               if (mval=="254"):
                 mval="50"
               elif (mval=="1"):
                 mval="10"
               elif (mval=="2"):
                 mval="20"
               elif (mval=="3"):
                 mval="30"
               elif (mval=="4"):
                 mval="40"
               elif (mval=="255"):
                 mval="0"
               try:
                #Devices[iUnit].Update(1,str(mval))
                UpdateDevice(iUnit, 1, str(mval))
               except Exception as e:
                Domoticz.Debug(str(e))
                return False
              elif subval=="wh":
                  self.read_time = time.time()
                  Domoticz.Debug("Proceso wh")
                  voltaje = 235
                  watts = amperios * voltaje
                  Domoticz.Debug("amperios: "+str(amperios))
                  Domoticz.Debug("voltaje: "+str(voltaje))
                  try:
                   mval = float(str(message).strip())
                  except:
                   mval = str(message).strip()
                  try:
                   Devices[iUnit].Update(nValue=0,sValue=str(watts)+";"+str(mval),TimedOut=0)
                   Domoticz.Debug("Update["+str(iUnit)+"]: "+str(watts)+";"+str(mval))
                  except Exception as e:
                   Domoticz.Debug(str(e))
                   return False			  
                  Domoticz.Debug("MQTT connected wh/kwh "+str(watts)+" / "+str(mval))#Domoticz.Device(Name=unitname, Unit=iUnit,Type=243,Subtype=29,Used=1,DeviceID=unitname).Create()
              elif subval=="divertmode": 
               mval = str(message).strip()
               Domoticz.Debug("divertmode: "+str(mval))
               if(mval=="2"):
                UpdateDevice(iUnit, 1, "On")
               elif(mval=="1"):
                UpdateDevice(iUnit, 0, "Off")
              elif subval=="Plugged": 
               Domoticz.Debug("Plugged: "+str(plugged))
               if(plugged=="1"):
                UpdateDevice(iUnit, 1, "On")
               elif(plugged=="0"):
                UpdateDevice(iUnit, 0, "Off")
              elif subval=="ManualOverride": 
               Domoticz.Debug("ManualOverride: "+str(ManualOverride))
               if(ManualOverride=="1"):
                UpdateDevice(iUnit, 1, "On")
               elif(ManualOverride=="0"):
                UpdateDevice(iUnit, 0, "Off")   
          
    # executed each time we click on device thru domoticz GUI
    #def onCommand(Unit, Command, Level, Hue):
    def onCommand(self, Unit, Command, Level, Color):  #
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level)+", DeviceID: "+Devices[Unit].DeviceID )
        if(Devices[Unit].DeviceID=="Toggle"):
         rapiTopic = self.base_topic + "/rapi/in/$F1"#FE ENABLE #FD DISABLE
         if (self.mqttClient.isConnected):
          try:
           self.mqttClient.publish(rapiTopic, "")
          except Exception as e:
           Domoticz.Debug(str(e))
        if(Devices[Unit].DeviceID=="Start"):
         rapiTopic = self.base_topic + "/rapi/in/$FE"#FE ENABLE #FD DISABLE
         if (self.mqttClient.isConnected):
          try:
           self.mqttClient.publish(rapiTopic, "")
          except Exception as e:
           Domoticz.Debug(str(e))
        if(Devices[Unit].DeviceID=="Stop"):
         rapiTopic = self.base_topic + "/rapi/in/$FD"#FE ENABLE #FD DISABLE
         if (self.mqttClient.isConnected):
          try:
           self.mqttClient.publish(rapiTopic, "")
          except Exception as e:
           Domoticz.Debug(str(e))

        if(Devices[Unit].DeviceID=="ManualOverride"):
           #Domoticz.Error(Devices[Unit].sValue)
           rapiTopic = self.base_topic + "/manual_override/set"#FE ENABLE #FD DISABLE
           ManualOverride = "0"
           if(str(Devices[Unit].sValue)=="On"):
            ManualOverride = "1"
           if (self.mqttClient.isConnected):
            try:
             self.mqttClient.publish(rapiTopic, ManualOverride)
            except Exception as e:
             Domoticz.Debug(str(e)) 
        if(Devices[Unit].DeviceID=="EcoMode"):
           #Domoticz.Error(Devices[Unit].sValue)
           rapiTopic = self.base_topic + "/divertmode/set"#FE ENABLE #FD DISABLE
           divertmode = "2"
           if(str(Devices[Unit].sValue)=="On"):
            divertmode = "1"
           if (self.mqttClient.isConnected):
            try:
             self.mqttClient.publish(rapiTopic, divertmode)
            except Exception as e:
             Domoticz.Debug(str(e))     
        if(Devices[Unit].DeviceID=="PilotSet"):
           #Domoticz.Error(Devices[Unit].sValue)
           value = int(float(Level))
           rapiTopic = self.base_topic + "/rapi/in/$SC"
           Domoticz.Debug(rapiTopic)  
           if (self.mqttClient.isConnected):
            try:
             self.mqttClient.publish(rapiTopic, str(value))
            except Exception as e:
             Domoticz.Debug(str(e))  			 
    def onConnect(self, Connection, Status, Description):
        if (Status == 0):
            Domoticz.Debug("MQTT connected successfully.")
            sendData = { 'Verb' : 'CONNECT',
                         'ID' : "645364363" }
            Connection.Send(sendData)
        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"]+" with error: "+Description)

    def onMessage(self, Connection, Data):
       if self.mqttClient is not None:
        self.mqttClient.onMessage(Connection, Data)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")
        self.mqttClient.isConnected = False

    def onHeartbeat(self):
      Domoticz.Debug("Heartbeating..."+str(self.mqttClient.isConnected))
      if self.mqttClient is not None:
       try:
        # Reconnect if connection has dropped
        if (self.mqttClient._connection is None) or (not self.mqttClient.isConnected):
            Domoticz.Debug("Reconnecting")
            self.mqttClient._open()
        else:
            self.mqttClient.ping()
       except Exception as e:
        Domoticz.Error(str(e))
        
       #rapiTopic = self.base_topic + "/rapi/in/$G0"
       #Domoticz.Debug(" Comando mqtt: "+rapiTopic)  
       #if (self.mqttClient.isConnected):
       # try:
       #  self.mqttClient.publish(rapiTopic, ":77")
       # except Exception as e:
       #  Domoticz.Debug(str(e))          
      self.elapsed_time = time.time() - self.read_time
      if(self.elapsed_time>80 and self.elapsed_time<90):
        Domoticz.Error("Last data: "+str(self.elapsed_time))
        for Device in Devices:
            if(Devices[Device].DeviceID=='Amps' or Devices[Device].DeviceID=='Energy' or Devices[Device].DeviceID=='Temp' or Devices[Device].DeviceID=='Pilot'  ):  
                Devices[Device].Update(nValue=Devices[Device].nValue,sValue=Devices[Device].sValue,TimedOut=1) 

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)
def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)
def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def DumpDictionaryToLog(theDict, Depth=""):
    if isinstance(theDict, dict):
        for x in theDict:
            if isinstance(theDict[x], dict):
                Domoticz.Log(Depth+"> Dict '"+x+"' ("+str(len(theDict[x]))+"):")
                DumpDictionaryToLog(theDict[x], Depth+"---")
            elif isinstance(theDict[x], list):
                Domoticz.Log(Depth+"> List '"+x+"' ("+str(len(theDict[x]))+"):")
                DumpListToLog(theDict[x], Depth+"---")
            elif isinstance(theDict[x], str):
                Domoticz.Log(Depth+">'" + x + "':'" + str(theDict[x]) + "'")
            else:
                Domoticz.Log(Depth+">'" + x + "': " + str(theDict[x]))

def DumpListToLog(theList, Depth):
    if isinstance(theList, list):
        for x in theList:
            if isinstance(x, dict):
                Domoticz.Log(Depth+"> Dict ("+str(len(x))+"):")
                DumpDictionaryToLog(x, Depth+"---")
            elif isinstance(x, list):
                Domoticz.Log(Depth+"> List ("+str(len(theList))+"):")
                DumpListToLog(x, Depth+"---")
            elif isinstance(x, str):
                Domoticz.Log(Depth+">'" + x + "':'" + str(theList[x]) + "'")
            else:
                Domoticz.Log(Depth+">'" + x + "': " + str(theList[x]))
def UpdateDevice(Unit, nValue, sValue):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue),TimedOut=0)
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return
