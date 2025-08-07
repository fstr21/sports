Here is my plan for my app idea. 

 I would like to make a discord server that presents upcoming sports game predictions and tells the subscribers to the discord what are good bets to place. Typically I had something similar done through step by step python scripts for example 
 1_schedule.py - this would fetch the upcoming games and teams
 2_teamstats.py - this would fetch the team stats for those upcoming games
 3_playerstats.py - this would fetch the player stats for those teams for those upcoming games
 4_props_odds.py - this would fetch the props and odds for the teams and players for those upcoming games
 5_calculations.py - this would calculate each prop for each entry teams and players 
 6_recommendations.py - this would based on the calculations and the odds and props present which bets to take

 now all of those were runners and all of the logic for those were in a different directory with the runners and it was..just oK

 I have since learned that i might want to look into MCP (model context protocol) to maybe improve my plan and possibly even take it a step forward and use an LLM to also talk to the MCP to fetch some of the data. I was also told I would probalby need to run the mcp on a server remotely. So I guess I would use some sort of MCP proxy to add the different MCPs on to and access through there? I am not sure this is where i am confused. 

 I am not very technical at all, i am vibecoding all of this and using AI to help me with the tasks. 


an example of the endpoints from ESPN for the api MCP to look at 

WNBA
Scores: http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard

News: http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/news

All Teams: http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/teams

Specific Team: http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/teams/:team


i was told to maybe look into turning my rest api into its own mcp server  

I was told to look into https://github.com/MagicBeansAI/magictunnel