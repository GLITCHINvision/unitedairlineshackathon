#  Flight Difficulty Scoring Project  

##  Overview  
This project builds a **data-driven framework** to compute a **Flight Difficulty Score (FDS)** for each flight, based on multiple datasets provided by United Airlines.  
The score quantifies the operational complexity of flights and helps identify which ones require proactive attention from ground teams.  

The analysis integrates flight-level, PNR-level, baggage-level, and airport-level data to capture ground time stress, passenger complexity, and baggage handling load — enabling **resource optimization and smarter operations**.

---

##  Objectives  
- Calculate a **daily-level difficulty score** for every flight.  
- Rank and classify flights as **Easy**, **Medium**, or **Difficult**.  
- Identify **key operational drivers** influencing difficulty.  
- Provide **data-backed recommendations** for better planning.  

---

##  Datasets Used  

##  Dataset Overview

| Dataset | Description | Key Columns Used |
|----------|--------------|------------------|
| **Flight Level Data.csv** | Contains detailed flight-level information including schedules, timing, delays, and aircraft details. | `flight_number`, `scheduled_departure_date_local`, `actual_departure_datetime_local`, `scheduled_ground_time_minutes`, `delay_minutes`, `minimum_turn_minutes` |
| **PNR Flight Level Data.csv** | Holds passenger booking information for each flight, including passenger counts and fare classes. | `record_locator`, `total_pax`, `basic_economy_pax`, `lap_child_count`, `is_child` |
| **PNR Remark Level Data.csv** | Stores remarks and special service requests (SSR) associated with passenger bookings. | `special_service_request`, `record_locator`, `flight_number` |
| **Bag Level Data.csv** | Includes data about checked and transfer baggage for each passenger and flight. | `bag_type`, `bag_tag_unique_number`, `flight_number` |
| **Airports Data.csv** | Provides airport metadata and country-level mapping information. | `airport_iata_code`, `iso_country_code` |


---

##  Feature Engineering Process  

Each dataset contributes features that influence the operational difficulty:

| Category               | Derived Feature | Description |
|-----------             |----------------|--------------|
| **Timing Stress**      | `delay_minutes`, `turnaround_ratio` | Measures schedule tightness & deviation |
| **Passenger Load**     | `load_factor` | Ratio of passengers to available seats |
| **Special Requests**   | `ssr_count_per_flight` | Wheelchair, stroller, or other requests per flight |
| **Baggage Stress**     | `transfer_to_checked_ratio` | Complexity of bag handling |
| **Ground Constraints** | `ground_stress_index` | Scheduled vs minimum turnaround time ratio |

All numeric features are normalized (Min–Max scaling) for fair comparison across flights.

---

##  Difficulty Score Formula  

A weighted formula combines all normalized feature values:

\[
\text{Flight Difficulty Score (FDS)} =
0.35(Delay) +
0.25(Passenger Load) +
0.15(SSR Density) +
0.15(Ground Stress) +
0.10(Baggage Stress)
\]

- Each day’s scores are normalized so that **max(FDS) = 1.0**  
- Flights are then ranked and classified:

| Category      | Score Range | Description                 |
|-----------    |-------------|-------------                |
| **Easy**      | 0.00 – 0.33 | Smooth operations           |
| **Medium**    | 0.34 – 0.66 | Moderate load and stress    |
| **Difficult** | 0.67 – 1.00 | High operational complexity |



##  Insights Generated  
- **Correlation** between passenger load & delay time.  
- Flights with **high SSR requests** often show greater delays.  
- Short ground time (< minimum_turn_minutes) leads to high-stress ratings.  
- Top “Difficult” routes include **ORD → EWR**, **ORD → DFW**, etc.  



##  Recommendations  
1. **Boost staffing** for flights with low ground time and high load.  
2. **Prioritize baggage handlers** for flights with high transfer ratios.  
3. **Early coordination for SSR passengers** (wheelchair/stroller).  
4. **Integrate live weather & ATC delay feeds** in the next iteration.  



##  Tech Stack  
- **Language:** Python 3.11  
- **Libraries:** `pandas`, `numpy`, `matplotlib`, `scikit-learn`  
- **Visualization:** Matplotlib, Seaborn  
- **Output:** `test_yourname.csv` (final difficulty score file)  



##  Folder Structure  

Flight-Difficulty-Project/
│
├── data/
│ ├── Airports Data.csv
│ ├── Bag Level Data.csv
│ ├── Flight Level Data.csv
│ ├── PNR Flight Level Data.csv
│ └── PNR Remark Level Data.csv
│
├── compute_difficulty.py
├── requirements.txt
├── README.md
├── test_yourname.csv
└── flight_difficulty_presentation.pptx



##  Steps to Run  

1. **Install dependencies**  
   ```bash
   pip install -r requirements.txt

Place the datasets
Copy all five CSVs into the /data/ folder.

Run the script 
python compute_difficulty.py

Output
A file named test_yourname.csv will be generated containing:

Flight details

Engineered features

Difficulty score

Daily rank & classification

Example Output

| flight_number | date | delay | load_factor | ground_stress | ssr_density | bag_stress | difficulty_score | category |
|----------------|------|--------|--------------|----------------|--------------|--------------------|------------|
| UA123 | 2025-01-05 | 0.65 | 0.80 | 0.72 | 0.50 | 0.40 | 0.69 | Difficult |
| UA456 | 2025-01-05 | 0.20 | 0.35 | 0.40 | 0.10 | 0.15 | 0.27 | Easy |

Author

Raman Sharma
Lakshya shukla 
Delhi Technological University | Electrical Engineering

