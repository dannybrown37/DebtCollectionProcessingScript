import pytest

from decimal import Decimal, getcontext

from main import (
    query_api_endpoints, 
    add_is_in_payment_plan_property,
    process_payments,
)


EXPECTED_DEBTS = [
    {"amount": Decimal(str(123.46)), "id": 0},
    {"amount": Decimal(str(100)),"id": 1},
    {"amount": Decimal(str(4920.34)), "id": 2},
    {"amount": Decimal(str(12938)), "id": 3},
    {"amount": Decimal(str(9238.02)), "id": 4},
]

EXPECTED_DEBTS_WITH_PAYMENT_PLAN_BOOL = [
    {'amount': Decimal(str(123.46)), 'id': 0, 'is_in_payment_plan': True}, 
    {'amount': Decimal(str(100)), 'id': 1, 'is_in_payment_plan': True}, 
    {'amount': Decimal(str(4920.34)), 'id': 2, 'is_in_payment_plan': True}, 
    {'amount': Decimal(str(12938)), 'id': 3, 'is_in_payment_plan': True}, 
    {'amount': Decimal(str(9238.02)), 'id': 4, 'is_in_payment_plan': False}
]

EXPECTED_PAYMENT_PLANS = [
    {
        "amount_to_pay": Decimal(str(102.5)),
        "debt_id": 0,
        "id": 0,
        "installment_amount": Decimal(str(51.25)),
        "installment_frequency": "WEEKLY",
        "start_date": "2020-09-28"
    },
    {
        "amount_to_pay": Decimal(str(100)),
        "debt_id": 1,
        "id": 1,
        "installment_amount": Decimal(str(25)),
        "installment_frequency": "WEEKLY",
        "start_date": "2020-08-01"
    },
    {
        "amount_to_pay": Decimal(str(4920.34)),
        "debt_id": 2,
        "id": 2,
        "installment_amount": Decimal(str(1230.085)),
        "installment_frequency": "BI_WEEKLY",
        "start_date": "2020-01-01"
    },
    {
        "amount_to_pay": Decimal(str(4312.67)),
        "debt_id": 3,
        "id": 3,
        "installment_amount": Decimal(str(1230.085)),
        "installment_frequency": "WEEKLY",
        "start_date": "2020-08-01"
    }
]

EXPECTED_PAYMENTS = [
    {
        "amount": Decimal(str(51.25)),
        "date": "2020-09-29",
        "payment_plan_id": 0
    },
    {
        "amount": Decimal(str(51.25)),
        "date": "2020-10-29",
        "payment_plan_id": 0
    },
    {
        "amount": Decimal(str(25)),
        "date": "2020-08-08",
        "payment_plan_id": 1
    },
    {
        "amount": Decimal(str(25)),
        "date": "2020-08-08",
        "payment_plan_id": 1
    },
    {
        "amount": Decimal(str(4312.67)),
        "date": "2020-08-08",
        "payment_plan_id": 2
    },
    {
        "amount": Decimal(str(1230.085)),
        "date": "2020-08-01",
        "payment_plan_id": 3
    },
    {
        "amount": Decimal(str(1230.085)),
        "date": "2020-08-08",
        "payment_plan_id": 3
    },
    {
        "amount": Decimal(str(1230.085)),
        "date": "2020-08-15",
        "payment_plan_id": 3
    }
]

def test_query_api_endpoints():
    debts, payment_plans, payments = query_api_endpoints()
    assert debts == EXPECTED_DEBTS
    assert payment_plans == EXPECTED_PAYMENT_PLANS
    assert payments == EXPECTED_PAYMENTS


def test_add_is_in_payment_plan_property():
    debts = add_is_in_payment_plan_property(EXPECTED_DEBTS, EXPECTED_PAYMENT_PLANS)
    assert debts == EXPECTED_DEBTS_WITH_PAYMENT_PLAN_BOOL


def test_process_payments():
    debts, payment_plans = process_payments(
        debts=EXPECTED_DEBTS_WITH_PAYMENT_PLAN_BOOL,
        payment_plans=EXPECTED_PAYMENT_PLANS,
        payments=EXPECTED_PAYMENTS,
    )

    assert debts == [
        {
            'amount': Decimal('123.46'),                                        
            'id': 0,                                                            
            'is_in_payment_plan': False,                                        
            'remaining_amount': Decimal('0.00')
        },                               
        {
            'amount': Decimal('100'),                                           
            'id': 1,                                                            
            'is_in_payment_plan': True,                                         
            'remaining_amount': Decimal('50')
        },                                 
        {
            'amount': Decimal('4920.34'),                                       
            'id': 2,                                                            
            'is_in_payment_plan': True,                                         
            'remaining_amount': Decimal('607.67')
        },                             
        {
            'amount': Decimal('12938'),                                         
            'id': 3,                                                            
            'is_in_payment_plan': True,                                         
            'remaining_amount': Decimal('622.415')
        },                            
        {'amount': Decimal('9238.02'), 'id': 4, 'is_in_payment_plan': False}
    ]

    assert payment_plans == [
        {
            'amount_to_pay': Decimal('0.00'),
            'debt_id': 0,
            'id': 0,
            'installment_amount': Decimal('51.25'),
            'installment_frequency': 'WEEKLY',
            'start_date': '2020-09-28'
        },
        {
            'amount_to_pay': Decimal('50'),
            'debt_id': 1,
            'id': 1,
            'installment_amount': Decimal('25'),
            'installment_frequency': 'WEEKLY',
            'start_date': '2020-08-01'
        },
        {
            'amount_to_pay': Decimal('607.67'),
            'debt_id': 2,
            'id': 2,
            'installment_amount': Decimal('1230.085'),
            'installment_frequency': 'BI_WEEKLY',
            'start_date': '2020-01-01'
        },
        {
            'amount_to_pay': Decimal('622.415'),
            'debt_id': 3,
            'id': 3,
            'installment_amount': Decimal('1230.085'),
            'installment_frequency': 'WEEKLY',
            'start_date': '2020-08-01'
        }
    ]