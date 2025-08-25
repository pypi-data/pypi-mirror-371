from interface import implements
from typing import Tuple, List, Dict, Optional, Union
from datetime import datetime, date

import math
import arrow
import pandas as pd
import httpx
import json

from fast_tradier.interfaces.IBrokerClient import IBrokerClient
from fast_tradier.models.trading.OptionOrder import OptionOrder # order to be placed
from fast_tradier.models.trading.EquityOrder import EquityOrder
from fast_tradier.models.trading.OrderBase import OrderBase
from fast_tradier.models.account.AccountOrder import AccountOrder # order retrieved from account
from fast_tradier.models.market_data.Quote import Quote
from fast_tradier.models.account.Position import Position
from fast_tradier.models.market_data.Hlocv import Hlocv
from fast_tradier.models.trading.Interval import Interval
from fast_tradier.models.account.AccountBalance import AccountBalance
from fast_tradier.interfaces.IRealTimeQuoteProvider import IRealTimeQuoteProvider
from fast_tradier.utils.TimeUtils import US_Eastern_TZ, YYYYMDHHMM_Format, YMD_Format, YMDHMS_Format, TimeUtils
from fast_tradier.utils.OptionUtils import OptionChain_Headers

class FastTradierClient(implements(IBrokerClient)):
    '''tradier client for interacting with Tradier API'''

    def __init__(self, access_token: str, account_id: str, is_prod: bool = True, real_time_quote_provider: Optional[IRealTimeQuoteProvider] = None, http_client: Optional[httpx.Client] = None):
        self.__bear_at = f'Bearer {access_token}'
        self.__auth_headers = {'Authorization': self.__bear_at, 'Accept': 'application/json'}
        self.__is_prod = is_prod
        self.__account_id = account_id
        self.__real_time_quote_provider = real_time_quote_provider
        self.__base_host = 'https://sandbox.tradier.com/v1/'
        self.__client = http_client
        self.__keep_client_alive = http_client is not None # keep the given client alive if not None
        if is_prod:
            self.__base_host = 'https://api.tradier.com/v1/'

    @property
    def market_open(self) -> datetime:
        return self.__market_open

    @property
    def keep_client_alive(self) -> bool:
        return self.__keep_client_alive

    @property
    def market_close(self) -> datetime:
        return self.__market_close

    @property
    def index_close(self) -> datetime:
        return self.__index_close
    
    @property
    def host_base(self) -> str:
        return self.__base_host
    
    @property
    def account_id(self) -> str:
        return self.__account_id

    def today(self) -> datetime:
        return datetime.now(US_Eastern_TZ)

    def is_market_in_session_now(self) -> Tuple:
        is_open, _, today_window = self.is_market_open_today()
        if not is_open:
            return False, False

        today = self.today()
        today_str = today.strftime(YMD_Format)
        open_hour = today_window['start']
        close_hour = today_window['end']
        index_close_hour = close_hour[: -2] + '15' # index options close at 16:15

        open_t = '{} {}'.format(today_str, open_hour) # make it look like '2022-01-22 09:30'
        close_t = '{} {}'.format(today_str, close_hour)
        index_close_t = '{} {}'.format(today_str, index_close_hour)
        self.__market_open = arrow.get(open_t, YYYYMDHHMM_Format, tzinfo=US_Eastern_TZ)
        self.__market_close = arrow.get(close_t, YYYYMDHHMM_Format, tzinfo=US_Eastern_TZ)
        self.__index_close = arrow.get(index_close_t, YYYYMDHHMM_Format, tzinfo=US_Eastern_TZ)
        is_index_open = (today <= self.index_close) #whether index options trade is still open

        if today < self.market_open or today > self.market_close:
            return False, is_index_open

        return True, True
    
    def is_market_open_today(self, market: str = 'NYSE') -> Tuple:
        today = self.today()
        url = 'https://api.tradier.com/v1/markets/calendar?month={}&year={}'.format(today.month, today.year)
        day_arr = []
        client = httpx.Client() if self.__client is None else self.__client
        try:
            response = client.get(url=url, headers=self.__auth_headers)
            json_res = response.json()
            day_arr = json_res["calendar"]["days"]["day"]
        finally:
            if not self.keep_client_alive:
                client.close()
        
        today_str = today.strftime("%Y-%m-%d")
        today_open_window = None

        is_open = False
        for day in day_arr:
            if day['date'] == today_str:
                if day['status'] == 'open':
                    is_open = True
                    today_open_window = day['open'] # e.g. {start: 09:30, end: 16:00}
                break

        open_day_strs = [d["date"] for d in day_arr] # e.g. ['2023-08-08']
        return is_open, open_day_strs, today_open_window
    
    # https://documentation.tradier.com/brokerage-api/markets/get-quotes
    def get_quotes(self, symbols: List[str]) -> List[Quote]:
        '''get quote for symbol, could be stock or option symbol'''
        url = f'{self.host_base}markets/quotes'
        params = {'symbols': ','.join(symbols), 'greeks': 'false'}
        results = []
        client = httpx.Client() if self.__client is None else self.__client
        try:
            response = client.post(url=url, data=params, headers=self.__auth_headers)
            json_res = response.json()
            if 'quotes' in json_res and json_res['quotes'] is not None:
                quote_objs = json_res['quotes']['quote']

                if quote_objs is not None:
                    if isinstance(quote_objs, List):
                        '''API returns a list of quotes if input is a list of tickers'''
                        for quote_obj in quote_objs:
                            results.append(Quote(**quote_obj))
                    elif isinstance(quote_objs, Dict):
                        '''API returns a single Dict object if input is a single ticker'''
                        results = [Quote(**quote_objs)]
            return results
        finally:
            if not self.keep_client_alive:
                client.close()

    def get_history(self, symbol: str, start_date: date, end_date: date, interval: Interval = Interval.Daily, open_hours_only: bool = True) -> Optional[pd.DataFrame]:
        url = f'{self.host_base}markets/history'
        client = httpx.Client() if self.__client is None else self.__client
        try:
            start_dt_str = start_date.strftime(YMD_Format)
            end_dt_str = end_date.strftime(YMD_Format)
            query_params = {
                'symbol': symbol.upper(),
                'interval': interval.value,
                'start': start_dt_str,
                'end': end_dt_str,
                'session_filter': 'open' if open_hours_only is True else 'all', 
            }
            response = client.get(url = url, params=query_params, headers=self.__auth_headers)
            json_res = response.json()
            history_data: List = []
            if 'history' in json_res:
                json_data_arr: List[Dict] = []
                if interval == Interval.Daily:
                    json_data_arr = json_res['history']['day']
                elif interval == Interval.Weekly:
                    json_data_arr = json_res['history']['week']
                else:
                    json_data_arr = json_res['history']['month']

                for his_json in json_data_arr:
                    cur_hlocv = Hlocv(**his_json)
                    row = [cur_hlocv.date, cur_hlocv.open_price, cur_hlocv.high, cur_hlocv.low, cur_hlocv.close, cur_hlocv.volume]
                    history_data.append(row)

            if len(history_data) > 0:
                df = pd.DataFrame(history_data)
                df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                return df
            return None
        finally:
            if not self.keep_client_alive:
                client.close()

    def get_order_status(self, order_id: int) -> Optional[str]:
        account_orders = self.get_account_orders()
        for acc_order in account_orders:
            if acc_order.id == order_id:
                return acc_order.status        

        return None
    
    def get_account_orders(self) -> List[AccountOrder]:
        url = f'{self.host_base}accounts/{self.account_id}/orders'
        client = httpx.Client() if self.__client is None else self.__client
        try:
            retrieved_orders = []
            response = client.get(url=url, params={'includeTags': 'true'}, headers=self.__auth_headers)
            json_res = response.json()
            if 'orders' in json_res and 'order' in json_res['orders']:
                order_obj = json_res['orders']['order']
                if isinstance(order_obj, Dict):
                    retrieved_orders = [AccountOrder(**order_obj)]
                elif isinstance(order_obj, List):
                    for order_json in order_obj:
                        retrieved_orders.append(AccountOrder(**order_json))

            return retrieved_orders
        finally:
            if not self.keep_client_alive:
                client.close()
    
    def get_single_account_order(self, order_id: int) -> Optional[AccountOrder]:
        """Get a single account order by id."""
        url = f'{self.host_base}accounts/{self.account_id}/orders/{order_id}'
        client = httpx.Client() if self.__client is None else self.__client
        try:
            response = client.get(url=url, headers=self.__auth_headers)
            json_res = response.json()
            if 'order' in json_res:
                return AccountOrder(**json_res['order'])
            return None
        finally:
            if not self.keep_client_alive:
                client.close()

    def get_option_expirations(self, symbol: str) -> List[str]:
        symbol = symbol.upper()
        url = f'{self.host_base}markets/options/expirations'
        client = httpx.Client() if self.__client is None else self.__client
        try:
            response = client.get(url, params={'symbol': symbol, 'includeAllRoots': 'true', 'strikes': 'false'}, headers=self.__auth_headers)
            json_res = response.json()
            if json_res["expirations"] is not None:
                return json_res["expirations"]["date"]
            return None
        finally:
            if not self.keep_client_alive:
                client.close()

    def place_order(self, order: OrderBase) -> Optional[int]:
        url = f'{self.host_base}accounts/{self.account_id}/orders'
        client = httpx.Client() if self.__client is None else self.__client
        try:
            order_json = order.to_json()
            if 'option_legs' in order_json:
                order_json.pop('option_legs') #clean up
            response = client.post(url, data=order_json, headers=self.__auth_headers)
            res = response.json()
            if res['order'] is not None and res['order']['status'] is not None and res['order']['status'].upper() == 'OK':
                return res['order']['id']
            return None
        finally:
            if not self.keep_client_alive:
                client.close()

    def place_option_order(self, order: OptionOrder) -> Optional[int]:
        return self.place_order(order)

    def place_equity_order(self, order: EquityOrder) -> Optional[int]:
        return self.place_order(order)

    def cancel_order(self, order_id: int) -> bool:
        url = f'{self.host_base}accounts/{self.account_id}/orders/{order_id}'
        client = httpx.Client() if self.__client is None else self.__client
        try:
            data = {}
            response = client.delete(url=url, params=data, headers=self.__auth_headers)
            res = response.json()
            if 'order' in res and 'status' in res['order']:
                return res['order']['status'].upper() == 'OK'
            return False
        finally:
            if not self.keep_client_alive:
                client.close()

    def get_option_chain(self, symbol: str, expiration: str, greeks: bool = True) -> Optional[Dict]:
        url = f'{self.host_base}markets/options/chains'
        symbol = symbol.upper()
        client = httpx.Client() if self.__client is None else self.__client
        try:
            call_options = []
            put_options = []

            response = client.get(url, params={'symbol': symbol, 'expiration': expiration, 'greeks': greeks}, headers=self.__auth_headers)
            json_res = response.json()
            if json_res["options"] is not None:
                chain = json_res["options"]["option"]
                underlying_price = None
                if self.__real_time_quote_provider is not None:
                    try:
                        underlying_price = self.__real_time_quote_provider.get_price(symbol)
                    except Exception as inner_ex:
                        print('exception getting real time quote: ', inner_ex)

                if underlying_price is None:
                    symbol_quotes = self.get_quotes([symbol])
                    if len(symbol_quotes) > 0:
                        underlying_price = symbol_quotes[0].last

                now_unixts = int(arrow.utcnow().datetime.timestamp())
                for o in chain:
                    gamma = 0
                    delta = 0
                    vega = 0
                    greeks_nums = o['greeks']
                    if greeks_nums is not None: 
                        gamma = greeks_nums['gamma'] if greeks_nums['gamma'] is not None and not math.isnan(greeks_nums['gamma']) else 0
                        delta = greeks_nums['delta'] if greeks_nums['delta'] is not None and not math.isnan(greeks_nums['delta']) else 0
                        vega = greeks_nums['vega'] if greeks_nums['vega'] is not None and not math.isnan(greeks_nums['vega']) else 0

                    row = o['symbol'], o['strike'], 0 if pd.isna(o['last']) else o['last'], o['open_interest'], o['ask'], o['bid'], o['expiration_date'], TimeUtils.convert_unix_ts(o['bid_date']).strftime(YMDHMS_Format), o['volume'], underlying_price, now_unixts, gamma, delta, vega
                    if o['option_type'] == 'call':
                        call_options.append(row)
                    else:
                        put_options.append(row)

            call_df = pd.DataFrame(call_options)
            call_df.columns = OptionChain_Headers
            put_df = pd.DataFrame(put_options)
            put_df.columns = OptionChain_Headers
            return {
                'expiration': expiration,
                'ticker': symbol,
                'call_chain': call_df,
                'put_chain': put_df
                }
        finally:
            if not self.keep_client_alive:
                client.close()

    def modify_option_order(self, modified_order: OptionOrder) -> bool:
        url = f'{self.host_base}accounts/{self.account_id}/orders/{modified_order.id}'
        client = httpx.Client() if self.__client is None else self.__client
        try:
            response = client.put(url=url, data=modified_order.to_json(), headers=self.__auth_headers)
            res = response.json()
            if 'order' in res and 'status' in res['order']:
                return res['order']['status'].upper() == 'OK'
            return False
        finally:
            if not self.keep_client_alive:
                client.close()

    def get_positions(self) -> List[Position]:
        url = f'{self.host_base}accounts/{self.account_id}/positions'
        client = httpx.Client() if self.__client is None else self.__client
        try:
            response = client.get(url=url,
                                params={},
                                headers=self.__auth_headers)
            res = response.json()
            results = []
            if res['positions'] is not None and 'position' in res['positions']:
                pos_obj = res['positions']['position']
                if isinstance(pos_obj, List):
                    for position_dict in pos_obj:
                        results.append(Position(**position_dict))
                elif isinstance(pos_obj, Dict):
                    results = [Position(**pos_obj)]
            return results
        finally:
            if not self.keep_client_alive:
                client.close()

    def get_account_balance(self) -> Optional[AccountBalance]:
        url = f'{self.host_base}accounts/{self.account_id}/balances'
        client = httpx.Client() if self.__client is None else self.__client
        balances = None
        try:
            response = client.get(url=url,
                                    params={},
                                    headers=self.__auth_headers)
            res = response.json()
            if res['balances'] is not None:
                balances = AccountBalance(**res['balances'])
            return balances
        finally:
            if not self.keep_client_alive:
                client.close()