#om sai ram

import numpy as np
import numpy.random as rnd
import matplotlib.pyplot as plt
from Nitesh_Final_Part1 import rsl
import config

# Simulation parameters
total_simulation_time = 14400                # Total simulation time in seconds
reporting_interval = 3600                    # Time interval for reporting statistics
road_length = config.road_length             # Length of the road in meters
step_size = 15                               # Distance traveled per time step (meters)
mean_call_duration = 180                     # Mean call duration in seconds
prob_making_call = 2/3600                    # Probability of making a new call per user per time step
rsl_threshold = -102                         # Signal strength threshold for call drop (in dBm)
handoff_margin = 3                           # Minimum signal strength difference for handoff (in dBm)
num_users = config.num_users                 # Total number of users on the road

# Initialization of variables
channels_alpha = 15  # Number of available channels in Alpha sector
channels_beta = 15   # Number of available channels in Beta sector


# Call statistics
call_attempts_alpha = 0 # stores the attempting calls in the alpha sector
call_attempts_beta = 0 # stores the attempting calls in the beta sector

call_blocks_alpha = 0 # stores the list of calls blocked due to low channel capacity in alpha sector
call_blocks_beta = 0 # stores the list of calls blocked due to low channel capacity in beta sector

call_drops_alpha = 0 # stores the list of calls dropped due to low signal strength in alpha sector
call_drops_beta = 0  # stores the list of calls dropped due to low signal strength in beta sector

successful_calls_alpha = 0 # stores the calls that were successful in alpha sector
successful_calls_beta = 0 # stores the calls that were successful in beta sector

handoff_attempts_alpha = 0 # stores the number of handoff attempts made by the alpha sector
handoff_attempts_beta = 0 # stores the number of handoff attempts made by the beta sector

successful_handoffs_alpha = 0 # number of successful handoffs by the alpha sector
successful_handoffs_beta = 0 # number of successful handoffs by the beta sector

failed_handoffs_alpha = 0 # number of failed handoffs by the alpha sector
failed_handoffs_beta = 0 # number of failed handoffs by the beta sector

active_calls_alpha = 0 # count of calls that are currently active in alpha sector
active_calls_beta = 0 # count of calls that are currently active in beta sector

# Storing successful call details
successful_call_details = [] # successful user calls = (crossed the road boundary or completed call duration)


# Function to print statistics which includes all the parametrs updated during the simulation

def print_final_statistics(channels_alpha,channels_beta,
                           call_attempts_alpha, call_attempts_beta,
                           call_blocks_alpha, call_blocks_beta,
                           call_drops_alpha, call_drops_beta,
                           successful_calls_alpha, successful_calls_beta,
                           handoff_attempts_alpha, handoff_attempts_beta,
                           successful_handoffs_alpha, successful_handoffs_beta,
                           failed_handoffs_alpha, failed_handoffs_beta,active_calls_alpha,active_calls_beta):
    
    print("\nStatistics:")
    print(f"channels available - Alpha: {channels_alpha}, Beta: {channels_beta}")
    print(f"Call Attempts - Alpha: {call_attempts_alpha}, Beta: {call_attempts_beta}")
    print(f"Call Blocks - Alpha: {call_blocks_alpha}, Beta: {call_blocks_beta}")
    print(f"Call Drops - Alpha: {call_drops_alpha}, Beta: {call_drops_beta}")
    print(f"Successful Calls - Alpha: {successful_calls_alpha}, Beta: {successful_calls_beta}")
    print(f"Handoff Attempts - Alpha: {handoff_attempts_alpha}, Beta: {handoff_attempts_beta}")
    print(f"Successful Handoffs - Alpha: {successful_handoffs_alpha}, Beta: {successful_handoffs_beta}")
    print(f"Failed Handoffs - Alpha: {failed_handoffs_alpha}, Beta: {failed_handoffs_beta}")
    print(f"Active Calls - Alpha: {active_calls_alpha},Beta:{active_calls_beta}")
    print("=" * 54)


# assigning id to the users to track their progress independently
new_users = [{'id': i} for i in range(num_users)]
active_users = [] # stores the users who satisfied the call probablity 

signal_to_interferences =[] # stores the (S/I) values after computing them
sector_assigned = [] # stores the sector deatils at different points of (S/I) value computation
locations = [] # stores the cordinates of points where the (S/I) value is computed


for time_step in range(total_simulation_time):  # running the loop for simulation time (4 hours or 14400 seconds)
    
    for user in active_users[:]:           # simulation is run for users with active calls 
        user['position'] += user['direction'] * step_size # updating user position based on the direction
        user['call_duration'] -= 1 # decrementing user call duration by 1 second after each iteration

        # checking conditions to record the call as successful call        
        if user['call_duration'] <= 0 or ( -road_length/2>user['position'] or user['position']>road_length/2):
            if user['sector'] == "Alpha":   # considering serving sector is the alpha sector
                channels_alpha += 1
                active_calls_alpha -=1
                successful_calls_alpha += 1
            else:                          # considering serving sector is the beta sector
                channels_beta += 1
                active_calls_beta -=1
                successful_calls_beta += 1
            successful_call_details.append(user)
            active_users.remove(user)
            continue

        
        rsl_alpha, rsl_beta = rsl(np.array([20,user['position']])) # calculating the rsl values after position update for the user with ongoing call

        if user['sector'] == "Alpha":
            if rsl_alpha < rsl_threshold:
                # call dropped due to signal strength
                call_drops_alpha += 1
                channels_alpha += 1
                active_calls_alpha-=1
                active_users.remove(user)
            elif rsl_beta >= rsl_alpha + handoff_margin:
                # Attempt handoff to Beta
                handoff_attempts_alpha += 1
                if channels_beta > 0:
                    channels_beta -= 1
                    active_calls_beta+=1
                    channels_alpha += 1
                    active_calls_alpha -=1
                    user['sector'] = "Beta"
                    successful_handoffs_alpha += 1
                else:
                    failed_handoffs_alpha += 1

        else:
            if rsl_beta < rsl_threshold:
                # call dropped due to signal strength
                call_drops_beta += 1
                channels_beta += 1
                active_calls_beta -=1
                active_users.remove(user)    
            elif rsl_alpha >= rsl_beta + handoff_margin:
                # Attempt handoff to Alpha
                handoff_attempts_beta += 1
                if channels_alpha > 0:
                    channels_alpha -= 1
                    active_calls_alpha +=1
                    channels_beta += 1
                    active_calls_beta -=1
                    user['sector'] = "Alpha"
                    successful_handoffs_beta += 1
                else:
                    failed_handoffs_beta += 1


        ########################################################################
        # updating the (S/I), sector assigned , position cordinates list simultaneously for finding the throughput 

        if user['sector'] == "Alpha":
            s_i = rsl_alpha - rsl_beta
            signal_to_interferences.append(s_i)
            sector_assigned.append("A")
            locations.append(user['position'])

        else:
            s_i = rsl_beta - rsl_alpha
            signal_to_interferences.append(s_i)
            sector_assigned.append("B")
            locations.append(user['position'])

        ############################################################################

    
    for user in new_users:
        if np.random.uniform(0, 1) < prob_making_call: # checking if the user will make a call or not
            position = np.random.uniform(-road_length / 2, road_length / 2) # assigning position to the user on the road
            direction = np.random.choice([-1, 1]) # assigning direction of movement to the user
            call_duration = int(np.random.exponential(mean_call_duration)) # finding the call duration length of the user
            rsl_alpha, rsl_beta = rsl(np.array([20,position])) # calculating the rsl values from both alpha and beta sectors at the initial position

            if rsl_alpha > rsl_beta:          # attempting the call to the loudest sector 
                call_attempts_alpha += 1
                if rsl_alpha >= rsl_threshold : # checking if the alpha sector rsl is enough to connect and establish the call
                    if channels_alpha > 0:  # checking if a channel is available in the alpha sector
                    # user assigned to the alpha sector
                        channels_alpha -= 1  
                        active_calls_alpha+=1
                        active_users.append({'id': user['id'], 'position': position, 'direction': direction,
                                            'call_duration': call_duration, 'sector': "Alpha","initial_duration":call_duration,
                                            'initial_position': position, 'initial_sector': "Alpha"})
                    else:#call block calculation in alpha
                        call_blocks_alpha +=1

                else:
                    # Drop call in Alpha
                    #print(user['id'],"call dropped in alpha because",rsl_alpha,"is less than -102")
                    call_drops_alpha += 1

            else:
                call_attempts_beta += 1
                if rsl_beta >= rsl_threshold: # checking if the beta sector rsl is enough to connect and establish the call
                    if  channels_beta > 0: # checking if a channel is available in the alpha sector
                    # user assigned to the beta sector
                        channels_beta -= 1
                        active_calls_beta +=1
                        active_users.append({'id': user['id'], 'position': position, 'direction': direction,
                                            'call_duration': call_duration, 'sector': "Beta","initial_duration":call_duration,
                                            'initial_position': position, 'initial_sector': "Beta"})
                    else:#call block calculation in beta
                        call_blocks_beta +=1
                else:
                    # Drop call in Beta
                    #print(user['id'],"call dropped beta because",rsl_beta,"is less than -102")
                    call_drops_beta += 1

    # Periodic statistics reporting
    if time_step % reporting_interval == 0:
       print(f"After {time_step} seconds")
       print_final_statistics(channels_alpha,channels_beta,
                              call_attempts_alpha, call_attempts_beta,
                              call_blocks_alpha, call_blocks_beta,
                              call_drops_alpha, call_drops_beta,
                              successful_calls_alpha, successful_calls_beta,
                              handoff_attempts_alpha, handoff_attempts_beta,
                              successful_handoffs_alpha, successful_handoffs_beta,
                              failed_handoffs_alpha, failed_handoffs_beta,active_calls_alpha,active_calls_beta)
                              

# Final statistics and details
print("Simulation Completed.")
print("After 14400 seconds")
print_final_statistics(channels_alpha,channels_beta,
                        call_attempts_alpha, call_attempts_beta,
                        call_blocks_alpha, call_blocks_beta,
                        call_drops_alpha, call_drops_beta,
                        successful_calls_alpha, successful_calls_beta,
                        handoff_attempts_alpha, handoff_attempts_beta,
                        successful_handoffs_alpha, successful_handoffs_beta,
                        failed_handoffs_alpha, failed_handoffs_beta,active_calls_alpha,active_calls_beta)

# print("Successful Call Details:")
# for detail in successful_call_details:
#     print(detail)

# print(len(signal_to_interferences))
# print(len(sector_assigned))
# print(len(locations))


# plotting (s/i) graphs

# Convert lists to NumPy arrays for element-wise operations
signal_to_interferences = np.array(signal_to_interferences)
sector_assigned = np.array(sector_assigned)
locations = np.array(locations)

# Roadway parameters
roadway_min = -road_length/2
roadway_max = road_length/2
ind_width = 100

ind = np.arange(roadway_min, roadway_max + ind_width, ind_width)
ind_centers = (ind[:-1] + ind[1:]) / 2  # Calculate bin centers for correct x-tick placement

# Initialize counts for each category
alpha_green_counts, alpha_magenta_counts, alpha_red_counts = [], [], []
beta_green_counts, beta_magenta_counts, beta_red_counts = [], [], []

# Count values for each bin
for i in range(len(ind) - 1):
    ind_start, ind_end = ind[i], ind[i + 1]
    
    # Filter points in the current bin
    in_bin = (locations >= ind_start) & (locations < ind_end)
    
    # For Alpha sector
    alpha_ind = in_bin & (sector_assigned == 'A')
    alpha_green_counts.append(np.sum(alpha_ind & (signal_to_interferences >= 10)))
    alpha_magenta_counts.append(np.sum(alpha_ind & (signal_to_interferences >= 5) & (signal_to_interferences < 10)))
    alpha_red_counts.append(np.sum(alpha_ind & (signal_to_interferences < 5)))

    
    # For Beta sector
    beta_ind = in_bin & (sector_assigned == 'B')
    beta_green_counts.append(np.sum(beta_ind & (signal_to_interferences >= 10)))
    beta_magenta_counts.append(np.sum(beta_ind & (signal_to_interferences >= 5) & (signal_to_interferences < 10)))
    beta_red_counts.append(np.sum(beta_ind & (signal_to_interferences < 5)))


# Generate bin labels from bins
ind_labels = [f"{int(ind[i])} to {int(ind[i + 1])}" for i in range(len(ind) - 1)]

# Plot for Alpha Sector - Green
#plt.figure(figsize=(8, 6))
plt.scatter(ind_labels, alpha_green_counts, color='green', label='Green', s=100)
plt.title('Alpha Sector - Green')
plt.xlabel('Cross sections on the road (in meters)')
plt.ylabel('Count of points corresponding to (S/I) value')
plt.xticks(rotation=45, ha='right')
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot for Alpha Sector - Magenta
#plt.figure(figsize=(8, 6))
plt.scatter(ind_labels, alpha_magenta_counts, color='magenta', label='Magenta', s=100)
plt.title('Alpha Sector - Magenta')
plt.xlabel('Cross sections on the road (in meters)')
plt.ylabel('Count of points corresponding to (S/I) value')
plt.xticks(rotation=45, ha='right')
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot for Alpha Sector - Red
#plt.figure(figsize=(8, 6))
plt.scatter(ind_labels, alpha_red_counts, color='red', label='Red', s=100)
plt.title('Alpha Sector - Red')
plt.xlabel('Cross sections on the road (in meters)')
plt.ylabel('Count of points corresponding to (S/I) value')
plt.xticks(rotation=45, ha='right')
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot for Beta Sector - Green
#plt.figure(figsize=(8, 6))
plt.scatter(ind_labels, beta_green_counts, color='green', label='Green', s=100)
plt.title('Beta Sector - Green')
plt.xlabel('Cross sections on the road (in meters)')
plt.ylabel('Count of points corresponding to (S/I) value')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.grid(True)
plt.show()

# Plot for Beta Sector - Magenta
#plt.figure(figsize=(8, 6))
plt.scatter(ind_labels, beta_magenta_counts, color='magenta', label='Magenta', s=100)
plt.title('Beta Sector - Magenta')
plt.xlabel('Cross sections on the road (in meters)')
plt.ylabel('Count of points corresponding to (S/I) value')
plt.xticks(rotation=45, ha='right')
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot for Beta Sector - Red
#plt.figure(figsize=(8, 6))
plt.scatter(ind_labels, beta_red_counts, color='red', label='Red', s=100)
plt.title('Beta Sector - Red')
plt.xlabel('Cross sections on the road (in meters)')
plt.ylabel('Count of points corresponding to (S/I) value')
plt.xticks(rotation=45, ha='right')
plt.grid(True)
plt.tight_layout()
plt.show()


