import unittest
import dateutil.parser

from staeon.tx_util import make_txid, make_transaction, validate_transaction
from staeon.exceptions import *

i = [
    ['18pvhMkv1MZbZZEncKucAmVDLXZsD9Dhk6', 3.2, 'KwuVvv359oft9TfzyYLAQBgpPyCFpcTSrV9ZgJF9jKdT8jd7XLH2'],
    ['14ZiHtrmT6Mi4RT2Liz51WKZMeyq2n5tgG', 0.5, 'KxWoW9Pj45UzUH1d5p3wPe7zxbdJqU7HHkDQF1YQS1AiQg9qeZ9H']
]
o = [
    ['16ViwyAVeKtz4vbTXWRSYgadT5w3Rj3yuq', 2.2],
    ['18pPTxvTc9rJZfD2tM1bNYHFhAcZjgqEdQ', 1.4]
]
def ledger(address):
    if address.startswith("18p"): return 3.2
    if address.startswith("14Z"): return 0.5

def bad_ledger(address):
    if address.startswith("18p"): return 1.0
    if address.startswith("14Z"): return 0.3

class BasicTransactionCreationTest(unittest.TestCase):
    def test(self):
        self.assertEqual(
            validate_transaction(make_transaction(i, o), ledger), True,
            msg="Basic transaction creation fails"
        )

class TooFewInputsTest(unittest.TestCase):
    # testing ledger callback catches coins being spent out of thin air.

    def test(self):
        msg="Catch input spending coin that doesn't exist"
        with self.assertRaises(InvalidAmounts, msg=msg):
            validate_transaction(make_transaction(i, o), bad_ledger)

class InvalidSigTest(unittest.TestCase):
    # testing invalid signature fails

    def test(self):
        bad_sig = make_transaction(i, o)
        bad_sig['inputs'][0][2] = "23784623kjhdfkjashdfkj837242387"
        msg="Invalid Signature not happening when sig is edited"
        with self.assertRaises(InvalidSignature,msg=msg):
            validate_transaction(bad_sig, ledger)

class ChangingInputsTest(unittest.TestCase):
    # testing changing values within already made transaction fails validation

    def test(self):
        bad_tx = make_transaction(i, o)
        bad_tx['inputs'][0][1] = 0.2
        msg="Invalid Signature not happening when amount is changed"

        with self.assertRaises(InvalidSignature, msg=msg):
            validate_transaction(bad_tx, ledger)

class OutputsExceedInputsTest(unittest.TestCase):
    # testing make_transaction fails when you make a tx with more outputs than inputs

    def test(self):
        bad_o = [
            ['16ViwyAVeKtz4vbTXWRSYgadT5w3Rj3yuq', 2.2],
            ['18pPTxvTc9rJZfD2tM1bNYHFhAcZjgqEdQ', 9.4]
        ]
        msg="Invalid Amount not happening when outputs exceed inputs when making new trasnaction"

        with self.assertRaises(InvalidAmounts, msg=msg):
            make_transaction(i, bad_o)

class ZeroInputTest(unittest.TestCase):
    # testing make_transaction fails when you add a zero input
    def test(self):
        bad_o = [
            ['16ViwyAVeKtz4vbTXWRSYgadT5w3Rj3yuq', 0],
            ['18pPTxvTc9rJZfD2tM1bNYHFhAcZjgqEdQ', 9.4]
        ]
        with self.assertRaises(InvalidAmounts, msg="Invalid Amount not happening when zero input is tried"):
            make_transaction(i, bad_o)

class NegativeInputTest(unittest.TestCase):
    # testing make_transaction fails when you add a negative input

    def test(self):
        bad_o = [
            ['16ViwyAVeKtz4vbTXWRSYgadT5w3Rj3yuq', -42.07],
            ['18pPTxvTc9rJZfD2tM1bNYHFhAcZjgqEdQ', 9.4]
        ]
        msg="Invalid Amount not happening when negative input is tried on transaction creation"
        with self.assertRaises(InvalidAmounts, msg=msg):
            make_transaction(i, bad_o)

class ValidatingOutputsExceedInputs(unittest.TestCase):
    # testing transaction with valid signatures, but invalid amounts are caught as invalid

    def test(self):
        bad_tx = {
            'inputs': [
                ['18pvhMkv1MZbZZEncKucAmVDLXZsD9Dhk6',3.2,'ILgSi/FsQX2pL5MPoqxvVOAk5o8Njl7a8+ruXXXgU4UIfMyYXx+yytSevMD55ZNceC+1ReVWZgXuFu8iUtOkz2k='],
                ['14ZiHtrmT6Mi4RT2Liz51WKZMeyq2n5tgG',0.5,'IEcFAR6XEdvNmivQDrCEg1DBMiYkwGR+KgB3sVZXdcVTbBD8qfR310m/p/Q5UFRFQ57Cc2mnY+bw8Qr0GQge8So=']
            ],
            'outputs': [
                ['18pPTxvTc9rJZfD2tM1bNYHFhAcZjgqEdQ', 9.4],
                ['16ViwyAVeKtz4vbTXWRSYgadT5w3Rj3yuq', 2.2]
            ],
            'timestamp': '2019-02-13T19:14:27.882253'
        }
        n = dateutil.parser.parse('2019-02-13T19:14:28.882253')
        msg = "Invalid Amount not happening when outputs exceed inputs when validating"
        with self.assertRaises(InvalidAmounts, msg=msg):
            validate_transaction(bad_tx, ledger, now=n)

class NegativeOutputs(unittest.TestCase):
    # valid signatures, but negative amounts

    def test(self):
        bad_tx = {
            'inputs': [
                ['18pvhMkv1MZbZZEncKucAmVDLXZsD9Dhk6',3.2,'H/vTjUELpBg7uB08QOprZCxkbnZTMefq5VJqgZPzzpLtFeBKClAFEPhzYtYQl5tcK6oq0V+GqIrE8dPUR2teLSg='],
                ['14ZiHtrmT6Mi4RT2Liz51WKZMeyq2n5tgG',0.5,'H5qfLufve25jEf8H2qydWKPG9haSgrFfNYct0G9pmqDZeq1fM1fdZzoMJ8e2H9YMVr6t9wpgJpYwEoWA4I4gJl8=']
            ],
            'outputs': [
                ['18pPTxvTc9rJZfD2tM1bNYHFhAcZjgqEdQ', -9.4],
                ['16ViwyAVeKtz4vbTXWRSYgadT5w3Rj3yuq', 2.2]
            ],
            'timestamp': '2019-02-13T19:47:07.354060'
        }
        msg="Invalid Amount not happening when outputs is negative when validating"
        with self.assertRaises(InvalidAmounts, msg=msg):
            validate_transaction(bad_tx, ledger)

class InvalidOutputAddress(unittest.TestCase):
    # testing that a transaction made with a valid signature but invalid address is caught

    def test(self):
        bad_tx = {
            'inputs': [
                ['18pvhMkv1MZbZZEncKucAmVDLXZsD9Dhk6',3.2,'IGFbFxYvnBuYh/b5f6C7BeM8hYABOY/yTON0aEKV0XyPZgkmVkdKrqS/a+4p5tiIC1N4R1y3CyR3fydhWc/WDyc='],
                ['14ZiHtrmT6Mi4RT2Liz51WKZMeyq2n5tgG',0.5,'IF8niJ+u11k3H/JUTWt3dRlmZ8v3Ou8gfwHuuLRPlUHGSc4O2TxgULqBGaQO1BcaAMW/zk89f85se3Rcq+guQNc=']],
            'outputs': [
                ['YYY', 2.2], ['XXX', 1.4]
            ],
            'timestamp': '2019-02-17T12:02:41.843542'
        }
        with self.assertRaises(InvalidAddress,msg="Invalid address not being caught."):
            validate_transaction(bad_tx, ledger)

class P2SHAddressTest(unittest.TestCase):
    # testing make_transaction fails on trying to use a "3" address

    def test(self):
        i = [
            ['18pvhMkv1MZbZZEncKucAmVDLXZsD9Dhk6', 3.2, 'KwuVvv359oft9TfzyYLAQBgpPyCFpcTSrV9ZgJF9jKdT8jd7XLH2'],
            ['14ZiHtrmT6Mi4RT2Liz51WKZMeyq2n5tgG', 0.5, 'KxWoW9Pj45UzUH1d5p3wPe7zxbdJqU7HHkDQF1YQS1AiQg9qeZ9H']
        ]
        o = [['3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy', 2.2]]

        with self.assertRaises(InvalidAddress, msg="3 addresses are invalid"):
            make_transaction(i, o)


if __name__ == '__main__':
    unittest.main()
