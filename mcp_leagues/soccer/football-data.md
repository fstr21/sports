Overview

On May 20, 2022 I released v4 for public use. I revised the entire reference documentation that you find here.

While v2 will remain available until further notice, I encourage you to migrate to v4. It's really worth it.


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