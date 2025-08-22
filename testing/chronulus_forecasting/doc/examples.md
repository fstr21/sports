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




Hospitality
Hotel Revenue Management
Hospitality revenue management teams play a crucial role in maximizing a hotel group's profitability through strategic pricing and inventory control. They leverage booking curves and occupancy forecasts to optimize revenue per available room (RevPAR).

Let's take a look at how the Chronulus SDK can be utilized to estimate booking curves and occupancy based on contextual information.

Booking Curve
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
Describe a Hypothetical Booking Curve Use Case
booking_curve_session = Session(
    name="Hotel Booking Curve",

    situation="""The Marriott Americas Revenue Management team is responsible 
    for optimizing the revenue per available room at each of their locations 
    across the United States. 
    """,

    task="""
    Part of the rev-par optimization process requires the team to estimate the 
    booking curve for a hotel ahead of each stay night. Forecast the booking 
    curve for the hotel and stay-night provided.
    """,

    env=dict(
        CHRONULUS_API_KEY="<YOUR-CHRONULUS-API-KEY>",
    )
)
Define the HotelLocation data model
class HotelLocation(BaseModel):
    name: str = Field(description="The name of the hotel location")
    brand_umbrella: str = Field(description="The umbrella or brand name of the hotel")
    address: str = Field(description="The street address of the hotel location")
    stay_night: str = Field(description="The date of the stay-night we would like to forecast.")
    assumptions: str = Field(description="Any additional occupancy assumptions.")
    exterior_images: List[ImageFromUrl] = Field(default=[], description="A list of images of the exterior of the location")
Create a Booking Curve Agent
booking_curve_agent = NormalizedForecaster(
    session=booking_curve_session,
    input_type=HotelLocation,
)
NYE @ Midtown Manhattan
For this example, let's use the Courtyard location near Bryant Park in Midtown Manhattan.

# Fill in the metadata for the item or concept you want to predict
location = HotelLocation(
    name = "Courtyard New York Manhattan/Fifth Avenue",
    brand_umbrella = "Courtyard",
    address = "3 E 40th St, New York, NY 10016",
    stay_night = "2025-12-31", 
    assumptions = "Assume all rooms are operational and able to be booked",
    exterior_images = [
        ImageFromUrl(url='https://s3-media0.fl.yelpcdn.com/bphoto/uj-Jm4GpYhOPItnp7zmhzg/o.jpg'),
    ]
)
We have included an image of the exterior of the hotel:


Booking Curve Prediction
# How far in advance we would like to start the curve
days_out = 180

# We'll choose the forecast horizon start date by counting backward from the stay-night in our location
forecast_start_date = datetime.strptime(location.stay_night, "%Y-%m-%d") - timedelta(days=days_out)

req = booking_curve_agent.queue(location, start_dt=forecast_start_date, days=days_out, note_length=(5, 7))
predictions = booking_curve_agent.get_predictions(req.request_id)
> predictions[0].to_pandas()

            y_hat
date    
2025-07-04  0.152556
2025-07-05  0.154901
2025-07-06  0.157653
2025-07-07  0.159953
2025-07-08  0.162440
... ...
2025-12-26  0.999714
2025-12-27  0.999946
2025-12-28  1.000000
2025-12-29  0.999918
2025-12-30  1.000000
> fig, ax = plt.subplots(1,1, figsize=(12, 4))
> predictions[0].to_pandas().plot(ax=ax, ylim=(0,1))
Booking Curve for NYC in Midtown
Explanation for Booking Curve
> predictions[0].text
For this Courtyard property in Midtown Manhattan, I expect a strong booking curve leading up to New Year's Eve 2025. The hotel's prime location near Fifth Avenue and proximity to Times Square makes it highly desirable for the New Year's celebration. The booking pattern should show early corporate bookings (180 days out) followed by leisure travelers securing rooms for the holiday. I anticipate a steeper curve starting in October as availability becomes scarce. The curve will reflect typical seasonal patterns, with a slight dip in August-September before the holiday booking surge. Being a Courtyard brand in NYC, I expect a mix of business and leisure travelers, with leisure dominant for this particular stay date.

Occupancy
Describe a Hypothetical Booking Curve Use Case
occupancy_session = Session(
    name="Hotel Occupancy",

    situation="""
    The Marriott Americas Revenue Management team is responsible for optimizing 
    the revenue per available room at each of their locations across the United 
    States. 
    """,

    task="""
    Part of the rev-par optimization process requires the team to forecast the 
    occupancy (share of rooms booked) for a hotel location in advance given a 
    specified discount from the base room rate. Forecast the occupancy for the 
    given hotel location.
    """,

    env=dict(
        CHRONULUS_API_KEY="<YOUR-CHRONULUS-API-KEY>",
    )
)
Define a new HotelLocation data model with rate info
class HotelLocationWithRates(BaseModel):
    name: str = Field(description="The name of the hotel location")
    brand_umbrella: str = Field(description="The umbrella or brand name of the hotel")
    address: str = Field(description="The street address of the hotel location")
    assumptions: str = Field(description="Any additional occupancy assumptions.")
    exterior_images: List[ImageFromUrl] = Field(default=[], description="A list of images of the exterior of the location")
    base_rate: float = Field(description="The base rate for the room per night in USD")
    discount_schedule: str = Field(description="The schedule of discounts for this room")
Create a Occupancy Forecasting Agent
occupancy_agent = NormalizedForecaster(
    session=occupancy_session,
    input_type=HotelLocationWithRates,
)
Holiday Occupancy @ Midtown Manhattan
# Fill in the metadata for the item or concept you want to predict
location = HotelLocationWithRates(
    name = "Courtyard New York Manhattan/Fifth Avenue",
    brand_umbrella = "Courtyard",
    address = "3 E 40th St, New York, NY 10016",
    assumptions = "Assume all rooms are operational and able to be booked",
    exterior_images = [
        ImageFromUrl(url='https://s3-media0.fl.yelpcdn.com/bphoto/uj-Jm4GpYhOPItnp7zmhzg/o.jpg'),
    ],
    base_rate = 186.00,
    discount_schedule = "No discounts scheduled."
)
forecast_start_date = datetime(2025,12,1)

req = occupancy_agent.queue(location, start_dt=forecast_start_date, days=60, note_length=(5, 7))
predictions = occupancy_agent.get_predictions(req.request_id)
> predictions[0].to_pandas()

            y_hat
date    
2025-12-01  0.825056
2025-12-02  0.785107
2025-12-03  0.795039
2025-12-04  0.815057
2025-12-05  0.835018
... ...
2026-01-25  0.835024
2026-01-26  0.785020
2026-01-27  0.794938
2026-01-28  0.804942
2026-01-29  0.814925
> fig, ax = plt.subplots(1,1, figsize=(12, 4))
> predictions[0].to_pandas().plot(ylim=(0,1), ax=ax)
Occupancy for Midtown

Explanation for the Occupancy Forecast
> predictions[0].text
This Courtyard property's location in Midtown Manhattan near Fifth Avenue suggests strong business traveler occupancy during weekdays and tourist occupancy on weekends. The December-January period spans major holidays and events in NYC, including Christmas, New Year's, and winter shopping season. Given the prime location and moderate base rate of $186, I expect high occupancy throughout, with peaks around New Year's Eve and holiday shopping periods. The first two weeks of December should see strong business travel, followed by a slight dip mid-month, then rising sharply for holiday tourists. Early January typically sees lower occupancy due to post-holiday slowdown, gradually increasing as business travel resumes mid-month. Weekend occupancy rates will generally be higher than weekdays during the holiday season, reversing the typical pattern for this location.










Transportation
Project Feasibility Study and Analysis
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
Describe the Foot Traffic Prediction Use Case
For a description of the Interborough Express Project, we use publicly available information provided on the project by NYC MTA.

Let's set the goal of predicting foot traffic between the IBX and an existing subway line. None of these connection points exist yet, but that shouldn't stop us from estimating what the foot traffic might look like.

chronulus_session = Session(
    name="NYC Interborough Express Feasibility Study",

   situation="""The Interborough Express (IBX) is a transformative rapid transit 
    project that will connect currently underserved areas of Brooklyn and Queens. 
    It will substantially cut down on travel times between the two boroughs, 
    reduce congestion, and expand economic opportunities for the people who live 
    and work in the surrounding neighborhoods. 

    The project would be built along the existing, LIRR-owned Bay Ridge Branch 
    and CSX-owned Fremont Secondary, a 14-mile freight line that extends from Bay 
    Ridge, Brooklyn, to Jackson Heights, Queens. It would create a new transit
    option for close to 900,000 residents of the neighborhoods along the route, 
    along with 260,000 people who work in Brooklyn and Queens. It would connect 
    with up to 17 different subway lines, as well as Long Island Rail Road, with 
    end-to-end travel times anticipated at less than 40 minutes. Daily weekday 
    ridership is estimated at 115,000. 

    Using the existing rail infrastructure means the Interborough Express could 
    be built more quickly and efficiently. It would also preserve the Bay Ridge
    Branch’s use as a freight line, providing an opportunity to connect to the 
    Port Authority’s Cross-Harbor Freight Project. 

    After extensive planning, analysis, and public engagement, Light Rail was 
    chosen because it will provide the best service for riders at the best value. 
    It also announced a preliminary list of stations and advanced other important 
    planning and engineering analysis of the project. The formal environmental 
    review process is anticipated to begin soon.

    Project benefits
    - A direct public transit option between Brooklyn and Queens
    - Connections with up to 17 subway lines and Long Island Rail Road
    - A faster commute — end-to-end rides are expected to take 40 minutes
    - A new transit option in underserved locations where more than a third of 
    residents are below the federal poverty line    
    """,

    task="""As part of the planning processing for IBX, we would like to forecast
     the seasonal foot traffic through a few candidate rail stations with 
     connections to subway lines. In each example, forecast the foot traffic 
     (number of passengers using the connection) from the source line to 
     destination line at the candidate location. Assume the connection and IBX 
     have already been open and in use for several months.
    """,

    env=dict(
        CHRONULUS_API_KEY="<YOUR-CHRONULUS-API-KEY>",
    )
)
Describe a prediction input
Here will define the data model that will describe a connection point.

class IBXConnectionPoint(BaseModel):
    candidate_location: str = Field(description="The name of the candidate location for the IBX connection.")
    source_line: str = Field(description="The name of the source line for the foot traffic.")
    destination_line: str = Field(description="The name of the destination line for the foot traffic.")
    project_images: List[ImageFromUrl] = Field(default=[], description="A list of images that provide context for the IBX project.")
    events_schedule: str = Field(description="A schedule of major events in 2025")
Create a Foot Traffic Forecasting Agent
Next, we define a forecasting agent. The agent needs our session context (situation and task) and the description of our inputs.

nf_agent = NormalizedForecaster(
    session=chronulus_session,
    input_type=IBXConnectionPoint,
)
Get a Forecast for a connection point
To make things interesting, let's get a forecast between the IBX and the 7 Line from August through September. We will also let the agent know when the 2025 US Open is schedule to take place.

# Fill in the metadata for the item or concept you want to predict
connection_point = IBXConnectionPoint(
    candidate_location="74 St - Broadway, with connections to the 7, E, F, M, and R lines",
    source_line="IBX",
    destination_line="F line",
    project_images=[
        ImageFromUrl(url='https://new.mta.info/sites/default/files/inline-images/011022_BRC%20Existing%20Conditions-01_0.png'), 
        ImageFromUrl(url='https://files.mta.info/s3fs-public/2023-12/ibxhero.png'),
    ],
    events_schedule="""
        - US Open: Mon, Aug 25, 2025 – Sun, Sep 7, 2025
    """
)
These are the images that we included from the MTA project page:



Forecast Daily foot traffic between the 7 Line and IBX
forecast_start_date = datetime(2025, 8, 1)
req = nf_agent.queue(connection_point, start_dt=forecast_start_date, days=60, note_length=(7, 10))
predictions = nf_agent.get_predictions(req.request_id)
> predictions[0].to_pandas()

            y_hat
date    
2025-08-01  0.632371
2025-08-02  0.482215
2025-08-03  0.452515
2025-08-04  0.651231
2025-08-05  0.649705
... ...
2025-09-25  0.682126
2025-09-26  0.691100
2025-09-27  0.514446
2025-09-28  0.491080
2025-09-29  0.686795
> fig, ax = plt.subplots(1,1, figsize=(12, 4))
> predictions[0].to_pandas().plot(ax=ax)
Foot Traffic between the 7 Line and IBX

Explanation for daily predictions
> predictions[0].text
The 74th St-Broadway connection point represents a major transit hub in Queens where the IBX will intersect with multiple subway lines. The 7 line to IBX transfer predictions factor in several key considerations. First, the 7 line serves a dense residential corridor with high commuter traffic, particularly during weekday rush hours. The US Open tournament (Aug 25-Sep 7) will significantly boost ridership due to the station's proximity to the USTA Tennis Center, with peaks during match sessions. Weekend ridership typically drops by 30-40% compared to weekdays, but maintains steady flows due to recreational travelers and weekend workers. Late August sees slightly lower baseline ridership due to vacation season, with a gradual increase in September as schools reopen and regular commuting patterns resume. Early morning and late evening hours show reduced transfer volumes, with peak transfers occurring during the 8-10 AM and 4-7 PM windows. The predictions also account for typical weather patterns in late summer that can affect surface-level light rail operations.

Forecast Hourly foot traffic between the 7 Line and IBX
Since our situation and task do not reference our time scale, we can simply reuse the same agent to predict the hour foot traffic. Let zoom in on the final 5 days of the US Open.

forecast_start_date = datetime(2025, 9, 4)
req = nf_agent.queue(connection_point, start_dt=forecast_start_date, hours=5*24, note_length=(7, 10))
predictions = nf_agent.get_predictions(req.request_id)
> fig, ax = plt.subplots(1,1, figsize=(12, 4))
> predictions[0].to_pandas().plot(ax=ax)
Hourly Foot Traffic between the 7 Line and IBX

Explanation for hourly predictions
> predictions[0].text
The 74 St-Broadway station is a major transit hub in Queens that will see significant transfer activity between the 7 line and IBX. For this prediction period during the US Open (September 4-8, 2025), I'm considering several key factors. The 7 line traditionally sees heightened ridership during the US Open due to its connection to the USTA Tennis Center. Morning rush hours (6-10 AM) will see moderate transfer volumes as commuters use the IBX for cross-borough travel. Peak transfer activity will occur during evening rush hours (4-8 PM), amplified by US Open attendees returning from matches. Weekend patterns will show more distributed ridership throughout the day, with peaks around mid-day when tennis matches are in full swing. Late night ridership drops significantly after the last US Open matches conclude. The prediction also accounts for typical weather patterns in early September and the station's location in a dense residential and commercial area. The overall transfer patterns reflect both regular commuter behavior and the special event impact of the US Open.
