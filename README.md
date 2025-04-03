# How to get iPhone health data xml file into csv format

1. iPhone health app > profile > "Export All Health Data" (bottom of page)
    - ***export.zip** saved to device after several minutes*
2. Airdrop **export.zip** to computer
3. expand to folder **apple_health_export**
4. Set up this folder structure and move **export.xml** into place:
```
    health_data
    |   main.py
    \---data
          export.xml
```
5. Run main.py from cli @health_data and csv will be generated in data folder<sup>1</sup>

<sup>*1*</sup> *Alternatively, use any of the following code snippets in a python shell*

## Easy Method: XML -> Pandas DF -> CSV

total time (t) ≈ 60s / 1GB (2.3 GHz intel i9)

### Requirements

```
import xml.etree.ElementTree as ET
import pandas as pd
```

### Parse XML

t ≈ 30s / 1GB

```
with open('data/export.xml') as f:
    data = ET.parse(f)
    root = data.getroot()
```

### Pandas write to CSV for all data

- Larger files will take longer, but Pandas makes column sorting easier:
- First two rows are currently set as the export info and personal biometric data, you can remove the [2:] slice if you want to keep them in.

t ≈ 45s / 1GB

```
health_df = pd.DataFrame([{**{'tag': child.tag}, **child.attrib} for child in root[2:]])
health_df.to_csv('data/health_data.csv', index=False)
```

#### CSV just for records

t ≈ 30s / 1GB

```
records_df = pd.DataFrame([{**{'tag': child.tag}, **child.attrib} for child in root[2:] if child.tag == 'Record'])
records_df = records_df.drop(columns=['tag'])
records_df.to_csv('data/records.csv', index=False)
```

#### CSV just for workout data

t < 5s / 1GB

```
workout_df = pd.DataFrame([{**{'tag': child.tag}, **child.attrib} for child in root[2:] if child.tag == 'Workout'])
workout_df = workout_df.drop(columns=['tag'])
workout_df.to_csv('data/workouts.csv', index=False)
```

#### CSV just for activity data

t < 5s / 1GB

```
activity_df = pd.DataFrame([{**{'tag': child.tag}, **child.attrib} for child in root[2:] if child.tag == 'ActivitySummary'])
activity_df = activity_df.drop(columns=['tag'])
activity_df.to_csv('data/activity.csv', index=False)
```

## Manual: XML -> DictWriter CSV (faster computation time)

### Requirements

```
import xml.etree.ElementTree as ET
import csv
```

**I Highly Recommend you select specific records you want to keep in order to minimize processing time**

- Record names can be found [here for quantities](https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier) and [here for categories](https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier).
- They follow the naming convention: "HKQuantityTypeIdentifierActiveEnergyBurned"

### DictWriter to CSV for selected data

total time < 30s / 1GB (2.3 GHz intel i9)

```
columns = ['type', 'startDate', 'endDate', 'value', 'unit']

selected_types = {
    'HKCategoryTypeIdentifierSleepAnalysis',
    'HKQuantityTypeIdentifierActiveEnergyBurned',
    'HKQuantityTypeIdentifierBasalEnergyBurned',
    'HKQuantityTypeIdentifierDistanceCycling',
    'HKQuantityTypeIdentifierDistanceSwimming',
    'HKQuantityTypeIdentifierDistanceWalkingRunning',
    'HKQuantityTypeIdentifierRestingHeartRate',
    'HKQuantityTypeIdentifierWalkingHeartRateAverage'
    }

with open('data/export.xml', 'r') as xmlf, open('data/health_data.csv', 'w') as csvf:
    writer = csv.DictWriter(csvf, fieldnames=columns, extrasaction='ignore')

    for event, elem in ET.iterparse(xmlf, events=('start',)):
        if elem.tag == 'Record':
            rec_dict = elem.attrib
            if rec_dict.get('type') in selected_types:
                writer.writerow(rec_dict)
            elem.clear()
```
