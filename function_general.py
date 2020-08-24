#TEMPLATE FOR RETURNS ANALYSIS WITH STOCKS DATA PULLED FROM INVESTING.COM 
#PLEASE READ DOCUMENTATION BEFORE RUNNING SCRIPT 

#pip3 install pandas numpy matplotlib seaborn scipy.stats 
#pip install pandas numpy matplotlib seaborn scipy.stats 

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches 
import seaborn as sns 
from scipy.stats import norm 
from datetime import datetime 

# ----------- GETTING USER PATH TO FILE & FOLDER LOCATION 
file_path = input('What is your file path: ')
figure_save = input('Where do you want your graphs saved to: ')

# ----------- function IMPORT AND CLEAN DATA 
df = pd.read_csv(str(file_path), index_col = 'Date', parse_dates = True, thousands = ',') #read csv file, index Date, remove , from numerics 
#df = df.drop(pd.to_datetime(datetime.date(datetime.now()))) #because the file will contain today's date, drop not useful data 
#df = df.drop([0,1]) #removed because functionality not needed
df = df.drop(['Vol.', 'Change %', 'High', 'Low'], axis = 1) #drop unused columns 

# ----------- CALCULATE RETURNS AND % RETURNS 
df['Price_1'] = df['Price'].shift(-1) #shift price 
df['Daily Returns'] = df['Price_1'] - df['Price'] #calculate daily returns 
df = df.dropna() #because the first value (descending) will have NaN for return, drop to avoid error when graphing 
df['%Returns'] = df['Daily Returns']/df['Price_1'] * 100 #percentage returns 

# ----------- MOVING AVERAGE AS A BUYING STRATEGY 
df['MA5'] = df['Price'].rolling('5d').mean() #ma5 calculation
df['MA10'] = df['Price'].rolling('10d').mean() #ma10 calculation
df['MA20'] = df['Price'].rolling('20d').mean() #ma20 calculation
df['MA50'] = df['Price'].rolling('50d').mean() #ma50 calculation 
df['MA100'] = df['Price'].rolling('100d').mean() #ma100 calculation 
df['MA200'] = df['Price'].rolling('200d').mean() #ma200 calculation 

#buy signal if MA10 exceed MA50, this will index 1/0 whether to buy or not   
#df['BuySig'] = [1 if df.loc[i, 'MA10'] > df.loc[i, 'MA50'] else 0 for i in df.index] #creating an easy to read buy signal based on MA's comparison 

#graphing moving averages - saved to the location that user indicated from the beginning
sns.set() 
plt.figure(figsize = [10,10])
plt.plot(df['MA5'], color='b')
plt.plot(df['MA10'], color='g') 
plt.plot(df['MA20'], color='r') 
plt.plot(df['MA50'], color='c') 
plt.plot(df['MA100'], color='m') 
plt.plot(df['MA200'], color='y') 
plt.xlabel('Time') 
plt.ylabel('Price') 
plt.title('Moving Averages') 
p0 = mpatches.Patch(color='b', label='MA5') 
p1 = mpatches.Patch(color='g', label='MA10') 
p2 = mpatches.Patch(color='r', label='MA20') 
p3 = mpatches.Patch(color='c', label='MA50') 
p4 = mpatches.Patch(color='m', label='MA100') 
p5 = mpatches.Patch(color='y', label='MA200') 
plt.legend(handles = [p0, p1, p2, p3, p4, p5])
plt.savefig(str(figure_save)+'/MA')

# ----------- LOG RETURNS AND DISTRIBUTION OF RETURNS 
# ----------- LOG RETURNS AND DISTRIBUTION OF RETURNS 
df['LogReturns'] = np.log(df['Price_1']) - np.log(df['Price']) #take the log return 

mu = df['LogReturns'].mean() #finding a log mean 
sigma = df['LogReturns'].std(ddof=1) #finding a log std (ddof=1) because it relies on one other variables 

# ----------- NORMALISATION  
pdf = pd.DataFrame() #empty dataFrame to store important variables 
pdf['x'] = np.arange(df['LogReturns'].min()-0.01, df['LogReturns'].max()+0.01, 0.001) #generating a range 'x', normal curve 
pdf['pdf'] = norm.pdf(pdf['x'], mu, sigma)  #using PDF function from norm to generate a normal curve, based on mu and sigma from data 

sns.set()
plt.figure(figsize=[10,10]) 
plt.plot(df['LogReturns'])
plt.show() 

#graphing distribution 
sns.set()
plt.figure(figsize=[10,10]) 
df['LogReturns'].hist(bins=20, color='lightseagreen') #log returns data 
plt.plot(pdf['x'],pdf['pdf'], color='blueviolet') #normal curve 
plt.title('Distribution of Log Returns')
plt.xlabel('Percentage Returns')
plt.ylabel('PDF(x)')
plt.savefig(str(figure_save)+'/LogReturns')

# ----------- LIKELIHOOD FOR % OF RETURNS (This calculates the probability that investment will gain/loss a certain % or above, refer to normal distribution curve the the cummulative density function to understand mathematics) 

loss_range_daily = np.arange(-10, 0, 1) 
gain_range_daily = np.arange(1, 11, 1) 

##DAILY CALCULATION
def likelihoodDaily(lst): #this function returns the likelihood of losing/gaining x% 
    likelihood = pd.DataFrame()
    likelihood['Loss/Gain Daily'] = lst 
    likelihood = likelihood.set_index('Loss/Gain Daily')
    values_list = [] 
    compound_list = []
    for i in lst: 
        value = norm.cdf((i/100), mu, sigma) 
        compounded_value = norm.cdf((i/100), mu, sigma)
        if i > 0: 
            value = 1 - value #because the PDF / CDF calculates the total area up to value, subtract from 1 
        values_list.append(value)
        compound_list.append(compounded_value)
    likelihood['%'] = values_list  
    likelihood['compound'] = compound_list
    if lst[0] > 0: 
        likelihood.to_csv(figure_save+'/gain_daily.csv')
    else:
        likelihood.to_csv(figure_save+'/loss_daily.csv')
    print(likelihood)

likelihoodDaily(loss_range_daily) #call function on loss list 
likelihoodDaily(gain_range_daily) #call function on gain list 

##QUARTERLY (multiples is 60, average active days in one quarter) 
mu60 = mu * 60 
sigma60 = (60**0.5) * sigma 

loss_range = np.arange(-25, -4, 1)
gain_range = np.arange(5, 26, 1)

#loss_quarterly = [-5, -10, -15, -20] #percentages loss list - larger because quarterly fluctuations = larger 
#gain_quarterly = [5, 10, 15, 20] #percentages gain list

def likelihoodQuarterly(lst): #this function returns the likelihood of losing/gaining x% 
    likelihood = pd.DataFrame() 
    likelihood['Loss/Gain Quarterly'] = lst
    likelihood = likelihood.set_index('Loss/Gain Quarterly')
    values_list = [] 
    compound_list = []
    for i in lst: 
        value = norm.cdf((i/100), mu60, sigma60) 
        compounded_value = norm.cdf((i/100), mu60, sigma60)
        if i > 0: 
            value = 1 - value #because the PDF / CDF calculates the total area up to value, subtract from 1 
        values_list.append(value)
        compound_list.append(compounded_value)
    likelihood['%'] = values_list  
    likelihood['compound'] = compound_list 
    if lst[0] > 1: 
        likelihood.to_csv(figure_save+'/gain_quarter.csv')
    else:
        likelihood.to_csv(figure_save+'/loss_quarter.csv')
    print(likelihood) 

likelihoodQuarterly(loss_range) #calling function on loss % 
likelihoodQuarterly(gain_range) #calling function on gain %

##YEARLY (the multiple will change depending on entires; 1Y data has 220 entries, 272 entries) 

# ----------- VALUES AT RISK AND BUYING STRATEGIES - Confidence Interval that Investment will return a gain/loss / two-tailed test

confidence_interval = [90,95]

sample_mean = df['LogReturns'].mean() 
sample_std = df['LogReturns'].std(ddof=1)/df.shape[0]**0.5 

##DAILY 
def findVaRDaily(lst): #this function returns VaR for implied quantiles at daily levels 
    var = pd.DataFrame() 
    var['Confidence Interval'] = confidence_interval 
    var = var.set_index('Confidence Interval') 
    left = [] 
    right = []
    for i in lst: 
        z_left = sample_mean - (i/2)/100
        z_right = sample_mean + (i/2)/100
        left_interval=sample_mean+z_left*sample_std 
        right_interval=sample_mean+z_right*sample_std 
        left.append(left_interval) 
        right.append(right_interval) 
    var['Minimum Returns %'] = left
    var['Maximum Returns %'] = right
    var.to_csv(figure_save+'/VaRDaily.csv')
    print(var)

findVaRDaily(confidence_interval) #calling function on VaR 

##QUARTERLY 
def findVaRQuarterly(lst): #this function returns VaR for implied quantiles at daily levels 
    var = pd.DataFrame() 
    var['Confidence Interval'] = confidence_interval 
    var = var.set_index('Confidence Interval') 
    left = [] 
    right = []
    for i in lst: 
        z_left = sample_mean*60 - (i/2)/100
        z_right = sample_mean*60 + (i/2)/100
        left_interval=(sample_mean*60)+z_left*sample_std*60
        right_interval=(sample_mean*60)+z_right*sample_std*60 
        left.append(left_interval) 
        right.append(right_interval) 
    var['Minimum Returns %'] = left
    var['Maximum Returns %'] = right
    var.to_csv(figure_save+'/VaRQuarterly.csv')
    print(var)  

findVaRQuarterly(confidence_interval)