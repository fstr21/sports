Available resources
See all available endpoints underneath. See Filtering table at the very bottom to see how to pass filters in an adequate format. You can also get an overview by running all available calls through Postman by importing this collection after download.
(Sub)Resource	Action	URI	Filters	Sample
Area	List one particular area.	/v4/areas/{id}	-	Open
Areas	List all available areas.	/v4/areas/	-	Open
Competition	List one particular competition.	/v4/competitions/PL	-	Open
Competition	List all available competitions.	/v4/competitions/	areas={AREAS}
Open
Competition / Standings	Show Standings for a particular competition.	/v4/competitions/{id}/standings	matchday={MATCHDAY}
season={YEAR}
date={DATE}	Open
Competition / Match	List all matches for a particular competition.	/v4/competitions/{id}/matches	dateFrom={DATE}
dateTo={DATE}
stage={STAGE}
status={STATUS}
matchday={MATCHDAY}
group={GROUP}
season={YEAR}	Open
Competition / Teams	List all teams for a particular competition.	/v4/competitions/{id}/teams	season={YEAR}	Open
Competition / (Top)Scorers	List top scorers for a particular competition.	/v4/competitions/{id}/scorers	limit={LIMIT}
season={YEAR}	Open
Team	Show one particular team.	/v4/teams/{id}	-	Open
Team	List teams.	/v4/teams/	limit={LIMIT}
offset={OFFSET}	Open
Match	Show all matches for a particular team.	/v4/teams/{id}/matches/	dateFrom={DATE}
dateTo={DATE}
season={YEAR}
competitions={competitionIds}
status={STATUS}
venue={VENUE}
limit={LIMIT}	Open
Person	List one particular person.	/v4/persons/{id}	-	Open
Person / Match	Show all matches for a particular person.	/v4/persons/{id}/matches	dateFrom={DATE}
dateTo={DATE}
status={STATUS}
competitions={competitionIds}
limit={LIMIT}
offset={OFFSET}	Open
Match	Show one particular match.	/v4/matches/{id}		Open
Match	List matches across (a set of) competitions.	/v4/matches	competitions={competitionIds}
ids={matchIds}
dateFrom={DATE}
dateTo={DATE}
status={STATUS}	Open
Match / Head2Head	List previous encounters for the teams of a match.	/v4/matches/{id}/head2head	limit={LIMIT}
dateFrom={DATE}
dateTo={DATE}
competitions={competitionIds}	Open

Filters and their data types
Filter	Type	Description / Possible values
id	Integer /[0-9]+/	The id of a resource.
ids	Integer /[0-9]+/	Comma separated list of ids.
matchday	Integer /[1-4]+[0-9]*/	
season	String /yyyy/	The starting year of a season e.g. 2017 or 2016
status	Enum /[A-Z]+/	The status of a match. [SCHEDULED | LIVE | IN_PLAY | PAUSED | FINISHED | POSTPONED | SUSPENDED | CANCELLED]
venue	Enum /[A-Z]+/	Defines the venue (type). [HOME | AWAY]
date / dateFrom / dateTo	String /yyyy-MM-dd/	e.g. 2018-06-22
stage	Enum /[A-Z]+/	FINAL | THIRD_PLACE | SEMI_FINALS | QUARTER_FINALS | LAST_16 | LAST_32 | LAST_64 | ROUND_4 | ROUND_3 | ROUND_2 | ROUND_1 | GROUP_STAGE | PRELIMINARY_ROUND | QUALIFICATION | QUALIFICATION_ROUND_1 | QUALIFICATION_ROUND_2 | QUALIFICATION_ROUND_3 | PLAYOFF_ROUND_1 | PLAYOFF_ROUND_2 | PLAYOFFS | REGULAR_SEASON | CLAUSURA | APERTURA | CHAMPIONSHIP | RELEGATION | RELEGATION_ROUND
plan	String /[A-Z]+/	TIER_ONE | TIER_TWO | TIER_THREE | TIER_FOUR
competitions	String /\d+,\d+/	Comma separated list of competition ids.
areas	String /\d+,\d+/	Comma separated list of area ids.
group	String /[A-Z_]+/	Allows filtering for groupings in a competition.
limit	Integer /\d+/	Limits your result set to the given number. Defaults to 10.
offset	Integer /\d+/	Skip offset no. of records when using a limit to page the result list.
Example Requests
See todays' matches of your subscribed competitions:
https://api.football-data.org/v4/matches
Get all matches of the Champions League:
https://api.football-data.org/v4/competitions/CL/matches
See all upcoming matches for Real Madrid:
https://api.football-data.org/v4/teams/86/matches?status=SCHEDULED
Get all matches where Gigi Buffon was in the squad:
https://api.football-data.org/v4/persons/2019/matches?status=FINISHED
Check schedules for Premier League on matchday 11:
https://api.football-data.org/v4/competitions/PL/matches?matchday=11
Get the league table for Eredivisie:
https://api.football-data.org/v4/competitions/DED/standings
See best 10 scorers of Italy's top league (scorers subresource defaults to limit=10):
https://api.football-data.org/v4/competitions/SA/scorers





Python (3.8+)
Prerequisites
You should have a running environment for Python 3 ready set up. We will utilize the excellent requests library to fetch the data. Check your version and install the library like so:

(base) ~ % python --version
Python 3.8.8
(base) ~ % pip3 install requests
In case there is no Python installed yet, I’d advice to use Anaconda to do so.

Plain request
import requests
import json

uri = 'https://api.football-data.org/v4/matches'
headers = { 'X-Auth-Token': 'UR_TOKEN' }

response = requests.get(uri, headers=headers)
for match in response.json()['matches']:
  print match
  Lookup Tables
Quick access to information that you’ll love. Because I know it’s super convenient to find all possible values for a given something of an external system, below you can find all enum types used in my backend and exposed via API. I also provide aggregated lists of stuff you likely already came across in other parts of the documentation.

Enum-Types
Because I know it’s super convenient to find all possible values for a given something of an external system, below you can find all enum types used in my backend and exposed via API.

Table 1. Enum-Types
Resource	Attribute	Possible values
Competition

type

LEAGUE | LEAGUE_CUP | CUP | PLAYOFFS

Team

type

CLUB | NATIONAL

Match

status

SCHEDULED | TIMED | IN_PLAY | PAUSED | EXTRA_TIME | PENALTY_SHOOTOUT | FINISHED | SUSPENDED | POSTPONED | CANCELLED | AWARDED

Match

stage

FINAL | THIRD_PLACE | SEMI_FINALS | QUARTER_FINALS | LAST_16 | LAST_32 | LAST_64 | ROUND_4 | ROUND_3 | ROUND_2 | ROUND_1 | GROUP_STAGE | PRELIMINARY_ROUND | QUALIFICATION | QUALIFICATION_ROUND_1 | QUALIFICATION_ROUND_2 | QUALIFICATION_ROUND_3 | PLAYOFF_ROUND_1 | PLAYOFF_ROUND_2 | PLAYOFFS | REGULAR_SEASON | CLAUSURA | APERTURA | CHAMPIONSHIP | RELEGATION | RELEGATION_ROUND

Match

group

GROUP_A | GROUP_B | GROUP_C | GROUP_D | GROUP_E | GROUP_F | GROUP_G | GROUP_H | GROUP_I | GROUP_J | GROUP_K | GROUP_L

Penalty

type

MATCH | SHOOTOUT

Score

duration

REGULAR | EXTRA_TIME | PENALTY_SHOOTOUT

Card

type

YELLOW | YELLOW_RED | RED

Goal

type

REGULAR | OWN | PENALTY

Person with type REF

role

REFEREE | ASSISTANT_REFEREE_N1 | ASSISTANT_REFEREE_N2 | ASSISTANT_REFEREE_N3 | FOURTH_OFFICIAL | VIDEO_ASSISTANT_REFEREE_N1 | VIDEO_ASSISTANT_REFEREE_N2 | VIDEO_ASSISTANT_REFEREE_N3

Request Headers
Header-Name	Possible values	Description
X-Auth-Token

[a-z1-9]+

Your authentication token

X-Unfold-Lineups

[ true | false ]

Unfold lineups within the reponse or not

X-Unfold-Bookings

[ true | false ]

Unfold bookings within the reponse or not

X-Unfold-Subs

[ true | false ]

Unfold substitutions within the reponse or not

X-Unfold-Goals

[ true | false ]

Unfold goals within the reponse or not

Response Headers
Examine the underneath HTTP response headers to debug responses that do not look like you expected.

Header-Name	Example value	Description
X-API-Version

v4

indicates the version you are using

X-Authenticated-Client

Jimbo Jones

Shows the detected API-client or 'anonymous'

X-RequestCounter-Reset

23

Defines the seconds left to reset your request counter.

X-RequestsAvailable

21

Shows the remaining requests before being blocked.

Filters
Filter	Possible value(s)	Description
id

Integer /[0-9]+/

The (unique) id of a resource.

matchday

Integer /[1-4]*[0-9]*/

Drill down on a matchday; defaults to null

areas

comma separated string
/\d+,\d+/

Drill down on areas; defaults to null ⇒ all

season

String /\d\d\d\d/

Defaults to the starting year of the current season, given as 4 digit like '2022'

venue

HOME|AWAY

Define the venue of the matches to be returned.

competitions

comma separated string
/\d+,\d+/

A list of, comma separated competition-code(s) for drill down.

date

A date in format yyyy-MM-dd

Drill down on a given date

dateFrom

A date in format yyyy-MM-dd

Use in conjunction with dateTo

dateTo

A date in format yyyy-MM-dd

Drill down on a given date range

status

Enum, see above

Drill down on a (comma separated list of) status

lineup

STARTING | BENCH

Lets you define the starting type of a player

e

GOAL | ASSIST | SUB_IN | SUB_OUT

Lets you define an event

limit

Integer [1-500]

Limit the result set

offset

Integer [1-500]

Use an offset with a limit to traverse a huge list

League-Codes
I once added codes to all competitions so I did not need to remember the id any more. You’re welcome to make use of them as well, you can use them anywhere where you’d want to use the id.

Table 2. League-Codes used in the Competition resource
Competition Id	League-Code	Caption	Country/Continent
2006

QCAF

WC Qualification CAF

Africa

2024

ASL

Liga Profesional

Argentina

2147

QAFC

WC Qualification AFC

Asia

2008

AAL

A League

Australia

2022

APL

Playoffs 1/2

Austria

2012

ABL

Bundesliga

Austria

2032

BJPP

Playoffs

Belgium

2009

BJL

Jupiler Pro League

Belgium

2029

BSB

Campeonato Brasileiro Série B

Brazil

2013

BSA

Campeonato Brasileiro Série A

Brazil

2048

CPD

Primera División

Chile

2044

CSL

Chinese Super League

China PR

2045

CLP

Liga Postobón

Colombia

2047

PRVA

Prva Liga

Croatia

2141

DELP

Euro League - Playoff

Denmark

2050

DSU

Superliga

Denmark

2016

ELC

Championship

England

2021

PL

Premier League

England

2139

FLC

Football League Cup

England

2030

EL1

League One

England

2053

ENL

National League

England

2054

EL2

League Two

England

2055

FAC

FA Cup

England

2056

COM

FA Community Shield

England

2018

EC

European Championship

Europe

2146

EL

UEFA Europa League

Europe

2154

UCL

UEFA Conference League

Europe

2001

CL

UEFA Champions League

Europe

2157

ESC

Supercup

Europe

2007

QUFA

WC Qualification UEFA

Europe

2031

VEI

Veikkausliiga

Finland

2142

FL2

Ligue 2

France

2143

FPL

Playoffs 1/2

France

2015

FL1

Ligue 1

France

2129

REG

Regionalliga

Germany

2134

GSC

DFL Super Cup

Germany

2140

BL3

3. Bundesliga

Germany

2156

BLREL

Relegation

Germany

2002

BL1

Bundesliga

Germany

2004

BL2

2. Bundesliga

Germany

2011

DFB

DFB-Pokal

Germany

2132

GSL

Super League

Greece

2128

HNB

NB I

Hungary

2125

ILH

Ligat ha’Al

Israel

2019

SA

Serie A

Italy

2121

SB

Serie B

Italy

2122

CIT

Coppa Italia

Italy

2123

ISC

Serie C

Italy

2158

IPL

Playoffs 1/2

Italy

2119

JJL

J. League

Japan

2113

LMX

Liga MX

Mexico

2109

KNV

KNVB Beker

Netherlands

2003

DED

Eredivisie

Netherlands

2005

DJL

Eerste Divisie

Netherlands

2106

TIP

Tippeligaen

Norway

2103

QOFC

WC Qualification OFC

Oceania

2101

PPD

Primera División

Peru

2017

PPL

Primeira Liga

Portugal

2094

RL1

Liga I

Romania

2137

RFPL

RFPL

Russia

2084

SPL

Premier League

Scotland

2152

CLI

Copa Libertadores

South America

2080

CA

Copa America

South America

2082

QCBL

WC Qualification CONMEBOL

South America

2077

SD

Segunda División

Spain

2079

CDR

Copa del Rey

Spain

2014

PD

Primera Division

Spain

2073

ALL

Allsvenskan

Sweden

2072

SSL

Super League

Switzerland

2070

TSL

Süper Lig

Turkey

2064

UPL

Premier Liha

Ukraine

2145

MLS

MLS

United States

2148

SUCU

Supercopa Uruguaya

Uruguay

2153

OLY

Summer Olympics

World

2000

WC

FIFA World Cup

World

2155

QCCF

WC Qualification CONCACAF

World


Person
Overview
Ok, so let’s talk about persons. It’s the tiniest resource in some way as it’s mostly other resources that contain persons but whatsoever. A Person resource mostly reflects a football player (79,13% of all persons in my database are players), but there’s also referee’s or staff members that can be retrieved via the Person resource.

Most likely the matches subresource will be of more interest as you can filter matches on attributes of that very player.

But first things first, see the entire beauty of the Person resource below.

curl -XGET 'https://api.football-data.org/v4/persons/16275' -H "X-Auth-Token: UR_TOKEN"
{
    "id": 16275,
    "name": "Djibril Sow",
    "firstName": "Djibril",
    "lastName": "Sow",
    "dateOfBirth": "1997-02-06",
    "nationality": "Switzerland",
    "position": "Central Midfield",
    "shirtNumber": 8,
    "lastUpdated": "2022-03-17T16:47:43Z",
    "currentTeam": {
        "area": {
            "id": 2088,
            "name": "Germany",
            "code": "DEU",
            "flag": "https://crests.football-data.org/759.svg"
        },
        "id": 19,
        "name": "Eintracht Frankfurt",
        "shortName": "Frankfurt",
        "tla": "SGE",
        "crest": "https://crests.football-data.org/19.svg",
        "address": "Mörfelder Landstraße 362 Frankfurt am Main 60528",
        "website": "http://www.eintracht.de",
        "founded": 1899,
        "clubColors": "Red / Black",
        "venue": "Deutsche Bank Park",
        "runningCompetitions": [
            {
                "id": 2002,
                "name": "Bundesliga",
                "code": "BL1",
                "type": "LEAGUE",
                "emblem": "https://crests.football-data.org/BL1.png"
            },
            {
                "id": 2011,
                "name": "DFB-Pokal",
                "code": "DFB",
                "type": "CUP",
                "emblem": "https://crests.football-data.org/DFB_CUP.png"
            },
            {
                "id": 2146,
                "name": "UEFA Europa League",
                "code": "EL",
                "type": "CUP",
                "emblem": "https://crests.football-data.org/EL.png"
            }
        ],
        "contract": {
            "start": "2019-07",
            "until": "2024-06"
        }
    }
}
Looks reasonable. You now know the players name and some more personal details except for his haircut. You can see what competitions his team participates this season, and how long he’s planning to play for that club.

You want to see all the matches he played this season? I was expecting that.

Matches
You use the Matches Subresource to fetch a list of matches that are pre-filtered by that very person.

{
    "filters": {
        "limit": 15,
        "offset": 0,
        "competitions": "BL1,DFB,EL",
        "permission": "TIER_THREE"
    },
    "resultSet": {
        "count": 15,
        "competitions": "BL1,EL",
        "first": "2022-02-19",
        "last": "2022-05-14"
    },
    "aggregations": {
        "matchesOnPitch": 15,
        "startingXI": 12,
        "minutesPlayed": 1086,
        "goals": 0,
        "ownGoals": 0,
        "assists": 1,
        "penalties": 0,
        "subbedOut": 3,
        "subbedIn": 0,
        "yellowCards": 3,
        "yellowRedCards": 0,
        "redCards": 0
    },
    "person": {
        "id": 16275,
        "name": "Djibril Sow",
        "firstName": "Djibril",
        "lastName": "Sow",
        "dateOfBirth": "1997-02-06",
        "nationality": "Switzerland",
        "position": "Midfield",
        "shirtNumber": null,
        "lastUpdated": "2022-03-17T16:47:43Z"
    },
    "matches": [ ... ]
}
You see the applied filters on the very top: by default this is a match limit of 15. The competitions and permission attributes are mostly for debugging purposes. It’s followed by the resultSet node which gives information on the boundaries of the match list at the very bottom and some basic aggregation data. Last but not least you find an aggregate node that holds aggregated information of the matches returned. Last but not least the list of match items follows.

Let’s play around a bit with the interface.

curl -XGET 'https://api.football-data.org/v4/persons/16275/matches' -H 'X-Auth-Token: UR_TOKEN'
No query parameters. The resource responds with this seasons' matches of that very player in descending order. Click here to see them with some layers of plumbing and transformation code in between.

Okay some more. Give me…​

…​the last 10 matches he failed and was pulled out to bench:

curl -XGET 'https://api.football-data.org/v4/persons/16275/matches?e=SUB_OUT&limit=10' -H 'X-Auth-Token: UR_TOKEN'
…​the last 3 matches where he shined and scored:

curl -XGET 'https://api.football-data.org/v4/persons/16275/matches?e=GOAL&limit=5' -H 'X-Auth-Token: UR_TOKEN'
Okay I hope you got it. See all possible query parameters for the Subresource within the table below:

Filters
Attribute name	Possible values
lineup

STARTING | BENCH

e

GOAL | ASSIST | SUB_IN | SUB_OUT

dateFrom

/?dateFrom=2022-01-01

dateTo

/?dateTo=2022-01-10

competitions

/?competitions=PL,FAC

limit

Integer [1-100]

offset

Integer [1-100]


Team
Overview
You use the Team resource to access base information about that very team, it’s squad, the running competitions it is participating this season or you might be interested in it’s latest matches.

Enough said, see the entire beauty of the Team resource resource below.

curl -XGET 'https://api.football-data.org/v4/teams/90' -H "X-Auth-Token: UR_TOKEN"
{
    "area": {
        "id": 2224,
        "name": "Spain",
        "code": "ESP",
        "flag": "https://crests.football-data.org/760.svg"
    },
    "id": 90,
    "name": "Real Betis Balompié",
    "shortName": "Real Betis",
    "tla": "BET",
    "crest": "https://crests.football-data.org/90.png",
    "address": "Avenida de Heliópolis, s/n Sevilla 41012",
    "website": "http://www.realbetisbalompie.es",
    "founded": 1907,
    "clubColors": "Green / White",
    "venue": "Estadio Benito Villamarín",
    "runningCompetitions": [
        {
            "id": 2014,
            "name": "Primera Division",
            "code": "PD",
            "type": "LEAGUE",
            "emblem": "https://crests.football-data.org/PD.png"
        },
        {
            "id": 2146,
            "name": "UEFA Europa League",
            "code": "EL",
            "type": "CUP",
            "emblem": "https://crests.football-data.org/EL.png"
        },
        {
            "id": 2079,
            "name": "Copa del Rey",
            "code": "CDR",
            "type": "CUP",
            "emblem": null
        }
    ],
    "coach": {
        "id": 11630,
        "firstName": "Manuel",
        "lastName": "Pellegrini",
        "name": "Manuel Pellegrini",
        "dateOfBirth": "1953-09-16",
        "nationality": "Chile",
        "contract": {
            "start": "2020-08",
            "until": "2023-06"
        }
    },
    "marketValue": 225100000,
    "squad": [
        {
            "id": 7821,
            "firstName": "",
            "lastName": "Joel",
            "name": "Joel Robles",
            "position": "Goalkeeper",
            "dateOfBirth": "1990-06-17",
            "nationality": "Spain",
            "shirtNumber": 1,
            "marketValue": 2000000,
            "contract": {
                "start": "2018-07",
                "until": "2022-06"
            }
        },
        {
            "id": 7879,
            "firstName": "Claudio",
            "lastName": "Bravo",
            "name": "Claudio Bravo",
            "position": "Goalkeeper",
            "dateOfBirth": "1983-04-13",
            "nationality": "Chile",
            "shirtNumber": 25,
            "marketValue": 900000,
            "contract": {
                "start": "2020-08",
                "until": "2023-06"
            }
        },
        {
            "id": 32014,
            "firstName": "",
            "lastName": "Rui Silva",
            "name": "Rui Silva",
            "position": "Goalkeeper",
            "dateOfBirth": "1994-02-07",
            "nationality": "Portugal",
            "shirtNumber": 13,
            "marketValue": 14000000,
            "contract": {
                "start": "2021-07",
                "until": "2026-06"
            }
        },
        {
            "id": 33035,
            "firstName": "",
            "lastName": "Dani Rebollo",
            "name": "Dani Rebollo",
            "position": "Goalkeeper",
            "dateOfBirth": "1999-12-10",
            "nationality": "Spain",
            "shirtNumber": 30,
            "marketValue": null,
            "contract": {
                "start": "2021-09",
                "until": "2022-06"
            }
        },
        {
            "id": 16,
            "firstName": "Andrés",
            "lastName": "Guardado",
            "name": "Andrés Guardado",
            "position": "Defence",
            "dateOfBirth": "1986-09-28",
            "nationality": "Mexico",
            "shirtNumber": 18,
            "marketValue": 1500000,
            "contract": {
                "start": "2017-07",
                "until": "2023-06"
            }
        },
        {
            "id": 1772,
            "firstName": "Germán",
            "lastName": "Pezzella",
            "name": "Germán Pezzella",
            "position": "Defence",
            "dateOfBirth": "1991-06-27",
            "nationality": "Argentina",
            "shirtNumber": 16,
            "marketValue": 5000000,
            "contract": {
                "start": "2021-08",
                "until": "2025-06"
            }
        },
        {
            "id": 3624,
            "firstName": "Youssouf",
            "lastName": "Sabaly",
            "name": "Youssouf Sabaly",
            "position": "Defence",
            "dateOfBirth": "1993-03-05",
            "nationality": "Senegal",
            "shirtNumber": 23,
            "marketValue": 3000000,
            "contract": {
                "start": "2021-07",
                "until": "2026-06"
            }
        },
        {
            "id": 7783,
            "firstName": "",
            "lastName": "Héctor Bellerín",
            "name": "Héctor Bellerín",
            "position": "Defence",
            "dateOfBirth": "1995-03-19",
            "nationality": "Spain",
            "shirtNumber": 19,
            "marketValue": 20000000,
            "contract": {
                "start": "2021-08",
                "until": "2022-06"
            }
        },
        {
            "id": 32123,
            "firstName": "",
            "lastName": "Álex Moreno",
            "name": "Alex Moreno",
            "position": "Defence",
            "dateOfBirth": "1993-06-08",
            "nationality": "Spain",
            "shirtNumber": 15,
            "marketValue": 10000000,
            "contract": {
                "start": "2019-08",
                "until": "2025-06"
            }
        },
        {
            "id": 32491,
            "firstName": "",
            "lastName": "Juan Miranda",
            "name": "Juan Miranda",
            "position": "Defence",
            "dateOfBirth": "2000-01-19",
            "nationality": "Spain",
            "shirtNumber": 33,
            "marketValue": 6000000,
            "contract": {
                "start": "2020-10",
                "until": "2024-06"
            }
        },
        {
            "id": 33038,
            "firstName": "",
            "lastName": "Bartra",
            "name": "Bartra",
            "position": "Defence",
            "dateOfBirth": "1991-01-15",
            "nationality": "Spain",
            "shirtNumber": 5,
            "marketValue": 6000000,
            "contract": {
                "start": "2018-07",
                "until": "2023-06"
            }
        },
        {
            "id": 33106,
            "firstName": "",
            "lastName": "Víctor Ruiz",
            "name": "Víctor Ruíz",
            "position": "Defence",
            "dateOfBirth": "1989-01-25",
            "nationality": "Spain",
            "shirtNumber": 6,
            "marketValue": 2000000,
            "contract": {
                "start": "2020-08",
                "until": "2023-06"
            }
        },
        {
            "id": 33139,
            "firstName": "",
            "lastName": "Martín Montoya",
            "name": "Martín Montoya",
            "position": "Defence",
            "dateOfBirth": "1991-04-14",
            "nationality": "Spain",
            "shirtNumber": 2,
            "marketValue": 2000000,
            "contract": {
                "start": "2020-08",
                "until": "2024-06"
            }
        },
        {
            "id": 58580,
            "firstName": "",
            "lastName": "Édgar González",
            "name": "Édgar González",
            "position": "Defence",
            "dateOfBirth": "1997-04-01",
            "nationality": "Spain",
            "shirtNumber": 3,
            "marketValue": 5000000,
            "contract": {
                "start": "2021-07",
                "until": "2025-06"
            }
        },
        {
            "id": 144708,
            "firstName": "",
            "lastName": "Marc Baró",
            "name": "Marc Baró Ortiz",
            "position": "Defence",
            "dateOfBirth": "1999-08-23",
            "nationality": "Spain",
            "shirtNumber": 36,
            "marketValue": null,
            "contract": {
                "start": "2022-01",
                "until": "2022-06"
            }
        },
        {
            "id": 150595,
            "firstName": "",
            "lastName": "Fran Delgado",
            "name": "Fran Delgado",
            "position": "Defence",
            "dateOfBirth": "2001-07-11",
            "nationality": "Spain",
            "shirtNumber": 32,
            "marketValue": null,
            "contract": {
                "start": "2020-09",
                "until": "2024-06"
            }
        },
        {
            "id": 161288,
            "firstName": "",
            "lastName": "Kike Hermoso",
            "name": "Kike Hermoso",
            "position": "Defence",
            "dateOfBirth": "1999-08-10",
            "nationality": "Spain",
            "shirtNumber": 37,
            "marketValue": null,
            "contract": {
                "start": "2021-07",
                "until": "2022-06"
            }
        },
        {
            "id": 18,
            "firstName": "",
            "lastName": "Joaquín",
            "name": "Joaquín",
            "position": "Midfield",
            "dateOfBirth": "1981-07-21",
            "nationality": "Spain",
            "shirtNumber": 17,
            "marketValue": 1500000,
            "contract": {
                "start": "2016-07",
                "until": "2022-06"
            }
        },
        {
            "id": 25,
            "firstName": "",
            "lastName": "Canales",
            "name": "Canales",
            "position": "Midfield",
            "dateOfBirth": "1991-02-16",
            "nationality": "Spain",
            "shirtNumber": 10,
            "marketValue": 20000000,
            "contract": {
                "start": "2019-07",
                "until": "2026-06"
            }
        },
        {
            "id": 3250,
            "firstName": "",
            "lastName": "William Carvalho",
            "name": "William Carvalho",
            "position": "Midfield",
            "dateOfBirth": "1992-04-07",
            "nationality": "Portugal",
            "shirtNumber": 14,
            "marketValue": 14000000,
            "contract": {
                "start": "2018-07",
                "until": "2023-06"
            }
        },
        {
            "id": 8464,
            "firstName": "Nabil",
            "lastName": "Fekir",
            "name": "Nabil Fekir",
            "position": "Midfield",
            "dateOfBirth": "1993-07-18",
            "nationality": "France",
            "shirtNumber": 8,
            "marketValue": 30000000,
            "contract": {
                "start": "2019-07",
                "until": "2026-06"
            }
        },
        {
            "id": 33040,
            "firstName": "",
            "lastName": "Víctor Camarasa",
            "name": "Víctor Camarasa",
            "position": "Midfield",
            "dateOfBirth": "1994-05-28",
            "nationality": "Spain",
            "shirtNumber": 22,
            "marketValue": 1200000,
            "contract": {
                "start": "2021-07",
                "until": "2022-06"
            }
        },
        {
            "id": 39104,
            "firstName": "Guido",
            "lastName": "Rodríguez",
            "name": "Guido Rodríguez",
            "position": "Midfield",
            "dateOfBirth": "1994-04-12",
            "nationality": "Argentina",
            "shirtNumber": 21,
            "marketValue": 25000000,
            "contract": {
                "start": "2020-01",
                "until": "2024-06"
            }
        },
        {
            "id": 81737,
            "firstName": "Paul",
            "lastName": "Akouokou",
            "name": "Paul Akouokou",
            "position": "Midfield",
            "dateOfBirth": "1997-12-20",
            "nationality": "Ivory Coast",
            "shirtNumber": 4,
            "marketValue": 2000000,
            "contract": {
                "start": "2020-09",
                "until": "2024-06"
            }
        },
        {
            "id": 180064,
            "firstName": "",
            "lastName": "Marchena",
            "name": "Marchena",
            "position": "Midfield",
            "dateOfBirth": "2002-07-27",
            "nationality": "Spain",
            "shirtNumber": 38,
            "marketValue": null,
            "contract": {
                "start": "2022-01",
                "until": "2022-06"
            }
        },
        {
            "id": 2,
            "firstName": "",
            "lastName": "Juanmi",
            "name": "Juanmi",
            "position": "Offence",
            "dateOfBirth": "1993-05-20",
            "nationality": "Spain",
            "shirtNumber": 7,
            "marketValue": 12000000,
            "contract": {
                "start": "2019-07",
                "until": "2024-06"
            }
        },
        {
            "id": 8,
            "firstName": "",
            "lastName": "Willian José",
            "name": "Willian José",
            "position": "Offence",
            "dateOfBirth": "1991-11-23",
            "nationality": "Brazil",
            "shirtNumber": 12,
            "marketValue": 18000000,
            "contract": {
                "start": "2021-08",
                "until": "2022-06"
            }
        },
        {
            "id": 17,
            "firstName": "Christian",
            "lastName": null,
            "name": "Tello",
            "position": "Offence",
            "dateOfBirth": "1991-08-11",
            "nationality": "Spain",
            "shirtNumber": 11,
            "marketValue": 6000000,
            "contract": {
                "start": "2017-07",
                "until": "2022-06"
            }
        },
        {
            "id": 32056,
            "firstName": "",
            "lastName": "Borja Iglesias",
            "name": "Borja Iglesias",
            "position": "Offence",
            "dateOfBirth": "1993-01-17",
            "nationality": "Spain",
            "shirtNumber": 9,
            "marketValue": 10000000,
            "contract": {
                "start": "2019-08",
                "until": "2026-06"
            }
        },
        {
            "id": 33045,
            "firstName": "",
            "lastName": "Aitor Ruibal",
            "name": "Aitor Ruibal",
            "position": "Offence",
            "dateOfBirth": "1996-03-22",
            "nationality": "Spain",
            "shirtNumber": 24,
            "marketValue": 3000000,
            "contract": {
                "start": "2020-07",
                "until": "2025-06"
            }
        },
        {
            "id": 39115,
            "firstName": "Diego",
            "lastName": "Lainez",
            "name": "Diego Lainez",
            "position": "Offence",
            "dateOfBirth": "2000-06-09",
            "nationality": "Mexico",
            "shirtNumber": 20,
            "marketValue": 5000000,
            "contract": {
                "start": "2019-07",
                "until": "2024-06"
            }
        },
        {
            "id": 130324,
            "firstName": "",
            "lastName": "Raúl",
            "name": "Raúl",
            "position": "Offence",
            "dateOfBirth": "2000-11-03",
            "nationality": "Spain",
            "shirtNumber": 35,
            "marketValue": null,
            "contract": {
                "start": "2019-09",
                "until": "2022-06"
            }
        },
        {
            "id": 142393,
            "firstName": "",
            "lastName": "Rodri",
            "name": "Salomón Rodríguez",
            "position": "Offence",
            "dateOfBirth": "2000-02-16",
            "nationality": "Spain",
            "shirtNumber": 28,
            "marketValue": null,
            "contract": {
                "start": "2020-06",
                "until": "2026-06"
            }
        },
        {
            "id": 180037,
            "firstName": "",
            "lastName": "Cristian Tello",
            "name": "Cristian Tello",
            "position": "Offence",
            "dateOfBirth": "1991-08-11",
            "nationality": "Spain",
            "shirtNumber": 11,
            "marketValue": null,
            "contract": {
                "start": "2018-07",
                "until": "2022-06"
            }
        }
    ],
    "staff": [
        {
            "id": 63306,
            "firstName": "",
            "lastName": "Fernando",
            "name": "Fernando Fernández",
            "dateOfBirth": "1979-06-02",
            "nationality": "Spain",
            "contract": {
                "start": "2020-08",
                "until": "2023-06"
            }
        },
        {
            "id": 180098,
            "firstName": "",
            "lastName": "Doblas",
            "name": "Doblas",
            "dateOfBirth": "1980-08-05",
            "nationality": "Spain",
            "contract": {
                "start": "2020-09",
                "until": "2023-06"
            }
        },
        {
            "id": 180135,
            "firstName": "Rubén",
            "lastName": "Cousillas",
            "name": "Rubén Cousillas",
            "dateOfBirth": "1957-05-09",
            "nationality": "Argentina",
            "contract": {
                "start": "2020-08",
                "until": "2023-06"
            }
        }
    ],
    "lastUpdated": "2022-05-03T08:22:26Z"
}
List Resource
A list resource is available to fetch just all teams available.

Matches
You can use the Match Subresource to fetch a list of matches that are pre-filtered by the team.

Click here to see a sample implementation (at the very bottom) with some layers of plumbing and transformation code in between.

curl -XGET 'https://api.football-data.org/v4/teams/583/matches?dateFrom=2021-07-01&dateTo=2022-01-01' -H "X-Auth-Token: UR_TOKEN"
Notice the matches are lacking lineups, bookings and so on as we did not set the unfolding headers as explained here.

{
    "filters": {
        "dateFrom": "2021-07-01",
        "dateTo": "2022-01-01",
        "permission": "TIER_THREE",
        "limit": 100
    },
    "resultSet": {
        "count": 15,
        "competitions": "PPL",
        "first": "2021-08-07",
        "last": "2021-12-28",
        "played": 15,
        "wins": 6,
        "draws": 6,
        "losses": 7
    },
    "matches": [ ... ]
}
You see the applied filters on the very top: by default the list is limited to 100 items. this, this is season 2021/22. And we explicitly defined to return only matches of matchday 23. The resultSet node gives the boundaries of the match list, a count and how many matches are in status FINISHED. Last but not least the list of match items follows.

Available filters for Match Subresource
Filter name	Possible values	Sample
dateFrom

A date in format yyyy-MM-dd

/?dateFrom=2022-01-01

dateTo

A date in format yyyy-MM-dd

/?dateTo=2022-01-10

season

An integer, like [\d]{4}

/?season=2021

status

Status enum

/?status=FINISHED

venue

Enum [ HOME | AWAY ]

/?venue=HOME

limit

Integer [1-500]

Limit the result set

Match
Overview
The Match Resource reflects a scheduled football game. A game belongs to a competition and a season. It owns a stage and is typically played on a certain matchday. As mentioned in the introducing chapters the latter two are only attributes of a match, whereas competition and season are annotated object-like.

If you need detailed information about former encounters between the teams, you can call the Head2head Subresource by appending /head2head to the URI.

The list resource appears as subresource for the Competition, Team and Person Resource.

Let’s see the entire beauty of the Match Resource underneath.

curl -XGET 'https://api.football-data.org/v4/matches/330299' -H "X-Auth-Token: UR_TOKEN"
{
    "area": {
        "id": 2081,
        "name": "France",
        "code": "FRA",
        "flag": "https://crests.football-data.org/773.svg"
    },
    "competition": {
        "id": 2015,
        "name": "Ligue 1",
        "code": "FL1",
        "type": "LEAGUE",
        "emblem": "https://crests.football-data.org/FL1.png"
    },
    "season": {
        "id": 746,
        "startDate": "2021-08-06",
        "endDate": "2022-05-21",
        "currentMatchday": 38,
        "winner": null,
        "stages": [
            "REGULAR_SEASON"
        ]
    },
    "id": 330299,
    "utcDate": "2022-02-27T16:05:00Z",
    "status": "FINISHED",
    "minute": 90,
    "injuryTime": 7,
    "attendance": 16871,
    "venue": "Stade de l'Aube",
    "matchday": 26,
    "stage": "REGULAR_SEASON",
    "group": null,
    "lastUpdated": "2022-06-06T08:20:24Z",
    "homeTeam": {
        "id": 531,
        "name": "ES Troyes AC",
        "shortName": "Troyes",
        "tla": "ETR",
        "crest": "https://crests.football-data.org/531.svg",
        "coach": {
            "id": 108988,
            "name": "Bruno Irles",
            "nationality": "France"
        },
        "leagueRank": null,
        "formation": "3-4-1-2",
        "lineup": [
            {
                "id": 899,
                "name": "Gauthier Gallon",
                "position": "Goalkeeper",
                "shirtNumber": 30
            },
            {
                "id": 8775,
                "name": "Yoann Salmier",
                "position": "Centre-Back",
                "shirtNumber": 17
            },
            {
                "id": 8348,
                "name": "Adil Rami",
                "position": "Centre-Back",
                "shirtNumber": 23
            },
            {
                "id": 9004,
                "name": "Erik Palmer-Brown",
                "position": "Centre-Back",
                "shirtNumber": 2
            },
            {
                "id": 123574,
                "name": "Issa Kaboré",
                "position": "Right-Back",
                "shirtNumber": 29
            },
            {
                "id": 37728,
                "name": "Abdu Conté",
                "position": "Left-Back",
                "shirtNumber": 12
            },
            {
                "id": 507,
                "name": "Florian Tardieu",
                "position": "Defensive Midfield",
                "shirtNumber": 10
            },
            {
                "id": 8623,
                "name": "Tristan Dingomé",
                "position": "Central Midfield",
                "shirtNumber": 5
            },
            {
                "id": 43707,
                "name": "Mama Baldé",
                "position": "Right Winger",
                "shirtNumber": 25
            },
            {
                "id": 8415,
                "name": "Rominigue Kouamé",
                "position": "Central Midfield",
                "shirtNumber": 6
            },
            {
                "id": 6406,
                "name": "Iké Ugbo",
                "position": "Centre-Forward",
                "shirtNumber": 13
            }
        ],
        "bench": [
            {
                "id": 74570,
                "name": "Sébastien Rénot",
                "position": "Goalkeeper",
                "shirtNumber": 16
            },
            {
                "id": 99805,
                "name": "Giulian Biancone",
                "position": "Right-Back",
                "shirtNumber": 4
            },
            {
                "id": 811,
                "name": "Youssouf Koné",
                "position": "Left-Back",
                "shirtNumber": 3
            },
            {
                "id": 133766,
                "name": "Yasser Larouci",
                "position": "Left-Back",
                "shirtNumber": 22
            },
            {
                "id": 8544,
                "name": "Dylan Chambost",
                "position": "Attacking Midfield",
                "shirtNumber": 14
            },
            {
                "id": 824,
                "name": "Xavier Chavalerin",
                "position": "Central Midfield",
                "shirtNumber": 24
            },
            {
                "id": 1043,
                "name": "Lebo Mothiba",
                "position": "Centre-Forward",
                "shirtNumber": 26
            },
            {
                "id": 519,
                "name": "Yoann Touzghar",
                "position": "Centre-Forward",
                "shirtNumber": 7
            },
            {
                "id": 169252,
                "name": "Metinho",
                "position": "Central Midfield",
                "shirtNumber": 31
            }
        ],
        "statistics": {
            "corner_kicks": 4,
            "free_kicks": 10,
            "goal_kicks": 5,
            "offsides": 4,
            "fouls": 16,
            "ball_possession": 41,
            "saves": 1,
            "throw_ins": 12,
            "shots": 8,
            "shots_on_goal": 3,
            "shots_off_goal": 5,
            "yellow_cards": 5,
            "yellow_red_cards": 0,
            "red_cards": 0
        }
    },
    "awayTeam": {
        "id": 516,
        "name": "Olympique de Marseille",
        "shortName": "Marseille",
        "tla": "MAR",
        "crest": "https://crests.football-data.org/516.png",
        "coach": {
            "id": 33636,
            "name": "Jorge Sampaoli",
            "nationality": "Argentina"
        },
        "leagueRank": null,
        "formation": "4-3-3",
        "lineup": [
            {
                "id": 32695,
                "name": "Pau López",
                "position": "Goalkeeper",
                "shirtNumber": 16
            },
            {
                "id": 80171,
                "name": "William Saliba",
                "position": "Centre-Back",
                "shirtNumber": 2
            },
            {
                "id": 10206,
                "name": "Duje Ćaleta-Car",
                "position": "Centre-Back",
                "shirtNumber": 15
            },
            {
                "id": 8346,
                "name": "Boubacar Kamara",
                "position": "Defensive Midfield",
                "shirtNumber": 4
            },
            {
                "id": 8695,
                "name": "Valentin Rongier",
                "position": "Central Midfield",
                "shirtNumber": 21
            },
            {
                "id": 1086,
                "name": "Luan Peres",
                "position": "Centre-Back",
                "shirtNumber": 14
            },
            {
                "id": 1815,
                "name": "Gerson",
                "position": "Central Midfield",
                "shirtNumber": 8
            },
            {
                "id": 600,
                "name": "Mattéo Guendouzi",
                "position": "Central Midfield",
                "shirtNumber": 6
            },
            {
                "id": 1818,
                "name": "Cengiz Ünder",
                "position": "Right Winger",
                "shirtNumber": 17
            },
            {
                "id": 8360,
                "name": "Dimitri Payet",
                "position": "Attacking Midfield",
                "shirtNumber": 10
            },
            {
                "id": 166640,
                "name": "Ahmadou Bamba Dieng",
                "position": null,
                "shirtNumber": 12
            }
        ],
        "bench": [
            {
                "id": 3356,
                "name": "Steve Mandanda",
                "position": "Goalkeeper",
                "shirtNumber": 30
            },
            {
                "id": 33108,
                "name": "Álvaro González",
                "position": "Centre-Back",
                "shirtNumber": 3
            },
            {
                "id": 7786,
                "name": "Sead Kolašinac",
                "position": "Left-Back",
                "shirtNumber": 23
            },
            {
                "id": 3714,
                "name": "Amine Harit",
                "position": "Attacking Midfield",
                "shirtNumber": 7
            },
            {
                "id": 633,
                "name": "Pape Gueye",
                "position": "Defensive Midfield",
                "shirtNumber": 22
            },
            {
                "id": 2105,
                "name": "Arkadiusz Milik",
                "position": "Centre-Forward",
                "shirtNumber": 9
            },
            {
                "id": 115074,
                "name": "Luis Henrique",
                "position": "Left Winger",
                "shirtNumber": 11
            },
            {
                "id": 21583,
                "name": "Cédric Bakambu",
                "position": "Centre-Forward",
                "shirtNumber": 13
            },
            {
                "id": 166642,
                "name": "Pol Lirola",
                "position": null,
                "shirtNumber": 29
            }
        ],
        "statistics": {
            "corner_kicks": 8,
            "free_kicks": 20,
            "goal_kicks": 7,
            "offsides": 0,
            "fouls": 10,
            "ball_possession": 59,
            "saves": 2,
            "throw_ins": 14,
            "shots": 4,
            "shots_on_goal": 2,
            "shots_off_goal": 2,
            "yellow_cards": 3,
            "yellow_red_cards": 0,
            "red_cards": 0
        }
    },
    "score": {
        "winner": "DRAW",
        "duration": "REGULAR",
        "fullTime": {
            "home": 1,
            "away": 1
        },
        "halfTime": {
            "home": 0,
            "away": 1
        }
    },
    "goals": [
        {
            "minute": 28,
            "injuryTime": null,
            "type": "PENALTY",
            "team": {
                "id": 516,
                "name": "Olympique de Marseille"
            },
            "scorer": {
                "id": 8360,
                "name": "Dimitri Payet"
            },
            "assist": null,
            "score": {
                "home": 0,
                "away": 1
            }
        },
        {
            "minute": 90,
            "injuryTime": null,
            "type": "REGULAR",
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "scorer": {
                "id": 519,
                "name": "Yoann Touzghar"
            },
            "assist": {
                "id": 811,
                "name": "Youssouf Koné"
            },
            "score": {
                "home": 1,
                "away": 1
            }
        }
    ],
    "penalties": [
        {
            "player": {
                "id": 8360,
                "name": "Dimitri Payet"
            },
            "team": {
                "id": null,
                "name": null
            },
            "scored": true
        }
    ],
    "bookings": [
        {
            "minute": 11,
            "team": {
                "id": 516,
                "name": "Olympique de Marseille"
            },
            "player": {
                "id": 8695,
                "name": "Valentin Rongier"
            },
            "card": "YELLOW"
        },
        {
            "minute": 27,
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "player": {
                "id": 43707,
                "name": "Mama Baldé"
            },
            "card": "YELLOW"
        },
        {
            "minute": 36,
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "player": {
                "id": 507,
                "name": "Florian Tardieu"
            },
            "card": "YELLOW"
        },
        {
            "minute": 36,
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "player": {
                "id": 8348,
                "name": "Adil Rami"
            },
            "card": "YELLOW"
        },
        {
            "minute": 49,
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "player": {
                "id": 37728,
                "name": "Abdu Conté"
            },
            "card": "YELLOW"
        },
        {
            "minute": 55,
            "team": {
                "id": 516,
                "name": "Olympique de Marseille"
            },
            "player": {
                "id": 8360,
                "name": "Dimitri Payet"
            },
            "card": "YELLOW"
        },
        {
            "minute": 85,
            "team": {
                "id": 516,
                "name": "Olympique de Marseille"
            },
            "player": {
                "id": 32695,
                "name": "Pau López"
            },
            "card": "YELLOW"
        },
        {
            "minute": 90,
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "player": {
                "id": 99805,
                "name": "Giulian Biancone"
            },
            "card": "YELLOW"
        }
    ],
    "substitutions": [
        {
            "minute": 57,
            "team": {
                "id": 516,
                "name": "Olympique de Marseille"
            },
            "playerOut": {
                "id": 8695,
                "name": "Valentin Rongier"
            },
            "playerIn": {
                "id": 166642,
                "name": "Pol Lirola"
            }
        },
        {
            "minute": 57,
            "team": {
                "id": 516,
                "name": "Olympique de Marseille"
            },
            "playerOut": {
                "id": 166640,
                "name": "Ahmadou Bamba Dieng"
            },
            "playerIn": {
                "id": 115074,
                "name": "Luis Henrique"
            }
        },
        {
            "minute": 58,
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "playerOut": {
                "id": 6406,
                "name": "Iké Ugbo"
            },
            "playerIn": {
                "id": 1043,
                "name": "Lebo Mothiba"
            }
        },
        {
            "minute": 59,
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "playerOut": {
                "id": 37728,
                "name": "Abdu Conté"
            },
            "playerIn": {
                "id": 811,
                "name": "Youssouf Koné"
            }
        },
        {
            "minute": 77,
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "playerOut": {
                "id": 9004,
                "name": "Erik Palmer-Brown"
            },
            "playerIn": {
                "id": 99805,
                "name": "Giulian Biancone"
            }
        },
        {
            "minute": 77,
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "playerOut": {
                "id": 43707,
                "name": "Mama Baldé"
            },
            "playerIn": {
                "id": 519,
                "name": "Yoann Touzghar"
            }
        },
        {
            "minute": 78,
            "team": {
                "id": 516,
                "name": "Olympique de Marseille"
            },
            "playerOut": {
                "id": 8360,
                "name": "Dimitri Payet"
            },
            "playerIn": {
                "id": 2105,
                "name": "Arkadiusz Milik"
            }
        },
        {
            "minute": 86,
            "team": {
                "id": 516,
                "name": "Olympique de Marseille"
            },
            "playerOut": {
                "id": 1818,
                "name": "Cengiz Ünder"
            },
            "playerIn": {
                "id": 633,
                "name": "Pape Gueye"
            }
        },
        {
            "minute": 87,
            "team": {
                "id": 516,
                "name": "Olympique de Marseille"
            },
            "playerOut": {
                "id": 1086,
                "name": "Luan Peres"
            },
            "playerIn": {
                "id": 7786,
                "name": "Sead Kolašinac"
            }
        },
        {
            "minute": 90,
            "team": {
                "id": 531,
                "name": "ES Troyes AC"
            },
            "playerOut": {
                "id": 8415,
                "name": "Rominigue Kouamé"
            },
            "playerIn": {
                "id": 824,
                "name": "Xavier Chavalerin"
            }
        }
    ],
    "odds": {
        "homeWin": 4.25,
        "draw": 3.72,
        "awayWin": 1.81
    },
    "referees": [
        {
            "id": 57080,
            "name": "Cyril Mugnier",
            "type": "ASSISTANT_REFEREE_N1",
            "nationality": "France"
        },
        {
            "id": 57049,
            "name": "Mehdi Rahmouni",
            "type": "ASSISTANT_REFEREE_N2",
            "nationality": "France"
        },
        {
            "id": 57031,
            "name": "Alexandre Perreau Niel",
            "type": "FOURTH_OFFICIAL",
            "nationality": "France"
        },
        {
            "id": 43918,
            "name": "François Letexier",
            "type": "REFEREE",
            "nationality": "France"
        },
        {
            "id": 57073,
            "name": "Jérémie Pignard",
            "type": "VIDEO_ASSISTANT_REFEREE_N1",
            "nationality": "France"
        },
        {
            "id": 166622,
            "name": "Abdelali Chaoui",
            "type": "VIDEO_ASSISTANT_REFEREE_N2",
            "nationality": null
        }
    ]
}
Available filters for the list resource
Filter name	Possible values	Sample	Description
ids

A list of integers, like [\d]{4}

/?ids=333,3303,3213

lists 3 matches with the given ids

date

A date in format yyyy-MM-dd

/?date=2022-01-01

Lists all matches for the given date

dateFrom

A date in format yyyy-MM-dd

/?dateFrom=2022-01-01

Must be used in conjunction with dateTo

dateTo

A date in format yyyy-MM-dd

/?dateTo=2022-01-10

Lists all matches before the given date until and including dateFrom

status

Status enum

/?status=FINISHED

only lists finished matches for the current day

Status workflow explained
The status field indicates the current phase a match is in. For the majority this is FINISHED (96,9% of all matches in my database contain that status) but how do matches get there? Lets try to depict that with a diagram. The slightly greenish boxes show the "happy flow".

match status v4
As soon as a match finds it’s way to the database and given there is a rough date set, it is stamped with status SCHEDULED. As soon the date is finalised with an exact date and time, the match enters status TIMED. It gets played (IN_PLAY), the players rest (PAUSED) and the final whistle pushes the match to FINISHED.

The grey box shows the 'pseudo-status' LIVE, that you can use as a match filter. It’s just for convenience, so in the end it combines status IN_PLAY and PAUSED (and the backend does exactly that if you pass LIVE as value for status).

Last but not least not all the time everything goes well, but I won’t go into detail here as I think everything is quite clear within the diagram.

Enums
Some fields contain values that are defined by an Enum, which is useful to reveal, so here we go:

Attribute name	Possible values
status

SCHEDULED, TIMED, IN_PLAY, PAUSED, FINISHED, SUSPENDED, POSTPONED, CANCELLED, AWARDED

stage

FINAL | THIRD_PLACE | SEMI_FINALS | QUARTER_FINALS | LAST_16 | LAST_32 | LAST_64 | ROUND_4 | ROUND_3 | ROUND_2 | ROUND_1 | GROUP_STAGE | PRELIMINARY_ROUND | QUALIFICATION | QUALIFICATION_ROUND_1 | QUALIFICATION_ROUND_2 | QUALIFICATION_ROUND_3 | PLAYOFF_ROUND_1 | PLAYOFF_ROUND_2 | PLAYOFFS | REGULAR_SEASON | CLAUSURA | APERTURA | CHAMPIONSHIP_ROUND | RELEGATION_ROUND

group

GROUP_A | GROUP_B | GROUP_C | GROUP_D | GROUP_E | GROUP_F | GROUP_G | GROUP_H | GROUP_I | GROUP_J | GROUP_K | GROUP_L

Competition
Overview
You will use the list representation of the Competition Resource to find out which competitions are available and see which ones you have access to. You can also get insight into how much historical data is available for a particular competition by calling the the resource by itself (with an id).

Let’s see the entire beauty of the competition resource below.

curl -XGET 'https://api.football-data.org/v4/competitions/PL' -H "X-Auth-Token: UR_TOKEN"
{
    "area": {
        "id": 2072,
        "name": "England",
        "code": "ENG",
        "flag": "https://crests.football-data.org/770.svg"
    },
    "id": 2021,
    "name": "Premier League",
    "code": "PL",
    "type": "LEAGUE",
    "emblem": "https://crests.football-data.org/PL.png",
    "currentSeason": {
        "id": 733,
        "startDate": "2021-08-13",
        "endDate": "2022-05-22",
        "currentMatchday": 37,
        "winner": null,
        "stages": [
            "REGULAR_SEASON"
        ]
    },
    "seasons": [
        {
            "id": 733,
            "startDate": "2021-08-13",
            "endDate": "2022-05-22",
            "currentMatchday": 37,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 619,
            "startDate": "2020-09-12",
            "endDate": "2021-05-23",
            "currentMatchday": 38,
            "winner": {
                "id": 65,
                "name": "Manchester City FC",
                "shortName": "Man City",
                "tla": "MCI",
                "crest": "https://crests.football-data.org/65.png",
                "address": "SportCity Manchester M11 3FF",
                "website": "https://www.mancity.com",
                "founded": 1880,
                "clubColors": "Sky Blue / White",
                "venue": "Etihad Stadium",
                "lastUpdated": "2022-02-10T19:48:37Z"
            },
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 468,
            "startDate": "2019-08-09",
            "endDate": "2020-07-26",
            "currentMatchday": 38,
            "winner": {
                "id": 64,
                "name": "Liverpool FC",
                "shortName": "Liverpool",
                "tla": "LIV",
                "crest": "https://crests.football-data.org/64.png",
                "address": "Anfield Road Liverpool L4 0TH",
                "website": "http://www.liverpoolfc.tv",
                "founded": 1892,
                "clubColors": "Red / White",
                "venue": "Anfield",
                "lastUpdated": "2022-02-10T19:30:22Z"
            },
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 151,
            "startDate": "2018-08-10",
            "endDate": "2019-05-12",
            "currentMatchday": 38,
            "winner": {
                "id": 65,
                "name": "Manchester City FC",
                "shortName": "Man City",
                "tla": "MCI",
                "crest": "https://crests.football-data.org/65.png",
                "address": "SportCity Manchester M11 3FF",
                "website": "https://www.mancity.com",
                "founded": 1880,
                "clubColors": "Sky Blue / White",
                "venue": "Etihad Stadium",
                "lastUpdated": "2022-02-10T19:48:37Z"
            },
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 23,
            "startDate": "2017-08-11",
            "endDate": "2018-05-13",
            "currentMatchday": 38,
            "winner": {
                "id": 65,
                "name": "Manchester City FC",
                "shortName": "Man City",
                "tla": "MCI",
                "crest": "https://crests.football-data.org/65.png",
                "address": "SportCity Manchester M11 3FF",
                "website": "https://www.mancity.com",
                "founded": 1880,
                "clubColors": "Sky Blue / White",
                "venue": "Etihad Stadium",
                "lastUpdated": "2022-02-10T19:48:37Z"
            },
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 256,
            "startDate": "2016-08-13",
            "endDate": "2017-05-21",
            "currentMatchday": null,
            "winner": {
                "id": 61,
                "name": "Chelsea FC",
                "shortName": "Chelsea",
                "tla": "CHE",
                "crest": "https://crests.football-data.org/61.png",
                "address": "Fulham Road London SW6 1HS",
                "website": "http://www.chelseafc.com",
                "founded": 1905,
                "clubColors": "Royal Blue / White",
                "venue": "Stamford Bridge",
                "lastUpdated": "2022-02-10T19:24:40Z"
            },
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        [ ... way more seasons ... ]
        {
            "id": 973,
            "startDate": "1898-08-30",
            "endDate": "1899-04-27",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 983,
            "startDate": "1897-08-30",
            "endDate": "1898-04-28",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 984,
            "startDate": "1896-08-30",
            "endDate": "1897-04-24",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 975,
            "startDate": "1895-08-31",
            "endDate": "1896-04-27",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 976,
            "startDate": "1894-08-30",
            "endDate": "1895-04-22",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 981,
            "startDate": "1893-08-31",
            "endDate": "1894-04-21",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 979,
            "startDate": "1892-09-01",
            "endDate": "1893-04-15",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 985,
            "startDate": "1891-09-03",
            "endDate": "1892-04-28",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 977,
            "startDate": "1890-09-04",
            "endDate": "1891-04-16",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 978,
            "startDate": "1889-09-05",
            "endDate": "1890-03-29",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        },
        {
            "id": 1040,
            "startDate": "1888-09-06",
            "endDate": "1889-04-18",
            "currentMatchday": null,
            "winner": null,
            "stages": [
                "REGULAR_SEASON"
            ]
        }
    ],
    "lastUpdated": "2022-03-20T08:58:54Z"
}
Available filters for the list resource
The resource itself does not provide any filters, but the list resource does. Please notice that by default the competitions are filtered for the authenticated client. You can disable authentication (not pass a token) to list all available competitions. Besides there is only:

Filter name	Possible values	Sample
areas

A (comma separated) list of area ids
like: String /\d+,\d+/

/?areas=2016,2023,2025

Standings
While in print media you only find one (overall) standing most of the time, actually there are way more standings and you use the Standing Subresource to access them.

Click here to see a sample implementation with some layers of plumbing and transformation code in between.

Standings give a quick overview of a teams' performance relative to their opponents by aggregating data points over a certain range of time.

I provide official standings for the running season, so you can show it on your website with confidence. However, be prepared to save a snapshot of the standing after the season ended for future use, as I will remove deducted points for past seasons. This is because the (my) main purpose of past data is data analysis targeting team performances. And these shall not be affected by legal decisions.
The Resource acts differently depending on the type of the competition it is based on. Basically this is three things:

it is not available (returns 404) for competitions of type CUP and PLAYOFFS

it returns a list of standings, one for each group for competitions of type LEAGUE_CUP

it returns a TOTAL, HOME and AWAY standing for competitions of type LEAGUE

Let’s see the entire beauty of the Standing Resource below.

curl -XGET 'https://api.football-data.org/v4/competitions/PD/standings' -H "X-Auth-Token: UR_TOKEN"
{
    "filters": {
        "season": "2021"
    },
    "area": {
        "id": 2224,
        "name": "Spain",
        "code": "ESP",
        "flag": "https://crests.football-data.org/760.svg"
    },
    "competition": {
        "id": 2014,
        "name": "Primera Division",
        "code": "PD",
        "type": "LEAGUE",
        "emblem": "https://crests.football-data.org/PD.png"
    },
    "season": {
        "id": 380,
        "startDate": "2021-08-13",
        "endDate": "2022-05-22",
        "currentMatchday": 34,
        "winner": null,
        "stages": [
            "REGULAR_SEASON"
        ]
    },
    "standings": [
        {
            "stage": "REGULAR_SEASON",
            "type": "TOTAL",
            "group": null,
            "table": [
                {
                    "position": 1,
                    "team": {
                        "id": 86,
                        "name": "Real Madrid CF",
                        "shortName": "Real Madrid",
                        "tla": "RMA",
                        "crest": "https://crests.football-data.org/86.png"
                    },
                    "playedGames": 34,
                    "form": "W,W,W,W,W",
                    "won": 25,
                    "draw": 6,
                    "lost": 3,
                    "points": 81,
                    "goalsFor": 73,
                    "goalsAgainst": 29,
                    "goalDifference": 44
                },
                {
                    "position": 2,
                    "team": {
                        "id": 81,
                        "name": "FC Barcelona",
                        "shortName": "Barça",
                        "tla": "FCB",
                        "crest": "https://crests.football-data.org/81.svg"
                    },
                    "playedGames": 34,
                    "form": "W,L,W,L,W",
                    "won": 19,
                    "draw": 9,
                    "lost": 6,
                    "points": 66,
                    "goalsFor": 63,
                    "goalsAgainst": 34,
                    "goalDifference": 29
                },
                {
                    "position": 3,
                    "team": {
                        "id": 559,
                        "name": "Sevilla FC",
                        "shortName": "Sevilla FC",
                        "tla": "SEV",
                        "crest": "https://crests.football-data.org/559.svg"
                    },
                    "playedGames": 34,
                    "form": "D,W,L,W,L",
                    "won": 17,
                    "draw": 13,
                    "lost": 4,
                    "points": 64,
                    "goalsFor": 50,
                    "goalsAgainst": 28,
                    "goalDifference": 22
                },
                {
                    "position": 4,
                    "team": {
                        "id": 78,
                        "name": "Club Atlético de Madrid",
                        "shortName": "Atleti",
                        "tla": "ATL",
                        "crest": "https://crests.football-data.org/78.svg"
                    },
                    "playedGames": 34,
                    "form": "L,D,W,L,W",
                    "won": 18,
                    "draw": 7,
                    "lost": 9,
                    "points": 61,
                    "goalsFor": 59,
                    "goalsAgainst": 41,
                    "goalDifference": 18
                },
                {
                    "position": 5,
                    "team": {
                        "id": 90,
                        "name": "Real Betis Balompié",
                        "shortName": "Real Betis",
                        "tla": "BET",
                        "crest": "https://crests.football-data.org/90.svg"
                    },
                    "playedGames": 33,
                    "form": "L,D,W,W,D",
                    "won": 17,
                    "draw": 6,
                    "lost": 10,
                    "points": 57,
                    "goalsFor": 56,
                    "goalsAgainst": 38,
                    "goalDifference": 18
                },
                [ ... way more standings ... ]
                {
                    "position": 19,
                    "team": {
                        "id": 263,
                        "name": "Deportivo Alavés",
                        "shortName": "Alavés",
                        "tla": "ALA",
                        "crest": "https://crests.football-data.org/263.png"
                    },
                    "playedGames": 34,
                    "form": "W,L,W,L,L",
                    "won": 7,
                    "draw": 7,
                    "lost": 20,
                    "points": 28,
                    "goalsFor": 28,
                    "goalsAgainst": 56,
                    "goalDifference": -28
                },
                {
                    "position": 20,
                    "team": {
                        "id": 88,
                        "name": "Levante UD",
                        "shortName": "Levante",
                        "tla": "LEV",
                        "crest": "https://crests.football-data.org/88.svg"
                    },
                    "playedGames": 34,
                    "form": "D,L,W,L,W",
                    "won": 5,
                    "draw": 11,
                    "lost": 18,
                    "points": 26,
                    "goalsFor": 42,
                    "goalsAgainst": 66,
                    "goalDifference": -24
                }
            ]
        },
        {
            "stage": "REGULAR_SEASON",
            "type": "HOME",
            "group": null,
            "table": [
                {
                    "position": 1,
                    "team": {
                        "id": 86,
                        "name": "Real Madrid CF",
                        "shortName": "Real Madrid",
                        "tla": "RMA",
                        "crest": "https://crests.football-data.org/86.png"
                    },
                    "playedGames": 17,
                    "form": "",
                    "won": 12,
                    "draw": 4,
                    "lost": 1,
                    "points": 40,
                    "goalsFor": 38,
                    "goalsAgainst": 13,
                    "goalDifference": 25
                },
                {
                    "position": 2,
                    "team": {
                        "id": 559,
                        "name": "Sevilla FC",
                        "shortName": "Sevilla FC",
                        "tla": "SEV",
                        "crest": "https://crests.football-data.org/559.svg"
                    },
                    "playedGames": 17,
                    "form": "",
                    "won": 11,
                    "draw": 5,
                    "lost": 1,
                    "points": 38,
                    "goalsFor": 35,
                    "goalsAgainst": 17,
                    "goalDifference": 18
                },
                {
                    "position": 3,
                    "team": {
                        "id": 78,
                        "name": "Club Atlético de Madrid",
                        "shortName": "Atleti",
                        "tla": "ATL",
                        "crest": "https://crests.football-data.org/78.svg"
                    },
                    "playedGames": 17,
                    "form": "",
                    "won": 11,
                    "draw": 4,
                    "lost": 2,
                    "points": 37,
                    "goalsFor": 31,
                    "goalsAgainst": 15,
                    "goalDifference": 16
                },
                {
                    "position": 4,
                    "team": {
                        "id": 94,
                        "name": "Villarreal CF",
                        "shortName": "Villarreal",
                        "tla": "VIL",
                        "crest": "https://crests.football-data.org/94.png"
                    },
                    "playedGames": 17,
                    "form": "",
                    "won": 10,
                    "draw": 5,
                    "lost": 2,
                    "points": 35,
                    "goalsFor": 38,
                    "goalsAgainst": 15,
                    "goalDifference": 23
                },
                [ ... way more standings ... ]
                {
                    "position": 20,
                    "team": {
                        "id": 264,
                        "name": "Cádiz CF",
                        "shortName": "Cádiz CF",
                        "tla": "CAD",
                        "crest": "https://crests.football-data.org/264.png"
                    },
                    "playedGames": 17,
                    "form": "",
                    "won": 2,
                    "draw": 8,
                    "lost": 7,
                    "points": 14,
                    "goalsFor": 15,
                    "goalsAgainst": 23,
                    "goalDifference": -8
                }
            ]
        },
        {
            "stage": "REGULAR_SEASON",
            "type": "AWAY",
            "group": null,
            "table": [
                {
                    "position": 1,
                    "team": {
                        "id": 86,
                        "name": "Real Madrid CF",
                        "shortName": "Real Madrid",
                        "tla": "RMA",
                        "crest": "https://crests.football-data.org/86.png"
                    },
                    "playedGames": 17,
                    "form": "",
                    "won": 13,
                    "draw": 2,
                    "lost": 2,
                    "points": 41,
                    "goalsFor": 35,
                    "goalsAgainst": 16,
                    "goalDifference": 19
                },
                [ ... way more standings ... ]
                {
                    "position": 17,
                    "team": {
                        "id": 88,
                        "name": "Levante UD",
                        "shortName": "Levante",
                        "tla": "LEV",
                        "crest": "https://crests.football-data.org/88.svg"
                    },
                    "playedGames": 17,
                    "form": "",
                    "won": 2,
                    "draw": 4,
                    "lost": 11,
                    "points": 10,
                    "goalsFor": 19,
                    "goalsAgainst": 38,
                    "goalDifference": -19
                },
                {
                    "position": 18,
                    "team": {
                        "id": 80,
                        "name": "RCD Espanyol de Barcelona",
                        "shortName": "Espanyol",
                        "tla": "ESP",
                        "crest": "https://crests.football-data.org/80.svg"
                    },
                    "playedGames": 17,
                    "form": "",
                    "won": 1,
                    "draw": 5,
                    "lost": 11,
                    "points": 8,
                    "goalsFor": 14,
                    "goalsAgainst": 32,
                    "goalDifference": -18
                },
                {
                    "position": 19,
                    "team": {
                        "id": 89,
                        "name": "RCD Mallorca",
                        "shortName": "Mallorca",
                        "tla": "MAL",
                        "crest": "https://crests.football-data.org/89.png"
                    },
                    "playedGames": 17,
                    "form": "",
                    "won": 2,
                    "draw": 2,
                    "lost": 13,
                    "points": 8,
                    "goalsFor": 14,
                    "goalsAgainst": 38,
                    "goalDifference": -24
                },
                {
                    "position": 20,
                    "team": {
                        "id": 263,
                        "name": "Deportivo Alavés",
                        "shortName": "Alavés",
                        "tla": "ALA",
                        "crest": "https://crests.football-data.org/263.png"
                    },
                    "playedGames": 17,
                    "form": "",
                    "won": 1,
                    "draw": 3,
                    "lost": 13,
                    "points": 6,
                    "goalsFor": 13,
                    "goalsAgainst": 37,
                    "goalDifference": -24
                }
            ]
        }
    ]
}
Available filters for Standings
Filter name	Possible values	Sample
season

An integer, like [\d]{4}

/?season=1981

matchday

An integer, like [\d]{2}

/?matchday=15

date

A date in format yyyy-MM-dd

/?date=2022-01-01 to find out who was in the lead at new years eve

You can combine the season and matchday filters. In case they are used, the resulting standings are compiled by match information only, so they lack possible deducted points.
(Top) Scorers
So who does really shine this season when it comes to bringing the teams in front? Use the Top Scorer Subresource to find out. It lists all assists and goals for a competitions' season including assists grouped by player.

Click here to see a sample implementation with some layers of plumbing and transformation code in between.

curl -XGET 'https://api.football-data.org/v4/competitions/SA/scorers' -H "X-Auth-Token: UR_TOKEN"
{
    "count": 10,
    "filters": {
        "limit": 10
    },
    "competition": {
        "id": 2019,
        "name": "Serie A",
        "code": "SA",
        "type": "LEAGUE",
        "emblem": "https://crests.football-data.org/SA.png"
    },
    "season": {
        "id": 638,
        "startDate": "2020-09-19",
        "endDate": "2021-05-23",
        "currentMatchday": 38,
        "winner": {
            "id": 108,
            "name": "FC Internazionale Milano",
            "shortName": "Inter",
            "tla": "INT",
            "crest": "https://crests.football-data.org/108.png",
            "address": "Corso Vittorio Emanuele II 9 Milano 20122",
            "phone": "+39 (02) 77151",
            "website": "http://www.inter.it",
            "email": "segreteriaccic@inter.it",
            "founded": 1908,
            "clubColors": "Blue / Black",
            "venue": "Stadio Giuseppe Meazza",
            "lastUpdated": "2021-11-24T14:55:58Z"
        },
        "stages": [
            "REGULAR_SEASON"
        ]
    },
    "scorers": [
        {
            "player": {
                "id": 44,
                "name": "Cristiano Ronaldo",
                "firstName": "Cristiano Ronaldo",
                "lastName": "dos Santos Aveiro",
                "dateOfBirth": "1985-02-05",
                "countryOfBirth": "Portugal",
                "nationality": "Portugal",
                "position": "Attacker",
                "shirtNumber": null,
                "lastUpdated": "2021-10-13T08:04:10Z"
            },
            "team": {
                "id": 109,
                "name": "Juventus FC",
                "shortName": "Juventus",
                "tla": "JUV",
                "crest": "https://crests.football-data.org/109.svg",
                "address": "Corso Galileo Ferraris, 32 Torino 10128",
                "phone": "+39 (011) 65631",
                "website": "http://www.juventus.com",
                "email": "francesco.gianello@juventus.com",
                "founded": 1897,
                "clubColors": "White / Black",
                "venue": "Allianz Stadium",
                "lastUpdated": "2020-11-26T02:19:40Z"
            },
            "goals": 29,
            "assists": 3,
            "penalties": 6
        },
        {
            "player": {
                "id": 3662,
                "name": "Romelu Lukaku",
                "firstName": "Romelu",
                "lastName": "Lukaku Menama",
                "dateOfBirth": "1993-05-13",
                "countryOfBirth": "Belgium",
                "nationality": "Belgium",
                "position": "Attacker",
                "shirtNumber": null,
                "lastUpdated": "2021-10-13T08:04:13Z"
            },
            "team": {
                "id": 108,
                "name": "FC Internazionale Milano",
                "shortName": "Inter",
                "tla": "INT",
                "crest": "https://crests.football-data.org/108.png",
                "address": "Corso Vittorio Emanuele II 9 Milano 20122",
                "phone": "+39 (02) 77151",
                "website": "http://www.inter.it",
                "email": "segreteriaccic@inter.it",
                "founded": 1908,
                "clubColors": "Blue / Black",
                "venue": "Stadio Giuseppe Meazza",
                "lastUpdated": "2021-11-24T14:55:58Z"
            },
            "goals": 24,
            "assists": 11,
            "penalties": 6
        },
        {
            "player": {
                "id": 57,
                "name": "Luis Muriel",
                "firstName": "Luis Fernando",
                "lastName": null,
                "dateOfBirth": "1991-04-16",
                "countryOfBirth": "Colombia",
                "nationality": "Colombia",
                "position": "Attacker",
                "shirtNumber": null,
                "lastUpdated": "2020-09-07T21:10:15Z"
            },
            "team": {
                "id": 102,
                "name": "Atalanta BC",
                "shortName": "Atalanta",
                "tla": "ATA",
                "crest": "https://crests.football-data.org/102.svg",
                "address": "Corso Europa, 46, Zingonia Ciserano 24040",
                "phone": "+39 (035) 4186211",
                "website": "http://www.atalanta.it",
                "email": "info@atalanta.it",
                "founded": 1904,
                "clubColors": "Black / Blue",
                "venue": "Stadio Atleti Azzurri d'Italia",
                "lastUpdated": "2020-11-26T02:19:32Z"
            },
            "goals": 22,
            "assists": 7,
            "penalties": 2
        },
        {
            "player": {
                "id": 82002,
                "name": "Dušan Vlahović",
                "firstName": "Dušan",
                "lastName": null,
                "dateOfBirth": "2000-01-28",
                "countryOfBirth": "Serbia",
                "nationality": "Serbia",
                "position": "Attacker",
                "shirtNumber": null,
                "lastUpdated": "2020-09-07T21:10:05Z"
            },
            "team": {
                "id": 99,
                "name": "ACF Fiorentina",
                "shortName": "Fiorentina",
                "tla": "FIO",
                "crest": "https://crests.football-data.org/99.svg",
                "address": "Viale Manfredo Fanti 4 Firenze 50137",
                "phone": "+39 (055) 5030190",
                "website": "http://www.acffiorentina.it",
                "email": "segreteria@acffiorentina.it",
                "founded": 1926,
                "clubColors": "Purple / White",
                "venue": "Stadio Artemio Franchi",
                "lastUpdated": "2020-11-26T02:23:02Z"
            },
            "goals": 21,
            "assists": 2,
            "penalties": 6
        },
        {
            "player": {
                "id": 2076,
                "name": "Ciro Immobile",
                "firstName": "Ciro",
                "lastName": "Immobile",
                "dateOfBirth": "1990-02-20",
                "countryOfBirth": "Italy",
                "nationality": "Italy",
                "position": "Attacker",
                "shirtNumber": null,
                "lastUpdated": "2021-10-13T08:03:51Z"
            },
            "team": {
                "id": 110,
                "name": "SS Lazio",
                "shortName": "Lazio",
                "tla": "LAZ",
                "crest": "https://crests.football-data.org/110.svg",
                "address": "Via di Santa Cornelia, 1000 Formello 00060",
                "phone": "+39 (06) 976071",
                "website": "http://www.sslazio.it",
                "email": "segreteria.lazio@sslazio.it",
                "founded": 1900,
                "clubColors": "White / Sky Blue",
                "venue": "Stadio Olimpico",
                "lastUpdated": "2020-11-26T02:19:41Z"
            },
            "goals": 20,
            "assists": 6,
            "penalties": 4
        },
        {
            "player": {
                "id": 2236,
                "name": "Simeon Nwankwo",
                "firstName": "Simeon",
                "lastName": null,
                "dateOfBirth": "1992-05-07",
                "countryOfBirth": "Nigeria",
                "nationality": "Nigeria",
                "position": "Attacker",
                "shirtNumber": null,
                "lastUpdated": "2020-09-07T21:10:48Z"
            },
            "team": {
                "id": 472,
                "name": "FC Crotone",
                "shortName": "Crotone",
                "tla": "CRO",
                "crest": "https://crests.football-data.org/472.png",
                "address": "Via Cutro Crotone 88900",
                "phone": "+39 (0962) 28 919",
                "website": "http://www.fccrotone.it",
                "email": "info@fccrotone.it",
                "founded": 1923,
                "clubColors": "Blue / Red",
                "venue": "Stadio Ezio Scida",
                "lastUpdated": "2022-03-20T17:52:58Z"
            },
            "goals": 20,
            "assists": 2,
            "penalties": 8
        },
        {
            "player": {
                "id": 2092,
                "name": "Lorenzo Insigne",
                "firstName": "Lorenzo",
                "lastName": "Insigne",
                "dateOfBirth": "1991-06-04",
                "countryOfBirth": "Italy",
                "nationality": "Italy",
                "position": "Midfielder",
                "shirtNumber": null,
                "lastUpdated": "2021-10-13T08:03:51Z"
            },
            "team": {
                "id": 113,
                "name": "SSC Napoli",
                "shortName": "Napoli",
                "tla": "NAP",
                "crest": "https://crests.football-data.org/113.svg",
                "address": "Centro Tecnico di Castel Volturno, Via S.S. Domitana, Km 35 Castel Volturno 81030",
                "phone": "+39 (081) 5095344",
                "website": "http://www.sscnapoli.it",
                "email": "infocalcio@sscn.it",
                "founded": 1904,
                "clubColors": "Sky Blue / White",
                "venue": "Stadio San Paolo",
                "lastUpdated": "2020-11-26T02:19:45Z"
            },
            "goals": 19,
            "assists": 8,
            "penalties": 7
        },
        {
            "player": {
                "id": 3220,
                "name": "Lautaro Martínez",
                "firstName": "Lautaro Javier",
                "lastName": null,
                "dateOfBirth": "1997-08-22",
                "countryOfBirth": "Argentina",
                "nationality": "Argentina",
                "position": "Attacker",
                "shirtNumber": null,
                "lastUpdated": "2020-09-07T21:10:27Z"
            },
            "team": {
                "id": 108,
                "name": "FC Internazionale Milano",
                "shortName": "Inter",
                "tla": "INT",
                "crest": "https://crests.football-data.org/108.png",
                "address": "Corso Vittorio Emanuele II 9 Milano 20122",
                "phone": "+39 (02) 77151",
                "website": "http://www.inter.it",
                "email": "segreteriaccic@inter.it",
                "founded": 1908,
                "clubColors": "Blue / Black",
                "venue": "Stadio Giuseppe Meazza",
                "lastUpdated": "2021-11-24T14:55:58Z"
            },
            "goals": 17,
            "assists": 5,
            "penalties": 2
        },
        {
            "player": {
                "id": 2202,
                "name": "Domenico Berardi",
                "firstName": "Domenico",
                "lastName": null,
                "dateOfBirth": "1994-08-01",
                "countryOfBirth": "Italy",
                "nationality": "Italy",
                "position": "Attacker",
                "shirtNumber": null,
                "lastUpdated": "2020-09-07T21:10:46Z"
            },
            "team": {
                "id": 471,
                "name": "US Sassuolo Calcio",
                "shortName": "Sassuolo",
                "tla": "SAS",
                "crest": "https://crests.football-data.org/471.svg",
                "address": "Piazza Risorgimento, 47 Sassuolo 41049",
                "phone": "+39 (0536) 882645",
                "website": "http://www.sassuolocalcio.it",
                "email": "info@sassuolocalcio.it",
                "founded": 1920,
                "clubColors": "Green / Black",
                "venue": "Mapei Stadium - Città del Tricolore",
                "lastUpdated": "2021-04-12T13:07:30Z"
            },
            "goals": 17,
            "assists": 7,
            "penalties": 7
        },
        {
            "player": {
                "id": 1907,
                "name": "João Pedro Galvão",
                "firstName": "João Pedro Geraldino",
                "lastName": null,
                "dateOfBirth": "1992-03-09",
                "countryOfBirth": "Brazil",
                "nationality": "Italy",
                "position": "Midfielder",
                "shirtNumber": null,
                "lastUpdated": "2022-01-25T07:53:22Z"
            },
            "team": {
                "id": 104,
                "name": "Cagliari Calcio",
                "shortName": "Cagliari",
                "tla": "CAG",
                "crest": "https://crests.football-data.org/104.svg",
                "address": "Viale la Plaia 15 Cagliari 09123",
                "phone": "+39 (070) 604 201",
                "website": "http://www.cagliaricalcio.net",
                "email": "info@cagliaricalcio.net",
                "founded": 1920,
                "clubColors": "Red / Navy Blue / White",
                "venue": "Sardegna Arena",
                "lastUpdated": "2020-11-26T02:23:05Z"
            },
            "goals": 16,
            "assists": 3,
            "penalties": 4
        }
    ]
}
Available filters for Scorers
Filter name	Possible values	Sample
season

An integer, like [\d]{4}

/?season=2021

matchday

An integer, like [\d]{2}

/?matchday=23

Again you can combine the season and matchday filter. That way you can easily compare the current scorer list with former years.
Matches
You can use the Match Subresource to fetch a list of matches that are pre-filtered by the competition. Typically you use this in a regular interval to update basic information like dates and scores.

Click here to see a sample implementation with some layers of plumbing and transformation code in between.

curl -XGET 'https://api.football-data.org/v4/competitions/DED/matches?matchday=23' -H "X-Auth-Token: UR_TOKEN"
{
    "filters": {
        "season": "2021",
        "matchday": "23"
    },
    "resultSet": {
        "count": 9,
        "first": "2022-02-19",
        "last": "2022-04-16",
        "played": 9
    },
    "competition": {
        "id": 2003,
        "name": "Eredivisie",
        "code": "DED",
        "type": "LEAGUE",
        "emblem": "https://crests.football-data.org/ED.png"
    },
    "matches": [ ... ]
}
You see the applied filters on the very top: by default the current season is used, as of writing this, this is season 2021/22. And we explicitly defined to return only matches of matchday 23. The resultSet node gives the boundaries of the match list, a count and how many matches are in status FINISHED. Last but not least the list of match items follows.

Available filters for Match Subresource
Filter name	Possible values	Sample
season

An integer, like [\d]{4}

/?season=2021

matchday

An integer, like [\d]{2}

/?matchday=23

status

Status enum

/?status=FINISHED

dateFrom

A date in format yyyy-MM-dd

/?dateFrom=2022-01-01

dateTo

A date in format yyyy-MM-dd

/?dateTo=2022-01-10

stage

Stage enum, like defined at the very bottom

/?stage=QUARTER_FINALS

group

Group enum, like defined at the very bottom

/?group=GROUP_F

Teams
You can use the Team Subresource to fetch a list of teams that are pre-filtered by the a competition.

curl -XGET 'https://api.football-data.org/v4/competitions/BL1/teams' -H "X-Auth-Token: UR_TOKEN"
I omit the json response here as the structure is the very same as any team list shown here for instance.

Available filters for Team Subresource
Filter name	Possible values	Sample
season

An integer, like [\d]{4}

/?season=2021

Enums
Some fields contain values that are defined by an Enum, which is useful to reveal, so here we go:

Attribute name	Possible values
stages

FINAL | THIRD_PLACE | SEMI_FINALS | QUARTER_FINALS | LAST_16 | LAST_32 | LAST_64 | ROUND_4 | ROUND_3 | ROUND_2 | ROUND_1 | GROUP_STAGE | PRELIMINARY_ROUND | QUALIFICATION | QUALIFICATION_ROUND_1 | QUALIFICATION_ROUND_2 | QUALIFICATION_ROUND_3 | PLAYOFF_ROUND_1 | PLAYOFF_ROUND_2 | PLAYOFFS | REGULAR_SEASON | CLAUSURA | APERTURA | CHAMPIONSHIP_ROUND | RELEGATION_ROUND

group

GROUP_A | GROUP_B | GROUP_C | GROUP_D | GROUP_E | GROUP_F | GROUP_G | GROUP_H | GROUP_I | GROUP_J | GROUP_K | GROUP_L