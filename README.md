Requirements:

- works best with python 3
- it is made specifically for windows
- please run the INSTALLER.bat (only works with pip)

Description:

The app uses Warframe's trade website API to analyze the market for certain items in a list. What this does is to simply get the data for each listing for each item, calculate different types of 
price margins and compute the best average price for the item. It then compares that average to the cheapest seller currently to calculate the overall profit. 

The system behind it keeps into account all the different server regions listings, calculates raw average, normalized average (which is ignoring the listings of sellers that have not logged in 
for a while, since the market moved prices, these become irrelevant) and finally the optimal average (which is ignoring prices that are too far away from the normalized average).

The game uses "Platinum" as its currency.

Configuration with a big list of instruments:

![image](https://github.com/AlexandruTentes/WarframeTradeBot/assets/35760618/57eee438-bd59-4da4-8112-9a3dd8c1e470)

The UI with the instruments active that hit the mark of 20 platinum profit

![image](https://github.com/AlexandruTentes/WarframeTradeBot/assets/35760618/1543dcbc-f343-4d8e-8e41-314e2b152a4b)

A screenshot of the windows notification received when "ash_prime_set" instrument hit a potential profit margin of 25.12 platinum (it also plays the windows notification nosund)

![image](https://github.com/AlexandruTentes/WarframeTradeBot/assets/35760618/4799f743-5e2f-43ee-8cb6-c0df653027cf)

Breakdown of one instrument box:

![image](https://github.com/AlexandruTentes/WarframeTradeBot/assets/35760618/b1627079-b430-435f-a263-b6685cba0f20)

From the top left: primed_bane_of_corrupted instrument top seller registered this item at a 10.48% lower than the Estimate price. Raw potential profit of 24.58 platinum.
Average price is the raw average of all listings in the order book.
Ideal price is the normalized average (removes the old listings, since market prices move constantly, older than 1-3 days items have lower impact, get ignored)
Estimate price is the final calculation, it is the optimal average, since it removes the listings that are too far outside of the ideal price.

You can pin the box so it always stays visible (if an instrument does not meet the set min profit amount (now set at 20 for this example) then that box never shows up. 
If you pin it it will stay up all the time.

Notify is for windows notification.
mod_ (the full name is not visible since it does not fit) but that is the mod_rank, used for certain types of items/instruments
Clipboard will save to the clipboard the message to be sent in game to the seller in order to buy the item.
The Rank is true if the instrument is supposed to have a rank.
(the rank is used for mods, if you want a certain mod level you can mark Rank and then set 10 for mod_) where 10 is max rank

It shows you the region the cheapest seller is selling from, the platform, how many items (quantity/size) and the price.
In this example the Estimate price is 234.58 plat and the seller sells at 210.00 plat, hence the 24.58 plat profit.

Sale min and Sale max is mostly indicative to market direction for the instrument.. it only registeres it while the app is running
Roughly 10 minutes later I got this picture featuring the same instrument described above:

![image](https://github.com/AlexandruTentes/WarframeTradeBot/assets/35760618/8e043c78-9abf-4705-8ec3-c9a9f30a7695)

sale min is still at 10.48 (as it was initially)
sale max is now at 19.86 - This indicates that the previous order of 210 plat was crossed and now someone is selling way cheaper than that (188 plat) This shows a fall in market and a potential raise in profit if buying now.

Note, sale min and max are all in procentile.

Finally Rank shows that instrument's top seller item rank (if you set to look for a mod and you ser Rank boolean mentioned earlier, the rank of the mod being sold will show up, check the following picture)

![image](https://github.com/AlexandruTentes/WarframeTradeBot/assets/35760618/6c248db7-188e-48fe-a227-db66334c762b)


Finally the Status shows if the top seller is ingame or just online on the website

![image](https://github.com/AlexandruTentes/WarframeTradeBot/assets/35760618/3bf4fbe3-0276-4c54-95b6-ad7114bd1c6f)

