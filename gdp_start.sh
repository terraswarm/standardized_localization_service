# author = "Filip Lemic"
# copyright = "Copyright 2017, EU eWine Project"
# version = "1.0.0"
# maintainer = "Filip Lemic"
# email = "lemic@tkn.tu-berlin.de"
# status = "Development"

# Starting a local GDP server and router, and defining a routing name.

xterm -hold -e "export EP_PARAM_PATH=/home/tkn/Desktop/ep_adm_params; python /home/tkn/Desktop/gdp_router/src/gdp_router.py" &
sleep 5 
xterm -hold -e "export EP_PARAM_PATH=/home/tkn/Desktop/ep_adm_params; /home/tkn/Desktop/gdp/gdplogd/gdplogd -F -N test.localization"
