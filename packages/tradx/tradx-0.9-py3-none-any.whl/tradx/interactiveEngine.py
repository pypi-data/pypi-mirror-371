# Importing from xts_api_client
from xts_api_client.xts_connect_async import XTSConnect
from xts_api_client.interactive_socket_client import InteractiveSocketClient
from xts_api_client.interactive_socket import OrderSocket_io

# Importing from self module
from tradx.logger.logger import *
from tradx.baseClass.baseAlgo import BaseAlgo as bA
from tradx.baseClass.interactive.orderEvent import OrderEvent
from tradx.baseClass.interactive.positionEvent import PositionEvent
from tradx.baseClass.interactive.tradeEvent import TradeEvent
from tradx.baseClass.interactive.tradeConversionEvent import TradeConversionEvent

# Importing other python module
from datetime import datetime
import os
from decimal import Decimal
from typing import Dict, Any
import asyncio
import shortuuid


class interactiveEngine(InteractiveSocketClient):
    """
    interactiveEngine class for handling interactive trading operations.
    This class extends the InteractiveSocketClient and provides methods for placing various types of orders,
    handling incoming messages, and managing the interactive trading session.
    Methods:
        __init__(self, user_logger: logging.Logger = None) -> None:
        async market_order(self, exchangeSegment: str, exchangeInstrumentID: int, productType: str, orderQuantity: int, orderUniqueIdentifier: str) -> None:
        async stop_market_order(self, exchangeSegment: str, exchangeInstrumentID: int, productType: str, orderQuantity: int, stopPrice: Decimal, orderUniqueIdentifier: str) -> None:
        async limit_order(self, exchangeSegment: str, exchangeInstrumentID: int, productType: str, orderQuantity: int, limitPrice: Decimal, orderUniqueIdentifier: str) -> None:
        async stop_limit_order(self, exchangeSegment: str, exchangeInstrumentID: int, productType: str, orderQuantity: int, limitPrice: Decimal, stopPrice: Decimal, orderUniqueIdentifier: str) -> None:
        async initialize(self) -> None:
        async on_order(self, message: str) -> None:
        async on_connect(self) -> None:
        async on_message(self, xts_message: Any) -> None:
        async on_error(self, xts_message: Any) -> None:
        async on_joined(self, data: Any) -> None:
        async on_messagelogout(self, data: Any) -> None:
        async on_disconnect(self) -> None:
        async on_trade(self, xts_message: str) -> None:
        async on_position(self, xts_message: str) -> None:
        async on_tradeconversion(self, xts_message: str) -> None:
        async login(self) -> None:
        async shutdown(self) -> None:
        async getBalance(self) -> int:
        async Liquidate(self, exchangeSegment: str) -> None:
        async cancel_order(self, appOrderID: Any, orderUniqueIdentifier: str) -> None
    """

    def __init__(
        self,
        api_key: str,
        api_password: str,
        source: str,
        root: str,
        user_logger: logging.Logger = None,
    ) -> None:
        """
        Initialize the InteractiveEngine object.
        Args:
            api_key (str): The API key required for authentication.
            api_password (str): The API password required for authentication.
            source (str): The source identifier.
            root (str): The root directory path.
            user_logger (logging.Logger, optional): Logger instance for user logging. Defaults to None.
        Raises:
            AssertionError: If any of the required arguments (api_key, api_password, source, root) are not provided.
        Attributes:
            _api_key (str): Internal API key.
            _api_password (str): Internal API password.
            _source (str): Internal source identifier.
            _root (str): Internal root directory path.
            api_key (str): Public API key.
            api_password (str): Public API password.
            source (str): Public source identifier.
            root (str): Public root directory path.
            shortuuid (shortuuid): Short UUID instance.
            set_interactiveToken (str): Interactive token, initially set to None.
            set_iuserID (str): User ID, initially set to None.
            funds (int): User funds, initially set to None.
            strategy_to_id (Dict[str, BaseAlgo]): Mapping of strategy names to BaseAlgo instances.
            position_diary_engine (dict): Position diary engine, initially an empty dictionary.
            user_logger (logging.Logger): Logger instance for user logging.
        """
        assert api_key, "API key is required"
        assert api_password, "API password is required"
        assert source, "Source is required"
        assert root, "Root is required"
        self._api_key: str = api_key
        self._api_password: str = api_password
        self._source: str = source
        self._root: str = root
        self.shortuuid: shortuuid = shortuuid
        self.set_interactiveToken: str = None
        self.set_iuserID: str = None
        self.set_isInvestorClient: str = None
        self.funds: int = None
        self.strategy_to_id: Dict[str, bA] = {}
        self.position_diary_engine = {}
        self.isConnected: bool = False
        self.isLive: bool = False
        self.user_logger = user_logger
        if user_logger:
            self.user_logger.info(
                "Interactive Engine Object initialized.",
                caller=f"{self.set_iuserID}.__init__",
            )

    async def market_order(
        self,
        exchangeSegment: str,
        exchangeInstrumentID: int,
        productType: str,
        orderQuantity: int,
        orderUniqueIdentifier: str,
    ) -> None:
        """
        Places a market order on the specified exchange.
        Args:
            exchangeSegment (str): The segment of the exchange where the order is to be placed. Allowed values: xts_api_client.xts_connect_async.EXCHANGE_NSECM, xts_api_client.xts_connect_async.EXCHANGE_BSECM, xts_api_client.xts_connect_async.EXCHANGE_NSEFO, xts_api_client.xts_connect_async.EXCHANGE_BSEFO, xts_api_client.xts_connect_async.EXCHANGE_NSECD, xts_api_client.xts_connect_async.EXCHANGE_MCXFO.
            exchangeInstrumentID (int): The ID of the instrument to be traded.
            productType (str): The type of product being traded. Allowed values: xts_api_client.xts_connect_async.PRODUCT_MIS, xts_api_client.xts_connect_async.PRODUCT_NRML.
            orderQuantity (int): The quantity of the order. Positive for buy, negative for sell.
            orderUniqueIdentifier (str): A unique identifier for the order.
        Returns:
            None
        Notes:
            - If the orderQuantity is 0, the function will return immediately without placing an order.
            - The order type is set to market order.
            - The order side is determined based on the sign of orderQuantity.
            - The time in force is set to day validity.
            - The disclosed quantity, limit price, and stop price are set to 0.
            - Logs the response if user_logger is available.
        """
        # assert (
        #     self.isConnected is True
        # ), f"Interactive Engine is not connected, Rejecting order with orderID: {orderUniqueIdentifier}."
        allowed_exchange_segments = [
            XTSConnect.EXCHANGE_NSECM,
            XTSConnect.EXCHANGE_BSECM,
            XTSConnect.EXCHANGE_NSEFO,
            XTSConnect.EXCHANGE_BSEFO,
            XTSConnect.EXCHANGE_NSECD,
            XTSConnect.EXCHANGE_MCXFO,
        ]
        allowed_product_types = [
            XTSConnect.PRODUCT_MIS,
            XTSConnect.PRODUCT_NRML,
            XTSConnect.PRODUCT_CNC,
        ]
        assert (
            exchangeSegment in allowed_exchange_segments
        ), f"Invalid exchangeSegment: {exchangeSegment}"
        assert (
            productType in allowed_product_types
        ), f"Invalid productType: {productType}"
        if orderQuantity == 0:
            return
        response = await self.xt.place_order(
            exchangeSegment=exchangeSegment,
            exchangeInstrumentID=exchangeInstrumentID,
            productType=productType,
            orderType=self.xt.ORDER_TYPE_MARKET,
            orderSide=(
                self.xt.TRANSACTION_TYPE_BUY
                if orderQuantity > 0
                else self.xt.TRANSACTION_TYPE_SELL
            ),
            timeInForce=self.xt.TimeinForce_DAY,
            disclosedQuantity=0,
            orderQuantity=abs(orderQuantity),
            limitPrice=0,
            stopPrice=0,
            orderUniqueIdentifier=orderUniqueIdentifier,
            clientID=self.set_iuserID,
        )
        if self.user_logger:
            self.user_logger.info(
                f"Place Order: {response}",
                caller=f"{self.set_iuserID}.market_order",
            )

    async def stop_market_order(
        self,
        exchangeSegment: str,
        exchangeInstrumentID: int,
        productType: str,
        orderQuantity: int,
        stopPrice: Decimal,
        orderUniqueIdentifier: str,
    ) -> None:
        """
        Places a stop market order on the specified exchange.
        Args:
            exchangeSegment (str): The segment of the exchange where the order is to be placed. Allowed values: xts_api_client.xts_connect_async.EXCHANGE_NSECM, xts_api_client.xts_connect_async.EXCHANGE_BSECM, xts_api_client.xts_connect_async.EXCHANGE_NSEFO, xts_api_client.xts_connect_async.EXCHANGE_BSEFO, xts_api_client.xts_connect_async.EXCHANGE_NSECD, xts_api_client.xts_connect_async.EXCHANGE_MCXFO.
            exchangeInstrumentID (int): The ID of the instrument to be traded.
            productType (str): The type of product being traded. Allowed values: xts_api_client.xts_connect_async.PRODUCT_MIS, xts_api_client.xts_connect_async.PRODUCT_NRML.
            orderQuantity (int): The quantity of the order. Positive for buy, negative for sell.
            stopPrice (Decimal): The stop price for the order.
            orderUniqueIdentifier (str): A unique identifier for the order.
        Returns:
            None
        Notes:
            - If orderQuantity is 0, the function will return immediately without placing an order.
            - The order type is set to stop market.
            - The order side is determined based on the sign of orderQuantity.
            - The time in force is set to day validity.
            - The disclosed quantity is set to 0.
            - The limit price is set to 0.
            - Logs the response if user_logger is available.
        """
        assert (
            self.isConnected is True
        ), f"Interactive Engine is not connected, Rejecting order with orderID: {orderUniqueIdentifier}."
        allowed_exchange_segments = [
            XTSConnect.EXCHANGE_NSECM,
            XTSConnect.EXCHANGE_BSECM,
            XTSConnect.EXCHANGE_NSEFO,
            XTSConnect.EXCHANGE_BSEFO,
            XTSConnect.EXCHANGE_NSECD,
            XTSConnect.EXCHANGE_MCXFO,
        ]
        allowed_product_types = [
            XTSConnect.PRODUCT_MIS,
            XTSConnect.PRODUCT_NRML,
            XTSConnect.PRODUCT_CNC,
        ]
        assert (
            exchangeSegment in allowed_exchange_segments
        ), f"Invalid exchangeSegment: {exchangeSegment}"
        assert (
            productType in allowed_product_types
        ), f"Invalid productType: {productType}"
        if orderQuantity == 0:
            return
        response = await self.xt.place_order(
            exchangeSegment=exchangeSegment,
            exchangeInstrumentID=exchangeInstrumentID,
            productType=productType,
            orderType=self.xt.ORDER_TYPE_STOPMARKET,
            orderSide=(
                self.xt.TRANSACTION_TYPE_BUY
                if orderQuantity > 0
                else self.xt.TRANSACTION_TYPE_SELL
            ),
            timeInForce=self.xt.TimeinForce_DAY,
            disclosedQuantity=0,
            orderQuantity=abs(orderQuantity),
            limitPrice=0,
            stopPrice=stopPrice.to_eng_string(),
            orderUniqueIdentifier=orderUniqueIdentifier,
            clientID=self.set_iuserID,
        )
        if self.user_logger:
            self.user_logger.info(
                f"Place Order: {response}",
                caller=f"{self.set_iuserID}.stop_market_order",
            )

    async def limit_order(
        self,
        exchangeSegment: str,
        exchangeInstrumentID: int,
        productType: str,
        orderQuantity: int,
        limitPrice: Decimal,
        orderUniqueIdentifier: str,
    ):
        """
        Places a limit order on the specified exchange.
        Args:
            exchangeSegment (str): The segment of the exchange where the order is to be placed. Allowed values: xts_api_client.xts_connect_async.EXCHANGE_NSECM, xts_api_client.xts_connect_async.EXCHANGE_BSECM, xts_api_client.xts_connect_async.EXCHANGE_NSEFO, xts_api_client.xts_connect_async.EXCHANGE_BSEFO, xts_api_client.xts_connect_async.EXCHANGE_NSECD, xts_api_client.xts_connect_async.EXCHANGE_MCXFO.
            exchangeInstrumentID (int): The ID of the instrument to be traded.
            productType (str): The type of product being traded. Allowed values: xts_api_client.xts_connect_async.PRODUCT_MIS, xts_api_client.xts_connect_async.PRODUCT_NRML.
            orderQuantity (int): The quantity of the order. Positive for buy, negative for sell.
            limitPrice (Decimal): The limit price for the order.
            orderUniqueIdentifier (str): A unique identifier for the order.
        Returns:
            None
        Notes:
            - If orderQuantity is 0, the function will return immediately without placing an order.
            - Logs the response of the order placement if user_logger is set.
        """
        assert (
            self.isConnected is True
        ), f"Interactive Engine is not connected, Rejecting order with orderID: {orderUniqueIdentifier}."
        allowed_exchange_segments = [
            XTSConnect.EXCHANGE_NSECM,
            XTSConnect.EXCHANGE_BSECM,
            XTSConnect.EXCHANGE_NSEFO,
            XTSConnect.EXCHANGE_BSEFO,
            XTSConnect.EXCHANGE_NSECD,
            XTSConnect.EXCHANGE_MCXFO,
        ]
        allowed_product_types = [
            XTSConnect.PRODUCT_MIS,
            XTSConnect.PRODUCT_NRML,
            XTSConnect.PRODUCT_CNC,
        ]
        assert (
            exchangeSegment in allowed_exchange_segments
        ), f"Invalid exchangeSegment: {exchangeSegment}"
        assert (
            productType in allowed_product_types
        ), f"Invalid productType: {productType}"
        if orderQuantity == 0:
            return
        response = await self.xt.place_order(
            exchangeSegment=exchangeSegment,
            exchangeInstrumentID=exchangeInstrumentID,
            productType=productType,
            orderType=self.xt.ORDER_TYPE_LIMIT,
            orderSide=(
                self.xt.TRANSACTION_TYPE_BUY
                if orderQuantity > 0
                else self.xt.TRANSACTION_TYPE_SELL
            ),
            timeInForce=self.xt.TimeinForce_DAY,
            disclosedQuantity=0,
            orderQuantity=abs(orderQuantity),
            limitPrice=limitPrice.to_eng_string(),
            stopPrice=0,
            orderUniqueIdentifier=orderUniqueIdentifier,
            clientID=self.set_iuserID,
        )
        if self.user_logger:
            self.user_logger.info(
                f"Place Order: {response}",
                caller=f"{self.set_iuserID}.limit_order",
            )

    async def stop_limit_order(
        self,
        exchangeSegment: str,
        exchangeInstrumentID: int,
        productType: str,
        orderQuantity: int,
        limitPrice: Decimal,
        stopPrice: Decimal,
        orderUniqueIdentifier: str,
    ) -> None:
        """
        Places a stop limit order on the specified exchange segment.
        Args:
            exchangeSegment (str): The segment of the exchange where the order is to be placed. Allowed values: xts_api_client.xts_connect_async.EXCHANGE_NSECM, xts_api_client.xts_connect_async.EXCHANGE_BSECM, xts_api_client.xts_connect_async.EXCHANGE_NSEFO, xts_api_client.xts_connect_async.EXCHANGE_BSEFO, xts_api_client.xts_connect_async.EXCHANGE_NSECD, xts_api_client.xts_connect_async.EXCHANGE_MCXFO.
            exchangeInstrumentID (int): The ID of the instrument to be traded.
            productType (str): The type of product being traded. Allowed values: xts_api_client.xts_connect_async.PRODUCT_MIS, xts_api_client.xts_connect_async.PRODUCT_NRML.
            orderQuantity (int): The quantity of the order. Positive for buy, negative for sell.
            limitPrice (Decimal): The limit price for the order.
            stopPrice (Decimal): The stop price for the order.
            orderUniqueIdentifier (str): A unique identifier for the order.
        Returns:
            None
        Raises:
            AssertionError: If any of the input parameters are invalid.
        Notes:
            - The function validates the input parameters before placing the order.
            - If the order quantity is zero, the function returns immediately without placing an order.
            - The function logs the response from the order placement if a user logger is available.
        """
        assert (
            self.isConnected is True
        ), f"Interactive Engine is not connected, Rejecting order with orderID: {orderUniqueIdentifier}."
        allowed_exchange_segments = [
            XTSConnect.EXCHANGE_NSECM,
            XTSConnect.EXCHANGE_BSECM,
            XTSConnect.EXCHANGE_NSEFO,
            XTSConnect.EXCHANGE_BSEFO,
            XTSConnect.EXCHANGE_NSECD,
            XTSConnect.EXCHANGE_MCXFO,
        ]
        allowed_product_types = [
            XTSConnect.PRODUCT_MIS,
            XTSConnect.PRODUCT_NRML,
            XTSConnect.PRODUCT_CNC,
        ]
        assert (
            exchangeSegment in allowed_exchange_segments
        ), f"Invalid exchangeSegment: {exchangeSegment}"
        assert (
            productType in allowed_product_types
        ), f"Invalid productType: {productType}"
        assert isinstance(exchangeSegment, str), "exchangeSegment must be a string"
        assert isinstance(
            exchangeInstrumentID, int
        ), "exchangeInstrumentID must be an integer"
        assert isinstance(productType, str), "productType must be a string"
        assert isinstance(orderQuantity, int), "orderQuantity must be an integer"
        assert isinstance(limitPrice, Decimal), "limitPrice must be a string"
        assert isinstance(stopPrice, Decimal), "stopPrice must be a Decimal"
        assert isinstance(
            orderUniqueIdentifier, str
        ), "orderUniqueIdentifier must be a string"
        if orderQuantity == 0:
            return
        response = await self.xt.place_order(
            exchangeSegment=exchangeSegment,
            exchangeInstrumentID=exchangeInstrumentID,
            productType=productType,
            orderType=self.xt.ORDER_TYPE_STOPLIMIT,
            orderSide=(
                self.xt.TRANSACTION_TYPE_BUY
                if orderQuantity > 0
                else self.xt.TRANSACTION_TYPE_SELL
            ),
            timeInForce=self.xt.TimeinForce_DAY,
            disclosedQuantity=0,
            orderQuantity=abs(orderQuantity),
            limitPrice=limitPrice.to_eng_string(),
            stopPrice=stopPrice.to_eng_string(),
            orderUniqueIdentifier=orderUniqueIdentifier,
            clientID=self.set_iuserID,
        )
        if self.user_logger:
            self.user_logger.info(
                f"Place Order: {response}",
                caller=f"{self.set_iuserID}.stop_limit_order",
            )

    async def modify_order(
        self,
        appOrderID: int,
        modifiedProductType: str,
        modifiedOrderType: str,
        modifiedOrderQuantity: int,
        modifiedLimitPrice: Decimal,
        modifiedStopPrice: Decimal,
        orderUniqueIdentifier: str,
    ):
        response = await self.xt.modify_order(
            appOrderID=appOrderID,
            modifiedProductType=modifiedProductType,
            modifiedOrderType=modifiedOrderType,
            modifiedOrderQuantity=modifiedOrderQuantity,
            modifiedDisclosedQuantity=0,
            modifiedLimitPrice=modifiedLimitPrice.to_eng_string(),
            modifiedStopPrice=modifiedStopPrice.to_eng_string(),
            modifiedTimeInForce=self.xt.TimeinForce_DAY,
            orderUniqueIdentifier=orderUniqueIdentifier,
            clientID=self.set_iuserID,
        )
        if self.user_logger:
            self.user_logger.info(
                f"Modified Order: {response}",
                caller=f"{self.set_iuserID}.modify_order",
            )

    async def initialize(self) -> None:
        """
        Asynchronously initializes the interactive engine by performing necessary setup tasks.
        This method performs the following actions:
        1. Logs into the system.
        2. Retrieves the current balance.
        Returns:
            None
        """

        await self.login()
        await self.getBalance()

    async def initializeClient(self, response: dict) -> None:
        """
        Initializes the trading client using an explicitly supplied login response.

        This method connects the trading socket (`XTSConnect`) using the provided
        API credentials and sets common session variables such as token, user ID,
        and investor client status. It is intended to be called when the login
        response has already been obtained externally (for example, from `login()`
        or shared from another session).

        Args:
            response (dict): A dictionary containing login information with keys:
                - "token" (str): The session token for authentication.
                - "userID" (str): The user identifier.
                - "isInvestorClient" (bool): Whether the client is an investor.

        Returns:
            None

        Raises:
            KeyError: If required keys are missing from the response dictionary.
            Exception: If initialization of XTSConnect fails.

        Example:
            ```
            # Using external login response
            login_response = {
                "token": "abc123token",
                "userID": "USER001", 
                "isInvestorClient": True
            }
            await interactive_engine.initializeClient(login_response)
            ```

        Note:
            - This method sets `isConnected = True` immediately upon initialization
            - The socket connection is not established in this method
            - Use `initialize()` for complete setup including login and socket connection
            - Useful for shared sessions or when login is handled by external systems
        """
        self.xt = XTSConnect(
            self._api_key, self._api_password, self._source, self._root
        )
        self.isConnected = True
        self.xt._set_common_variables(
            response["token"], response["userID"], response["isInvestorClient"]
        )
        print("Intialized interactive client.")

    async def on_order(self, message: str) -> None:
        """
        Handles incoming order messages.
        This asynchronous method processes order messages by converting them into
        an OrderEvent object and dispatching the event to the appropriate strategy
        based on the order's unique identifier. It also logs the order event if a
        user logger is available.
        Args:
            message (str): The incoming order message in string format.
        Returns:
            None
        """

        __ = OrderEvent(message)
        if __.OrderUniqueIdentifier != "Liquidated":
            strategy_id = __.OrderUniqueIdentifier[:4]
            asyncio.ensure_future(self.strategy_to_id[strategy_id].order_(__))
        if self.user_logger:
            self.user_logger.info(
                __,
                caller=f"{self.set_iuserID}.on_order",
            )

    async def on_connect(self) -> None:
        """
        Asynchronous method that handles actions to be performed upon a successful connection.
        This method logs a message indicating that the interactive socket has connected successfully,
        provided that a user logger is available.
        Returns:
            None
        """
        self.isConnected = True
        if self.user_logger:
            self.user_logger.info(
                "Interactive socket connected successfully!",
                caller=f"{self.set_iuserID}.on_connect",
            )

    async def on_message(self, xts_message: Any) -> None:
        """
        Asynchronously handles incoming messages.
        This method is triggered when a new message is received. It parses the
        message from JSON format and logs the message if a user logger is available.
        Args:
            xts_message (Any): The incoming message in JSON format.
        Returns:
            None
        """
        if self.user_logger:
            self.user_logger.info(
                f"Received a message: {xts_message}",
                caller=f"{self.set_iuserID}.on_message",
            )

    async def on_error(self, xts_message: Any) -> None:
        """
        Handles error messages received from the XTS system.
        Args:
            xts_message (Any): The error message received from the XTS system.
        Returns:
            None
        """
        if self.user_logger:
            self.user_logger.error(
                f"Received a error: {xts_message}",
                caller=f"{self.set_iuserID}.on_error",
            )

    async def on_joined(self, data: Any) -> None:
        """
        Handles the event when the interactive socket has successfully joined.
        Args:
            data (Any): The data received upon joining the socket.
        Logs:
            Logs an informational message indicating the successful joining of the interactive socket.
        """

        if self.user_logger:
            self.user_logger.info(
                f"Interactive socket joined successfully! {data}",
                caller=f"{self.set_iuserID}.on_joined",
            )

    async def on_messagelogout(self, data: Any) -> None:
        """
        Callback for handling logout messages.
        This method is called when a logout message is received. It logs the logout
        event using the user_logger if it is available.
        Args:
            data (Any): The data associated with the logout message.
        Returns:
            None
        """
        if self.user_logger:
            self.user_logger.info(
                f"logged out! {data}", caller=f"{self.set_iuserID}.on_messagelogout"
            )

    async def reconnect(self):
        """
        Attempts to reconnect the interactive trading socket after a disconnection.

        This method recreates the OrderSocket_io connection using existing session
        credentials (token and user ID) without performing a new login. It is typically
        called automatically by the `on_disconnect()` event handler during market hours
        to restore trading connectivity.

        Process:
            1. Reinitializes the OrderSocket_io object with existing session credentials
            2. Attempts to establish the socket connection
            3. Logs the reconnection attempt status
            4. Handles any connection errors gracefully

        Raises:
            Exception: If socket initialization or connection fails. The exception
                    is logged but not re-raised to allow retry attempts.

        Returns:
            None

        Notes:
            - Uses existing session token (`self.set_interactiveToken`) and user ID
            - Does not perform a new API login, assumes existing session is valid
            - Called automatically during market hours when `isLive = True`
            - Logs both successful reconnection and any errors encountered
            - Does not update `self.isConnected` flag (handled by socket events)

        Example:
            ```
            # Automatic reconnection in on_disconnect()
            if current_time < market_close_time and self.isLive:
                await self.reconnect()
            ```
            See Also:
            - `on_disconnect()`: Main disconnection handler that calls this method
            - `login()`: Initial login and connection establishment
            - `on_connect()`: Event handler for successful connections
    """
        try:
            # Initialize and connect OrderSocket_io object
            self.socket = OrderSocket_io(
                self.set_interactiveToken,
                self.set_iuserID,
                self._root,
                self,
            )
            # Log successful login
            if self.user_logger:
                self.user_logger.info(
                    f"Login successful.", caller=f"{self.set_iuserID}.reconnect"
                )

            await self.socket.connect()

        except Exception as e:
            if self.user_logger:
                self.user_logger.error(e, caller=f"{self.set_iuserID}.reconnect")

    async def on_disconnect(self) -> None:
        """
        Callback for handling disconnection events.
        This method is called when the interactive socket gets disconnected.
        It logs an informational message indicating the disconnection event.
        Returns:
            None
        """
        self.isConnected = False
        if self.user_logger:
            self.user_logger.info(
                "Interactive Socket disconnected!",
                caller=f"{self.set_iuserID}.on_disconnect",
            )
        current_time = datetime.now().time()
        cnt: int = 0
        if current_time < datetime.strptime("15:30", "%H:%M").time():
            while not self.isConnected and self.isLive:
                print(
                    "Attempting to reconnect as the time is before 3:30 PM and isConnected is False for interactive Socket."
                )
                if self.user_logger:
                    self.user_logger.info(
                        "Attempting to reconnect as the time is before 3:30 PM and isConnected is False.",
                        caller=f"{self.set_iuserID}.on_disconnect",
                    )
                await self.reconnect()
                await asyncio.sleep(3)
                cnt += 1
                if not self.isConnected and self.user_logger:
                    print(
                        f"Reconnection attempt {cnt} failed for interactive socket. Retrying..."
                    )
                    self.user_logger.warning(
                        f"Reconnection attempt {cnt} failed. Retrying...",
                        caller=f"{self.set_iuserID}.on_disconnect",
                    )

        """
        if cnt >= 8:
            if self.user_logger:
                self.user_logger.error(
                    f"Reconnection attempts failed. Please check the network connection.",
                    caller=f"{self.set_iuserID}.on_disconnect",
                )
            print(
                "Interactive Socket reconnection failed, emergency square off triggered."
            )
            # Log the initiation of the liquidation process
            if self.user_logger:
                self.user_logger.info(
                    f"Socket Disconnected, emergency square off triggered.",
                    caller=f"{self.set_iuserID}.on_disconnect",
                )

            # Retrieve day-wise positions
            response = await self.xt.get_position_daywise("*****")

            list_of_exchangeSegment = []

            # Square off any open positions by placing market orders in the opposite direction
            for i in response["result"]["positionList"]:
                if int(i["Quantity"]) != 0 and i["ProductType"] != "CNC":
                    orderQuantity = -1 * int(i["Quantity"])
                    list_of_exchangeSegment.append(i["ExchangeSegment"])
                    asyncio.ensure_future(
                        self.xt.place_order(
                            exchangeSegment=i["ExchangeSegment"],
                            exchangeInstrumentID=int(i["ExchangeInstrumentId"]),
                            productType=i["ProductType"],
                            orderType=self.xt.ORDER_TYPE_MARKET,
                            orderSide=(
                                self.xt.TRANSACTION_TYPE_BUY
                                if orderQuantity > 0
                                else self.xt.TRANSACTION_TYPE_SELL
                            ),
                            timeInForce=self.xt.TimeinForce_DAY,
                            disclosedQuantity=0,
                            orderQuantity=abs(orderQuantity),
                            limitPrice=0,
                            stopPrice=0,
                            orderUniqueIdentifier="Liquidated",
                            clientID=self.set_iuserID,
                        )
                    ).add_done_callback(
                        lambda future: (
                            self.user_logger.info(
                                f"Place Order: {future.result()}",
                                caller=f"{self.set_iuserID}.on_disconnect",
                            )
                            if self.user_logger
                            else None
                        )
                    )

            # Cancel all open orders for the specified exchange segment
            for exchangeSegment in list_of_exchangeSegment:

                asyncio.ensure_future(
                    self.xt.cancelall_order(exchangeSegment, 0)
                ).add_done_callback(
                    lambda future: (
                        self.user_logger.info(
                            f"Cancel Order: {future.result()}",
                            caller=f"{self.set_iuserID}.Liquidate",
                        )
                        if self.user_logger
                        else None
                    )
                )
            os._exit(0)
        """

    async def on_trade(self, xts_message: str) -> None:
        """
        Handle a trade event received from the exchange.
        Args:
            xts_message (str): The trade event message in string format.
        Returns:
            None
        Logs:
            Logs the received trade event if user_logger is set.
        Actions:
            - Parses the trade event message into a TradeEvent object.
            - If the trade is not marked as "Liquidated", extracts the strategy ID
              from the OrderUniqueIdentifier and triggers the trade_ method
              of the corresponding strategy.
        """

        __ = TradeEvent(xts_message)
        if self.user_logger:
            self.user_logger.info(
                f"Received a trade: {__}", caller=f"{self.set_iuserID}.on_trade"
            )
        if __.OrderUniqueIdentifier != "Liquidated":
            strategy_id = __.OrderUniqueIdentifier[:4]
            await self.strategy_to_id[strategy_id].trade_(__)

    async def on_position(self, xts_message: str) -> None:
        """
        Handles the position event received from the XTS message.
        This method processes the position event, logs the received position if a user logger is available,
        and updates the Interactive Engine Position Diary.
        Args:
            xts_message (str): The message received containing position information.
        Returns:
            None
        """
        print(f"Position Event received with message: {xts_message}")
        try:
            __ = PositionEvent(xts_message)
            if self.user_logger:
                self.user_logger.info(
                    f"Received a position: {__}",
                    caller=f"{self.set_iuserID}.on_position",
                )
        except Exception as e:
            print(f"Error in position event {xts_message}: {e}")
        """Update Interactive Engine Position Diary."""
        # ExchangeInstrumentID = int(on_position["ExchangeInstrumentID"])
        # if ExchangeInstrumentID not in self.position_diary_engine:
        #     self.position_diary_engine[ExchangeInstrumentID] = 0
        # self.position_diary_engine[ExchangeInstrumentID] += int(
        #     on_position["NetPosition"]
        # )

    async def on_tradeconversion(self, xts_message: str) -> None:
        """
        Handles the trade conversion event received from the XTS message.
        This method processes the trade conversion event, logs the event if a user logger is available,
        and dispatches the event to the appropriate strategy based on the order's unique identifier.
        Args:
            xts_message (str): The message received containing trade conversion information.
        Returns:
            None
        """

        __ = TradeConversionEvent(xts_message)
        if self.user_logger:
            self.user_logger.info(
                f"Received a trade conversion: {__}",
                caller=f"{self.set_iuserID}.on_tradeconversion",
            )

    async def login(self) -> None:
        """
        Asynchronously logs in to the XTSConnect service and initializes the OrderSocket_io connection.
        This method performs the following steps:
        1. Initializes the XTSConnect object with the provided API credentials.
        2. Performs an interactive login to obtain the interactive token and user ID.
        3. Logs the successful login if a user logger is available.
        4. Initializes and connects the OrderSocket_io object using the obtained token and user ID.
        Raises:
            Exception: If any error occurs during the login process, it is logged and re-raised.
        Attributes:
            self.xt (XTSConnect): The XTSConnect object initialized with API credentials.
            self.set_interactiveToken (str): The token obtained from the interactive login response.
            self.set_iuserID (str): The user ID obtained from the interactive login response.
            self.socket (OrderSocket_io): The OrderSocket_io object initialized with the token and user ID.
        """

        try:
            # Initialize XTSConnect object
            self.xt = XTSConnect(
                self._api_key, self._api_password, self._source, self._root
            )

            # Perform interactive login
            response = await self.xt.interactive_login()

            self.set_interactiveToken = response["result"]["token"]
            self.set_iuserID = response["result"]["userID"]
            self.set_isInvestorClient = response["result"]["isInvestorClient"]
            # Log successful login
            if self.user_logger:
                self.user_logger.info(
                    f"Login successful.", caller=f"{self.set_iuserID}.login"
                )

            # Initialize and connect OrderSocket_io object
            self.socket = OrderSocket_io(
                self.set_interactiveToken,
                self.set_iuserID,
                self._root,
                self,
                logger=self.user_logger,
            )
            await self.socket.connect()

        except Exception as e:
            # Log and re-raise any exceptions
            if self.user_logger:
                self.user_logger.error(e, caller=f"{self.set_iuserID}.login")
            raise (e)

    async def shutdown(self) -> None:
        """
        Asynchronously shuts down the interactive engine.
        This method performs the following steps:
        1. Logs an informational message indicating the start of the shutdown process.
        2. Disconnects the socket connection.
        3. Logs out from the interactive session.
        4. Logs informational messages indicating successful logout and end of trading.
        If an exception occurs during the shutdown process, it logs the error and re-raises the exception.
        Raises:
            Exception: If an error occurs during the shutdown process.
        Returns:
            None
        """

        try:
            # Log the start of the shutdown process
            if self.user_logger:
                self.user_logger.info(
                    "Entering shut down mode.", caller=f"{self.set_iuserID}.shutdown"
                )

            # Disconnect the socket connection
            await self.socket.disconnect()

            # Log out from the interactive session
            await self.xt.interactive_logout()

            # Log successful logout and end of trading
            if self.user_logger:
                self.user_logger.info(
                    f"Logged Out.",
                    caller=f"{self.set_iuserID}.shutdown",
                )

        except Exception as e:
            # Log and re-raise any exceptions
            if self.user_logger:
                self.user_logger.error(e, caller=f"{self.set_iuserID}.shutdown")
            raise (e)

    async def getBalance(self) -> int:
        """
        Retrieves the balance for the user.
        This method is intended for retail API users only. Dealers can view their balance on the dealer terminal.
        Currently, it returns a constant value for demonstration purposes.
        Returns:
            int: The user's balance.
        """
        # self.funds = self.xt.get_balance(clientID=self.set_iuserID)
        self.funds = 1000000
        return self.funds

    async def Liquidate(self, exchangeSegment: str) -> None:
        """
        Liquidate open orders and square off positions for a given exchange segment.
        This method cancels all open orders for the specified exchange segment and
        squares off any open positions by placing market orders in the opposite direction.
        Currently "CNC" type order are not allowed in liquidate.
        Args:
            exchangeSegment (str): The segment of the exchange where the order is to be placed. Allowed values: xts_api_client.xts_connect_async.EXCHANGE_NSECM, xts_api_client.xts_connect_async.EXCHANGE_BSECM, xts_api_client.xts_connect_async.EXCHANGE_NSEFO, xts_api_client.xts_connect_async.EXCHANGE_BSEFO, xts_api_client.xts_connect_async.EXCHANGE_NSECD, xts_api_client.xts_connect_async.EXCHANGE_MCXFO.
        Returns:
            None
        Logs:
            Logs the initiation of the liquidation process, the response from the order
            cancellation, and the details of the market orders placed to square off positions.
        """
        # Define allowed exchange segments
        allowed_exchange_segments = [
            XTSConnect.EXCHANGE_NSECM,
            XTSConnect.EXCHANGE_BSECM,
            XTSConnect.EXCHANGE_NSEFO,
            XTSConnect.EXCHANGE_BSEFO,
            XTSConnect.EXCHANGE_NSECD,
            XTSConnect.EXCHANGE_MCXFO,
        ]

        # Validate the exchange segment
        assert (
            exchangeSegment in allowed_exchange_segments
        ), f"Invalid exchangeSegment: {exchangeSegment}"

        # Log the initiation of the liquidation process
        if self.user_logger:
            self.user_logger.info(
                f"Cancel open order and square off position for {exchangeSegment}",
                caller=f"{self.set_iuserID}.Liquidate",
            )

        # Cancel all open orders for the specified exchange segment
        response = await self.xt.cancelall_order(exchangeSegment, 0)

        # Log the response from the order cancellation
        if self.user_logger:
            self.user_logger.info(
                response,
                caller=f"{self.set_iuserID}.Liquidate",
            )

        # Retrieve day-wise positions
        response = await self.xt.get_position_daywise("*****")

        # Square off any open positions by placing market orders in the opposite direction
        for i in response["result"]["positionList"]:
            if int(i["Quantity"]) != 0 and i["ProductType"] != "CNC":
                asyncio.ensure_future(
                    self.market_order(
                        i["ExchangeSegment"],
                        int(i["ExchangeInstrumentId"]),
                        i["ProductType"],
                        -1 * int(i["Quantity"]),
                        "Liquidated",
                    )
                )

    async def cancel_order(self, appOrderID: Any, orderUniqueIdentifier: str) -> None:
        """
        Cancel an order with the given application order ID and unique order identifier.
        Args:
            appOrderID (Any): The application order ID to cancel.
            orderUniqueIdentifier (str): The unique identifier for the order.
        Returns:
            None
        Raises:
            AssertionError: If appOrderID or orderUniqueIdentifier is None.
        Logs:
            Logs the response of the cancel order operation if user_logger is available.
        """

        assert appOrderID is not None, "appOrderID is required"
        assert orderUniqueIdentifier is not None, "orderUniqueIdentifier is required"
        response = await self.xt.cancel_order(
            appOrderID, orderUniqueIdentifier, self.set_iuserID
        )
        if self.user_logger:
            self.user_logger.info(
                f"Cancel Order: {response}",
                caller=f"{self.set_iuserID}.cancel_order",
            )
