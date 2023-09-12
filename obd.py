#!/usr/bin/python3

import redis
import can
import time
import os
import queue
import shmreader
from threading import Thread


#Redis pipe initialization
r = redis.Redis()
r.ping()

#Dictionay for PID-function number traduction
dyctionary = {
        0x00 : ["PIDs_SUPPORTED_[1-20]", 1],
        0x01 : ["MONITOR_STATUS_DTCLEAR", 2],
        0x02 : ["FREZEE_DTC ", 3],
        0x03 : ["FUEL_SYSTEM_STATUS ", 4],
        0x04 : ["CALCULATED_ENGINE_LOAD", 5],
        0x05 : ["ENGINE_COOLANT_TEMP", 6],
        0x06 : ["SHORT_TERM_FUEL_TRIM_1", 7],
        0x07 : ["LONG_TERM_FUEL_TRIM_1", 7],
        0x08 : ["SHORT_TERM_FUEL_TRIM_2", 7],
        0x09 : ["LONG_TERM_FUEL_TRIM_2 ", 7],
        0x0A : ["FUEL_PRESSURE", 8],
        0x0B : ["INTAKE_MAINFOLD_ABS_PRESSURE", 9],
        0x0C : ["ENGINE_RPM", 10],
        0x0D : ["VEHICLE_SPEED", 11],
        0x0E : ["TIMING_ADVANCE", 12],
        0x0F : ["INTAKE_AIR_TEMP ", 6],
        0x10 : ["MAF_SENSOR", 13],
        0x11 : ["THROTTLE POSITION", 5],
        0x12 : ["SECONDARY_AIR_STATUS", 14],
        0x13 : ["02_SENSORS", 15],#IN 2 BANKS
        0x14 : ["02_SENSOR_1", 16],
        0x15 : ["02_SENSOR_2", 16],
        0x16 : ["02_SENSOR_3", 16],
        0x17 : ["02_SENSOR_4", 16],
        0x18 : ["02_SENSOR_5", 16],
        0x19 : ["02_SENSOR_6", 16],
        0x1A : ["02_SENSOR_7", 16],
        0x1B : ["02_SENSOR_8", 16],
        0x1C : ["OBD_STANDARDS", 17],
        0x1D : ["02_SENSORS", 18],#IN 4 BANKS
        0x1E : ["AUX_INPUT_STATUS", 19],
        0x1F : ["RUNTIME_ENGINE_STARTED", 20],
        0x20 : ["PIDs_SUPPORTED_[21-40]", 21],
        0x21 : ["DIST_MALFUNCTION_INDICATOR", 22],
        0x22 : ["FUEL_RAIL_PRESSURE", 23],
        0x23 : ["FUEL_RAIL_GAUGE_PRESSURE", 24],
        0x24 : ["02_SENSOR_1_LAMBDA", 25],
        0x25 : ["02_SENSOR_2_LAMBDA", 25],
        0x26 : ["02_SENSOR_3_LAMBDA", 25],
        0x27 : ["02_SENSOR_4_LAMBDA", 25],
        0x28 : ["02_SENSOR_5_LAMBDA", 25],
        0x29 : ["02_SENSOR_6_LAMBDA", 25],
        0x2A : ["02_SENSOR_7_LAMBDA", 25],
        0x2B : ["02_SENSOR_8_LAMBDA", 25],
        0x2C : ["COMMANDED_EGR", 5],
        0x2D : ["EGR_ERROR", 26],
        0x2E : ["COMMANDED EVAPORATIVE_PURGUE", 5],
        0x2F : ["FUEL_TANK_LEVEL_INPUT", 5],
        0x30 : ["WARMP_UPs_SINCE_CODES_CLEARED", 27],
        0x31 : ["DISTANCE_SINCE_CODES_CLEARED", 28],
        0x32 : ["EVAP_SYSTEM_PRESSURE", 29],
        0x33 : ["ABS_BAROMETRIC_PRESSURE", 30],
        0x34 : ["02_SENSOR_1_LAMBDA_mA", 31],
        0X35 : ["02_SENSOR_2_LAMBDA_mA", 31],
        0x36 : ["02_SENSOR_3_LAMBDA_mA", 31],
        0x37 : ["02_SENSOR_4_LAMBDA_mA", 31],
        0x38 : ["02_SENSOR_5_LAMBDA_mA", 31],
        0x39 : ["02_SENSOR_6_LAMBDA_mA", 31],
        0x3A : ["02_SENSOR_7_LAMBDa_mA", 31],
        0x3B : ["02_SENSOR_8_LAMBDA_mA", 31],
        0x3C : ["CATALYST_TEMP_B1_S1", 32],
        0x3D : ["CATALYST_TEMP_B2_S1", 32],
        0x3E : ["CATALYST_TEMP_B1_S2", 32],
        0x3F : ["CATALYST_TEMP_B2_S2", 32],
        0x40 : ["PIDs_SUPPOTED_[41-60]", 33],
        0x41 : ["MONITOR_STATUS_DRIVE_CYCLE", 34],
        0x42 : ["CONTROL_MODULE_V", 35],
        0x43 : ["ABS_LOAD_VALUE", 36],
        0x44 : ["COMM_AIR-FUEL_EQUIVALENCE_RATIO", 37],
        0x45 : ["RELATIVE_THROTTLE_POS", 5],
        0x46 : ["AMBIENT_AIR_TEMP", 6],
        0x47 : ["ABS_THROTTLE_POS_B", 5],
        0x48 : ["ABS_THROTTLE_POS_C", 5],
        0x49 : ["ACC_PEDAL_POS_D", 5],
        0x4A : ["ACC_PEDAL_POS_E", 5],
        0x4B : ["ACC_PEDAL_POS_F", 5],
        0x4C : ["COMM_THROTTLE_ACTUATOR", 5],
        0x4D : ["TIME_WITH_MIL_ON", 38],
        0x4E : ["TIME_SINCE_TROUBLE_CODES_CLREARED", 38],
        0x4F : ["MAX_VALUE_FOR_LOTS_OF_THINGS", 39],
        0x50 : ["MAX_VALUE_MASS_AIR_FLOW_SENSOR", 40],
        0x51 : ["FUEL_TYPE", 41],
        0x52 : ["ETHANOL_PERCENTAGE", 5],
        0x53 : ["ABS_AVAP_SYST_PRESSURE", 42],
        0x54 : ["EVAP_SYST_PRESSURE", 43],
        0x55 : ["SHORT_TERM_OXIGEN_TRIM_1", 44],
        0x56 : ["LONG_TERM_OXIGEN_TRIM_1", 44],
        0x57 : ["SHORT_TERM_OXIGEN_TRIM_2", 45],
        0x58 : ["LONG_TERM_OXIGEN_TRIM_2 ", 45],
        0x59 : ["FUEL_RAIL_ABS_PRESSURE", 46],
        0x5A : ["REL_ACC_PEDAL_POS", 5],
        0x5B : ["HYBRID_BATT_REMAINING_LIFE", 5],
        0x5C : ["ENGINE_OIL_TEMP", 6],
        0x5D : ["FUEL_INJECTION_TIMING", 47],
        0x5E : ["ENGINE_FUEL_RATE", 48],
        ##0x5F : ["EMISSIONS_REQUIREMENTS", 63],
        0x60 : ["PIDs_SUPPORTED_[61-80]", 49],
        0x61 : ["DRIVERS_DEMAND_TORQUE", 50],
        0x62 : ["ACTUAL_ENGINE_TORQUE", 51],
        0x63 : ["ENGINE_REFERENCE_TORQUE", 51],
        0x64 : ["ENGINE_TORQUE_DATA", 52],
        #0x65 : ["AUX_IN/OUT_SUPPORTED", 69],
        0x66 : ["MASS_AIR_FLOW_SENSOR", 53],
        0x67 : ["ENGINE_COOLANT_TEMP", 54],
        0x67 : ["INTAKE_AIR_TEMP", 55],
        0x67 : ["DIESEL_PARTICULATE_FILTER_TEMP", 56]
	}

# Dictionary 
# key = shared memory tag (MAX length 32) 
# value = shared memory value C type INT = 0, FLOAT = 1, BOOL = 2, LONG_LONG = 3, DOUBLE = 4
variables_dict= {
        "CALCULATED_ENGINE_LOAD" : 1,
        "ENGINE_COOLANT_TEMP" : 0,
        "SHORT_TERM_FUEL_TRIM_1" : 1,
        "LONG_TERM_FUEL_TRIM_1" : 1,
        "SHORT_TERM_FUEL_TRIM_2" : 1,
        "LONG_TERM_FUEL_TRIM_2 " : 1,
        "FUEL_PRESSURE" : 0,
        "INTAKE_MAINFOLD_ABS_PRESSURE" : 0,
        "ENGINE_RPM" : 1,
        "VEHICLE_SPEED" : 0,
        "TIMING_ADVANCE" : 1,
        "INTAKE_AIR_TEMP " : 0,
        "MAF_SENSOR" : 1,
        "THROTTLE POSITION" : 1,
        "SECONDARY_AIR_STATUS" : 0,
        "02_SENSORS" : 0,#IN 2 BANKS
        "02_SENSOR_1" : 1,
        "02_SENSOR_2" : 1,
        "02_SENSOR_3" : 1,
        "02_SENSOR_4" : 1,
        "02_SENSOR_5" : 1,
        "02_SENSOR_6" : 1,
        "02_SENSOR_7" : 1,
        "02_SENSOR_8" : 1,
        "OBD_STANDARDS" : 0,
        "02_SENSORS": 0,#IN 4 BANKS
        "AUX_INPUT_STATUS" : 0,
        "RUNTIME_ENGINE_STARTED" : 1,
        "DIST_MALFUNCTION_INDICATOR" : 1,
        "FUEL_RAIL_PRESSURE" : 1,
        "FUEL_RAIL_GAUGE_PRESSURE" : 1,
        "02_SENSOR_1_LAMBDA" : 1,
        "02_SENSOR_2_LAMBDA" : 1,
        "02_SENSOR_3_LAMBDA": 1,
        "02_SENSOR_4_LAMBDA" : 1,
        "02_SENSOR_5_LAMBDA" : 1,
        "02_SENSOR_6_LAMBDA" : 1,
        "02_SENSOR_7_LAMBDA" : 1,
        "02_SENSOR_8_LAMBDA" : 1,
        "COMMANDED_EGR" : 1,
        "EGR_ERROR" : 1,
        "COMMANDED EVAPORATIVE_PURGUE" : 1,
        "FUEL_TANK_LEVEL_INPUT" : 1,
        "WARMP_UPs_SINCE_CODES_CLEARED" : 0,
        "DISTANCE_SINCE_CODES_CLEARED" : 1,
        "EVAP_SYSTEM_PRESSURE" : 1,
        "ABS_BAROMETRIC_PRESSURE" : 1,
        "02_SENSOR_1_LAMBDA_mA" : 1,
        "02_SENSOR_2_LAMBDA_mA" : 1,
        "02_SENSOR_3_LAMBDA_mA" : 1,
        "02_SENSOR_4_LAMBDA_mA" : 1,
        "02_SENSOR_5_LAMBDA_mA" : 1,
        "02_SENSOR_6_LAMBDA_mA" : 1,
        "02_SENSOR_7_LAMBDa_mA" : 1,
        "02_SENSOR_8_LAMBDA_mA" : 1,
        "CATALYST_TEMP_B1_S1" : 1,
        "CATALYST_TEMP_B2_S1" : 1,
        "CATALYST_TEMP_B1_S2" : 1,
        "CATALYST_TEMP_B2_S2" : 1,
        "CONTROL_MODULE_V" : 1,
        "ABS_LOAD_VALUE" : 1,
        "COMM_AIR-FUEL_EQUIVALENCE_RATIO": 1,
        "RELATIVE_THROTTLE_POS" : 1,
        "AMBIENT_AIR_TEMP" : 0,
        "ABS_THROTTLE_POS_B" : 1,
        "ABS_THROTTLE_POS_C" : 1,
        "ACC_PEDAL_POS_D" : 1,
        "ACC_PEDAL_POS_E" : 1,
        "ACC_PEDAL_POS_F" : 1,
        "COMM_THROTTLE_ACTUATOR" : 1,
        "TIME_WITH_MIL_ON" : 1,
        "TIME_SINCE_TROUBLE_CODES_CLREAR" : 1,
        "FUEL_TYPE" : 1,
        "ETHANOL_PERCENTAGE" : 1,
        "ABS_AVAP_SYST_PRESSURE" : 1,
        "EVAP_SYST_PRESSURE" : 1,
        "SHORT_TERM_OXIGEN_TRIM_1" : 1,
        "LONG_TERM_OXIGEN_TRIM_1" : 1,
        "SHORT_TERM_OXIGEN_TRIM_2" : 1,
        "LONG_TERM_OXIGEN_TRIM_2 " : 1,
        "FUEL_RAIL_ABS_PRESSURE" : 1,
        "REL_ACC_PEDAL_POS" : 1,
        "HYBRID_BATT_REMAINING_LIFE" : 1,
        "ENGINE_OIL_TEMP": 0,
        "FUEL_INJECTION_TIMING" : 1,
        "ENGINE_FUEL_RATE" : 1,
        "DRIVERS_DEMAND_TORQUE" : 1,
        "ACTUAL_ENGINE_TORQUE" : 1,
        "ENGINE_REFERENCE_TORQUE" : 1,
        "ENGINE_TORQUE_DATA" : 1,
        "MASS_AIR_FLOW_SENSOR" : 1,
        "ENGINE_COOLANT_TEMP" : 0,
        "INTAKE_AIR_TEMP" : 0,
        "DIESEL_PARTICULATE_FILTER_TEMP" : 0
}

data1 = data2 = data3 = data4 = data5 = 0
gName = ""
PID_REQUEST = 0x7DF
PID_REPLY = 0x7E8
outfile = open('/var/log/obd2.txt','w')
list_PID = []
engRPM = 0
vehicleSpeed = 0
throotlePos = 0
ambientTemp = 0
oilTemp = 0
coolantTemp = 0
tankLevel = 0


class PythonSwitch:
        def get(self, functionN):

                default = "Incorrect function"

                return getattr(self, 'case_' + str(functionN))()

        def case_1(self):
                
                if data1&128 != 0:
                        list_PID.append(0x01)
                if data1&64 != 0:
                        list_PID.append(0x02) 
                if data1&32 != 0:
                        list_PID.append(0x03)
                if data1&16 != 0:
                        list_PID.append(0x04)
                if data1&8 != 0:
                        list_PID.append(0x05)
                if data1&4 != 0:
                        list_PID.append(0x06)
                if data1&2 != 0:
                        list_PID.append(0x07)
                if data1&1 != 0:
                        list_PID.append(0x08)
               
                
                if data2&128 != 0:
                        list_PID.append(0x09)
                if data2&64 != 0:
                        list_PID.append(0x0A) 
                if data2&32 != 0:
                        list_PID.append(0x0B)
                if data2&16 != 0:
                        list_PID.append(0x0C)
                if data2&8 != 0:
                        list_PID.append(0x0D)
                if data2&4 != 0:
                        list_PID.append(0x0E)
                if data2&2 != 0:
                        list_PID.append(0x0F)
                if data2&1 != 0:
                        list_PID.append(0x10)
                                                               
                if data3&128 != 0:
                        list_PID.append(0x11)
                if data3&64 != 0:
                        list_PID.append(0x12)
                if data3&32 != 0:
                        list_PID.append(0x13) 
                if data3&16 != 0:
                        list_PID.append(0x14)
                if data3&8 != 0:
                        list_PID.append(0x15)
                if data3&4 != 0:
                        list_PID.append(0x16)
                if data3&2 != 0:
                        list_PID.append(0x17)  
                if data3&1 != 0:
                        list_PID.append(0x18)                      
                    
                if data4&128 != 0:
                        list_PID.append(0x19)
                if data4&64 != 0:
                        list_PID.append(0x1A)
                if data4&32 != 0:
                        list_PID.append(0x1B)
                if data4&16 != 0:
                        list_PID.append(0x1C)
                if data4&8 != 0:
                        list_PID.append(0x1D)
                if data4&4 != 0:
                        list_PID.append(0x1E) 
                if data4&2 != 0:
                        list_PID.append(0x1F)
                if data4&1 != 0:
                        list_PID.append(0x20)                            

                return 1

        def case_2(self):
                if data1&128 != 0:
                        print("The check engine light is ON")
                        print("The check engine light is ON",file = outfile)
                return 1
        
        def case_3(self):
            #PIDs supported
                return 1

        def case_4(self):
                prhase = "The fuel system #1 status is:"
                
                if data1 == 0:
                        prhase = prhase + "The motor is off"
                if data1 == 1:
                        prhase = prhase + "Open loop due to insufficient engine temperature"
                if data1 == 2:
                        prhase = prhase + "Closed loop, using oxygen sensor feedback to determine fuel mix"
                if data1 == 4:
                        prhase = prhase + "Open loop due to engine load OR fuel cut due to deceleration "
                if data1 == 8:
                        prhase = prhase + "Open loop due to system failure "
                if data1 == 16:
                        prhase = prhase + "Closed loop, using at least one oxygen sensor but there is a fault in the feedback system "

                print(prhase)
                print(prhase,file = outfile)
                #hw.update_shm_key(10007,gName,prhase)
                
                if data2 != 0 and data2 != 1 and data2 != 2 and data2 != 4 and data2 != 8 and data2 != 16:
                        prhase2 = "The fuel system #2 status is:"
                        if data2 == 0:
                                prhase2 = prhase2 + "The motor is off"
                        if data2 == 1:
                                prhase2 = prhase2 + "Open loop due to insufficient engine temperature"
                        if data2 == 2:
                                prhase2 = prhase2 + "Closed loop, using oxygen sensor feedback to determine fuel mix"
                        if data2 == 4:
                                prhase2 = prhase2 + "Open loop due to engine load OR fuel cut due to deceleration "
                        if data2 == 8:
                                prhase2 = prhase2 + "Open loop due to system failure "
                        if data2 == 16:
                                prhase2 = prhase2 + "Closed loop, using at least one oxygen sensor but there is a fault in the feedback system "
                        else:
                                prhase2 = prhase2 + "No data"
                        print(prhase2)
                        print(prhase2,file = outfile)
                        #hw.update_shm_key(10007,gName,prhase)
                return 1

        def case_5(self):
                global throotlePos, tankLevel
                load = 100*data1/255
                prhase = "The " + gName +  " is " + "{:.2f}".format(load) + "%"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,load)

                
                if gName == "THROTTLE POSITION":
                        difference = abs(load - throotlePos)
                        if difference < 3:
                                pass
                        else:
                                throotlePos = load
                                data = "{\"ts\":" + str(time.time()) + ",values:{\"throttle\":" + "{:.2f}".format(throotlePos) + "}}"
                                #Send data
                                r.rpush("q-out", data)
                if gName == "FUEL_TANK_LEVEL_INPUT":
                        difference = abs(load - tankLevel)
                        if difference < 3:
                                pass
                        else:
                                tankLevel = load
                                data = "{\"ts\":" + str(time.time()) + ",values:{\"fuel.level\":" + "{:.2f}".format(tankLevel) + "}}"
                                #Send data
                                r.rpush("q-out", data)

                
                return 1

        def case_6(self):
                global coolantTemp, ambientTemp, oilTemp
                temp = data1 - 40
                prhase = "The " + gName + " is "  + "{:.2f}".format(temp) + "ºC"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,temp)
                if gName == "ENGINE_COOLANT_TEMP":
                        difference = abs(coolantTemp - temp)
                        if difference > 0.9:
                                coolantTemp = temp
                                data = "{\"ts\":" + str(time.time()) + ",values:{\"coolant.temp\":" + "{:.2f}".format(coolantTemp) + "}}"
                                #Send data
                                r.rpush("q-out", data)
                if gName == "AMBIENT_AIR_TEMP":
                        difference = abs(ambientTemp - temp)
                        if difference > 0.9:
                                ambientTemp = temp
                                data = "{\"ts\":" + str(time.time()) + ",values:{\"air.temp\":" + "{:.2f}".format(ambientTemp) + "}}"
                                #Send data
                                r.rpush("q-out", data)
                if gName == "ENGINE_OIL_TEMP":
                        difference = abs(oilTemp - temp)
                        if difference > 0.9:
                                oilTemp = temp
                                data = "{\"ts\":" + str(time.time()) + ",values:{\"oil.temp\":" + "{:.2f}".format(oilTemp) + "}}"
                                #Send data
                                r.rpush("q-out", data)
                        
                
                return 1

        def case_7(self):
                temp = (100*data1/128) -100
                prhase = "The " + gName + " is at " + "{:.2f}".format(temp) + "%"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,temp)
                return 1

        def case_8(self):
                press = 3*data1
                prhase = "The fuel pressure is " + "{:.2f}".format(press) + "kPa"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,press)
                return 1

        def case_9(self):
                prhase = "The intake mainfold absolute pressure is " + "{:.2f}".format(data1) + "kPa"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,data1)
                return 1
        
        def case_10(self):
                global engRPM
                rpm = (256*data1 + data2)/4
                prhase = "The vehicle's engine speed is " + "{:.2f}".format(rpm) + "rpm"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,rpm)
                
                difference = abs(rpm - engRPM)
                if difference < 100:
                        pass
                else:
                        engRPM = rpm
                        data = "{\"ts\":" + str(time.time()) + ",values:{\"rpm\":" + "{:.2f}".format(engRPM) + "}}"
                        #Send data
                        r.rpush("q-out", data)
                return 1

        def case_11(self):
                global vehicleSpeed
                prhase = "The vehicle's speed is " + "{:.2f}".format(data1) + "km/h"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,data1)

                difference = abs(data1 - vehicleSpeed)
                if difference < 3:
                        pass
                else:
                        vehicleSpeed = data1
                        data = "{\"ts\":" + str(time.time()) + ",values:{\"speed\":" + "{:.2f}".format(vehicleSpeed) + "}}"
                        #Send data
                        r.rpush("q-out", data)
                return 1

        def case_12(self):
                press = data1/2 - 64
                prhase = "The timing advance is " + "{:.2f}".format(press) + "?"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,press)
                return 1

        def case_13(self):
                press = (256*data1 + data2)/100
                prhase = "The Mass Air Flow rate is " + "{:.2f}".format(press) + "g/s"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,press)
                return 1

        def case_14(self):
                prhase = "The secondary air status is:"
                if data1 == 1:
                        prhase = prhase + "Upstream"
                if data1 == 2:
                        prhase = prhase + "Downstream of catalytic converter "
                if data1 == 4:
                        prhase = prhase + "From the outside atmosphere or off "
                if data1 == 8:
                        prhase = prhase + "Pump commanded on for diagnostics "
                print(prhase)
                print(prhase,file = outfile)
                #hw.update_shm_key(10007,gName,prhase)
        
        def case_15(self):
                prhase = "The available Oxygen sensors are: "
                if data1&128 != 0:
                        prhase = prhase + "Bank 1 Sensor 1 "
                if data1&64 != 0:
                        prhase = prhase + "Bank 1 Sensor 2 "
                if data1&32 != 0:
                        prhase = prhase + "Bank 1 Sensor 3 "
                if data1&16 != 0:
                        prhase = prhase + "Bank 1 Sensor 4 "
                if data1&8 != 0:
                        prhase = prhase + "Bank 2 Sensor 1 "
                if data1&4 != 0:
                        prhase = prhase + "Bank 2 Sensor 2 "
                if data1&2 != 0:
                        prhase = prhase + "Bank 2 Sensor 3 "
                if data1&1 != 0:
                        prhase = prhase + "Bank 2 Sensor 4 "
                print(prhase)
                print(prhase,file = outfile)
                #hw.update_shm_key(10007,gName,prhase)

        def case_16(self):
                v = data1/200
                trim = 100*data2/128 - 100
                prhase = "The voltage at " + gName + "is " + "{:.2f}".format(v) + "V and it's short term fuel trim is at " + "{:.2f}".format(trim) + "%"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,  v)
                return 1

        def case_17(self):
                prhase = "The OBD standard this vehicle conforms to "
                if data1 == 1:
                        prhase = prhase + "OBD-II as defined by the CARB"
                elif data1 == 2:
                        prhase = prhase + "OBD as defined by the EPA"
                elif data1 == 3:
                        prhase = prhase + "OBD and OBD-II"
                elif data1 == 4:
                        prhase = prhase + "OBD-I"
                elif data1 == 5:
                        prhase = prhase + "Not OBD compliant"
                elif data1 == 6:
                        prhase = prhase + "EOBD (Europe)"
                elif data1 == 7:
                        prhase = prhase + "EOBD and OBD-II"
                elif data1 == 8:
                        prhase = prhase + "EOBD and OBD"
                elif data1 == 9:
                        prhase = prhase + "EOBD, OBD and OBD II"
                elif data1 == 10:
                        prhase = prhase + "JOBD (Japan)"
                elif data1 == 11:
                        prhase = prhase + "JOBD and OBD II"
                elif data1 == 12:
                        prhase = prhase + "JOBD and EOBD "
                elif data1 == 13:
                        prhase = prhase + "JOBD, EOBD, and OBD II"
                elif data1 == 14:
                        prhase = prhase + "Reserved"
                elif data1 == 15:
                        prhase = prhase + "Reserved"
                elif data1 == 16:
                        prhase = prhase + "Reserved"
                elif data1 == 17:
                        prhase = prhase + "Engine Manufacturer Diagnostics (EMD)"
                elif data1 == 18:
                        prhase = prhase + "Engine Manufacturer Diagnostics Enhanced (EMD+)"
                elif data1 == 19:
                        prhase = prhase + "Heavy Duty On-Board Diagnostics (Child/Partial) (HD OBD-C)"
                elif data1 == 20:
                        prhase = prhase + "Heavy Duty On-Board Diagnostics (HD OBD)"
                elif data1 == 21:
                        prhase = prhase + "World Wide Harmonized OBD (WWH OBD)"
                elif data1 == 22:
                        prhase = prhase + "Reserved"
                elif data1 == 23:
                        prhase = prhase + "Heavy Duty Euro OBD Stage I without NOx control (HD EOBD-I)"
                elif data1 == 24:
                        prhase = prhase + "Heavy Duty Euro OBD Stage I with NOx control (HD EOBD-I N)"
                elif data1 == 25:
                        prhase = prhase + "Heavy Duty Euro OBD Stage II without NOx control (HD EOBD-II)"
                elif data1 == 26:
                        prhase = prhase + "Heavy Duty Euro OBD Stage II with NOx control (HD EOBD-II N)"
                elif data1 == 27:
                        prhase = prhase + "Reserved"
                elif data1 == 28:
                        prhase = prhase + "Brazil OBD Phase 1 (OBDBr-1)"
                elif data1 == 29:
                        prhase = prhase + "Brazil OBD Phase 2 (OBDBr-2)"
                elif data1 == 30:
                        prhase = prhase + "Korean OBD (KOBD)"
                elif data1 == 31:
                        prhase = prhase + "India OBD I (IOBD I)"
                elif data1 == 32:
                        prhase = prhase + "India OBD II (IOBD II)"
                elif data1 == 33:
                        prhase = prhase + "Heavy Duty Euro OBD Stage VI (HD EOBD-IV)"
                else:
                        prhase = prhase + "Reserved"
        
                print(prhase)
                print(prhase,file = outfile)
                #hw.update_shm_key(10007,gName,prhase)
                return 1


        def case_18(self):
                prhase = "The available Oxygen sensors are: "
                if data1&128 != 0:
                        prhase = prhase + "Bank 1 Sensor 1 "
                if data1&64 != 0:
                        prhase = prhase + "Bank 1 Sensor 2 "
                if data1&32 != 0:
                        prhase = prhase + "Bank 2 Sensor 1 "
                if data1&16 != 0:
                        prhase = prhase + "Bank 2 Sensor 2 "
                if data1&8 != 0:
                        prhase = prhase + "Bank 3 Sensor 1 "
                if data1&4 != 0:
                        prhase = prhase + "Bank 3 Sensor 2 "
                if data1&2 != 0:
                        prhase = prhase + "Bank 4 Sensor 1 "
                if data1&1 != 0:
                        prhase = prhase + "Bank 4 Sensor 2 "

                print(prhase)
                print(prhase,file = outfile)
                #hw.update_shm_key(10007,gName,prhase)
                return 1

        def case_19(self):
                prhase = "The Auxiliary input status is: "
                if data1&128 != 0:
                        prhase = prhase + "Active"
                else:
                        prhase = prhase + "Inactive"

                print(prhase)
                print(prhase,file = outfile)
                #hw.update_shm_key(10007,gName,prhase)
                return 1
        def case_20(self):
                time = 256*data1 + data2
                prhase = "The run time since engine started is " + "{:.2f}".format(time) + "s"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,time)
                return 1
        def case_21(self):
                if data1&128 != 0:
                        list_PID.append(0x21)
                if data1&64 != 0:
                        list_PID.append(0x22) 
                if data1&32 != 0:
                        list_PID.append(0x23)
                if data1&16 != 0:
                        list_PID.append(0x24)
                if data1&8 != 0:
                        list_PID.append(0x25)
                if data1&4 != 0:
                        list_PID.append(0x26)
                if data1&2 != 0:
                        list_PID.append(0x27)
                if data1&1 != 0:
                        list_PID.append(0x28)
               
                
                if data2&128 != 0:
                        list_PID.append(0x29)
                if data2&64 != 0:
                        list_PID.append(0x2A) 
                if data2&32 != 0:
                        list_PID.append(0x2B)
                if data2&16 != 0:
                        list_PID.append(0x2C)
                if data2&8 != 0:
                        list_PID.append(0x2D)
                if data2&4 != 0:
                        list_PID.append(0x2E)
                if data2&2 != 0:
                        list_PID.append(0x2F)
                if data2&1 != 0:
                        list_PID.append(0x30)
                                                               
                if data3&128 != 0:
                        list_PID.append(0x31)
                if data3&64 != 0:
                        list_PID.append(0x32)
                if data3&32 != 0:
                        list_PID.append(0x33) 
                if data3&16 != 0:
                        list_PID.append(0x34)
                if data3&8 != 0:
                        list_PID.append(0x35)
                if data3&4 != 0:
                        list_PID.append(0x36)
                if data3&2 != 0:
                        list_PID.append(0x37)  
                if data3&1 != 0:
                        list_PID.append(0x38)                      
                    
                if data4&128 != 0:
                        list_PID.append(0x39)
                if data4&64 != 0:
                        list_PID.append(0x3A)
                if data4&32 != 0:
                        list_PID.append(0x3B)
                if data4&16 != 0:
                        list_PID.append(0x3C)
                if data4&8 != 0:
                        list_PID.append(0x3D)
                if data4&4 != 0:
                        list_PID.append(0x3E) 
                if data4&2 != 0:
                        list_PID.append(0x3F)
                if data4&1 != 0:
                        list_PID.append(0x30)                            
                return 1
                
        def case_22(self):
                dist = 256*data1 + data2
                prhase = "The distance traveled with malfunction indicator lamp on is " + "{:.2f}".format(dist) + "km"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,dist)
                
                return 1

        def case_23(self):
                press = 0.079*(256*data1 + data2)
                prhase = "The fuel rail pressure relative to mainfold vacuum is " + "{:.2f}".format(press) + "kPa"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,press)
                return 1

        def case_24(self):
                press = 10*(256*data1 + data2)
                prhase = "The fuel Gauge pressure is " + "{:.2f}".format(press) + "kPa"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,press)
                return 1

        def case_25(self):
                ratio = (2/65536)*(256*data1 + data2)
                v = (8/65536)*(256*data3 + data4)
                prhase = "The Air-Fuel Equivalence Ratio at " + gName + " is " + "{:.2f}".format(ratio) + " and the related voltage is "+ "{:.2f}".format(v) + "v"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,ratio)
                return 1
        
        def case_26(self):
                ratio = 100*data1/128 - 100
                prhase = "The EGR error is "  + "{:.2f}".format(ratio) + "%"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,ratio)
                return 1

        def case_27(self):
                prhase = "The warm up number since codes cleared is "  + "{:.2f}".format(data1)
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,data1)
                return 1

        def case_28(self):
                time = 256*data1 + data2
                prhase = "The distance traveled since codes cleared is " + "{:.2f}".format(time) + "km"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,time)
                return 1

        def case_29(self):
                press = (256*data1 + data2)/4
                prhase = "The evaporaion system vapor pressure is " + "{:.2f}".format(press) + "Pa"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,press)
                return 1

        def case_30(self):
                prhase = "The absolute barotmetric pressure is " + "{:.2f}".format(data1) + "kPa"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,data1)
                return 1

        def case_31(self):
                ratio = (2/65536)*(256*data1 + data2)
                mA = ((256*data3 + data4)/256) - 128
                prhase = "The Air-Fuel Equivalence Ratio at " + gName + " is " + "{:.2f}".format(ratio) + " and the related curent is "+ "{:.2f}".format(mA) + "mA"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,ratio)
                return 1

        def case_32(self):
                ratio = ((256*data1 +data2)/10) - 40
                prhase = "The " + gName+ " is " + "{:.2f}".format(ratio) + "º"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,ratio)
                return 1

        def case_33(self):
                if data1&128 != 0:
                        list_PID.append(0x41)
                if data1&64 != 0:
                        list_PID.append(0x42) 
                if data1&32 != 0:
                        list_PID.append(0x43)
                if data1&16 != 0:
                        list_PID.append(0x44)
                if data1&8 != 0:
                        list_PID.append(0x45)
                if data1&4 != 0:
                        list_PID.append(0x46)
                if data1&2 != 0:
                        list_PID.append(0x47)
                if data1&1 != 0:
                        list_PID.append(0x48)
               
                
                if data2&128 != 0:
                        list_PID.append(0x49)
                if data2&64 != 0:
                        list_PID.append(0x4A) 
                if data2&32 != 0:
                        list_PID.append(0x4B)
                if data2&16 != 0:
                        list_PID.append(0x4C)
                if data2&8 != 0:
                        list_PID.append(0x4D)
                if data2&4 != 0:
                        list_PID.append(0x4E)
                if data2&2 != 0:
                        list_PID.append(0x4F)
                if data2&1 != 0:
                        list_PID.append(0x50)
                                                               
                if data3&128 != 0:
                        list_PID.append(0x51)
                if data3&64 != 0:
                        list_PID.append(0x52)
                if data3&32 != 0:
                        list_PID.append(0x53) 
                if data3&16 != 0:
                        list_PID.append(0x54)
                if data3&8 != 0:
                        list_PID.append(0x55)
                if data3&4 != 0:
                        list_PID.append(0x56)
                if data3&2 != 0:
                        list_PID.append(0x57)  
                if data3&1 != 0:
                        list_PID.append(0x58)                      
                    
                if data4&128 != 0:
                        list_PID.append(0x59)
                if data4&64 != 0:
                        list_PID.append(0x5A)
                if data4&32 != 0:
                        list_PID.append(0x5B)
                if data4&16 != 0:
                        list_PID.append(0x5C)
                if data4&8 != 0:
                        list_PID.append(0x5D)
                if data4&4 != 0:
                        list_PID.append(0x5E) 
                if data4&2 != 0:
                        list_PID.append(0x5F)
                if data4&1 != 0:
                        list_PID.append(0x60)                            
                
                return 1

        def case_34(self):
                if data2&128 != 0:
                        B0 = 1
                else: 
                        B0 = 0
                if data2&64 != 0:
                        B1 = 1
                else: 
                        B1 = 0
                if data2&32 != 0:
                        B2 = 1
                else: 
                        B2 = 0
                if data2&16 != 0:
                        B3 = 1
                else: 
                        B3 = 0
                if data2&8 != 0:
                        B4 = 1
                else: 
                        B4 = 0
                if data2&4 != 0:
                        B5 = 1
                else: 
                        B5 = 0
                if data2&2 != 0:
                        B6 = 1
                else: 
                        B6 = 0
                if data2&1 != 0:
                        B7 = 1
                else: 
                        B7 = 0
                table = [["Components", B2, B6], ["Fuel System", B1, B2], ["Misfire", B0, B4]]
                prhase = tabulate(table, headers=["","Test available","Test Incomplete"])
                print(prhase)
                print(prhase,file = outfile)
                return 1

        def case_35(self):
                ratio = (256*data1 +data2)/1000
                prhase = "The " + gName+ " is " + "{:.2f}".format(ratio) + "V"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,ratio)
                return 1

        def case_36(self):
                ratio = ((256*data1 + data2)*100/255)
                prhase = "The " + gName+ " is " + "{:.2f}".format(ratio) + "%"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,ratio)
                return 1

        def case_37(self):
                ratio = ((256*data1 +data2)*2/65536)
                prhase = "The " + gName+ " is " + "{:.2f}".format(ratio) + "º"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,ratio)
                return 1
        
        def case_38(self):
                ratio = 256*data1 +data2
                prhase = "The " + gName+ " is " + "{:.2f}".format(ratio) + "min"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,ratio)
                return 1
        
        def case_39(self):
                
                prhase = "The maximum value for Fuel-Air equivalence ratio is " + "{:.2f}".format(data1*10) + "\n"
                prhase = prhase + "The maximum value for Oxigen sensor voltage is " + "{:.2f}".format(data2*10) + "V\n"
                prhase = prhase + "The maximum value for Oxygen sensor currrent is " + "{:.2f}".format(data3*10) + "mA\n"
                prhase = prhase + "The maximum value for Intake mainfold absolute pressure is " + "{:.2f}".format(data4*10) + "kPa\n"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,data1*10)
                return 1

        def case_40(self):
                prhase = "The maximum value for air flow rate from mass air flow sensor is " + "{:.2f}".format(data1*10) + "g/s"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,data1*10)
                return 1

        def case_41(self):
                prhase = "The fuel type is: "
                if data1 == 0:
                        prhase = prhase + "Not available "
                if data1 == 1:
                        prhase = prhase + "Gasoline"
                if data1 == 2:
                        prhase = prhase + "Methanol"
                if data1 == 3:
                        prhase = prhase + "Ethanol"
                if data1 == 4:
                        prhase = prhase + "Diesel"
                if data1 == 5:
                        prhase = prhase + "LPG"
                if data1 == 6:
                        prhase = prhase + "CNG"
                if data1 == 7:
                        prhase = prhase + "Propane"
                if data1 == 8:
                        prhase = prhase + "Electric"
                if data1 == 9:
                        prhase = prhase + "Bifuel running Gasoline "
                if data1 == 10:
                        prhase = prhase + "Bifuel running Methanol "
                if data1 == 11:
                        prhase = prhase + "Bifuel running Ethanol  "
                if data1 == 12:
                        prhase = prhase + "Bifuel running LPG "
                if data1 == 13:
                        prhase = prhase + "Bifuel running CNG "
                if data1 == 14:
                        prhase = prhase + "Bifuel running Propane "
                if data1 == 15:
                        prhase = prhase + "Bifuel running Electricity "
                if data1 == 16:
                        prhase = prhase + "Bifuel running electric and combustion engine " 
                if data1 == 17:
                        prhase = prhase + "Hybrid gasoline "
                if data1 == 18:
                        prhase = prhase + "Hybrid Ethanol "
                if data1 == 19:
                        prhase = prhase + "Hybrid Diesel "
                if data1 == 20:
                        prhase = prhase + "Hybrid Electric "
                if data1 == 21:
                        prhase = prhase + "Hybrid running electric and combustion engine "
                if data1 == 22:
                        prhase = prhase + "Hybrid Regenerative "
                if data1 == 23:
                        prhase = prhase + "Bifuel running diesel "
                print(prhase)
                print(prhase,file = outfile)
                #hw.update_shm_key(10007,gName,prhase)
                return 1

        def case_42(self):
                prhase = "The abslute evaporation system pressure is", "{:.2f}".format((data1*256 + data2)/200) + "kPa"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,(data1*256 + data2)/200)
                return 1
        
        def case_43(self):
                prhase = "The evaporation system pressure is" + "{:.2f}".format(data1*256 + data2) + "kPa"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,(data1*256 + data2))
                return 1
        def case_44(self):
                v = 100*data1/128 - 100
                trim = 100*data2/128 - 100
                prhase = "The bank 1 is at" + str(v) + " %"," and bank 3 is at " + "{:.2f}".format(trim) + "%"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,v)
                return 1
        
        def case_45(self):
                v = 100*data1/128 - 100
                trim = 100*data2/128 - 100
                prhase = "The bank 2 is at" + str(v) + " %"," and bank 4 is at " + "{:.2f}".format(trim) + "%"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,v)
                return 1

        def case_46(self):
                prhase = "The fuel rail absolute pressure is " + "{:.2f}".format(10*(256*data1 + data2)) + "kPa"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,(10*(256*data1 + data2)))
                return 1

        def case_47(self):
                prhase = "The fuel injection timing is" + "{:.2f}".format(((256*data1 + data2)/128)-210) + "º"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,(((256*data1 + data2)/128)-210))
                return 1

        def case_48(self):
                prhase = "The engine fuel rate is" + "{:.2f}".format((256*data1 + data2)/20) + "L/h"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,((256*data1 + data2)/20))
                return 1

        def case_49(self):
                if data1&128 != 0:
                        list_PID.append(0x61)
                if data1&64 != 0:
                        list_PID.append(0x62) 
                if data1&32 != 0:
                        list_PID.append(0x63)
                if data1&16 != 0:
                        list_PID.append(0x64)
                if data1&8 != 0:
                        list_PID.append(0x65)
                if data1&4 != 0:
                        list_PID.append(0x66)
                if data1&2 != 0:
                        list_PID.append(0x67)
                if data1&1 != 0:
                        list_PID.append(0x68)
               
                
                if data2&128 != 0:
                        list_PID.append(0x69)
                if data2&64 != 0:
                        list_PID.append(0x6A) 
                if data2&32 != 0:
                        list_PID.append(0x6B)
                if data2&16 != 0:
                        list_PID.append(0x6C)
                if data2&8 != 0:
                        list_PID.append(0x6D)
                if data2&4 != 0:
                        list_PID.append(0x6E)
                if data2&2 != 0:
                        list_PID.append(0x6F)
                if data2&1 != 0:
                        list_PID.append(0x70)
                                                               
                if data3&128 != 0:
                        list_PID.append(0x71)
                if data3&64 != 0:
                        list_PID.append(0x72)
                if data3&32 != 0:
                        list_PID.append(0x73) 
                if data3&16 != 0:
                        list_PID.append(0x74)
                if data3&8 != 0:
                        list_PID.append(0x75)
                if data3&4 != 0:
                        list_PID.append(0x76)
                if data3&2 != 0:
                        list_PID.append(0x77)  
                if data3&1 != 0:
                        list_PID.append(0x78)                      
                    
                if data4&128 != 0:
                        list_PID.append(0x79)
                if data4&64 != 0:
                        list_PID.append(0x7A)
                if data4&32 != 0:
                        list_PID.append(0x7B)
                if data4&16 != 0:
                        list_PID.append(0x7C)
                if data4&8 != 0:
                        list_PID.append(0x7D)
                if data4&4 != 0:
                        list_PID.append(0x7E) 
                if data4&2 != 0:
                        list_PID.append(0x7F)
                if data4&1 != 0:
                        list_PID.append(0x80)                            
                 
                prhase = "The supported PIDs (in decimal) are: " + str(list_PID)
                print(prhase)
                print(prhase,file = outfile)
                #hw.update_shm_key(10007,gName,prhase)
                return 1

        def case_50(self):
                prhase = "The "+ gName +" is" + "{:.2f}".format(data1 -125) + "%"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,(data1 -125))
                return 1

        def case_51(self):
                prhase = "The engine reference torque is " + "{:.2f}".format(256*data1 + data2) + "N.m"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,(256*data1 + data2))
                return 1

        def case_52(self):
                prhase = "The engine percent torque daata at idle is" + "{:.2f}".format(data1 - 125) + "%"
                prhase = prhase + "The engine percent torque daata at Engine point 1 is" + "{:.2f}".format(data2 - 125) + "%"
                prhase = prhase + "The engine percent torque daata at Engine point 2 is" + "{:.2f}".format(data3 - 125) + "%"
                prhase = prhase + "The engine percent torque daata at Engine point 3 is" + "{:.2f}".format(data4 - 125) + "%"
                prhase = prhase + "The engine percent torque daata at Engine point 4 is" + "{:.2f}".format(data5 - 125) + "%"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,(256*data1 + data2))
                return 1

        def case_53(self):
                if data1&128 != 0:
                        sens1 = (256*data2 +data3)/32
                        hw.update_shm_key(10007,gName,sens1)
                if data1&64 != 0:
                        sens2 = (256*data4 +data5)/32
                        hw.update_shm_key(10007,gName,sens2)
                if data1&128 != 0 and data1&64 != 0:
                        media = (sens1 + sens2)/2
                        hw.update_shm_key(10007,gName,media)
                prhase = "The mass air flow sensor 1 marks:" + "{:.2f}".format(sens1) +"g/s. At sensor 2:" + "{:.2f}".format(sens2) + "g/s. And the average is:" + "{:.2f}".format(media) + "g/s"
                print(prhase,file = outfile)
                return 1

        def case_54(self):
                if data1&128 != 0:
                        sens1 = data2 - 40
                        hw.update_shm_key(10007,gName,sens1)
                if data1&64 != 0:
                        sens2 = data3 - 40
                        hw.update_shm_key(10007,gName,sens2)
                if data1&128 != 0 and data1&64 != 0:
                        media = (sens1 + sens2)/2
                        hw.update_shm_key(10007,gName,media)
                prhase = "The engine coolant temperature sensor 1 marks:" + "{:.2f}".format(sens1) +"ºC. At sensor 2:" + "{:.2f}".format(sens2) + "ºC. And the average is:" + "{:.2f}".format(media) +"ºC"
                print(prhase,file = outfile)
                return 1
        def case_55(self):
                if data1&128 != 0:
                        sens1 = data2 - 40
                        hw.update_shm_key(10007,gName,sens1)
                if data1&64 != 0:
                        sens2 = data3 - 40
                        hw.update_shm_key(10007,gName,sens2)
                if data1&128 != 0 and data1&64 != 0:
                        media = (sens1 + sens2)/2
                        hw.update_shm_key(10007,gName,media)
                prhase = "The intake air temperature sensor 1 marks:" + "{:.2f}".format(sens1) +"ºC. At sensor 2:" + "{:.2f}".format(sens2) + "ºC. And the average is:" + "{:.2f}".format(media) + "ºC"
                print(prhase,file = outfile)
                return 1
        
        def case_56(self):
                temp = ((256*data1 + data2)/10) - 40
                prhase = "The diesel particulate filter temperature is" + "{:.2f}".format(temp) + "ºC"
                print(prhase)
                print(prhase,file = outfile)
                hw.update_shm_key(10007,gName,(256*data1 + data2))
                return 1


print('\n\rCAN connection test')
print('Bringing up CAN1....')

# Bring up can1 interface at 500kbps
try:
        os.system("sudo /sbin/ip link set vcan0 up type can bitrate 500000")
except OSError:
        print('An error was encountered while bringing up CAN interface')
        print('An error was encountered while bringing up CAN interface',file = outfile)
        exit()

time.sleep(0.5)
print('CAN1 interface ready')

#Bring up CAN bus
try:
        bus = can.interface.Bus(channel='can1', bustype='socketcan_native')
except OSError:
        print('Connection with the CAN1 bus failed')
        exit()

#Create shared memory allocation in the owa450 
print('Creating shared memory')
hw = shmreader.ShmReader()
hw.create_shm(10007,variables_dict)

def can_rx_task():      # Receive thread while program is running
        while True:
                message = bus.recv()
                if message.arbitration_id == PID_REPLY:
                        q.put(message)  # Put message into queue if it is a reply

def can_tx_task():      # Transmit thread
        print('Requesting available PIDs...')
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x00,0x00,0x00,0x00,0x00,0x00],extended_id=False)
        bus.send(msg)
        time.sleep(0.05)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x20,0x00,0x00,0x00,0x00,0x00],extended_id=False)
        bus.send(msg)
        time.sleep(0.05)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x40,0x00,0x00,0x00,0x00,0x00],extended_id=False)
        bus.send(msg)
        time.sleep(0.05)
        msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x60,0x00,0x00,0x00,0x00,0x00],extended_id=False)
        bus.send(msg)
        time.sleep(0.05)

        #Set peridic sending messages for variables sent via redis network
        if 0x05 in list_PID:
                list_PID.remove(0x05)
                msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x05,0x00,0x00,0x00,0x00,0x00],extended_id=False)
                bus.send_periodic(msg,300)
                time.sleep(0.05)

        if 0x0C in list_PID:
                list_PID.remove(0x0C)
                msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x0C,0x00,0x00,0x00,0x00,0x00],extended_id=False)
                bus.send_periodic(msg,3)
                time.sleep(0.05)

        if 0x0D in list_PID:
                list_PID.remove(0x0D)
                msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x0D,0x00,0x00,0x00,0x00,0x00],extended_id=False)
                bus.send_periodic(msg,3)
                time.sleep(0.05)
        
        if 0x46 in list_PID:
                list_PID.remove(0x46)
                msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x46,0x00,0x00,0x00,0x00,0x00],extended_id=False)
                bus.send_periodic(msg,300)
                time.sleep(0.05)

        if 0x11 in list_PID:
                list_PID.remove(0x11)
                msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x11,0x00,0x00,0x00,0x00,0x00],extended_id=False)
                bus.send_periodic(msg,3)
                time.sleep(0.05)

        if 0x5C in list_PID:
                list_PID.remove(0x5C)
                msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x5C,0x00,0x00,0x00,0x00,0x00],extended_id=False)
                bus.send_periodic(msg,300)
                time.sleep(0.05)

        if 0x2F in list_PID:
                list_PID.remove(0x2F)
                msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,0x2F,0x00,0x00,0x00,0x00,0x00],extended_id=False)
                bus.send_periodic(msg,300)
                time.sleep(0.05)

        while True: #Send the messages only registerend in the log file and saved into linux shared memory
                for x in list_PID:
                        msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,x,0x00,0x00,0x00,0x00,0x00],extended_id=False)
                        bus.send(msg)
                        time.sleep(0.05)

                time.sleep(0.1)


q = queue.Queue() #Creation of the queue
rx = Thread(target = can_rx_task) #Transmiting thread
rx.start()
tx = Thread(target = can_tx_task) #Receiving thread
tx.start()

my_switch = PythonSwitch() #Creation of the function switch

# Main loop
try:
        while True:
                while(q.empty() == True): # Wait until there is a message
                        pass
                message = q.get() #Get message from the queue         

                if message.arbitration_id == PID_REPLY:
                        PID = message.data[2]
                        if PID in dyctionary:
                                data1 = message.data[3]
                                data2 = message.data[4]
                                data3 = message.data[5]
                                data4 = message.data[6]
                                data5 = message.data[7]
                                name,functionN = dyctionary.get(PID)
                                gName = name
                                my_switch.get(functionN)




except KeyboardInterrupt:
        #Catch keyboard interrupt
        outfile.close()         # Close logger file
        os.system("sudo /sbin/ip link set can1 down")
        print('\n\rKeyboard interrtupt')
        exit(1)

