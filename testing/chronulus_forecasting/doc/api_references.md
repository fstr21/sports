hronulus Python SDK
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
width	str	Width of the generated context following CSS format. Default is "800px".


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
