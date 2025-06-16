from datetime import datetime
from zoneinfo import ZoneInfo

NYC_TZ = ZoneInfo("America/New_York")


class Position:
    """Base class for financial positions."""

    def __init__(self, quantity, symbol, sec_type, market_value, cost, unit_cost,
                 adj_cost, adj_unit_cost, adj_gainloss, adj_gainloss_percent,
                 company_name, last, bid, ask, vol, close, change, change_percent,
                 time, purchase_date, day_held):
        self.quantity = quantity
        self.symbol = symbol
        self.sec_type = sec_type  # 1 for stock, 2 for option
        self.market_value = market_value
        self.cost = cost
        self.unit_cost = unit_cost
        self.adj_cost = adj_cost
        self.adj_unit_cost = adj_unit_cost
        self.adj_gainloss = adj_gainloss
        self.adj_gainloss_percent = adj_gainloss_percent
        self.company_name = company_name
        self.last = last
        self.bid = bid
        self.ask = ask
        self.vol = vol
        self.close = close
        self.change = change
        self.change_percent = change_percent
        self.time = time
        self.purchase_date = purchase_date
        self.day_held = day_held

    def get_current_value(self):
        """Calculate current value of the position."""
        return self.quantity * self.last

    def get_profit_loss(self):
        """Calculate profit/loss for the position."""
        return self.market_value - self.cost

    def __str__(self):
        return (f"{self.__class__.__name__}: {self.quantity} of {self.symbol} "
                f"({self.company_name}) at ${self.last:.2f}, "
                f"Market Value: ${self.market_value:.2f}")


class Stock(Position):
    """Class representing a stock position."""

    def __init__(self, quantity, symbol, sec_type, market_value, cost, unit_cost,
                 adj_cost, adj_unit_cost, adj_gainloss, adj_gainloss_percent,
                 company_name, last, bid, ask, vol, close, change, change_percent,
                 time, purchase_date, day_held, eps, pe, div_share, yield_,
                 ex_div_date, div_date, market_cap, beta, annual_div_rate,
                 avg_vol, _52w_high, _52w_low, has_lots, open_px, day_high, day_low):
        super().__init__(quantity, symbol, sec_type, market_value, cost, unit_cost,
                         adj_cost, adj_unit_cost, adj_gainloss, adj_gainloss_percent,
                         company_name, last, bid, ask, vol, close, change,
                         change_percent, time, purchase_date, day_held)
        self.eps = eps
        self.pe = pe
        self.div_share = div_share
        self.yield_ = yield_
        self.ex_div_date = ex_div_date
        self.div_date = div_date
        self.market_cap = market_cap
        self.beta = beta
        self.annual_div_rate = annual_div_rate
        self.avg_vol = avg_vol
        self._52w_high = _52w_high
        self._52w_low = _52w_low
        self.has_lots = has_lots
        self.open_px = open_px
        self.day_high = day_high
        self.day_low = day_low

    def get_dividend_yield(self):
        """Calculate dividend yield."""
        return self.yield_ if self.yield_ else 0

    def is_near_52w_high(self):
        """Check if stock is near its 52-week high."""
        return self.last >= self._52w_high * 0.95


class Option(Position):
    """Class representing an option position."""

    def __init__(self, quantity, symbol, sec_type, market_value, cost, unit_cost,
                 adj_cost, adj_unit_cost, adj_gainloss, adj_gainloss_percent,
                 company_name, last, bid, ask, vol, close, change, change_percent,
                 time, purchase_date, day_held, asksize, bidsize, today_share,
                 today_exe_price, drip, loan):
        super().__init__(quantity, symbol, sec_type, market_value, cost, unit_cost,
                         adj_cost, adj_unit_cost, adj_gainloss, adj_gainloss_percent,
                         company_name, last, bid, ask, vol, close, change,
                         change_percent, time, purchase_date, day_held)
        self.asksize = asksize
        self.bidsize = bidsize
        self.today_share = today_share
        self.today_exe_price = today_exe_price
        self.drip = drip
        self.loan = loan
        # Parse option details from symbol
        self.ticker, self.expiration_date, self.strike_price, self.option_type = self.parse_option_symbol(symbol)

    @staticmethod
    def parse_option_symbol(symbol: str) -> tuple[str, datetime, float, str]:
        """
        Parse an option symbol to extract ticker, expiration date, strike price, and option type.

        Args:
            symbol (str): Option symbol (e.g., 'OSCR260116P00016000').

        Returns:
            tuple[str, datetime, float, str]: (ticker, expiration_date, strike_price, option_type).

        Raises:
            ValueError: If the symbol format is invalid.
        """
        try:
            # Find the position where the 6-digit date starts (YYMMDD)
            # Assume date is followed by C or P and 8-digit strike
            for i in range(len(symbol) - 14, -1, -1):  # At least 14 chars for date+C/P+strike
                if symbol[i:i + 6].isdigit() and symbol[i + 6] in ['C', 'P'] and symbol[i + 7:i + 15].isdigit():
                    ticker = symbol[:i]
                    date_str = symbol[i:i + 6]
                    option_type = 'Call' if symbol[i + 6] == 'C' else 'Put'
                    strike_str = symbol[i + 7:i + 15]
                    break
            else:
                raise ValueError(f"Invalid option symbol format: {symbol}")

            # Parse expiration date (YYMMDD to datetime)
            year = int(date_str[:2]) + 2000  # Assume 20XX
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            expiration_date = datetime(year, month, day, tzinfo=NYC_TZ)

            # Parse strike price (8 digits, last 3 are decimals, e.g., 00016000 = 16.00)
            strike_price = int(strike_str) / 1000.0

            return ticker, expiration_date, strike_price, option_type

        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse option symbol {symbol}: {str(e)}")

    # NOTE: LLM went stupid
    # def is_in_the_money(self):
    #     """Check if option is in-the-money (simplified check based on last price)."""
    #     if self.last > 0:
    #         return True
    #     return False

    def day_to_expiration(self):
        """Calculate time to expiration in days (NYC timezone)."""
        if self.expiration_date:
            now_nyc = datetime.now(NYC_TZ).date()
            expiration_date_nyc = self.expiration_date.date()
            return (expiration_date_nyc - now_nyc).days
        return None

    def get_contract_type(self):
        """Return the option type (Call or Put)."""
        return self.option_type

    def __str__(self):
        return (f"{self.__class__.__name__}: {self.quantity} of {self.symbol} "
                f"({self.ticker} {self.expiration_date.strftime('%m/%d/%Y')} "
                f"${self.strike_price:.2f} {self.option_type}) at ${self.last:.2f}, "
                f"Market Value: ${self.market_value:.2f}")
