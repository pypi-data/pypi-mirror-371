OrderBook API
=============

Advanced Level 2 orderbook management and market microstructure analysis.

Overview
--------

The OrderBook class provides institutional-grade orderbook analytics for real-time market depth analysis. It includes advanced features like iceberg order detection with price level history tracking, market imbalance analysis, volume profiling, and dynamic support/resistance identification based on temporal patterns.

**New in v1.1.4**: Enhanced analytics using price level refresh history for detecting persistent levels, iceberg orders, and market maker activity zones.

.. currentmodule:: project_x_py

.. automodule:: project_x_py.orderbook
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Quick Start
-----------

.. code-block:: python

   import asyncio
   from project_x_py import ProjectX, create_orderbook, create_realtime_client
   
   async def analyze_orderbook():
       # Create client and orderbook with dynamic tick size detection
       async with ProjectX.from_env() as client:
           await client.authenticate()
           
           # Get instrument and create orderbook
           instrument = await client.get_instrument("MGC")
           realtime_client = create_realtime_client(client.session_token)
           orderbook = create_orderbook(instrument, client, realtime_client)
       
           # Get real-time market depth (requires real-time data subscription)
           snapshot = await orderbook.get_orderbook_snapshot(levels=10)
           print(f"Best Bid: ${snapshot['metadata']['best_bid']:.2f}")
           print(f"Best Ask: ${snapshot['metadata']['best_ask']:.2f}")
           print(f"Spread: ${snapshot['metadata']['spread']:.2f}")
       
           # Advanced market microstructure analysis
           metrics = await orderbook.get_advanced_market_metrics()
           print(f"Market Imbalance: {metrics['market_imbalance']['direction']}")
   
   asyncio.run(analyze_orderbook())

Core OrderBook Class
-------------------

.. autoclass:: OrderBook
   :members:
   :undoc-members:
   :show-inheritance:

Core Methods
------------

Market Depth Management
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: OrderBook.process_market_depth
.. automethod:: OrderBook.get_orderbook_snapshot
.. automethod:: OrderBook.get_orderbook_bids
.. automethod:: OrderBook.get_orderbook_asks
.. automethod:: OrderBook.get_best_bid_ask

Basic Analysis
~~~~~~~~~~~~~~

.. automethod:: OrderBook.get_orderbook_depth
.. automethod:: OrderBook.get_order_type_statistics
.. automethod:: OrderBook.get_statistics

Advanced Market Microstructure
------------------------------

Liquidity Analysis
~~~~~~~~~~~~~~~~~~

.. automethod:: OrderBook.get_liquidity_levels
.. automethod:: OrderBook.detect_order_clusters
.. automethod:: OrderBook.get_market_imbalance

Trade Flow Analysis
~~~~~~~~~~~~~~~~~~~

.. automethod:: OrderBook.get_trade_flow_summary
.. automethod:: OrderBook.get_cumulative_delta
.. automethod:: OrderBook.get_volume_profile

Institutional Features
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: OrderBook.detect_iceberg_orders
.. automethod:: OrderBook.detect_iceberg_orders_advanced
.. automethod:: OrderBook.get_support_resistance_levels

Comprehensive Analysis
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: OrderBook.get_advanced_market_metrics

Event Management
----------------

.. automethod:: OrderBook.add_callback
.. automethod:: OrderBook.remove_callback

Usage Examples
--------------

Basic OrderBook Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from project_x_py import OrderBook, ProjectX, create_realtime_client
   
   async def basic_orderbook_analysis():
       async with ProjectX.from_env() as client:
           await client.authenticate()
           
           # Get instrument details
           instrument = await client.get_instrument("MGC")
           
           # Initialize orderbook for Gold futures
           orderbook = OrderBook(instrument, timezone="America/Chicago")
           
           # Connect to real-time data for live orderbook
           realtime_client = create_realtime_client(client.session_token)
           await realtime_client.connect()
           
           # Subscribe to market depth
           await realtime_client.subscribe_market_depth(instrument.id)
           
           # Wait a moment for data to populate
           await asyncio.sleep(2)
           
           # Get current market depth
           snapshot = await orderbook.get_orderbook_snapshot(levels=5)
           
           print("=== Market Depth ===")
           print(f"Best Bid: ${snapshot['metadata']['best_bid']:.2f}")
           print(f"Best Ask: ${snapshot['metadata']['best_ask']:.2f}")
           print(f"Spread: ${snapshot['metadata']['spread']:.2f}")
           print(f"Mid Price: ${snapshot['metadata']['mid_price']:.2f}")
           
           print("\n=== Top 5 Bids ===")
           for bid in snapshot['bids'].to_dicts():
               print(f"${bid['price']:.2f} x {bid['volume']}")
           
           print("\n=== Top 5 Asks ===")
           for ask in snapshot['asks'].to_dicts():
               print(f"${ask['price']:.2f} x {ask['volume']}")
   
   asyncio.run(basic_orderbook_analysis())

Advanced Market Analysis
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def advanced_analysis():
       # Assumes orderbook is already initialized and connected
       # Comprehensive market microstructure analysis
       metrics = await orderbook.get_advanced_market_metrics()
       
       # Market imbalance analysis
       imbalance = metrics['market_imbalance']
       print(f"Market Direction: {imbalance['direction']}")
       print(f"Imbalance Ratio: {imbalance['imbalance_ratio']:.3f}")
       print(f"Confidence: {imbalance['confidence']}")
       
       # Liquidity analysis
       liquidity = metrics['liquidity_analysis']
       print(f"\nSignificant Bid Levels: {len(liquidity['bid_liquidity'])}")
       print(f"Significant Ask Levels: {len(liquidity['ask_liquidity'])}")
       
       # Volume profile
       volume_profile = metrics['volume_profile']
       if volume_profile['poc']:
           print(f"\nPoint of Control: ${volume_profile['poc']['price']:.2f}")
           print(f"POC Volume: {volume_profile['poc']['volume']}")

Iceberg Order Detection
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def detect_icebergs():
       # Advanced iceberg detection with statistical analysis
       icebergs = await orderbook.detect_iceberg_orders_advanced(
           time_window_minutes=30,
           min_refresh_count=5,
           volume_consistency_threshold=0.85,
           statistical_confidence=0.95
       )
       
       print("=== Iceberg Detection Results ===")
       print(f"Potential Icebergs Found: {len(icebergs.get('potential_icebergs', []))}")
       
       for iceberg in icebergs.get('potential_icebergs', []):
           print(f"\nPrice: ${iceberg['price']:.2f}")
           print(f"Confidence: {iceberg['confidence']:.2%}")
           print(f"Total Volume: {iceberg['total_volume_seen']}")
           print(f"Refresh Count: {iceberg['refresh_count']}")
           print(f"Statistical Score: {iceberg['statistical_score']:.3f}")

Support and Resistance Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def analyze_support_resistance():
       # Dynamic support and resistance identification
       levels = await orderbook.get_support_resistance_levels(lookback_minutes=60)
       
       print("=== Support Levels ===")
       for level in levels['support_levels'][:3]:  # Top 3 support levels
           print(f"${level['price']:.2f} - Strength: {level['strength']:.2f} - Volume: {level['volume']}")
       
       print("\n=== Resistance Levels ===")
       for level in levels['resistance_levels'][:3]:  # Top 3 resistance levels
           print(f"${level['price']:.2f} - Strength: {level['strength']:.2f} - Volume: {level['volume']}")

Real-time Integration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from project_x_py import ProjectX, create_realtime_client, OrderBook
   
   async def setup_realtime_orderbook():
       async with ProjectX.from_env() as client:
           await client.authenticate()
           
           # Get instrument
           instrument = await client.get_instrument("MGC")
           
           # Set up real-time data with orderbook callbacks
           rt_client = create_realtime_client(client.session_token)
           orderbook = OrderBook(instrument)
           
           async def on_market_depth_update(data):
               """Handle real-time market depth updates"""
               await orderbook.process_market_depth(data)
               
               # Get updated metrics
               snapshot = await orderbook.get_orderbook_snapshot(levels=5)
               best_bid = snapshot['metadata']['best_bid']
               best_ask = snapshot['metadata']['best_ask']
               
               print(f"Updated: ${best_bid:.2f} x ${best_ask:.2f}")
           
           # Register callback for market depth updates
           orderbook.add_callback('market_depth', on_market_depth_update)
           
           # Connect and subscribe to real-time market data
           await rt_client.connect()
           await rt_client.subscribe_market_depth(instrument.id)
           
           # Keep running for 60 seconds
           await asyncio.sleep(60)
   
   asyncio.run(setup_realtime_orderbook())

Market Imbalance Strategy
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   
   async def monitor_market_imbalance(orderbook):
       """Monitor market for trading opportunities based on imbalance"""
       
       while True:
           # Get current market metrics
           imbalance = await orderbook.get_market_imbalance()
           
           # Check for significant imbalance
           if abs(imbalance['imbalance_ratio']) > 0.3:  # 30% imbalance threshold
               direction = imbalance['direction']
               confidence = imbalance['confidence']
               
               print(f"SIGNAL: {direction.upper()} imbalance detected")
               print(f"Ratio: {imbalance['imbalance_ratio']:.3f}")
               print(f"Confidence: {confidence}")
               
               # Additional confirmation from volume profile
               volume_metrics = await orderbook.get_volume_profile()
               if volume_metrics['poc']:
                   bid_ask = await orderbook.get_best_bid_ask()
                   current_price = bid_ask['mid']
                   poc_price = volume_metrics['poc']['price']
                   
                   if direction == 'bullish' and current_price > poc_price:
                       print("✅ Volume profile confirms bullish signal")
                   elif direction == 'bearish' and current_price < poc_price:
                       print("✅ Volume profile confirms bearish signal")
           
           await asyncio.sleep(1)  # Check every second
   
   # Run monitoring as part of main async flow
   # await monitor_market_imbalance(orderbook)

Data Structures
---------------

OrderBook Snapshot
~~~~~~~~~~~~~~~~~~

The ``get_orderbook_snapshot()`` method returns:

.. code-block:: python

   {
       "bids": pl.DataFrame,           # Bid levels with price, volume, timestamp
       "asks": pl.DataFrame,           # Ask levels with price, volume, timestamp  
       "metadata": {
           "best_bid": float,          # Highest bid price
           "best_ask": float,          # Lowest ask price
           "spread": float,            # Bid-ask spread
           "mid_price": float,         # Mid-market price
           "total_bid_volume": int,    # Total volume on bid side
           "total_ask_volume": int,    # Total volume on ask side
           "last_update": datetime,    # Last update timestamp
           "levels_count": {           # Number of price levels
               "bids": int,
               "asks": int
           }
       }
   }

Market Imbalance Data
~~~~~~~~~~~~~~~~~~~

The ``get_market_imbalance()`` method returns:

.. code-block:: python

   {
       "imbalance_ratio": float,       # -1 to 1 (negative = bearish, positive = bullish)
       "direction": str,               # "bullish", "bearish", or "neutral"
       "confidence": str,              # "low", "medium", "high"
       "bid_pressure": float,          # Normalized bid pressure
       "ask_pressure": float,          # Normalized ask pressure
       "trade_flow_confirmation": float # Trade flow alignment
   }

Iceberg Detection Result
~~~~~~~~~~~~~~~~~~~~~~

The ``detect_iceberg_orders_advanced()`` method returns:

.. code-block:: python

   {
       "potential_icebergs": [
           {
               "price": float,                    # Price level
               "confidence": float,               # Detection confidence (0-1)
               "total_volume_seen": int,          # Total volume observed
               "refresh_count": int,              # Number of refreshes
               "avg_visible_size": float,         # Average visible size
               "volume_consistency": float,       # Volume consistency score
               "statistical_score": float,       # Statistical significance
               "side": str                        # "bid" or "ask"
           }
       ],
       "analysis_summary": {
           "total_suspicious_levels": int,
           "confidence_threshold": float,
           "time_window_analyzed": int
       }
   }

Volume Profile Data
~~~~~~~~~~~~~~~~~

The ``get_volume_profile()`` method returns:

.. code-block:: python

   {
       "profile": [
           {
               "avg_price": float,        # Average price for bucket
               "total_volume": int,       # Total volume traded
               "buy_volume": int,         # Buy-side volume
               "sell_volume": int,        # Sell-side volume
               "trade_count": int         # Number of trades
           }
       ],
       "poc": {                          # Point of Control (highest volume)
           "price": float,
           "volume": int
       },
       "value_area": {                   # 70% of volume area
           "upper": float,
           "lower": float,
           "volume_percentage": float
       }
   }

Performance Considerations
-------------------------

Memory Management
~~~~~~~~~~~~~~~~

The OrderBook automatically manages memory by:

- Limiting orderbook levels to top 100 per side
- Maintaining rolling windows for trade data
- Automatic cleanup of old data beyond time windows

.. code-block:: python

   # Configure memory settings
   orderbook = OrderBook(
       "MGC", 
       timezone="America/Chicago"
   )
   
   # The orderbook automatically:
   # - Keeps top 100 levels per side
   # - Maintains trade history for analysis windows
   # - Cleans up data older than analysis periods

Async Concurrency
~~~~~~~~~~~~~~~~

The OrderBook supports concurrent async access:

.. code-block:: python

   import asyncio
   
   async def worker_task(orderbook, task_id):
       # Safe to call concurrently
       snapshot = await orderbook.get_orderbook_snapshot()
       metrics = await orderbook.get_advanced_market_metrics()
       print(f"Task {task_id} completed")
   
   # Multiple async tasks can access orderbook concurrently
   async def run_concurrent_tasks(orderbook):
       tasks = [worker_task(orderbook, i) for i in range(5)]
       await asyncio.gather(*tasks)

Optimization Tips
~~~~~~~~~~~~~~~~

1. **Batch Analysis**: Use ``get_advanced_market_metrics()`` for comprehensive analysis in one call
2. **Selective Levels**: Request only needed levels (e.g., ``levels=5`` instead of default 10)
3. **Time Windows**: Adjust analysis time windows based on trading timeframe
4. **Callback Efficiency**: Keep callback functions lightweight for real-time performance

.. code-block:: python

   # Efficient: Get all metrics at once
   metrics = await orderbook.get_advanced_market_metrics()
   
   # Less efficient: Multiple separate calls
   imbalance = await orderbook.get_market_imbalance()
   liquidity = await orderbook.get_liquidity_levels()
   profile = await orderbook.get_volume_profile()

Error Handling
--------------

.. code-block:: python

   async def safe_orderbook_analysis():
       try:
           # OrderBook operations
           snapshot = await orderbook.get_orderbook_snapshot()
           
           if not snapshot['metadata']['best_bid']:
               print("No bid data available")
               return
               
           # Advanced analysis
           icebergs = await orderbook.detect_iceberg_orders_advanced()
           
       except Exception as e:
           print(f"OrderBook error: {e}")
           # Handle gracefully - orderbook returns empty/default data on errors

Integration with Trading
-----------------------

.. code-block:: python

   from project_x_py import ProjectX, create_order_manager, create_realtime_client
   
   async def smart_limit_order():
       """Place limit order using orderbook analysis"""
       
       async with ProjectX.from_env() as client:
           await client.authenticate()
           
           # Get instrument and create components
           instrument = await client.get_instrument("MGC")
           realtime_client = create_realtime_client(client.session_token)
           order_manager = create_order_manager(client, realtime_client)
           orderbook = OrderBook(instrument)
           
           # Connect and get market data
           await realtime_client.connect()
           await realtime_client.subscribe_market_depth(instrument.id)
           await asyncio.sleep(2)  # Wait for data
           
           # Analyze current market structure
           snapshot = await orderbook.get_orderbook_snapshot(levels=10)
           imbalance = await orderbook.get_market_imbalance()
           liquidity = await orderbook.get_liquidity_levels()
           
           best_bid = snapshot['metadata']['best_bid']
           best_ask = snapshot['metadata']['best_ask']
           
           # Determine optimal order placement
           if imbalance['direction'] == 'bullish':
               # Place buy order closer to mid for better fill probability
               target_price = best_bid + (snapshot['metadata']['spread'] * 0.3)
               side = 0  # Buy
           else:
               # Place sell order closer to mid
               target_price = best_ask - (snapshot['metadata']['spread'] * 0.3)
               side = 1  # Sell
           
           # Check for significant liquidity levels
           liquidity_side = 'bid_liquidity' if side == 0 else 'ask_liquidity'
           for level in liquidity[liquidity_side].to_dicts():
               if abs(level['price'] - target_price) < 0.5:  # Within 0.5 of liquidity
                   target_price = level['price']  # Join the liquidity
                   break
           
           # Place the order
           response = await order_manager.place_limit_order(
               contract_id=instrument.id,
               side=side,
               size=1,
               limit_price=target_price
           )
           
           print(f"Order placed at ${target_price:.2f} based on orderbook analysis")
           return response
   
   # Run the smart order placement
   asyncio.run(smart_limit_order())

Best Practices
--------------

1. **Real-time Data**: OrderBook requires real-time market depth data for accurate analysis
2. **Time Windows**: Adjust analysis time windows based on market volatility and trading timeframe  
3. **Statistical Confidence**: Use higher confidence thresholds for iceberg detection in volatile markets
4. **Market Hours**: Results are most reliable during active trading hours
5. **Instrument-Specific**: Different instruments may require parameter tuning for optimal detection

.. code-block:: python

   # Example: Configure for different market conditions
   
   async def configure_for_market_conditions():
       async with ProjectX.from_env() as client:
           await client.authenticate()
           
           # High-frequency scalping (short windows)
           mnq = await client.get_instrument("MNQ")
           scalping_orderbook = OrderBook(mnq)
           icebergs = await scalping_orderbook.detect_iceberg_orders_advanced(
               time_window_minutes=5,      # Short window
               min_refresh_count=3,        # Lower threshold
               statistical_confidence=0.90 # Slightly lower confidence
           )
           
           # Position trading (longer windows)  
           mgc = await client.get_instrument("MGC")
           position_orderbook = OrderBook(mgc)
           icebergs = await position_orderbook.detect_iceberg_orders_advanced(
               time_window_minutes=120,    # Longer window
               min_refresh_count=10,       # Higher threshold
               statistical_confidence=0.95 # Higher confidence
           ) 