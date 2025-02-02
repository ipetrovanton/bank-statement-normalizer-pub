import datetime
from typing import Optional

from pydantic import BaseModel


class TransactionData(BaseModel):
    file_link: str
    debtor_account_number: str
    currency_code: str
    debtor_bank_name: str
    document_type_code: str
    document_number: str
    document_operation_date: datetime.date  # Здесь можно использовать datetime.date
    payer_or_recipient_name: str
    payer_or_recipient_inn: str
    payer_or_recipient_kpp: str
    account_number: str
    debit_amount: Optional[float]
    credit_amount: Optional[float]
    payment_purpose: str
    correspondent_account_number: str
    payer_or_recipient_bank: str
    bank_bik: str