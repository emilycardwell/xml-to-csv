columns = ['type', 'startDate', 'endDate', 'value', 'unit']


def get_method():
    method = 0
    while method not in [1, 2, 3]:
        method = int(input('Easy (1), Faster (2), or Manual (3) Method?  '))
    return method


def pandas_convert():
    import xml.etree.ElementTree as ET
    import pandas as pd

    r_select = 0
    while r_select not in range(1,4):
        r_select = int(input('Which data do you want to save: all (1), records (2), \
    workouts (3), activity (3) [2 recommended]  '))

    print('parsing xml...')
    with open('data/export.xml') as f:
        data = ET.parse(f)
        root = data.getroot()

    print('writing to csv...')
    if r_select == 1:
        health_df = pd.DataFrame([{**{'tag': child.tag}, **child.attrib} for child in root])
        health_df.to_csv('data/health_data.csv', index=False)
        print('done!')
    if r_select == 2:
        r_tag = 'Record'
    elif r_select == 3:
        r_tag = 'Workout'
    elif r_select == 4:
        r_tag = 'ActivitySummary'

    selected_df = pd.DataFrame([{**{'tag': child.tag}, **child.attrib} for child in root if child.tag == r_tag])
    selected_df = selected_df.drop(columns=['tag'])
    selected_df.to_csv('data/health_data.csv', index=False)
    print('done!')


def faster_convert():
    import xml.etree.ElementTree as ET
    import csv

    columns = ['type', 'startDate', 'endDate', 'value', 'unit']
    default_types = {
            'HKCategoryTypeIdentifierSleepAnalysis',
            'HKQuantityTypeIdentifierActiveEnergyBurned',
            'HKQuantityTypeIdentifierBasalEnergyBurned',
            'HKQuantityTypeIdentifierDistanceCycling',
            'HKQuantityTypeIdentifierDistanceSwimming',
            'HKQuantityTypeIdentifierDistanceWalkingRunning',
            'HKQuantityTypeIdentifierRestingHeartRate',
            'HKQuantityTypeIdentifierWalkingHeartRateAverage'
            }

    r_select = 0
    while r_select not in [1, 2]:
        r_select = int(input('Do you want all records (1) or default records (2)?' ))

    print('converting...')
    with open('data/test_data.xml', 'r') as xmlf, open('data/test_out.csv', 'w') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=columns, extrasaction='ignore')

        if r_select == 1:
            for _, elem in ET.iterparse(xmlf, events=('start',)):
                if elem.tag == 'Record':
                    writer.writerow(elem.attrib)
                elem.clear()

        elif r_select == 2:
            for _, elem in ET.iterparse(xmlf, events=('start',)):
                rec_dict = elem.attrib
                if rec_dict.get('type') in default_types:
                    writer.writerow(rec_dict)
                elem.clear()

        print('done!')

def manual_convert():

    import xml.etree.ElementTree as ET
    import csv

    with open('data/export.xml', 'r') as xmlf, open('data/health_data.csv', 'w') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=columns, extrasaction='ignore')
        prev_tags = set([])

        for _, elem in ET.iterparse(xmlf, events=('start',)):
            if elem.tag == 'Record':
                rec_dict = elem.attrib
                rec_type = rec_dict.get('type')
                if rec_type in prev_tags:
                    writer.writerow(rec_dict)
                else:
                    decision = ''
                    while decision not in ['y', 'n']:
                        decision = input(f"Record type: {rec_type} (y/n)    ")
                    if decision == 'y':
                        writer.writerow(rec_dict)
                    prev_tags.add(rec_type)
            elem.clear()

if __name__ == "__main__":
    method = get_method()
    if method == 1:
        pandas_convert()
    elif method == 2:
        faster_convert()
    elif method == 3:
        manual_convert()
