import json
import sys
from decimal import Decimal
from typing import TypedDict, Union

import jsonlines
import requests

ROOT = 'https://my-json-server.typicode.com/druska/trueaccord-mock-payments-api'
DEBTS_ENDPOINT = ROOT + '/debts'
PAYMENT_PLANS_ENDPOINT = ROOT + '/payment_plans'
PAYMENTS_ENDPOINT = ROOT + '/payments'


# Define data types for clearer type hinting

class Debt(TypedDict):
    amount: Decimal
    id: int


class DebtWithPaymentPlan(TypedDict):
    amount: Decimal
    id: int
    is_in_payment_plan: bool


class DebtWithRemainingAmount(TypedDict):
    amount: Decimal
    id: int
    is_in_payment_plan: bool
    remaining_amount: Decimal


class PaymentPlan(TypedDict):
    amount_to_pay: Decimal
    debt_id: int
    id: int
    installment_amount: Decimal
    installment_frequency: str
    start_date: str


class Payment(TypedDict):
    amount: Decimal
    date: str
    payment_plan_id: int


class DecimalEncoder(json.JSONEncoder):
    """Utility function to convert Decimal -> str -> float for JSON"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(str(obj))
        return json.JSONEncoder.default(self, obj)


# Define functions that carry out task at hand

def query_api_endpoints() -> tuple[list[Union[Debt, PaymentPlan, Payment]]]:
    """Queries raw data from API endpoints and puts it in TypedDicts
    
        for monetary precision convert all amounts to str and then Decimal
    """
    debts = [Debt(**d) for d in requests.get(DEBTS_ENDPOINT).json()]
    for debt in debts:
        debt['amount'] = Decimal(str(debt['amount']))
    payment_plans = [
        PaymentPlan(**p) for p in requests.get(PAYMENT_PLANS_ENDPOINT).json()
    ]
    for plan in payment_plans:
        plan['amount_to_pay'] = Decimal(str(plan['amount_to_pay']))
        plan['installment_amount'] = Decimal(str(plan['installment_amount']))
    payments = [Payment(**p) for p in requests.get(PAYMENTS_ENDPOINT).json()]
    for payment in payments:
        payment['amount'] = Decimal(str(payment['amount']))
    return debts, payment_plans, payments


def add_is_in_payment_plan_property(
        debts: list[Debt],
        payment_plans: list[Debt],
    ) -> list[DebtWithPaymentPlan]:
    """Adds is_in_payment_plan to each debt in debts"""
    for payment_plan in payment_plans:
        # instructions say not to mark True if payment plan is finished
        if payment_plan['amount_to_pay'] <= 0:
            continue
        debts[payment_plan['debt_id']]['is_in_payment_plan'] = True
    for debt in debts:
        if 'is_in_payment_plan' not in debt:
            debt['is_in_payment_plan'] = False
    return debts


def process_payments(
        debts: list[DebtWithPaymentPlan], 
        payment_plans: list[PaymentPlan],
        payments: list[Payment],
    ) -> tuple[list[DebtWithRemainingAmount], list[PaymentPlan]]:
    """Process each payment in payments against debt or payment plan.
    
        Adds the remaining_amount to debts that received payments and 
        did not already have this value.
    """
    for payment in payments:
        plan_index, plan = next(
            (i, p) for i, p in enumerate(payment_plans) 
            if p['id'] == payment['payment_plan_id']
        )
        # when payment plan is completed, clear the debt as well
        new_amount = plan['amount_to_pay'] - payment['amount']
        payment_plans[plan_index]['amount_to_pay'] = new_amount
        debt_index, debt = next(
            (i, d) for i, d in enumerate(debts) 
            if d['id'] == plan['debt_id']
        )
        debt['remaining_amount'] = new_amount
        if new_amount <= 0:
            debt['is_in_payment_plan'] = False
        debts[debt_index] = DebtWithRemainingAmount(**debt)
    return debts, payment_plans


def write_output_with_jsonlines(
        message: str, 
        debts: list[Union[Debt, DebtWithPaymentPlan, DebtWithRemainingAmount]],
    ) -> None:
    print('\n' + message)
    fp = sys.stdout  # file-like object
    with jsonlines.Writer(fp) as writer:
        for debt in debts:
            writer.write(json.dump(debt, fp, cls=DecimalEncoder))

            
def main():
    debts, payment_plans, payments = query_api_endpoints()
    write_output_with_jsonlines('Initial debts:', debts)
    debts = add_is_in_payment_plan_property(debts, payment_plans)
    write_output_with_jsonlines('Debts after finding payment plans:', debts)
    debts, payment_plans = process_payments(debts, payment_plans, payments)
    write_output_with_jsonlines('Debts after processing payments:', debts)


if __name__ == "__main__":
    main()