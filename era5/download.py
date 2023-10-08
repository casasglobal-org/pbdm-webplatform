

FILE_KEYS = ['Temperature-Air-2m-Min-24h','Temperature-Air-2m-Max-24h', 'Solar-Radiation-Flux','Precipitation-Flux','Relative-Humidity-2m-06h', 'Relative-Humidity-2m-09h','Relative-Humidity-2m-12h','Relative-Humidity-2m-15h','Relative-Humidity-2m-18h','Wind-Speed-10m-Mean']

import cdsapi

c = cdsapi.Client()

for year in range(1979, 2024):
    for month in range(1,12+1):
        print('{}'.format(month).zfill(2))
        c.retrieve(
            'sis-agrometeorological-indicators',
            {
                'format': 'zip',
                'variable': '2m_relative_humidity',
                #'statistic': '24_hour_maximum',
                'year': '{}'.format(year),
                'month': '{}'.format(month).zfill(2),
                'version':'1_1',
                'day': [
                    '01', '02', '03',
                    '04', '05', '06',
                    '07', '08', '09',
                    '10', '11', '12',
                    '13', '14', '15',
                    '16', '17', '18',
                    '19', '20', '21',
                    '22', '23', '24',
                    '25', '26', '27',
                    '28', '29', '30',
                    '31',
                ],
                'time': '06_00',
            },
            '{}_{}_{}.zip'.format("./agera5_rel_06/Relative-Humidity-2m-06h", year, month))