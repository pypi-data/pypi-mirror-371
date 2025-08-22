import os
from dataclasses import dataclass
from web3 import Web3, Account
from hexbytes import HexBytes
from eth_abi.abi import encode

from .module_data.module_data import ModuleData


@dataclass
class SignedAction:
    subaccount_id: int
    owner: str
    signer: str
    signature_expiry_sec: int
    nonce: int
    module_address: str
    module_data: ModuleData
    DOMAIN_SEPARATOR: str
    ACTION_TYPEHASH: str
    signature: str = ""
    """
    Used to sign and validate actions.

    :param subaccount_id: The subaccount id of the user.
    :param owner: The owner of the account on the v2 protocol (not the session key).
    :param signer: The signer of the action - can be the owner or a session key.
    :param signature_expiry_sec: The expiry time of the signature in seconds. Must be >5min from now.
    :param nonce: Unique nonce defined as <UTC_timestamp in ms><random_number_up_to_6_digits> (e.g. 1695836058725001, where 001 is the random number).
    :param module_address: The contract address of the module. Refer to Protocol Constants table in docs.derive.xyz.
    :param module_data: Data defined by the specific protocol module (e.g. for orders use module_data.trade.TradeModuleData).
    :param DOMAIN_SEPARATOR: The domain separator of the protocol. Refer to Protocol Constants table in docs.derive.xyz.
    :param ACTION_TYPEHASH: The typehash of the action. Refer to Protocol Constants table in docs.derive.xyz.
    :param signature: The signature of the action. Use sign() to generate the signature.
    """

    def sign(self, signer_private_key: str):
        signer_wallet = Web3().eth.account.from_key(signer_private_key)
        signature: Account = signer_wallet.unsafe_sign_hash(self._to_typed_data_hash())
        self.signature = signature.signature.hex()
        return self.signature

    def to_json(self):
        return {
            "subaccount_id": self.subaccount_id,
            "nonce": self.nonce,
            "signer": self.signer,
            "signature_expiry_sec": self.signature_expiry_sec,
            "signature": self.signature,
            **self.module_data.to_json(),
        }

    def validate_signature(self):
        data_hash = self._to_typed_data_hash()
        recovered = Account._recover_hash(
            data_hash.hex(),
            signature=HexBytes(self.signature),
        )

        if recovered.lower() != self.signer.lower():
            raise ValueError("Invalid signature. Recovered signer does not match expected signer.")

    @property
    def domain_separator(self) -> bytes:
        try:
            return bytes.fromhex(self.DOMAIN_SEPARATOR[2:])
        except:
            raise ValueError(
                "Unable to extract bytes from DOMAIN_SEPARATOR. Ensure value is copied from Protocol Constants in docs.derive.xyz."
            )

    @property
    def action_typehash(self) -> bytes:
        try:
            return bytes.fromhex(self.ACTION_TYPEHASH[2:])
        except:
            raise ValueError(
                "Unable to extract bytes from ACTION_TYPEHASH. Ensure value is copied from Protocol Constants in docs.derive.xyz."
            )

    def _to_typed_data_hash(self) -> HexBytes:
        encoded_typed_data_hash = "".join(["0x1901", self.DOMAIN_SEPARATOR[2:], self._get_action_hash().hex()])
        return Web3.keccak(hexstr=encoded_typed_data_hash)

    def _get_action_hash(self) -> HexBytes:
        return Web3.keccak(
            encode(
                [
                    "bytes32",
                    "uint",
                    "uint",
                    "address",
                    "bytes32",
                    "uint",
                    "address",
                    "address",
                ],
                [
                    self.action_typehash,
                    self.subaccount_id,
                    self.nonce,
                    Web3.to_checksum_address(self.module_address),
                    Web3.keccak(self.module_data.to_abi_encoded()),
                    self.signature_expiry_sec,
                    Web3.to_checksum_address(self.owner),
                    Web3.to_checksum_address(self.signer),
                ],
            )
        )
