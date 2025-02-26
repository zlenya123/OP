from datetime import datetime

class MeterReading:
    def __init__(self, resource_type: str, date: datetime, value: float):
        self.resource_type = resource_type
        self.date = date
        self.value = value

class WaterMeterReading(MeterReading):
    def __init__(self, resource_type: str, date: datetime, value: float, flow_rate: float, total_volume: float):
        super().__init__(resource_type, date, value)
        self.flow_rate = flow_rate
        self.total_volume = total_volume

    @staticmethod
    def parse_line(line: str):
        parts = line.strip().split(';')
        resource_type = parts[0]
        date = datetime.strptime(parts[1], '%d.%m.%Y')
        value = float(parts[2].replace(',', '.'))
        flow_rate = float(parts[3].replace(',', '.'))
        total_volume = float(parts[4].replace(',', '.'))
        return WaterMeterReading(resource_type, date, value, flow_rate, total_volume)

    def __str__(self):
        return (f"Тип: {self.resource_type}, Дата: {self.date.strftime('%d.%m.%Y')}, "
                f"Значение с последнего замера: {self.value}, Текущий расход: {self.flow_rate}, Общее потребление воды: {self.total_volume}")

class ElectricityMeterReading(MeterReading):
    def __init__(self, resource_type: str, date: datetime, value: float, power: float, total_energy: float, frequency: float):
        super().__init__(resource_type, date, value)
        self.power = power
        self.total_energy = total_energy
        self.frequency = frequency

    @staticmethod
    def parse_line(line: str):
        parts = line.strip().split(';')
        resource_type = parts[0]
        date = datetime.strptime(parts[1], '%d.%m.%Y')
        value = float(parts[2].replace(',', '.'))
        power = float(parts[3].replace(',', '.'))
        total_energy = float(parts[4].replace(',', '.'))
        frequency = float(parts[5].replace(',', '.'))
        return ElectricityMeterReading(resource_type, date, value, power, total_energy, frequency)

    def __str__(self):
        return (f"Тип: {self.resource_type}, Дата: {self.date.strftime('%d.%m.%Y')}, "
                f"Значение с последнего замера: {self.value}, Текущая мощность: {self.power}, Общее потребление энергии: {self.total_energy}, Частота: {self.frequency}")

def parse_meter_readings(file_path: str):
    water_readings = []
    electricity_readings = []

    with open(file_path, 'r', encoding='cp1251') as file:
        for line in file:
            if line.startswith('Вода'):
                water_readings.append(WaterMeterReading.parse_line(line))
            elif line.startswith('Электричество'):
                electricity_readings.append(ElectricityMeterReading.parse_line(line))
    return water_readings, electricity_readings

if __name__ == "__main__":
    water_readings, electricity_readings = parse_meter_readings("text.csv")

    for reading in water_readings:
        print(reading)

    for reading in electricity_readings:
        print(reading)
