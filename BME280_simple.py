import smbus
import time

class BME280:
    #address
    BME280_ADDRESS = 0x76
    #registers
    REG_ID = 0xD0
    REG_ID_STATUS = 0xF3
    REG_CTRL_MEAS = 0xF4
    REG_CTRL_HUM = 0xF2
    REG_START_DATA = 0xF7
    REG_DIG_T1 = 0x88
    REG_DIG_T2 = 0x8A
    REG_DIG_T3 = 0x8C
    REG_DIG_P1 = 0x8E
    REG_DIG_P2 = 0x90
    REG_DIG_P3 = 0x92
    REG_DIG_P4 = 0x94
    REG_DIG_P5 = 0x96
    REG_DIG_P6 = 0x98
    REG_DIG_P7 = 0x9A
    REG_DIG_P8 = 0x9C
    REG_DIG_P9 = 0x9E
    REG_DIG_H1 = 0xA1
    REG_DIG_H2 = 0xE1
    REG_DIG_H3 = 0xE3
    REG_DIG_H4 = 0xE4
    REG_DIG_H5 = 0xE5
    REG_DIG_H6 = 0xE7
    #connection
    __bus = None
    #chip ID
    __chipID = 0
    #calibration values for temperature
    __dig_T = {
        1: 0.0,
        2: 0.0,
        3: 0.0
    }
    #calibration values for pressure
    __dig_P = {
        1: 0.0,
        2: 0.0,
        3: 0.0,
        4: 0.0,
        5: 0.0,
        6: 0.0,
        7: 0.0,
        8: 0.0,
        9: 0.0
    }
    #calibration values for humidity
    __dig_H = {
        1: 0.0,
        2: 0.0,
        3: 0.0,
        4: 0.0,
        5: 0.0,
        6: 0.0
    }
    #raw data
    __raw_data = {
        'pressure': 0.0,
        'temperature': 0.0,
        'humidity':0.0,
        't_fine': 0
    }
    #compensated_data
    data = {
        'pressure_Pa': 0.0,
        'temperature_deg_C': 0.0,
        'humidity_RH':0.0
    }

    def __init__(self):
        self.__bus = smbus.SMBus(1)
        self.__chipID = self.__bus.read_byte_data(self.BME280_ADDRESS, self.REG_ID)

        self.__dig_T[1] = self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_T1) & 0xFFFF
        self.__dig_T[2] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_T2) & 0xFFFF)
        self.__dig_T[3] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_T3) & 0xFFFF)

        self.__dig_P[1] = self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_P1) & 0xFFFF
        self.__dig_P[2] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_P2) & 0xFFFF)
        self.__dig_P[3] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_P3) & 0xFFFF)
        self.__dig_P[4] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_P4) & 0xFFFF)
        self.__dig_P[5] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_P5) & 0xFFFF)
        self.__dig_P[6] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_P6) & 0xFFFF)
        self.__dig_P[7] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_P7) & 0xFFFF)
        self.__dig_P[8] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_P8) & 0xFFFF)
        self.__dig_P[9] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_P9) & 0xFFFF)

        self.__dig_H[1] = self.__bus.read_byte_data(self.BME280_ADDRESS, self.REG_DIG_H1) & 0xFF
        self.__dig_H[2] = (lambda x: (x - 65536) if x > 32767 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_H2) & 0xFFFF)
        self.__dig_H[3] = self.__bus.read_byte_data(self.BME280_ADDRESS, self.REG_DIG_H3) & 0xFF
        h4 = (lambda x: (x - 256) if x > 127 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_H4) & 0xFF)
        h4 = (h4 << 4)
        self.__dig_H[4] = h4 | (self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_H5) & 0x0F)
        h5 = (lambda x: (x - 256) if x > 127 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_H6) & 0xFF)
        h5 = (h5 << 4)
        self.__dig_H[5] = h5 | ((self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_H5) >> 4) & 0x0F)
        self.__dig_H[6] = (lambda x: (x - 256) if x > 127 else x)(self.__bus.read_word_data(self.BME280_ADDRESS, self.REG_DIG_H6) & 0xFF)

    def __compensate_humidity(self):
        #need t_fine from temperature count
        if self.__raw_data['t_fine'] == 0:
            self.__compensate_temperature()
        var1 = float(self.__raw_data['t_fine']) - 76800.0
        var2 = (self.__dig_H[4] * 64.0 + (self.__dig_H[5] / 16384.0) * var1)
        var3 = self.__raw_data['humidity'] - var2
        var4 = self.__dig_H[2] / 65536.0
        var5 = (1.0 + (self.__dig_H[3] / 67108864.0) * var1)
        var6 = (1.0 + (self.__dig_H[6] / 67108864.0) * var1 * var5)
        var6 = (var3 * var4 * (var5 * var6))
        self.data['humidity_RH'] = var6 * (1.0 - self.__dig_H[1] * var6 / 524288.0)

    def __compensate_pressure(self):
        #need t_fine from temperature count
        if self.__raw_data['t_fine'] == 0:
            self.__compensate_temperature()
        var1 = (float(self.__raw_data['t_fine']) / 2.0) - 64000.0
        var2 = var1 * var1 * self.__dig_P[6] / 32768.0
        var2 = var2 + var1 * self.__dig_P[5] / 2.0
        var2 = (var2 / 4.0) + (self.__dig_P[4] * 65536.0)
        var3 = self.__dig_P[2] *var1 * var1 / 524288.0
        var1 = (var3 + self.__dig_P[2] *var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.__dig_P[1]
        self.data['pressure_Pa'] = 1048576.0 - self.__raw_data['pressure']
        self.data['pressure_Pa'] = (self.data['pressure_Pa'] - (var2 / 4096.0)) * 6250.0 / var1
        var1 = self.__dig_P[9] * self.data['pressure_Pa'] * self.data['pressure_Pa'] / 2147483648.0
        var2 = self.data['pressure_Pa'] * self.__dig_P[8] / 32768.0
        self.data['pressure_Pa'] = self.data['pressure_Pa'] + (var1 + var2 + self.__dig_P[7]) / 16.0

    def __compensate_temperature(self):
        #for float
        if self.__raw_data['t_fine'] != 0:
            #probably temperature compensation was calculated already
            return
        var1 = ((self.__raw_data['temperature'] / 16384.0) - (self.__dig_T[1] / 1024.0)) * self.__dig_T[2]
        var2 = (((self.__raw_data['temperature'] / 131072.0) - (self.__dig_T[1] / 8192.0)) * ((self.__raw_data['temperature'] / 131072.0) - (self.__dig_T[1] / 8192.0))) * self.__dig_T[3]
        self.__raw_data['t_fine'] = int(var1 + var2)
        self.data['temperature_deg_C'] = (self.__raw_data['t_fine'] / 5120.0)

    def __settings(self):
        OSRS_T = 0x05 		# temperature oversampling x16
        OSRS_P = 0x05		# pressure oversampling x16
        OSRS_H = 0x05       # humudity oversampling x16
        MODE = 0x01		    # mode forced
        ctrl_meas = ((OSRS_T << 5) | (OSRS_P << 2) | (MODE << 0))
        ctrl_hum = (OSRS_H << 0)
        self.__bus.write_byte_data(self.BME280_ADDRESS, self.REG_CTRL_MEAS, ctrl_meas)
        self.__bus.write_byte_data(self.BME280_ADDRESS, self.REG_CTRL_HUM, ctrl_hum)

    def __getMeasuringStatus(self):
        return ((self.__bus.read_byte_data(self.BME280_ADDRESS, self.REG_ID_STATUS)  & 0x08) >> 3)

    def __getImUpdateStatus(self):
        return (self.__bus.read_byte_data(self.BME280_ADDRESS, self.REG_ID_STATUS) & 0x01)

    def __getRawData(self):
        data = self.__bus.read_i2c_block_data(self.BME280_ADDRESS, self.REG_START_DATA, 8)
        self.__raw_data['pressure'] = ((data[0] << 12) | (data[1] << 4) | (data[2] >> 4))
        self.__raw_data['temperature'] = ((data[3] << 12) | (data[4] << 4) | (data[5] >> 4))
        self.__raw_data['humidity'] = ((data[6] << 8) | (data[7] << 0))

    def getData(self):
        self.__settings()
        count = 0
        while self.__getMeasuringStatus() == 1:
            count = count + 1
            time.sleep(0.5)
            if count == 10:
                return
        self.__getRawData()
        self.__compensate_temperature()
        self.__compensate_humidity()
        self.__compensate_pressure()
        return self.data

if __name__ == "__main__":
    data = BME280()
    result = data.getData()
    print(result)