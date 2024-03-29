# OpenEVSEPlugin
OpenEVSE mqtt domoticz plugin

Últimos cambios
* Adaptado a nueva V4 ESP32
* Añadido dummy Manual Override
* Añadido dummy para ver si el coche está enchufado al cargador 

![OpenEVSE_Plugin](https://github.com/ayasystems/OpenEVSEPlugin/raw/master/openevse_plugin.jpg)


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
git pull
```
3. Start domoticz
```
sudo systemctl start domoticz
```
**Me gustaría agradecer a [Alexander Nagy](https://github.com/enesbcs) su plugin sirvió de inspiración y ejemplo para el desarrollo de este plugin



