import csv
import timeit
import json
from cliff.api import Cliff

cliffClient = Cliff('http://localhost:8080')

# Row Data Structure
# Record ID, Type, LocationType, LocationName, Lat, Lon, CountryCode, Confidence/Score (major references have a score, minor have a confidence rating)
results = []

# Timer for estimating total run time
startTime = timeit.default_timer()

with open('input.csv') as csv_file:
    csvReader = csv.reader(csv_file, delimiter=',', quotechar='"')

    idIndex = 1
    titleIndex = 2
    abstractIndex = 3

    lineCount = 0
    locationCount = 0
    uniqueTaggedTexts = 0

    rows = list(csvReader)
    totalLines = len(rows)

    for row in rows:

        if lineCount == 0:
            lineCount += 1
            continue  # header row

        if lineCount % 1000 == 0:
            percentage = lineCount/totalLines
            timeDiff = timeit.default_timer() - startTime
            timeRemaining = timeDiff / percentage
            print(f'{timeDiff:.0f}s {percentage*100:.2f}% - processing {lineCount} of {totalLines} lines... ~{timeRemaining:.0f}s remaining')

        lineCount += 1
        locations = cliffClient.parse_text(row[titleIndex] + ' ' + row[abstractIndex])

        mentions = locations['results']['places']['mentions']
        focuses = locations['results']['places']['focus']

        if len(focuses) > 0:
            cities = focuses['cities']
            countries = focuses['countries']
            states = focuses['states']

            for city in cities:
                results.append([
                    row[idIndex], row[titleIndex], "major", "city", city['name'], city['lat'], city['lon'],
                    city['countryCode'], city['score']
                ])

            for state in states:
                results.append([
                    row[idIndex], row[titleIndex], "major", "state", state['name'], state['lat'], state['lon'],
                    state['countryCode'], state['score']
                ])

            for country in countries:
                results.append([
                    row[idIndex], row[titleIndex], "major", "country", country['name'], country['lat'], country['lon'],
                    country['countryCode'], country['score']
                ])

        if len(mentions) > 0:
            locationCount += len(mentions)
            uniqueTaggedTexts += 1

            for mention in mentions:
                results.append([
                    row[idIndex], row[titleIndex], "minor", mention['featureCode'], mention['name'], mention['lat'],
                    mention['lon'], mention['countryCode'], mention['confidence']
                ])

    print(f'Processed {lineCount} lines, found {locationCount} location mentions in {uniqueTaggedTexts} tagged texts')

#  write the results to CSV
with open('output.csv', 'w', newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for row in results:
        writer.writerow(row)
