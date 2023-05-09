

import sys
import os
import time
from DFRobot_PH import DFRobot_PH
from DFRobot_ADS1115 import ADS1115
ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16
ads1115 = ADS1115()
ph = DFRobot_PH()

machine_name="vat1"
thresholdPH=7

while True :
    #Set the IIC address
    temperature = 25
    ads1115.set_addr_ADS1115(0x48)
    #Sets the gain and input voltage range.
    ads1115.set_gain(ADS1115_REG_CONFIG_PGA_6_144V)
    #Get the Digital Value of Analog of selected channel
    adc0 = ads1115.read_voltage(0)
    PH = ph.read_PH(adc0['r'],temperature)
    print(temperature)
    print(PH)
    print("---------------")
    var = "curl -i -XPOST 'http://influxdb.docker.local:8086/write?db=ph' --data '"+machine_name+" temp="+str(temperature)+",ph="+str(PH)+",thresholdPH="+str(thresholdPH)+"'"
    os.system(var)
    time.sleep(1.0)
