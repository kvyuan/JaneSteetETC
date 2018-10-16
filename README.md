# JaneSteetETC
Trading algorithms and summary of Jane Street Electronic Trading Challenge 

## Our Team ## 
Yuanzhe Liu: CS undergrad, rich experience in software development, VPN business
owner

Hao Yuan: Industrial Engineering and CS undergrad, trading algorithms developer 
on Quantopian, 2 year stock and option trading experience

## What Our Team Did ##

* Coded everything in python

* Concurrent development: Yuanzhe focuses on TCP connection, Hao focuses on 
  strategies

## Our Strategies ##

**common stock & ADR pairing:** Since common stock is more liquid than its pairing
ADR, we use common stock to estimate its ADR's fair value. When ADR is 
undervalued, we buy ADR, pay a fee to convert to common stock, and sell in 
strength 

**ETF Arbitrage:** We use the holdings of the ETF to estimates its fair value.
When ETF is undervalued, we buy ETF, pay a fee to convert to common stocks of 
the holdings, and sell in strength. When ETF is over valued, we buy common 
stocks of the holdings, pay a fee to convert to ETF, and sell in strength. 

## What Did Our Team Do Well? ##

* chose a progamming language that was easy to use

* Divided the roles, stayed focused, and helped each other 

* Started from simple strategies to complex ones

* Top 4 of the competition

## What We Should Have Done Better? ## 

* Set up TCP earlier, our first test began 3 hours after the pool opened 

* Track pending orders and cancel the ones we don't need

* Less aggressive algorithms (We were top 2 for 2 rounds and bottom 5 for a few)

* Implement hedging strategies for risk protection


