Skip to content
logo
Chronulus SDK
0.0.14
Intro
Search

Get Started
API Reference
API Reference
Intro
Session
Agent
Attribute
Prediction
Environment
Table of contents
Core Components
Session
Agent
Normalized Forecaster
Binary Predictor
Chronulus Python SDK
Core Components
Session
Set your API Key
Provide broad stroke situational context on the goal of your organization and team motivating the task
Provide a description of the forecasting task to be accomplished
Agent
Normalized Forecaster
Provides scale-free forecast estimates that are normalized between 0.0 and 1.0.

Time Scales: hours, days, weeks
Estimates Range: [0.0, 1.0]
Binary Predictor
Gives robust probability estimates for open-ended questions with binary outcomes by leveraging a panel of experts for consensus. A Beta distribution is estimated over the expert opinions and return along with the underlying opinions and predictions.

Number of Experts: 2 to 30
Estimate Range: [0.0, 1.0]
Beta parameters: (alpha, beta)
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs









Skip to content
logo
Chronulus SDK
0.0.14
Retail - New Product Forecasting
Search

Get Started
API Reference
Get Started
Welcome to Chronulus
Create Account & API Key
Install / Upgrade
Usage Examples
Retail - New Product Forecasting
Hospitality - Hotel Bookings
Transportation - Project Feasibility
Table of contents
New Product Forecasting
Import Packages
Describe the Use Case
Describe a prediction input
Create a NormalizedForecaster agent
Get a Forecast for an Item
Predict Weekly
Explanation for weekly predictions
Predict Daily
Explanation for daily predictions
Retail
New Product Forecasting
Import Packages
# python imports
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
from matplotlib import pyplot as plt

# chronulus sdk imports
from chronulus import Session
from chronulus.estimator import NormalizedForecaster
from chronulus_core.types.attribute import ImageFromUrl
Describe the Use Case
Chronulus Agent flows are structured in STAR format:

Situation (Broad context about your use case)
Task (Specific details on the forecasting task)
Agent (Preforms the actions)
Result (Prediction or Forecast returned by the Agent)
To start, let's create a Session object that provides the Situation and Task context to the Chronulus Agent.

chronulus_session = Session(
    name="ASIN Prediction",

    situation="""Amazon is the largest ecommerce retailer with extensive 
    forecasting capability, but it does not yet have the ability to 
    forecast demand for new products that lack a sufficient history of 
    sales. 
    """,

    task="""We would like to forecast the demand for an ASIN, which is 
    Amazon's name for a SKU. A unique ASIN is assigned to individual 
    products, to product variants, and to product bundles. We would like 
    to predict seasonal demand for an ASIN in the US Marketplace. 
    """,

    env=dict(
        CHRONULUS_API_KEY="<YOUR-CHRONULUS-API-KEY>",
    )
)
Describe a prediction input
To help the Chronulus Agent make sense of your inputs, you will need to define the structure of your input for the agent.

We do this extending the pydantic BaseModel. Our agents currently handle simple input types including:

generic python types: str, int, float, and bool
Chronulus-provided attributes:
ImageFromUrl
Additionally, field should be annotated with a description using Field(description="your description"). This provides our agents with useful information about what to expect in the field.

class ASIN(BaseModel):
    brand: str = Field(description="The brand of the product")
    product_name: str = Field(description="The name of the product. This may include the brand and other descriptive info")
    product_details: str = Field(description="A long form description of the product and its characteristics / features")
    price: float = Field(description="The price of the ASIN in USD")
    product_images: List[ImageFromUrl] = Field(default=[], description="A list of image urls associated with this product")
Create a NormalizedForecaster agent
Next, we define a forecasting agent. The agent needs our session context (situation and task) and the description of our inputs.

nf_agent = NormalizedForecaster(
    session=chronulus_session,
    input_type=ASIN
)
Get a Forecast for an Item
Let's try this box of Ferrero Rocher chocolates as an example.

Below, we will fill in the product info by hand. Of course, if we worked at Amazon, we could do this all programmatically.

item_chocolate = ASIN(
    brand="Ferrero Rocher",
    product_name="Ferrero Rocher, 16 Count, Gourmet Milk Chocolate Hazelnut, Valentine's Chocolate, Individually Wrapped, 6.2 oz",
    product_details="""
    - GOURMET CHOCOLATE GIFT BOX: Share the indulgent taste of Ferrero Rocher with this 16-count heart-shaped gift box of individually wrapped chocolates for Valentine's Day gifting that they're sure to love
    -MILK CHOCOLATE HAZELNUT: A tempting combination made with a whole crunchy hazelnut dipped in delicious, creamy chocolate hazelnut filling and covered with milk chocolate, crispy wafers and gently roasted hazelnut pieces
    -CELEBRATE THE MOMENT: Share special moments with your family and friends, or take a moment just for you. Ferrero chocolates make indulgent treats that are great for unwinding after a long day
    -PREMIUM CHOCOLATE: Expertly crafted from premium gourmet chocolate, these timeless classics deliver decadent taste one exquisite bite at a time
    -THE PERFECT VALENTINE: These luxury chocolates make the perfect romantic gift for her or him this Valentine's Day
    """,
    price=10.49,
    product_images=[
        ImageFromUrl(url='https://m.media-amazon.com/images/I/91QLXefin2L._SX569_.jpg'),
        ImageFromUrl(url='https://m.media-amazon.com/images/I/91AOFusWGeL._SX569_.jpg'),
        ImageFromUrl(url='https://m.media-amazon.com/images/I/81EOAzOaNSL._SL1500_.jpg'),
    ]
)
We have included a few of the product image url as inputs for our forecasting agent to read and use:

  
Predict Weekly
forecast_start_date = datetime(2025, 1, 9)
req = nf_agent.queue(item_chocolate, start_dt=forecast_start_date, weeks=52, note_length=(5, 7))
predictions = nf_agent.get_predictions(req.request_id)
> predictions[0].to_pandas()

         date     y_hat
0  2025-01-12  0.649931
1  2025-01-19  0.779941
2  2025-01-26  0.890004
3  2025-02-02  0.950051
4  2025-02-09  0.980053
...
47 2025-12-07  0.780181
48 2025-12-14  0.850078
49 2025-12-21  0.900191
50 2025-12-28  0.750021
51 2026-01-04  0.679949
> fig, ax = plt.subplots(1,1, figsize=(12, 4))
> predictions[0].to_pandas().plot(ax=ax)

Explanation for weekly predictions
> predictions[0].text
Ferrero Rocher's premium chocolate gift box shows strong seasonal demand patterns centered around key romantic and holiday occasions. The Valentine's Day theme and heart-shaped packaging make this a particularly strong seller in the weeks leading up to February 14th, with peak demand occurring 1-2 weeks before the holiday. Secondary peaks occur during the winter holiday season (November-December) and Mother's Day period. The premium positioning and reasonable price point ($10.49) make it an attractive gift option, while the 16-count size is ideal for romantic gifting. The brand's strong reputation and product quality support consistent baseline demand throughout the year, though significantly lower than seasonal peaks. The individually wrapped format and luxury presentation also drive gift-giving during other special occasions and celebrations throughout the year.

Predict Daily
forecast_start_date = datetime(2025, 1, 9)
req = nf_agent.queue(item_chocolate, start_dt=forecast_start_date, days=60, note_length=(5, 7))
predictions = nf_agent.get_predictions(req.request_id)
> predictions[0].to_pandas()

         date     y_hat
0  2025-01-09  0.119964
1  2025-01-10  0.125001
2  2025-01-11  0.130098
3  2025-01-12  0.134989
4  2025-01-13  0.139822
...
55 2025-03-05  0.069831
56 2025-03-06  0.059999
57 2025-03-07  0.050010
58 2025-03-08  0.040116
59 2025-03-09  0.030057
> fig, ax = plt.subplots(1,1, figsize=(12, 4))
> predictions[0].to_pandas().plot(ax=ax)

Explanation for daily predictions
> predictions[0].text
Ferrero Rocher's heart-shaped Valentine's gift box traditionally experiences strong seasonal demand leading up to Valentine's Day. Based on its premium positioning and romantic gift appeal, we expect demand to start building gradually from early January, with acceleration beginning around January 20th. Peak demand should occur 3-5 days before Valentine's Day as consumers make their romantic gift purchases. The product's moderate price point of $10.49 makes it an accessible luxury gift option. After Valentine's Day, demand will decline sharply but maintain some baseline as the chocolates remain desirable for general consumption and small gifts. The heart-shaped packaging may limit post-Valentine's appeal, leading to lower sustained demand in late February and early March.

Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs



Skip to content
logo
Chronulus SDK
0.0.14
Environment
Search

Get Started
API Reference
API Reference
Intro
Session
Agent
Attribute
Prediction
Environment
Table of contents
Env
BaseEnv
get_default_env_path
get_default_headers
chronulus.environment
Env
Bases: BaseSettings

Environment settings class for managing API configuration.

This class handles environment variables and configuration for the Chronulus API, with support for loading from environment files.

Attributes:

Name	Type	Description
API_URI	str	The URI for the Chronulus API endpoint.
CHRONULUS_API_KEY	str or None	The API key for authentication. Defaults to the value in CHRONULUS_API_KEY environment variable.
Notes
Configuration is loaded from environment files in order of precedence, with the default.env file serving as the base configuration.

Source code in src/chronulus/environment.py
BaseEnv
Base class for environment-aware components.

This class provides basic environment configuration and header management for API interactions.

Parameters:

Name	Type	Description	Default
**kwargs		Keyword arguments to pass to the Env initialization.	{}
Attributes:

Name	Type	Description
env	Env	The environment settings instance.
headers	dict	Default headers for API requests, including authentication.
Source code in src/chronulus/environment.py
get_default_env_path()
Get the path to the default environment file in the package.

Returns:

Type	Description
str	The absolute path to the default.env file.
Source code in src/chronulus/environment.py
get_default_headers(env)
Generate default headers for API requests.

Parameters:

Name	Type	Description	Default
env	Env	The environment settings instance containing the API key.	required
Returns:

Type	Description
dict	A dictionary containing the X-API-Key header with the API key.
Source code in src/chronulus/environment.py
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs





Skip to content
logo
Chronulus SDK
0.0.14
Prediction
Search

Get Started
API Reference
API Reference
Intro
Session
Agent
Attribute
Prediction
Environment
Table of contents
Prediction
id
Forecast
data
text
to_json
to_pandas
NormalizedForecast
to_rescaled_forecast
RescaledForecast
from_forecast
BetaParams
ExpertOpinion
prob
text
BinaryPair
prob_a
prob
text
BinaryPrediction
opinion_set
prob_a
prob
text
to_dict
BinaryPredictionSet
to_dict
chronulus.prediction
Prediction
A class representing the output of a prediction request

Parameters:

Name	Type	Description	Default
_id	str	Unique identifier for the prediction.	required
Attributes:

Name	Type	Description
_id	str	Unique identifier for the prediction.
Source code in src/chronulus/prediction.py
id property
Get the unique identifier for the prediction

Forecast
Bases: Prediction

A class representing the output of a prediction request, containing both numerical results and explanatory text.

This class encapsulates the prediction results returned from the chronulus API, including a unique identifier, descriptive text, and the numerical predictions in a pandas DataFrame format.

Parameters:

Name	Type	Description	Default
_id	str	Unique identifier for the prediction.	required
text	str	Descriptive text or notes explaining the prediction results.	required
data	dict	JSON-Split formatted dictionary containing the prediction results.	required
Attributes:

Name	Type	Description
_id	str	Unique identifier for the prediction.
_text	str	Explanatory text describing the prediction results.
_data	dict	JSON-Split formatted dictionary containing the prediction results.
Source code in src/chronulus/prediction.py
data property
Get the forecast data after the transformation defined by this forecast

text property
Get the forecast explanation after the transformation defined by this forecast

to_json(orient='columns')
Convert the forecast data to JSON format with specified orientation.

Parameters:

Name	Type	Description	Default
orient	str	Data orientation for the JSON output. Options are:
'split': Original JSON-split format
'rows': List of dictionaries, each representing a row
'columns': Dictionary of lists, each representing a column Default is 'columns'.
'columns'
Returns:

Type	Description
dict or list	Forecast data in the specified JSON format:
For 'split': Original JSON-split dictionary
For 'rows': List of row dictionaries
For 'columns': Dictionary of column arrays
Examples:

>>> # Get data in columns format
>>> json_cols = forecast.to_json(orient='columns')
>>> # Get data in rows format
>>> json_rows = forecast.to_json(orient='rows')
Source code in src/chronulus/prediction.py
to_pandas()
Convert the forecast data to a pandas DataFrame.

The first column is automatically set as the index of the resulting DataFrame. Typically, this is a timestamp or date column.

Returns:

Type	Description
DataFrame	DataFrame containing the forecast data with the first column as index.
Raises:

Type	Description
ImportError	If pandas is not installed in the environment.
Examples:

>>> df = forecast.to_pandas()
>>> print(df.head())
           y_hat
date
2025-01-01   .12345
2025-01-02   .67890
Source code in src/chronulus/prediction.py
NormalizedForecast
Bases: Forecast

A class representing the output of a NormalizedForecast prediction request, containing both numerical results and explanatory text.

This class provides methods for operating on normalized forecast data.

Parameters:

Name	Type	Description	Default
_id	str	Unique identifier for the prediction.	required
text	str	Descriptive text or notes explaining the prediction results.	required
data	dict	JSON-Split formatted dictionary containing the prediction results.	required
y_min	float	The minimum value of the source scale.	0.0
y_max	float	The maximum value of the source scale	1.0
Source code in src/chronulus/prediction.py
to_rescaled_forecast(y_min=0.0, y_max=1.0, invert_scale=False)
Create a RescaledForecast instance from NormalizedForecast object.

This static method allows conversion from a generic Forecast to a RescaledForecast, applying the specified scaling parameters.

Parameters:

Name	Type	Description	Default
y_min	float	The minimum value of the target scale.	0.0
y_max	float	The maximum value of the target scale.	1.0
invert_scale	bool	Whether to invert the scale before rescaling.	False
Returns:

Type	Description
RescaledForecast	A new RescaledForecast instance containing the rescaled data.
Source code in src/chronulus/prediction.py
RescaledForecast
Bases: Forecast

A class representing a RescaledForecast prediction

This class provides methods for rescaling (denormalizing) a Forecast.

Parameters:

Name	Type	Description	Default
_id	str	Unique identifier for the prediction.	required
text	str	Descriptive text or notes explaining the prediction results.	required
data	dict	JSON-Split formatted dictionary containing the prediction results.	required
y_min	float	The minimum value of the source scale.	0.0
y_max	float	The maximum value of the source scale	1.0
invert_scale	bool	Should we invert the scale before rescaling?	False
Source code in src/chronulus/prediction.py
from_forecast(forecast, y_min=0.0, y_max=1.0, invert_scale=False) staticmethod
Convert the normalized forecast to a rescaled forecast with specified scale parameters.

This method creates a new RescaledForecast instance using the current forecast's data, allowing you to specify the target range and whether to invert the scale.

Parameters:

Name	Type	Description	Default
y_min	float	The minimum value of the target scale.	0.0
y_max	float	The maximum value of the target scale.	1.0
invert_scale	bool	Whether to invert the scale before rescaling.	False
Returns:

Type	Description
RescaledForecast	A new forecast instance with values rescaled to the specified range.
Source code in src/chronulus/prediction.py
BetaParams
Bases: BaseModel

Collection of alpha and beta parameters for a Beta distribution.

The intuition for alpha and beta is simple. Consider the batting average of a baseball player. Alpha represents the number of hits the player records over a period of time. Beta represents the number of at-bats without a hit. Together, the batting average of the player over that period of time is alpha / (alpha + beta), which is exactly the mean of the Beta distribution. Also, as the player accumulates more at-bats, we become more and more confident of their true batting average.

Parameters:

Name	Type	Description	Default
alpha	float	The shape parameter of successes	required
beta	float	The shape parameter of failures	required
Attributes:

Name	Type	Description
alpha	float	The shape parameter of successes
beta	float	The shape parameter of failures
Source code in src/chronulus/prediction.py
ExpertOpinion
Bases: BaseModel

The opinion of an expert agent consulted by BinaryPredictor

Parameters:

Name	Type	Description	Default
prob_a		The probability estimated or implied by complementation	required
question		The reframed question that the agent considered during estimation	required
notes		The text explanation justifying the expert's estimate	required
beta_params	BetaParams	The alpha and beta parameters for the Beta distribution over the opinion	required
Attributes:

Name	Type	Description
prob_a	float	The probability estimated or implied by complementation
question	str	The reframed question that the agent considered during estimation
notes	str	The text explanation justifying the expert's estimate
beta_params	BetaParams	The alpha and beta parameters for the Beta distribution over the opinion
Source code in src/chronulus/prediction.py
prob property
Gets the estimated probability and its complement.

text property
Gets the text representation of the expert opinion

BinaryPair
Bases: BaseModel

A pair of ExpertOpinions produced independently by the same expert agent

Each agent consider the question posed by the user from the original perspective as well as its complementary one. Considering both perspectives mitigates framing bias and improves the consistency of the probability estimate.

Parameters:

Name	Type	Description	Default
positive		The expert opinion of expert under the user's original perspective.	required
negative		The expert opinion of expert from the perspective complementary to the user's original perspective.	required
beta_params	BetaParams	The alpha and beta parameters for the consensus Beta distribution over both opinions	required
Attributes:

Name	Type	Description
positive	ExpertOpinion	The expert opinion of expert under the user's original perspective.
negative	ExpertOpinion	The expert opinion of expert from the perspective complementary to the user's original perspective.
beta_params	BetaParams	The alpha and beta parameters for the consensus Beta distribution over both opinions
Source code in src/chronulus/prediction.py
prob_a property
Get the consensus probability of the expert opinion pair.

prob property
Get the consensus probability and its complement over the expert opinion pair.

text property
Gets the text representation of the pair of expert opinions

BinaryPrediction
Bases: Prediction

A class representing the output of a prediction request, containing both numerical results and explanatory text.

This class encapsulates the prediction results returned from the chronulus API, including a unique identifier, descriptive text, and the numerical predictions in a pandas DataFrame format.

Parameters:

Name	Type	Description	Default
_id	str	Unique identifier for the prediction.	required
opinion_set	BinaryPair	A set of opinions provided by the expert	required
Attributes:

Name	Type	Description
_id	str	Unique identifier for the prediction.
Source code in src/chronulus/prediction.py
opinion_set property
Gets the set of opinions provided by the expert.

prob_a property
Get the consensus probability of the expert opinion set.

prob property
Get the consensus probability and its complement over the expert opinion set.

text property
Get the text representation of the expert opinion set.

to_dict()
Convert the prediction to a python dict

Returns:

Type	Description
dict	A python dict containing the prediction results.
Source code in src/chronulus/prediction.py
BinaryPredictionSet
A collection of BinaryPrediction results from BinaryPredictor

The class provides access to aggregate functions over the collection predictions, including access to the Beta distribution estimated over the underlying predictions.

Parameters:

Name	Type	Description	Default
predictions	List[BinaryPrediction]	The list of BinaryPredictions for each expert	required
beta_params	BetaParams	The alpha and beta parameters for the Beta distribution	required
Source code in src/chronulus/prediction.py
to_dict()
Convert the prediction set to a python dict

Returns:

Type	Description
dict	A python dict containing the prediction set results.
Source code in src/chronulus/prediction.py
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs



Skip to content
logo
Chronulus SDK
0.0.14
Image
Search

Get Started
API Reference
API Reference
Intro
Session
Agent
Attribute
Image
PDF
Text
Prediction
Environment
Table of contents
Image
ImageFromBytes
ImageFromFile
ImageFromUrl
chronulus_core.types.attribute
Image
Bases: BaseModel

Attribute to upload an image from base64 encoded string

The image should be provided as a base64 encoded string and the PIL image type specified

Parameters:

Name	Type	Description	Default
type	str	The PIL image type, e.g., PNG, JPEG, etc.	required
data	str	The base64 encoded image string	required
Attributes:

Name	Type	Description
type	str	The PIL image type, e.g., PNG, JPEG, etc.
data	str	The base64 encoded image string
Source code in src2/chronulus_core/types/attribute.py
ImageFromBytes
Bases: BaseModel

Attribute to upload an image from bytes

The image should be provided in raw bytes and the PIL image type specified

Parameters:

Name	Type	Description	Default
image_bytes	bytes	raw bytes of the image	required
type	str	The PIL image type, e.g., PNG, JPEG, etc.	required
Attributes:

Name	Type	Description
image_bytes	bytes	raw bytes of the image
type	str	The PIL image type, e.g., PNG, JPEG, etc.
data	Optional[str]	The base64 encoded image string
Source code in src2/chronulus_core/types/attribute.py
ImageFromFile
Bases: BaseModel

Attribute to upload an image from a local file

The image should be accessible in your local file system by the client

Parameters:

Name	Type	Description	Default
file_path	str	Path to image file, e.g., '/path/to/image.jpg'	required
type	Optional[str]	The PIL image type, e.g., PNG, JPEG, etc.	required
Attributes:

Name	Type	Description
file_path	str	Path to image file, e.g., '/path/to/image.jpg'
type	Optional[str]	The PIL image type, e.g., PNG, JPEG, etc.
data	Optional[str]	The base64 encoded image string
Source code in src2/chronulus_core/types/attribute.py
ImageFromUrl
Bases: BaseModel

Attribute to fetch an image from a specified remote URL

The remote URL should be publicly accessible otherwise our systems will fail to retrieve it.

Parameters:

Name	Type	Description	Default
url	str	URL of the remote image	required
type	Optional[str]	The PIL image type, e.g., PNG, JPEG, etc.	required
Attributes:

Name	Type	Description
url	str	URL of the remote image
type	Optional[str]	The PIL image type, e.g., PNG, JPEG, etc.
Source code in src2/chronulus_core/types/attribute.py
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs




Skip to content
logo
Chronulus SDK
0.0.14
PDF
Search

Get Started
API Reference
API Reference
Intro
Session
Agent
Attribute
Image
PDF
Text
Prediction
Environment
Table of contents
Pdf
PdfFromFile
chronulus_core.types.attribute
Pdf
Bases: BaseModel

Attribute to upload a PDF from a base64 encoded string

The PDF should be provided as a base64 encoded string

Parameters:

Name	Type	Description	Default
data	str	The base64 encoded PDF	required
Attributes:

Name	Type	Description
data	str	The base64 encoded PDF
Source code in src2/chronulus_core/types/attribute.py
PdfFromFile
Bases: BaseModel

Attribute to upload PDF from a local file

The PDF should be accessible in your local file system by the client

Parameters:

Name	Type	Description	Default
file_path	str	Path to PDF file, e.g., '/path/to/doc.pdf'	required
Attributes:

Name	Type	Description
file_path	str	Path to PDF file, e.g., '/path/to/doc.pdf'
data	Optional[str]	The base64 encoded PDF
Source code in src2/chronulus_core/types/attribute.py
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs




Skip to content
logo
Chronulus SDK
0.0.14
Text
Search

Get Started
API Reference
API Reference
Intro
Session
Agent
Attribute
Image
PDF
Text
Prediction
Environment
Table of contents
Text
TextFromFile
chronulus_core.types.attribute
Text
Bases: BaseModel

Attribute to upload a large text document

Parameters:

Name	Type	Description	Default
data	str	The content of the large text document	required
Attributes:

Name	Type	Description
data	str	The content of the large text document
Source code in src2/chronulus_core/types/attribute.py
TextFromFile
Bases: BaseModel

Attribute to upload a text document from a local file

The text should be accessible in your local file system by the client

Parameters:

Name	Type	Description	Default
file_path	str	Path to text file, e.g., '/path/to/text.txt'	required
Attributes:

Name	Type	Description
file_path	str	Path to text file, e.g., '/path/to/text.txt'
data	Optional[str]	The content of the large text document
Source code in src2/chronulus_core/types/attribute.py
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs



Skip to content
logo
Chronulus SDK
0.0.14
Base
Search

Get Started
API Reference
API Reference
Intro
Session
Agent
Base
BinaryPredictor
NormalizedForecaster
Attribute
Prediction
Environment
Table of contents
Estimator
__init__
chronulus.estimator.base
Estimator
Base class for implementing estimators that process data through the API.

This class provides the foundation for creating specific estimators by handling session management and input type validation. Subclasses should implement specific estimation logic while inheriting the base functionality.

Attributes:

Name	Type	Description
estimator_name	str	Name identifier for the estimator. Default is "EstimatorBase".
estimator_version	str	Version string for the estimator. Default is "1".
prediction_version	str	Version string for the prediction. Set to "1".
estimator_id	None	Identifier for a specific estimator instance, initialized as None.
session	Session	Session instance used for API communication.
input_type	Type[BaseModelSubclass]	Pydantic model class used for input validation.
Notes
The BaseModelSubclass type variable ensures that input_type must be a subclass of pydantic.BaseModel, enabling automatic input validation.

Source code in src/chronulus/estimator/base.py
__init__(session, input_type)
Parameters:

Name	Type	Description	Default
session	Session	Active session instance for API communication.	required
input_type	Type[BaseModelSubclass]	Pydantic model class that defines the expected input data structure.	required
Source code in src/chronulus/estimator/base.py
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs



Skip to content
logo
Chronulus SDK
0.0.14
BinaryPredictor
Search

Get Started
API Reference
API Reference
Intro
Session
Agent
Base
BinaryPredictor
NormalizedForecaster
Attribute
Prediction
Environment
Table of contents
BinaryPredictor
create
estimate_usage
get_predictions_static
get_request_predictions
get_request_predictions_static
queue
chronulus.estimator.binary_predictor
BinaryPredictor
Bases: Estimator

A prediction agent that estimates the probability binary events / outcomes.

This class handles the creation, queuing, and retrieval of binary event predictions and explanatory notes.

Parameters:

Name	Type	Description	Default
session	Session	Active session instance for API communication.	required
input_type	Type[BaseModelSubclass]	Pydantic model class that defines the expected input data structure.	required
Attributes:

Name	Type	Description
estimator_name	str	Name identifier for the estimator. Set to "BinaryPredictor".
estimator_version	str	Version string for the estimator. Set to "1".
prediction_version	str	Version string for the prediction. Set to "1".
estimator_id	str or None	Unique identifier assigned by the API after creation.
Source code in src/chronulus/estimator/binary_predictor.py
create()
Initialize the agent instance with the API.

Creates a agent instance on the API side with the specified input schema. The schema is serialized before transmission.

Raises:

Type	Description
ValueError	If the API fails to create the estimator or returns an invalid response.
Source code in src/chronulus/estimator/binary_predictor.py
estimate_usage(item, num_experts=2, note_length=(3, 5), use_llm_context_caching=True)
Get an estimate for the usage over an item and agent parameters

Parameters:

Name	Type	Description	Default
item	BaseModelSubclass	The input data conforming to the specified input_type schema.	required
num_experts	int	Number of experts to consult for the prediction request. (minimum=2, maximum=30, default=2)	2
note_length	tuple[int, int]	Desired length range (number of sentences) for explanatory notes (min, max), by default (3, 5).	(3, 5)
use_llm_context_caching	bool	Whether to use context caching in the LLM layer. (default = True).	True
Returns:

Type	Description
UsageEstimateResponse	Response object containing the usage estimate
Raises:

Type	Description
TypeError	If the provided item doesn't match the expected input_type.
Source code in src/chronulus/estimator/binary_predictor.py
get_predictions_static(prediction_ids, env=None, verbose=True) staticmethod
Static method to retrieve a batch of predictions with prediction_ids.

Parameters:

Name	Type	Description	Default
prediction_ids	List[str]	A list of prediction ids	required
env	dict	Environment configuration dictionary. If None, default environment will be used.	None
verbose	bool	Print feedback to stdout if True. Default: True	True
Returns:

Type	Description
BinaryPredictionSet or None	A BinaryPredictionSet containing predictions and explanations from each expert, None if the predictions couldn't be retrieved.
Source code in src/chronulus/estimator/binary_predictor.py
get_request_predictions(request_id, try_every=3, max_tries=20)
Retrieve predictions for a queued request.

Parameters:

Name	Type	Description	Default
request_id	str	The ID of the queued prediction request.	required
try_every	int	Seconds to wait between retry attempts, by default 3.	3
max_tries	int	Maximum number of retry attempts, by default 20.	20
Returns:

Type	Description
Union[BinaryPredictionSet, dict, None]	A BinaryPredictionSet containing predictions and explanations from each expert
Raises:

Type	Description
Exception	If the maximum retry limit is exceeded or if an API error occurs.
Source code in src/chronulus/estimator/binary_predictor.py
get_request_predictions_static(request_id, try_every=3, max_tries=20, env=None, verbose=True) staticmethod
Retrieve predictions for a queued request.

Parameters:

Name	Type	Description	Default
request_id	str	The ID of the queued prediction request.	required
try_every	int	Seconds to wait between retry attempts, by default 3.	3
max_tries	int	Maximum number of retry attempts, by default 20.	20
env	dict	Environment configuration dictionary. If None, default environment will be used.	None
verbose	bool	Print feedback to stdout if True. Default: True	True
Returns:

Type	Description
Union[BinaryPredictionSet, dict, None]	A BinaryPredictionSet containing predictions and explanations from each expert
Raises:

Type	Description
Exception	If the maximum retry limit is exceeded or if an API error occurs.
Source code in src/chronulus/estimator/binary_predictor.py
queue(item, num_experts=2, note_length=(3, 5), use_llm_context_caching=True)
Queue a prediction request for processing.

Parameters:

Name	Type	Description	Default
item	BaseModelSubclass	The input data conforming to the specified input_type schema.	required
num_experts	int	Number of experts to consult for the prediction request. (minimum=2, maximum=30, default=2)	2
note_length	tuple[int, int]	Desired length range (number of sentences) for explanatory notes (min, max), by default (3, 5).	(3, 5)
use_llm_context_caching	bool	Whether to use context caching in the LLM layer. (default = True).	True
Returns:

Type	Description
QueuePredictionResponse	Response object containing the request status and ID.
Raises:

Type	Description
TypeError	If the provided item doesn't match the expected input_type.
Source code in src/chronulus/estimator/binary_predictor.py
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs



Skip to content
logo
Chronulus SDK
0.0.14
NormalizedForecaster
Search

Get Started
API Reference
API Reference
Intro
Session
Agent
Base
BinaryPredictor
NormalizedForecaster
Attribute
Prediction
Environment
Table of contents
NormalizedForecaster
create
get_prediction
get_prediction_static
get_predictions
predict
queue
chronulus.estimator.normalized_forecaster
NormalizedForecaster
Bases: Estimator

A forecasting agent that generates time series predictions normalized between 0 and 1.

This class handles the creation, queuing, and retrieval of normalized time series forecasts through the API. It supports various time horizons and can generate both numerical predictions and explanatory notes.

Parameters:

Name	Type	Description	Default
session	Session	Active session instance for API communication.	required
input_type	Type[BaseModelSubclass]	Pydantic model class that defines the expected input data structure.	required
Attributes:

Name	Type	Description
estimator_name	str	Name identifier for the estimator. Set to "NormalizedForecaster".
estimator_version	str	Version string for the estimator. Set to "1".
prediction_version	str	Version string for the prediction. Set to "1".
estimator_id	str or None	Unique identifier assigned by the API after creation.
Source code in src/chronulus/estimator/normalized_forecaster.py
create()
Initialize the forecaster instance with the API.

Creates a new forecaster instance on the API side with the specified input schema. The schema is serialized and base64 encoded before transmission.

Raises:

Type	Description
ValueError	If the API fails to create the estimator or returns an invalid response.
Source code in src/chronulus/estimator/normalized_forecaster.py
get_prediction(prediction_id)
Retrieve a single prediction by its ID.

Parameters:

Name	Type	Description	Default
prediction_id	str	Unique identifier for the prediction.	required
Returns:

Type	Description
Forecast or None	Forecast object containing the forecast results and notes if successful, None if the prediction couldn't be retrieved.
Source code in src/chronulus/estimator/normalized_forecaster.py
get_prediction_static(prediction_id, env=None, verbose=True) staticmethod
Static method to retrieve a single prediction with a prediction_id and session_id or session.

Parameters:

Name	Type	Description	Default
prediction_id	str	Unique identifier for the prediction.	required
env	dict	Environment configuration dictionary. If None, default environment will be used.	None
verbose	bool	Print feedback to stdout if True. Default: True	True
Returns:

Type	Description
NormalizedForecast or None	NormalizedForecast object containing the forecast results and notes if successful, None if the prediction couldn't be retrieved.
Source code in src/chronulus/estimator/normalized_forecaster.py
get_predictions(request_id, try_every=3, max_tries=20)
Retrieve predictions for a queued request.

Parameters:

Name	Type	Description	Default
request_id	str	The ID of the queued prediction request.	required
try_every	int	Seconds to wait between retry attempts, by default 3.	3
max_tries	int	Maximum number of retry attempts, by default 20.	20
Returns:

Type	Description
list[NormalizedForecast] or dict	List of NormalizedForecast objects if successful, or error dictionary if failed.
Raises:

Type	Description
Exception	If the maximum retry limit is exceeded or if an API error occurs.
Source code in src/chronulus/estimator/normalized_forecaster.py
predict(item, start_dt=None, weeks=None, days=None, hours=None, note_length=(3, 5))
Convenience method to queue and retrieve predictions in a single call.

This method combines the queue and get_predictions steps into a single operation, waiting for the prediction to complete before returning.

Parameters:

Name	Type	Description	Default
item	BaseModelSubclass	The input data conforming to the specified input_type schema.	required
start_dt	datetime	The starting datetime for the forecast.	None
weeks	int	Number of weeks to forecast.	None
days	int	Number of days to forecast.	None
hours	int	Number of hours to forecast.	None
note_length	tuple[int, int]	Desired length range for explanatory notes (min, max), by default (3, 5).	(3, 5)
Returns:

Type	Description
NormalizedForecast or None	The completed prediction if successful, None otherwise.
Source code in src/chronulus/estimator/normalized_forecaster.py
queue(item, start_dt, weeks=None, days=None, hours=None, note_length=(3, 5))
Queue a prediction request for processing.

Parameters:

Name	Type	Description	Default
item	BaseModelSubclass	The input data conforming to the specified input_type schema.	required
start_dt	datetime	The starting datetime for the forecast.	required
weeks	int	Number of weeks to forecast.	None
days	int	Number of days to forecast.	None
hours	int	Number of hours to forecast.	None
note_length	tuple[int, int]	Desired length range (number of sentences) for explanatory notes (min, max), by default (3, 5).	(3, 5)
Returns:

Type	Description
QueuePredictionResponse	Response object containing the request status and ID.
Raises:

Type	Description
TypeError	If the provided item doesn't match the expected input_type.
Source code in src/chronulus/estimator/normalized_forecaster.py
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs


Skip to content
logo
Chronulus SDK
0.0.14
Session
Search

Get Started
API Reference
API Reference
Intro
Session
Session
Risk Assessment
Agent
Attribute
Prediction
Environment
Table of contents
Session
create
load_from_saved_session
risk_scorecard
chronulus.session
Session
Bases: BaseEnv

A class to manage API sessions for handling specific situations and tasks.

Parameters:

Name	Type	Description	Default
name	str	The name identifier for the session.	required
situation	str	The context or situation description for the session.	required
task	str	The task to be performed in this session.	required
session_id	str	Unique identifier for an existing session. If None, a new session will be created.	None
env	dict	Environment configuration dictionary. If None, default environment will be used.	None
verbose	bool	
Print feedback to stdout if True. Default: True
True
Attributes:

Name	Type	Description
session_version	str	Version string for the Session. Set to "1".
name	str	The name identifier for the session.
situation	str	The context or situation description.
task	str	The task description.
session_id	str	Unique identifier for the session.
scorecard	Optional[Scorecard]	Risk assessment scorecard for this session.
Source code in src/chronulus/session.py
create()
Create a new session using the API.

This method sends a POST request to create a new session with the specified name, situation, and task. Upon successful creation, the session_id is updated with the response from the API.

Raises:

Type	Description
Exception	If the API key is invalid or not active (403 status code). If the session creation fails with any other status code.
Source code in src/chronulus/session.py
load_from_saved_session(session_id, env=None, verbose=True) staticmethod
Load an existing session using a session ID.

Parameters:

Name	Type	Description	Default
session_id	str	The unique identifier of the session to load.	required
env	dict	Environment configuration dictionary. If None, default environment will be used.	None
verbose	bool	Print feedback to stdout if True. Default: True	True
Returns:

Type	Description
Session	A new Session instance initialized with the saved session data.
Raises:

Type	Description
ValueError	If the session loading fails or if the response cannot be parsed.
Source code in src/chronulus/session.py
risk_scorecard(width='800px')
Retrieves the risk scorecard for the current session

This method retrieves the risk scorecard (Rostami-Tabar et al., 2024) for the current session and returns an HTML formatted representation of the risk scorecard. HTML can be easily open in a browser, embedded in Markdown, or displayed inline Jupyter notebooks.

Example

from IPython.display import Markdown, display
scorecard_html = session.risk_scorecard()
display(Markdown(scorecard_html))
Citations
Rostami-Tabar, B., Greene, T., Shmueli, G., & Hyndman, R. J. (2024). Responsible forecasting: identifying and typifying forecasting harms. arXiv preprint arXiv:2411.16531.

Parameters:

Name	Type	Description	Default
width	str	Width of the generated context following CSS format. Default is "800px".	'800px'
Source code in src/chronulus/session.py
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs

Skip to content
logo
Chronulus SDK
0.0.14
Risk Assessment
Search

Get Started
API Reference
API Reference
Intro
Session
Session
Risk Assessment
Agent
Attribute
Prediction
Environment
Table of contents
RiskCategory
Scorecard
chronulus_core.types.risk
RiskCategory
Bases: BaseModel

Describes a Risk Category referenced in a risk Scorecard

Parameters:

Name	Type	Description	Default
name	str	Name of the category	required
score		Numeric score of the category	required
max_score	float	The maximum score achievable in this category	required
risks		The list of risk factors identified in this category	required
Source code in src2/chronulus_core/types/risk.py
Scorecard
Bases: BaseModel

The risk assessment scorecard for a Session

Our risk scorecard is based on the Responsible Forecast framework (Rostami-Tabar et al., 2024).

Citations
Rostami-Tabar, B., Greene, T., Shmueli, G., & Hyndman, R. J. (2024). Responsible forecasting: identifying and typifying forecasting harms. arXiv preprint arXiv:2411.16531.

Parameters:

Name	Type	Description	Default
categories	List[RiskCategory]	A list of categories	required
assessment		Overall assessment of the risk for the session	required
recommendation	str	Recommendations and risk mitigation strategies for risks highlighted in the assessment	required
Attributes:

Name	Type	Description
categories	List[RiskCategory]	A list of categories
assessment	str	Overall assessment of the risk for the session
recommendation	str	Recommendations and risk mitigation strategies for risks highlighted in the assessment
Source code in src2/chronulus_core/types/risk.py
Copyright © 2024-2025 Chronulus AI Inc. All rights reserved
Made with Material for MkDocs

