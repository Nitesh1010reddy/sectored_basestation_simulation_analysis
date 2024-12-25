# om sai ram

import numpy as np
import numpy.random as rnd
import matplotlib.pyplot as plt
import math
import config


#Basic and Basestation parameters
ROAD_LENGTH = 3 # in km
SIMULATION_TIMESTEP = 1 #in seconds
TOTAL_SIMULATIONTIME = 1 #in hours

H_B = 50 # in meters
P_T = 47 # in dbm
L = 1 #in db
G_T= 14.8 # in dbi
NUMBER_CHANNELS = 15 # number of channels per sector
F = 1910 # in Mhz for all sectors


# User parameters

USERS =config.num_users # number of users
CALL_RATE = 2 # (avg. calls per hour [lamda])
H = (1/20) # (avg. call duration)
V = 15 #m/s 54kmph 33.553977mph (user speed)
H_M = 1.5 #in meters
D = 20 #in meters (distance of mobile from basestation)


#Channel properties and path loss

#Propogation loss using COST-231 Model for small city

def cost_231(delta,co_ord):

    x = np.linalg.norm(delta-co_ord)
    #x = np.sum(np.abs(delta-co_ord))
    
    C_m = 0
    a= (1.1*np.log10(F)-0.7)*H_M - (1.56*np.log10(F)-0.8)
    path_loss = 46.3 + 33.9*np.log10(F) - 13.82*np.log10(H_B) + (44.9 - 6.55*np.log10(H_B))*np.log10(x/1000)-a+C_m
    # a= (1.1*math.log10(F)-0.7)*H_M - (1.56*math.log10(F)-0.8)
    # path_loss = 46.3 + 33.9*math.log10(F) - 13.82*math.log10(H_B) + (44.9 - 6.55*math.log10(H_B))*math.log10(x/1000)-a+C_m

    return path_loss


mu = 0
sigma = 2 #in db
road_len = config.road_length
intervals = np.arange(-road_len/2,road_len/2,10)

shadowing = np.random.normal(mu, sigma,len(intervals)) #in dB

#shadowing (using normal distribution)
def Shadowing(j):

    mid = len(shadowing)/2
    ind= 0
    if(j>=0): #-1500<y<+1500 ('y' cordinate of user)
        ind = mid + j//10
    else:
        ind = mid + j//10

    shadowing_alpha_beta = shadowing[int(ind)]

    return shadowing_alpha_beta

#fading (using a rayleigh distribtuion)
def Fading():

    fading = np.random.rayleigh(1,10)
    min_element = min(fading)
    # fading.sort(reverse=True)
    # fading_net = fading[:-1]
    fading=list(fading)
    fading.remove(min_element)
    final_fade_1 = min(fading)
    final_fade = 20*np.log10(final_fade_1)

    return final_fade

#print(Fading())

x = (20) #in m
y_array = np.arange(-1500,1500,1) #in m

alpha = np.array([0,1])
beta = np.array([0.8660254037,-0.5])



#reading descrimination values from txt file for net eirp

key_dict = {}

with open('antenna_pattern.txt', 'r') as file:
    for line in file:
        
        parts = line.split()
        
        angle = float(parts[0])   
        disc_val = float(parts[1])  
        key_dict[angle] = disc_val

#print(key_dict)        


#to find angle between antenna and position vector of user

def angle (u,v):
    product = np.dot(u,v)
    norm_u = np.linalg.norm(u)  
    norm_v = np.linalg.norm(v)
    #denominator = np.sqrt((u**2)*(v**2))
    denominator = norm_u*norm_v
    THETA =np.arccos((product)/(denominator))
    theta_degrees = np.rad2deg(THETA)
    # print(THETA)
    return np.round(theta_degrees)
    #return np.ceil(theta_degrees)
    #return np.floor(theta_degrees)

ang_val = []

def net_eirp(gamma,x,y):
    pos = np.array([x,y])
    
    ang = angle(gamma,pos)
    ang_val.append(ang)
    # print(ang)

    #EIRP at boresight at transmitter antenna for both alpha and beta
    EIRP_BORESIGHT = P_T+G_T-L   #in dBm
    NET_EIRP = EIRP_BORESIGHT - key_dict[ang] #in dBm

    return NET_EIRP


net_eirp_val1 = [] #list for storing net eirp values of alpha sector
net_eirp_val2 = [] #list for storing net eirp values of beta sector

dist_alpha = [] #distance of cordinate on road from alpha sector
dist_beta = [] # distance of cordinate on road from beta sector

loss_val_1=[] # cost 231 path loss for alpha sector
loss_val_2=[] # cost 231 path loss for beta sector

new1 = [] # (net_eirp - path loss) for alpha sector
new2 = [] # (net_eirp - path loss) for beta sector

shadowing_1=[] #(signal level after subtracting shadowing for alpha sector)
shadowing_2=[] #(signal level after subtracting shadowing for beta sector)

fade_1=[] #(rsl after adding fading for alpha sector)
fade_2=[] #(rsl after adding fading for beta sector)

def rsl(pos_1):
    # Extract x and y coordinates of the user's position
    x, y = pos_1
    
    # Compute net EIRP for alpha and beta sectors
    val1 = net_eirp(alpha, x, y)
    val2 = net_eirp(beta, x, y)
    
    # Compute distance from alpha and beta sectors
    vec1 = np.array([x, y])
    dist1 = np.linalg.norm(alpha - vec1)
    dist2 = np.linalg.norm(beta - vec1)
    
    # Path loss using COST-231
    a1 = cost_231(alpha, vec1)
    b = cost_231(beta, vec1)
    
    # Compute shadowing and fading
    s = Shadowing(y)
    f1 = Fading()
    f2 = Fading()
    
    # Calculate signal levels
    shadowing_alpha = val1 - a1 + s
    shadowing_beta = val2 - b + s
    
    fade_alpha = shadowing_alpha + f1
    fade_beta = shadowing_beta + f2
    
    return fade_alpha,fade_beta