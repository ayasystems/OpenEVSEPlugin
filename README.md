# OpenEVSEPlugin
OpenEVSE mqtt domoticz plugin

Últimos cambios
* Añadida activación / desactivación Shaper
* Vuelve a funcionar start / stop / toggle 
* Añadidos dos nuevos sensores Uptime y WifiSignal
* Corregido PilotSet (Solo visualizará el valor al que está operando) 

<img width="1209" height="523" alt="image" src="https://github.com/user-attachments/assets/49cfa5d7-14fd-4756-b5e8-a2b97176849d" />

<img width="1226" height="323" alt="image" src="https://github.com/user-attachments/assets/d4385eca-7574-413a-a34c-c92e3b8c0b19" />

[Instalar plugin OpenEvSe en domoticz paso a paso](https://domotuto.com/integracion-domoticz-openevse-mqtt/) 



OpenEvSe es un cargador para vehículos electricos que permite control via Wifi. Para más información sobre OpenEvSe ir a la web del fabricante [OpenEvSe web](https://www.openevse.com/) 
## Instalación

1. Clona el repositorio dentro de tu carpeta de plugins de domoticz
```
cd domoticz/plugins
git clone https://github.com/ayasystems/OpenEVSEPlugin.git
```
2. Reinicia domotiz
```
sudo systemctl stop domoticz
sudo systemctl start domoticz
```
3. Ve a la página de "Hardware" y añade un nuevo hardware, en tipo selecciona "OpenEVSE mqtt plugin"
4. Especifica tu servidor MQTT y el topic de tu OpenEVSE
5. Recuerda permitir añadir nuevos dispositivos en el menú de ajustes


## Actualización del plugin


1. Para domoticz 
```
sudo systemctl stop domoticz
```
2. Ve al directorio del plugin y haz un git pull para que actualice la versión 
```
cd domoticz/plugins/OpenEVSEPlugin
git reset --hard
git pull
```
3. Start domoticz
```
sudo systemctl start domoticz
```
**Me gustaría agradecer a [Alexander Nagy](https://github.com/enesbcs) su plugin sirvió de inspiración y ejemplo para el desarrollo de este plugin



