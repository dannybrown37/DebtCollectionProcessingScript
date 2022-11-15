# Project Summary

This is a quick-and-dirty script to retrieve and process sample API data 
relating to hypotetical debts, payment plans, and payments against same.
It was written as a code sample in about two hours. 


## Instructions: Environment Setup and Running the Program

0. Prerequisite is Python/pip 3.7+ (this sample project was developed with 3.11).

1. Create a virtual environment and activate it:
```
python -m venv .venv    
source .venv/bin/activate  # Windows: .venv/scripts/activate    
```

2. Install requirements:
```
pip install -r requirements.txt 
```

3. Run tests:
```
pytest
```

4. Run script:
```
python main.py
```


## How I Spent My Time On This

The bulk of my effort on this project was spent in trying to find the 
best way to coerce the float data points to Decimals, something I 
accomplished but that I would have liked to do more elegantly. Decimals 
were useful in this case for precision given that we are dealing with 
monetary cacluations.

Otherwise this was a pretty straightforward task where data was pulled
from an API, foreign keys were used to relate entities with others,
and calculations were made based on the data pulled/related.


## Process, Aproach, Next Steps

I took a very iterative approach, writing a function at a time to take 
some items and return transformed items. I also took a test-driven 
development approach and wrote tests concurrently with each function.

First I wrote `query_api_endpoints()` which collects the data from the API
and coerces it into the correct data types. This is also the step where 
I defined the TypedDicts that I used for type hints.

Next I wrote `add_is_in_payment_plan_property()`, which processes all the
payment plans and adds a bool to each debt record indicating whether there
is a payment plan active. 

Finally I wrote `process_payments()` which processes each of the payment
records in the API against the payment plan and/or debt as required. 

To wrap it up I wrote `write_output_with_jsonlines()` which uses the 
`jsonlines` library, which was requested. I haven't encountered this 
library before and am sure I must be missing some of its perks, as my 
usage here is pretty rudimentary and probably not any different than 
just using `json` itself. 

With more time, I would have:

1) Looked into `jsonlines` more
2) Added more test sets of payment data for a more diverse set of 
   scenarios. For example, the API didn't include any payments against
   debts that did not have a payment plan in place.
3) Handle edge cases that did not exist in the test data provided but
   that could theoretically exist, such as described in point 2 above. 
4) Further build this out into a module with `pip` installation, et al.


## For Those Reviewing This Code

The entry point for the script is the `main()` function toward the 
bottom of `main.py`. The script takes a functional approach and uses 
type hinting and doc strings to attempt to make what it is doing very 
clear. Each function performs one task and has reliable output. The 
`test_functions.py` file (called with a simple `pytest` from the project
root), has more examples of each function in use and also includes all 
of the relevant test data for the repo.


## Design Decisions and Assumptions

I took a very straightforward, TDD approach with a functional design pattern
for this script. The functional design is just based on my current preference 
but easily could have been done with OOP as well. 

I assumed that edge cases that didn't come up in the test data did not 
need to all be handled (some still were). 