from efficient_frontier import risk_return

# Dates
start_date = '2013-01-01' 
end_date = '2025-03-27' 

# tickers
symbols = ["AAPL", "MSFT", "GOOG"]

# Calling function
risk_return(symbols, start_date, end_date)