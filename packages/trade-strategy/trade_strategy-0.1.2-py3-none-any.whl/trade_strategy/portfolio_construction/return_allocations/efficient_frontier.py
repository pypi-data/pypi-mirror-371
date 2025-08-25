# Importing modules
import random                                                                                                                                                                                                              
import pandas as pd        
import numpy as np 
import yfinance as yf
import datetime as dt                                                                                                      
from datetime import datetime  

RF = 0 # risk free rate
portfolio_returns = []
portfolio_risks = []
sharpe_ratios = []
portfolio_weights = []

# start_date = '2013-01-01' 
# end_date = '2025-03-27' 

# Object for creating an optimal portfolio                                                                                  
class EfPortfolio():                                                                                                        
    def __init__(self, symbols):                                                                                          
        self.assets = symbols                                   
    # Instantiating Variables                                                                                               
    def Vars(self, symbols, start_date, end_date):                                                                        
        self.tickers = symbols                                                                                  
        # Datetime                                                                                                          
        now = datetime.now()                                                                                                
        # Start date                                                                                                        
        self.start = start_date                                                                                           
        # End date                                                                                                          
        self.end= end_date          
        # Number of portfolios to create                                                                                 
        self.number_of_portfolios = 500                                                                                     
        # Create a Dataframe                                                                                                         
        self.data = pd.DataFrame()                                                                                          
        self.returns = pd.DataFrame() 
           
    # Storing results in a DataFrame                                                                                             
    def StockData(self):                                                                                                    
        for self.ticker in self.tickers:                                                                                    
            self.data[self.ticker] = yf.download(self.ticker, start=self.start, end=self.end, auto_adjust=False)['Adj Close'].pct_change()     
                                                                                                                                    
            if self.returns.empty:                                                                                          
                self.returns = self.data[[self.ticker]]                                                                     
            else:                                                                                                           
                self.returns = self.returns.join(self.data[[self.ticker]], how='outer')            
    # Calculating risk returns                                                                       
    def risk_reward(self):                                                                                                 
        for portfolio in range(self.number_of_portfolios):                                                                  
            #Generate random portfolio weights                                                                              
            self.weights = np.random.random_sample(len(self.tickers))                                                       
            self.weights = np.round((self.weights / np.sum(self.weights)), 3)                                               
            portfolio_weights.append(self.weights)                                                                
                                                                                                                                    
            #Calculate annualized returns                                                                                   
            self.annualized_return = np.sum(self.returns.mean() * self.weights) * 252                                       
            portfolio_returns.append(self.annualized_return)                                                                
                                                                                                                                    
            #Matrix covariance & portfolio risk calculation                                                                 
            self.matrix_covariance = self.returns.cov() * 252                                                               
            self.portfolio_variance = np.dot(self.weights.T,                                                                
                                            np.dot(self.matrix_covariance, self.weights))                                       
            self.portfolio_standard_deviation = np.sqrt(self.portfolio_variance)                                            
            portfolio_risks.append(self.portfolio_standard_deviation)                                                       
                                                                                                                                    
            #Sharpe ratio                                                                                                   
            self.sharpe_ratio = (self.annualized_return - RF) / self.portfolio_standard_deviation                           
            sharpe_ratios.append(self.sharpe_ratio)
    # Outputting optimization results                
    def results(self):
        self.portfolio_returns = np.array(portfolio_returns)
        self.portfolio_risks = np.array(portfolio_risks)
        self.sharpe_ratios = np.array(sharpe_ratios)

        self.portfolio_metrics = [self.portfolio_returns, self.portfolio_risks, self.sharpe_ratios, portfolio_weights]

        # Create DataFrame for Portfolio Metrics
        self.portfolios_df = pd.DataFrame(self.portfolio_metrics).T
        self.portfolios_df.columns = ['Returns', 'Risk', 'Sharpe Ratio', 'Weights']

        # Calculate Minimum Risk Portfolio
        self.min_risk = self.portfolios_df.iloc[self.portfolios_df['Risk'].astype(float).idxmin()]

        # Calculate Portfolio with Highest Return
        self.highest_return = self.portfolios_df.iloc[self.portfolios_df['Returns'].astype(float).idxmax()]

        # Calculate Portfolio with Highest Sharpe Ratio
        self.highest_sharpe = self.portfolios_df.iloc[self.portfolios_df['Sharpe Ratio'].astype(float).idxmax()] 

        # Portfolio yielding the lowest risk                                                                                                                 
        print('Lowest risk Allocation')                                                                                                
        print(self.min_risk)                                                                                                
        print(self.tickers)                                                                                                 
        print('')                                                                                                           
        # Portfolio yielding the highest                                                                                                                         
        print('Highest Returns Allocation')                                                                                            
        print(self.highest_return)                                                                                          
        print(self.tickers)                                                                                                 
        print('')                                                                                                           
        # Portfolio yielding the highest risk                                                                                                                         
        print('Highest Sharpe Allocation')                                                                                             
        print(self.highest_sharpe)                                                                                          
        print(self.tickers)                                                                                                 
        print('')


# Function for Calling Object
def risk_return(symbols, start_date, end_date):                                                                                                             
    # Instantiating Object                                                                                                        
    cEfPortfolio = EfPortfolio(symbols)                                                                                                                                                                         
    cEfPortfolio.Vars(symbols, start_date, end_date)                                                                                          
    cEfPortfolio.StockData()                                                                                                
    cEfPortfolio.risk_reward()                                                                                             
    cEfPortfolio.results()        
                                                                                
# risk_return(symbols)
