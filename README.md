<h1 align="center">
  Beacon (API)
</h1>

> This is a fast (< 200ms) and basic API for tracking development of the new coronavirus (COVID-19, SARS-CoV-2). It's written in python using 🍼 Flask. Supports multiple sources!
**Live global stats (provided by [fight-covid19/bagdes](https://github.com/fight-covid19/bagdes)) from this API:**

![Covid-19 Confirmed](https://covid19-badges.herokuapp.com/confirmed/latest)
![Covid-19 Recovered](https://covid19-badges.herokuapp.com/recovered/latest)
![Covid-19 Deaths](https://covid19-badges.herokuapp.com/deaths/latest)

## Endpoints

All requests must be made to the base url: ``https://beacon-api.herokuapp.com/v2/`` (e.g: https://beacon-api.herokuapp.com/v2/locations). You can try them out in your browser to further inspect responses.

### Picking data source

We provide multiple data-sources you can pick from, simply add the query parameter ``?source=your_source_of_choice`` to your requests. JHU will be used as a default if you don't provide one.

#### Available sources:

* **jhu** - https://github.com/CSSEGISandData/COVID-19 - Data repository operated by the Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE).

* **... more to come later**.

### Getting latest amount of total confirmed cases, deaths, and recoveries.
```http
GET /v2/latest
```
```json
{
  "latest": {
    "confirmed": 197146,
    "deaths": 7905,
    "recovered": 80840
  }
}
```

### Getting all locations.
```http
GET /v2/locations
```
```json
{
  "latest": {
    "confirmed": 272166,
    "deaths": 11299,
    "recovered": 87256
  },
  "locations": [
    {
      "id": 0,
      "country": "Thailand",
      "country_code": "TH",
      "province": "",
      "last_updated": "2020-03-21T06:59:11.315422Z",
      "coordinates": {
        "latitude": "15",
        "longitude": "101"
      },
      "latest": {
        "confirmed": 177,
        "deaths": 1,
        "recovered": 41
      }
    },
    {
      "id": 39,
      "country": "Norway",
      "country_code": "NO",
      "province": "",
      "last_updated": "2020-03-21T06:59:11.315422Z",
      "coordinates": {
        "latitude": "60.472",
        "longitude": "8.4689"
      },
      "latest": {
        "confirmed": 1463,
        "deaths": 3,
        "recovered": 1
      }
    }
  ]
}
```

Additionally, you can also filter by any attribute, including province and country ([alpha-2 country_code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)).
```http
GET /v2/locations?country_code=US
```

Include timelines.
```http
GET /v2/locations?timelines=1
```

### Getting a specific location (includes timelines by default).
```http
GET /v2/locations/:id
```
```json
{
  "location": {
    "id": 39,
    "country": "Norway",
    "country_code": "NO",
    "province": "",
    "last_updated": "2020-03-21T06:59:11.315422Z",
    "coordinates": { },
    "latest": { },
    "timelines": {
      "confirmed": {
        "latest": 1463,
        "timeline": {
          "2020-03-16T00:00:00Z": 1333,
          "2020-03-17T00:00:00Z": 1463
        }
      },
      "deaths": { },
      "recovered": { }
    }
  }
}
```

Exclude timelines.
```http
GET /v2/locations?timelines=0
```

### Getting US per county information.
```http
GET /v2/locations?source=csbs
```
```json
{
  "latest": {
    "confirmed": 7596,
    "deaths": 43,
    "recovered": 0
  },
  "locations": [
    {
      "id": 0,
      "country": "US",
      "country_code": "US",
      "province": "New York",
      "state": "New York",
      "county": "New York",
      "last_updated": "2020-03-21T14:00:00Z",
      "coordinates": {
        "latitude": 40.71455,
        "longitude": -74.00714
      },
      "latest": {
        "confirmed": 6211,
        "deaths": 43,
        "recovered": 0
      }
    },
    {
      "id": 1,
      "country": "US",
      "country_code": "US",
      "province": "New York",
      "state": "New York",
      "county": "Westchester",
      "last_updated": "2020-03-21T14:00:00Z",
      "coordinates": {
        "latitude": 41.16319759,
        "longitude": -73.7560629
      },
      "latest": {
        "confirmed": 1385,
        "deaths": 0,
        "recovered": 0
      },
    }
  ]
}
```


## Prerequisites

You will need the following things properly installed on your computer.

* [Python 3](https://www.python.org/downloads/) (with pip)
* [Flask](https://pypi.org/project/Flask/)
* [pipenv](https://pypi.org/project/pipenv/)

## Installation

* `git clone https://github.com/mustaphee/beacon.git`
* `cd beacon`
* `pipenv shell`
* `pipenv install`

## Running / Development

* `flask run`
* Visit your app at [http://localhost:5000](http://localhost:5000).

### Running Tests

* `make test`

### Linting

* `make lint`

## License

See [LICENSE.md](LICENSE.md) for the license. Please link to this repo somewhere in your project :).
