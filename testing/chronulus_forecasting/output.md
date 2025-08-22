PS C:\Users\fstr2\Desktop\sports> & C:\Python313\python.exe c:/Users/fstr2/Desktop/sports/testing/chronulus_forecasting/debug_response.py
Debugging your completed Rockies prediction...
DEBUGGING PREDICTION RESPONSE STRUCTURE
============================================================
Checking prediction: 2829dbe2-722b-4aea-8aee-bb64516f0cb6
SUCCESS: Got prediction response
Response Type: <class 'chronulus.prediction.BinaryPredictionSet'>
Response Attributes: ['beta_params', 'id_map', 'predictions', 'prob', 'prob_a', 'text', 'to_dict']

Found predictions list with 3 items

PREDICTION 1:
  Type: <class 'chronulus.prediction.BinaryPrediction'>
  Attributes: ['id', 'opinion_set', 'prob', 'prob_a', 'text', 'to_dict']
  prob: (0.36406024393143627, 0.6359397560685638) (type: <class 'tuple'>)
  text: [Positive]

Q: What is the probability that the Colorado Rockies will win their away game against th...
  Full object: <chronulus.prediction.BinaryPrediction object at 0x000002827D7C1400>

PREDICTION 2:
  Type: <class 'chronulus.prediction.BinaryPrediction'>
  Attributes: ['id', 'opinion_set', 'prob', 'prob_a', 'text', 'to_dict']
  prob: (0.35917444587314246, 0.6408255541268575) (type: <class 'tuple'>)
  text: [Positive]

Q: What is the probability that the Colorado Rockies will win their away game against th...
  Full object: <chronulus.prediction.BinaryPrediction object at 0x000002827D86D6D0>

PREDICTION 3:
  Type: <class 'chronulus.prediction.BinaryPrediction'>
  Attributes: ['id', 'opinion_set', 'prob', 'prob_a', 'text', 'to_dict']
  prob: (0.3542194940923411, 0.6457805059076589) (type: <class 'tuple'>)
  text: [Positive]

Q: What is the probability that the Colorado Rockies will win their away game against th...
  Full object: <chronulus.prediction.BinaryPrediction object at 0x000002827D86DF90>

Full predictions object:
--- Expert 1 ---

[Positive]

Q: What is the probability that the Colorado Rockies will win their away game against the Pittsburgh Pirates at PNC Park on August 22, 2025?

Pred: (38.58%*, 61.42%)

A: My expectation weighs the stark contrast between season-long performance and recent form. While the Pirates' overall record and run differential suggest they should be solid favorites, their recent 3-7 slump combined with the Rockies' surprising 7-3 hot streak indicates significant momentum shift. I predict with moderate certainty given the competing factors at play. Results are likely skewed right, reflecting a higher than market-implied probability for a Rockies victory due to their recent form improvement. However, there remains a risk of fat tails given the Rockies' abysmal season-long road performance and run differential. The current betting line appears to overweight season-long trends while undervaluing recent performance shifts.

[Negative]

Q: What is the probability that the Colorado Rockies will LOSE this away game against the Pittsburgh Pirates?

Pred: (34.65%, 65.35%*)

A: Based on the comprehensive data, I expect the Rockies to lose this game around 65% of the time, despite their recent hot streak. This assessment stems from their abysmal road performance and significantly worse run differential compared to the Pirates. I predict with moderate certainty due to the conflicting signals between recent form and season-long metrics. The outcomes are slightly skewed toward higher loss probabilities due to the Rockies' historical road struggles and their league-worst runs allowed per game. However, the recent 7-3 streak for the Rockies creates a wider distribution of possible outcomes, suggesting some meaningful risk of extreme results in either direction.

--- Expert 2 ---

[Positive]

Q: What is the probability that the Colorado Rockies will win their away game against the Pittsburgh Pirates given the current form and season-long performance of both teams?

Pred: (38.38%*, 61.62%)

A: Based on analyzing the conflicting signals between season-long performance and recent form, I expect this game to be more competitive than the betting lines suggest. While season-long statistics heavily favor Pittsburgh, the Rockies' recent surge (7-3 last 10) compared to Pirates' slump (3-7 last 10) indicates significant momentum shift. The results are likely skewed right, reflecting some possibility of a convincing Rockies victory despite their underdog status. I predict with moderate certainty, acknowledging both the strong recent form and poor overall road performance of the Rockies. There is a meaningful risk of extreme outcomes given the high variance nature of baseball and the stark contrast between recent and season-long performance metrics.

[Negative]

Q: What is the probability that the Colorado Rockies will LOSE this away game against the Pittsburgh Pirates?

Pred: (33.99%, 66.01%*)

A: I expect the Rockies to lose this game despite their recent hot streak, with results centered around a 65.5% chance of a Pirates victory. My prediction carries moderate uncertainty due to the conflicting signals between season-long performance and recent form. Results are slightly skewed toward higher probabilities of a Pirates win, reflecting their significantly better season-long metrics despite recent struggles. The outcome distribution shows some concentration around my expectation, though there is a moderate risk of extreme outcomes given the volatile nature of both teams' performance. The stark contrast between recent form and season-long metrics creates a wider range of plausible outcomes than typical.

--- Expert 3 ---

[Positive]

Q: What is the probability that the Colorado Rockies will win their away game against the Pittsburgh Pirates, considering their recent strong form despite poor overall season performance?

Pred: (38.58%*, 61.42%)

A: Given the stark contrast between recent form and season-long performance, I expect this game to be more competitive than the overall records suggest. My prediction reflects moderate uncertainty given the volatile nature of both teams' current trajectories. The outcomes are slightly skewed toward a Pirates victory given home field advantage and significantly better season-long performance metrics, particularly run differential. However, the Rockies' recent surge (7-3 last 10) combined with the Pirates' slump (3-7 last 10) suggests meaningful momentum that partially offsets the baseline advantages. The current betting lines appear to overweight season-long performance while undervaluing recent form, creating potential value on the Rockies side. Results are moderately dispersed around the mean given the high variance nature of baseball and these teams' inconsistent performance patterns.

[Negative]

Q: What is the probability that the Colorado Rockies will LOSE this away game against the Pittsburgh Pirates?

Pred: (33.92%, 66.08%*)

A: Given the underlying season-long statistics and home field advantage, I expect the Pirates to win this game despite their recent slump. The Pirates' vastly superior run differential and better pitching metrics provide strong fundamentals for a home victory. While the recent form creates uncertainty, I predict with moderate certainty that regression to the mean will occur. Results are likely skewed right, reflecting that while the Pirates' slump adds uncertainty, their fundamental advantages are significant. There is a moderate risk of fat tails given the volatile recent performance of both teams. The home field advantage at PNC Park adds another layer of support for a Pirates victory.

DEBUG COMPLETE - Check output above for probability extraction method
PS C:\Users\fstr2\Desktop\sports> 