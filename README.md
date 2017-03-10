# GDP-based Standardized Localization Service

This is a prototype GDP-based implementation of the Standardized Localization Service. More details about the design, architecture and standardized interfaces can be found in the following publications:

http://www.tkn.tu-berlin.de/fileadmin/fg112/Papers/2016/lemic16_sli.pdf

## Short description

Standardized Localization Service is a modular localization service architecture that consists of location-based applications, an integrated location service enabling handover, fusion and integration of location information provisioning services, and resources for generating location information. A unified
style of interaction among these components is enabled by a set of well-defined Application Programming Interfaces (APIs).

## Installation procedure

You will need the Global Data Plane (GDP), which can be downloaded from:

https://swarmlab.eecs.berkeley.edu/projects/4814/global-data-plane

There is also a set of dependencies you will have to satisfy:

- scipy
- numpy 
- threading 
- Queue 
- daemon 
- json 
- subprocess 
- gdp

Obviously, you will need the source code of the Standardized Localization Service:

```
git clone https://github.com/terraswarm/standardized_localization_service.git
cd standardized_location_service
```

Distributed messaging between the components of this prototype implementation is implemented with a set of GDP logs following the principle - one interaction primitive, one GDP-log. 

In order to introduce a location-based application to the system, you will have to generate a set of application-specific GDP logs, namely *Request location* and *Report location* logs (at this point, more logs coming). This can be done with the following command, *application_id* being a unique ID of the application. 

```
sh generate_application_logs.sh application_id
```

Similarly, for introducing a provisioning service a set of GDP-logs has to be created. The following logs are needed *Service discovery*, *Service offering*, *Request location*, *Report location*. This can be done with the following command, *provisioning_service_id* being a unique ID of the provisioning service. 

```
sh generate_provisioning_logs.sh provisioning_service_id
```

Additionally, you will have to register the service with the core of the Standardized Localization Service, namely the Integrated Location Service, which can be done with the following command:

```
sh register_provisioning_service.ch provisioning_service_id
```

## Initial benchmarks

Currently the Standardized Localization Service uses a set of 8 provisioning services based on WiFi fingerprinting. The Standardized Localization Service is operating on the 2nd floor of the TKN building in Berlin. The benchmarks are coming. 