# Sectored_basestation_simulation_analysis

Overview of the Project :

This project involves implementing a Python-based simulation to study the downlink behavior of a 3-sectored basestation along a road. The simulation examines coverage, interference, throughput, and various performance metrics such as call drops, blocks, handoff failures, and system capacity under different scenarios. The simulation considers two sectors of the basestation (alpha and beta), ignoring the gamma sector since it does not cover the road. The project is broken into two parts:

**Part 1: Building Core Functions**

The first part focuses on developing and testing individual functions that model the physical characteristics and performance of the basestation and user interactions. Specifically:

1. **Propagation Loss (COST231 Model)**:
   - Models signal loss over distance based on mobile and basestation heights.
   - Considers the distance between the mobile and the basestation.

2. **Shadowing**:
   - Introduces randomness to signal strength using a log-normal distribution.
   - Shadowing is pre-computed for fixed locations along the road and does not vary over time.

3. **Fading**:
   - Models rapid signal fluctuations caused by environmental factors using a Rayleigh distribution.
   - Uses a filtering technique to simulate real-world fading behavior (removes deepest fading and uses the second-deepest value).

4. **EIRP Calculations**:
   - Computes the effective isotropic radiated power in the direction of the mobile based on the mobile’s location and the basestation's antenna pattern.
   - Takes into account antenna discrimination based on angles off boresight.

5. **RSL (Received Signal Level)**:
   - Combines EIRP, propagation loss, shadowing, and fading to compute the signal strength received by the mobile.
   - Determines whether the signal strength meets the threshold for successful communication.

**Part 2: Full Simulation**

This part involves implementing a dynamic simulation using the tested functions from Part 1. The simulation runs with discrete 1-second time steps for several hours, tracking user movement, call attempts, handoffs, and signal levels. The key tasks include:

1. **Simulating User Behavior**:
   - Users are distributed uniformly along the road and travel in either direction (north or south).
   - Users make call attempts with a defined probability and direction of travel.

2. **Handling Calls**:
   - Calls are initiated based on the strongest RSL.
   - Calls can be blocked (due to capacity limits) or dropped (due to low signal strength).
   - Calls are maintained until completion or failure, with updates to the user’s location and signal levels at every time step.

3. **Handoff Mechanism**:
   - As users move, calls may hand off between sectors based on signal strength.
   - A handoff is triggered if the signal from the other sector surpasses the current sector's signal by a specified margin and a channel is available.

4. **Tracking and Reporting**:
   - The simulation records various statistics, including:
     - Number of call attempts.
     - Successful calls, blocked calls, dropped calls, and handoff outcomes.
     - Signal-to-interference ratios (S/I) for data throughput evaluation.
   - At the end of each hour, and at the end of the simulation, reports are generated to summarize performance.


The project includes four main analysis questions based on different scenarios:

**Q1**: Baseline Performance
- **Scenario**: Simulate a 3 km road for 4 hours with the given parameters.
- **Objective**:
  - Determine the number of dropped calls, blocked calls, and handoff failures.
  - Calculate the percentage of problematic call attempts.
  - Assess whether the basestation performs well overall and compare the performance of the two sectors.
- **Analysis**: Examine the differences in performance between alpha and beta sectors, considering factors like road geometry, antenna orientation, and signal interference.

**Q2**: Impact of Road Length
- **Scenario**: Extend the road length to 6 km while keeping the basestation at the midpoint.
- **Objective**:
  - Re-run the simulation for 4 hours and analyze changes in performance.
  - Identify the main causes of additional problems (e.g., increased signal drops due to distance, capacity limits, or handoff issues).
- **Analysis**: Compare the performance with Q1 to understand the impact of larger coverage areas and increased distance from the basestation.

**Q3**: Effect of User Density
- **Scenario**: Return to a 3 km road but increase the number of users from 160 to 640.
- **Objective**:
  - Simulate for 4 hours and evaluate the effects of increased user density.
  - Identify the primary causes of additional problems (e.g., capacity-related call blocks/drops or increased handoff failures).
  - Analyze the impact on handoff performance and system stability.
- **Analysis**: Assess how the system scales with higher user loads and whether the basestation can handle the increased traffic without significant performance degradation.

**Q4**: Throughput Analysis
- **Scenario**: Analyze throughput results from Q1.
- **Objective**:
  - Identify road sections (for alpha and beta sectors) with high (green), medium (magenta), and low (red) S/I values.
  - Determine which sector performs better in terms of data throughput.
- **Analysis**: Evaluate spatial performance differences along the road and identify any sector-specific advantages or challenges.
