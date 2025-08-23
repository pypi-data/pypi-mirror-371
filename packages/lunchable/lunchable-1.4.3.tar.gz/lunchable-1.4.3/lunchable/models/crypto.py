"""
Lunch Money - Crypto

https://lunchmoney.dev/#crypto
"""

import datetime
import logging
from typing import List, Optional

from pydantic import Field

from lunchable._config import APIConfig
from lunchable.models._base import LunchableModel
from lunchable.models._core import LunchMoneyAPIClient
from lunchable.models._descriptions import _CryptoDescriptions

logger = logging.getLogger(__name__)


class CryptoObject(LunchableModel):
    """
    Crypto Asset Object

    https://lunchmoney.dev/#crypto-object
    """

    id: int = Field(description=_CryptoDescriptions.id)
    zabo_account_id: Optional[int] = Field(
        None, description=_CryptoDescriptions.zabo_account_id
    )
    source: str = Field(description=_CryptoDescriptions.source)
    name: str = Field(description="Name of the crypto asset")
    display_name: Optional[str] = Field(
        None, description=_CryptoDescriptions.display_name
    )
    balance: float = Field(description="Current balance")
    balance_as_of: Optional[datetime.datetime] = Field(
        None, description=_CryptoDescriptions.balance_as_of
    )
    currency: Optional[str] = Field(
        None, description="Abbreviation for the cryptocurrency"
    )
    status: Optional[str] = Field(None, description=_CryptoDescriptions.status)
    institution_name: Optional[str] = Field(
        default=None, description="Name of provider holding the asset"
    )
    created_at: datetime.datetime = Field(description=_CryptoDescriptions.created_at)


class CryptoParamsPut(LunchableModel):
    """
    https://lunchmoney.dev/#update-manual-crypto-asset
    """

    name: Optional[str] = None
    display_name: Optional[str] = None
    institution_name: Optional[str] = None
    balance: Optional[float] = None
    currency: Optional[str] = None


class CryptoClient(LunchMoneyAPIClient):
    """
    Lunch Money Tag Interactions
    """

    def get_crypto(self) -> List[CryptoObject]:
        """
        Get Crypto Assets

        Use this endpoint to get a list of all cryptocurrency assets associated
        with the user's account. Both crypto balances from synced and manual
        accounts will be returned.

        https://lunchmoney.dev/#get-all-crypto

        Returns
        -------
        List[CryptoObject]
        """
        response_data = self.make_request(
            method=self.Methods.GET, url_path=APIConfig.LUNCHMONEY_CRYPTO
        )
        crypto_data = response_data["crypto"]
        crypto_objects = [CryptoObject.model_validate(item) for item in crypto_data]
        return crypto_objects

    def update_crypto(
        self,
        crypto_id: int,
        name: Optional[str] = None,
        display_name: Optional[str] = None,
        institution_name: Optional[str] = None,
        balance: Optional[float] = None,
        currency: Optional[str] = None,
    ) -> CryptoObject:
        """
        Update a Manual Crypto Asset

        Use this endpoint to update a single manually-managed crypto asset (does not include
        assets received from syncing with your wallet/exchange/etc). These are denoted by
        source: manual from the GET call above.

        https://lunchmoney.dev/#update-manual-crypto-asset

        Parameters
        ----------
        crypto_id: int
            ID of the crypto asset to update
        name: Optional[str]
            Official or full name of the account. Max 45 characters
        display_name: Optional[str]
            Display name for the account. Max 25 characters
        institution_name: Optional[str]
            Name of provider that holds the account. Max 50 characters
        balance: Optional[float]
            Numeric value of the current balance of the account. Do not include any
            special characters aside from a decimal point!
        currency: Optional[str]
            Cryptocurrency that is supported for manual tracking in our database

        Returns
        -------
        CryptoObject
        """
        crypto_body = CryptoParamsPut(
            name=name,
            display_name=display_name,
            institution_name=institution_name,
            balance=balance,
            currency=currency,
        ).model_dump(exclude_none=True)
        response_data = self.make_request(
            method=self.Methods.PUT,
            url_path=[
                APIConfig.LUNCHMONEY_CRYPTO,
                APIConfig.LUNCHMONEY_CRYPTO_MANUAL,
                crypto_id,
            ],
            payload=crypto_body,
        )
        crypto = CryptoObject.model_validate(response_data)
        return crypto
