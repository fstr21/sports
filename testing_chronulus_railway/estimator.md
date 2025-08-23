Here is a complete code example showing how to set up an agent, create an item to predict, and get a cost estimate for it.

Python

# python imports
from pydantic import BaseModel, Field

# chronulus sdk imports
from chronulus import Session
from chronulus.estimator import BinaryPredictor

# --- 1. Set up your Session and define your input data structure ---
# This part is similar to a normal prediction request.

chronulus_session = Session(
    name="Sports Betting Analysis",
    situation="""
    We are a sports analytics firm trying to predict the outcome of MLB games.
    """,
    task="""
    Predict the probability that the home team will win the game based on
    the provided data.
    """,
    env=dict(
        CHRONULUS_API_KEY="<YOUR-CHRONULUS-API-KEY>",
    )
)

# Define the structure of your prediction input
class MLBGame(BaseModel):
    home_team: str = Field(description="The home team")
    away_team: str = Field(description="The away team")
    venue: str = Field(description="The stadium where the game is played")
    analyst_notes: str = Field(description="Any specific notes or context from an analyst")

# --- 2. Create the BinaryPredictor Agent ---
# This agent is linked to your session and input type.

predictor_agent = BinaryPredictor(
    session=chronulus_session,
    input_type=MLBGame
)

# --- 3. Create the specific item you want to analyze ---

game_to_predict = MLBGame(
    home_team="New York Yankees",
    away_team="Boston Red Sox",
    venue="Yankee Stadium",
    analyst_notes="Both teams are on a 3-game winning streak. Key pitchers are starting."
)


# --- 4. Call the .estimate_usage() method BEFORE queueing ---
# This is the key step. You pass the item and any parameters (like num_experts)
# to see how much the prediction would cost.

print("🔍 Getting usage estimate...")

# The estimate_usage method lets you test different parameters
usage_estimate = predictor_agent.estimate_usage(
    item=game_to_predict,
    num_experts=5, # You can change this number to see how it affects the cost
    note_length=(10, 15)
)

# --- 5. Review the estimate ---
# The response object contains the cost in "chrons".
# You would typically inspect the object to see its full structure.

if usage_estimate:
    # Assuming the response object has a 'cost' attribute for the chron value
    print(f"✅ Estimated Cost: {usage_estimate.cost} chrons")
    print("You can now decide whether to proceed with this cost.")

    # You could add logic here to only proceed if the cost is below a certain threshold
    # For example:
    # if usage_estimate.cost <= 100:
    #   request = predictor_agent.queue(item=game_to_predict, num_experts=5)
    #   print("Prediction has been queued!")
    # else:
    #   print("Cost is too high, not running prediction.")

else:
    print("❌ Could not retrieve a usage estimate.")

This approach, which uses the estimate_usage method from the BinaryPredictor class, gives you full control over your costs by allowing you to check the "chron" price before committing to a prediction.