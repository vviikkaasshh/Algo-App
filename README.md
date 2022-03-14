Algo-App:

Zerodha Client for Order management and Sample Algo strategies.

What It has:
1. Trade Management.
2. Sample Algo Strategies, can derive from base strategy and implement your own implentation.
3. Technical Indicator (RSI, SMI, EMA and many more)
4. Telegram Logger support (Update your chat_id, token in telegram logger)

Steps to install configuration:
1. Download dependencies from requirement.txt.
2. Run it on local server on http://127.0.0.1:5000.
3. Update ClientId, appkey and AppSecret in src/brokerapp.json.

Steps to run:
1. If using VS code, press F5, it will start Flask development server.
2. Login to Zerodha and Start the Algo execution.
3. If not using VS code, set flask environment path and execute as a module.

Future Scope:
1. Support for other Brokers (eg: Upstox, IIFL etc.)
2. Order support for greater than presecribed limit of NSE.
3. Frontend in React for order status check and Order manager.
