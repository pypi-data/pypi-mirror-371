import requests
from typing import Dict, Optional

from .exceptions import (
    TsPayError,
    AuthenticationError,
    TransactionNotFound,
    InvalidRequestError,
    NetworkError,
    ServerError,
)


class TsPayClient:
    """TSPay uchun rasmiy Python klienti (faqat do'kon access_token bilan ishlaydi)"""

    BASE_URL = "https://tspay.uz/api/v1"

    def __init__(self, base_url: str = None):
        self.base_url = base_url or self.BASE_URL

    def create_transaction(
        self,
        amount: float,
        access_token: str,
        redirect_url: str = "",
        comment: str = ""
    ) -> Dict:
        """Do'kon access_token bilan yangi tranzaksiya yaratish"""
        url = f"{self.base_url}/transactions/create/"

        if not access_token:
            raise AuthenticationError("Do'kon access_token ko'rsatilmagan")

        data = {
            "amount": amount,
            "redirect_url": redirect_url,
            "comment": comment,
            "access_token": access_token,
        }

        try:
            response = requests.post(url, json=data)

            if response.status_code == 401:
                raise AuthenticationError("Noto‘g‘ri yoki faol bo‘lmagan access_token")
            if response.status_code >= 500:
                raise ServerError("TSPay serverida muammo")

            response.raise_for_status()
            transaction_data = response.json()

            if not transaction_data.get("transaction"):
                raise TsPayError("Tranzaksiya ma'lumotlari qaytmadi")

            return transaction_data["transaction"]

        except requests.RequestException as e:
            raise NetworkError(f"Tranzaksiya yaratishda xato: {str(e)}")
        except ValueError as e:
            raise InvalidRequestError(f"JSON javobini tahlil qilishda xato: {str(e)}")

    def check_transaction(self, access_token: str, cheque_id: str) -> Dict:
        """Tranzaksiya holatini tekshirish (do'kon access_token orqali)"""
        if not cheque_id:
            raise InvalidRequestError("Tranzaksiya ID (cheque_id) ko'rsatilmagan")

        url = f"{self.base_url}/transactions/{cheque_id}/"
        params = {"access_token": access_token}

        try:
            response = requests.get(url, params=params)

            if response.status_code == 401:
                raise AuthenticationError("Noto‘g‘ri yoki faol bo‘lmagan access_token")
            if response.status_code == 404:
                raise TransactionNotFound("Bunday cheque_id bilan tranzaksiya topilmadi")
            if response.status_code >= 500:
                raise ServerError("TSPay serverida muammo")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise NetworkError(f"Tranzaksiyani tekshirishda xato: {str(e)}")
        except ValueError as e:
            raise InvalidRequestError(f"JSON javobini tahlil qilishda xato: {str(e)}")