import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from trade_strategy.portfolio_construction.return_allocations.efficient_frontier import EfPortfolio, risk_return, portfolio_returns, portfolio_risks, sharpe_ratios, portfolio_weights

class TestEfficientFrontier(unittest.TestCase):

    def setUp(self):
        # Clear global lists before each test
        portfolio_returns.clear()
        portfolio_risks.clear()
        sharpe_ratios.clear()
        portfolio_weights.clear()

    @patch('yfinance.download')
    def test_risk_return_function(self, mock_yf_download):
        # Mock yfinance.download to return predictable data
        mock_data = pd.DataFrame({
            'Adj Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01', periods=11, freq='D')))
        mock_yf_download.return_value = mock_data

        symbols = ['AAPL', 'GOOG']
        start_date = '2023-01-01'
        end_date = '2023-01-10'

        # Call the main function
        risk_return(symbols, start_date, end_date)

        # Assertions
        self.assertGreater(len(portfolio_returns), 0)
        self.assertGreater(len(portfolio_risks), 0)
        self.assertGreater(len(sharpe_ratios), 0)
        self.assertGreater(len(portfolio_weights), 0)

        self.assertEqual(len(portfolio_returns), len(portfolio_risks))
        self.assertEqual(len(portfolio_returns), len(sharpe_ratios))
        self.assertEqual(len(portfolio_returns), len(portfolio_weights))

        # Check if the results DataFrame is created and has expected columns
        # We need to instantiate EfPortfolio again to access its internal state after risk_return
        ef_portfolio_instance = EfPortfolio(symbols)
        ef_portfolio_instance.Vars(symbols, start_date, end_date)
        ef_portfolio_instance.StockData()
        ef_portfolio_instance.risk_reward()
        ef_portfolio_instance.results()

        self.assertIsInstance(ef_portfolio_instance.portfolios_df, pd.DataFrame)
        self.assertListEqual(list(ef_portfolio_instance.portfolios_df.columns), ['Returns', 'Risk', 'Sharpe Ratio', 'Weights'])
        self.assertFalse(ef_portfolio_instance.portfolios_df.empty)

        # Check if min_risk, highest_return, highest_sharpe are Series
        self.assertIsInstance(ef_portfolio_instance.min_risk, pd.Series)
        self.assertIsInstance(ef_portfolio_instance.highest_return, pd.Series)
        self.assertIsInstance(ef_portfolio_instance.highest_sharpe, pd.Series)

        

    @patch('yfinance.download')
    def test_ef_portfolio_stock_data(self, mock_yf_download):
        mock_data = pd.DataFrame({
            'Adj Close': [100, 101, 102, 103, 104, 105]
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01', periods=6, freq='D')))
        mock_yf_download.return_value = mock_data

        symbols = ['MSFT']
        start_date = '2023-01-01'
        end_date = '2023-01-05'

        ef = EfPortfolio(symbols)
        ef.Vars(symbols, start_date, end_date)
        ef.StockData()

        self.assertIsInstance(ef.data, pd.DataFrame)
        self.assertIsInstance(ef.returns, pd.DataFrame)
        self.assertIn('MSFT', ef.data.columns)
        self.assertIn('MSFT', ef.returns.columns)
        self.assertFalse(ef.returns.empty)
        self.assertTrue(np.isnan(ef.returns['MSFT'].iloc[0])) # First value is NaN due to pct_change()
        self.assertAlmostEqual(ef.returns['MSFT'].iloc[1], 0.01) # (101-100)/100

    @patch('yfinance.download')
    def test_ef_portfolio_risk_reward_calculations(self, mock_yf_download):
        mock_data = pd.DataFrame({
            'Adj Close': [100, 101, 102, 103, 104, 105]
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01', periods=6, freq='D')))
        mock_yf_download.return_value = mock_data

        symbols = ['MSFT']
        start_date = '2023-01-01'
        end_date = '2023-01-05'

        ef = EfPortfolio(symbols)
        ef.Vars(symbols, start_date, end_date)
        ef.StockData()
        ef.number_of_portfolios = 5 # Reduce for faster testing

        # Patch numpy.random.random_sample to return a fixed weight for predictability
        with patch('numpy.random.random_sample', return_value=np.array([1.0])):
            ef.risk_reward()

        self.assertEqual(len(portfolio_returns), ef.number_of_portfolios)
        self.assertEqual(len(portfolio_risks), ef.number_of_portfolios)
        self.assertEqual(len(sharpe_ratios), ef.number_of_portfolios)
        self.assertEqual(len(portfolio_weights), ef.number_of_portfolios)

        # Check if weights sum to 1 (approximately due to rounding)
        for weights in portfolio_weights:
            self.assertAlmostEqual(np.sum(weights), 1.0, places=3)

        # Basic check for non-zero values (since we mocked data, they should be calculable)
        self.assertTrue(all(r != 0 for r in portfolio_returns))
        self.assertTrue(all(r != 0 for r in portfolio_risks))
        # Sharpe ratio can be zero or negative, so not checking for non-zero

if __name__ == '__main__':
    unittest.main()
