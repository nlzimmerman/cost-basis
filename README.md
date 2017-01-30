# Cost basis tracking

Some code to track the cost basis of your investments, both for tax purposes and to give you a clear picture of where you stand. Right now, there's no documentation, no demo, and the only way to interact with it is by writing code that interacts with the classes.

# Motivation

Doing this in a LibreOffice spreadsheet (my current method) is silly. It's far better, in my opinion, to write code that figures everything out from a set of declared facts.

# Accounting methods currently supported:

- [Average cost method](https://investor.vanguard.com/taxes/cost-basis/average-cost)
- [SpecID](https://investor.vanguard.com/taxes/cost-basis/specific-identification)

# Accounting methods currently unsupported

- [FIFO](https://investor.vanguard.com/taxes/cost-basis/first-in-first-out)
- [Highest In, First Out](https://www.gainskeeper.com/us/HIFO.aspx) (There seem to be a lot of different acronyms for that!)
- LIFO

Of course, all of these are really special cases of SpecID.

Todo:

- Implement other cost-basis methods. IN PROGRESS.
- Read/Write CSVs.
- Visualize unrealized gains and losses over time.
- Useful examples.
