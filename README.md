# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/multiversx/mx-sdk-py/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                                           |    Stmts |     Miss |   Cover |   Missing |
|--------------------------------------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| multiversx\_sdk/\_\_init\_\_.py                                                                                |       43 |        0 |    100% |           |
| multiversx\_sdk/adapters/\_\_init\_\_.py                                                                       |        2 |        0 |    100% |           |
| multiversx\_sdk/adapters/query\_runner\_adapter.py                                                             |       33 |        7 |     79% |12, 15, 18, 21, 24, 34, 39 |
| multiversx\_sdk/converters/\_\_init\_\_.py                                                                     |        2 |        0 |    100% |           |
| multiversx\_sdk/converters/errors.py                                                                           |        3 |        1 |     67% |         3 |
| multiversx\_sdk/converters/transactions\_converter.py                                                          |       67 |        6 |     91% |105, 109, 113, 117, 134, 138 |
| multiversx\_sdk/core/\_\_init\_\_.py                                                                           |       25 |        0 |    100% |           |
| multiversx\_sdk/core/account.py                                                                                |        9 |        0 |    100% |           |
| multiversx\_sdk/core/address.py                                                                                |      110 |       16 |     85% |20, 23, 68, 76, 87, 99, 121-125, 133, 187, 199, 203, 212, 216 |
| multiversx\_sdk/core/bech32.py                                                                                 |       79 |       25 |     68% |67, 73, 77, 90, 100, 106-118, 123-129 |
| multiversx\_sdk/core/code\_metadata.py                                                                         |       28 |        0 |    100% |           |
| multiversx\_sdk/core/codec.py                                                                                  |       12 |        1 |     92% |        21 |
| multiversx\_sdk/core/constants.py                                                                              |       21 |        0 |    100% |           |
| multiversx\_sdk/core/contract\_query.py                                                                        |       19 |        0 |    100% |           |
| multiversx\_sdk/core/contract\_query\_builder.py                                                               |       14 |        0 |    100% |           |
| multiversx\_sdk/core/errors.py                                                                                 |       37 |        3 |     92% |16, 36, 51 |
| multiversx\_sdk/core/interfaces.py                                                                             |       77 |       10 |     87% |6, 9, 46, 74, 77, 82, 89, 92, 97, 109 |
| multiversx\_sdk/core/message.py                                                                                |       39 |        0 |    100% |           |
| multiversx\_sdk/core/proto/\_\_init\_\_.py                                                                     |        0 |        0 |    100% |           |
| multiversx\_sdk/core/proto/transaction\_pb2.py                                                                 |       13 |        0 |    100% |           |
| multiversx\_sdk/core/proto/transaction\_serializer.py                                                          |       52 |        0 |    100% |           |
| multiversx\_sdk/core/serializer.py                                                                             |       32 |        2 |     94% |    43, 46 |
| multiversx\_sdk/core/smart\_contract\_queries\_controller.py                                                   |       15 |        1 |     93% |         9 |
| multiversx\_sdk/core/smart\_contract\_query.py                                                                 |       14 |        0 |    100% |           |
| multiversx\_sdk/core/token\_payment.py                                                                         |       67 |        2 |     97% |    51, 89 |
| multiversx\_sdk/core/tokens.py                                                                                 |       79 |        5 |     94% |103, 110, 113, 116, 120 |
| multiversx\_sdk/core/transaction.py                                                                            |       19 |        0 |    100% |           |
| multiversx\_sdk/core/transaction\_builders/\_\_init\_\_.py                                                     |        8 |        0 |    100% |           |
| multiversx\_sdk/core/transaction\_builders/contract\_builders.py                                               |       62 |        0 |    100% |           |
| multiversx\_sdk/core/transaction\_builders/default\_configuration.py                                           |       17 |        0 |    100% |           |
| multiversx\_sdk/core/transaction\_builders/esdt\_builders.py                                                   |       31 |        0 |    100% |           |
| multiversx\_sdk/core/transaction\_builders/relayed\_v1\_builder.py                                             |       58 |        1 |     98% |        96 |
| multiversx\_sdk/core/transaction\_builders/relayed\_v2\_builder.py                                             |       36 |        0 |    100% |           |
| multiversx\_sdk/core/transaction\_builders/transaction\_builder.py                                             |       65 |        2 |     97% |   83, 107 |
| multiversx\_sdk/core/transaction\_builders/transfers\_builders.py                                              |       62 |        0 |    100% |           |
| multiversx\_sdk/core/transaction\_computer.py                                                                  |       89 |        1 |     99% |        85 |
| multiversx\_sdk/core/transaction\_parsers/\_\_init\_\_.py                                                      |        2 |        0 |    100% |           |
| multiversx\_sdk/core/transaction\_parsers/interfaces.py                                                        |       28 |        0 |    100% |           |
| multiversx\_sdk/core/transaction\_parsers/token\_operations\_outcome\_parser.py                                |      151 |       88 |     42% |32-37, 40-45, 48-53, 56-65, 68-69, 72-73, 110-119, 122-126, 129-133, 136-145, 148-157, 160-169, 172-180, 183-191, 194-202, 214 |
| multiversx\_sdk/core/transaction\_parsers/token\_operations\_outcome\_parser\_types.py                         |       61 |        0 |    100% |           |
| multiversx\_sdk/core/transaction\_parsers/transaction\_on\_network\_wrapper.py                                 |       51 |        7 |     86% |23-26, 33, 35, 44, 56 |
| multiversx\_sdk/core/transaction\_payload.py                                                                   |       23 |        5 |     78% |12, 26-27, 30, 36 |
| multiversx\_sdk/core/transactions\_factories/\_\_init\_\_.py                                                   |        8 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_factories/account\_transactions\_factory.py                                 |       44 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_factories/delegation\_transactions\_factory.py                              |      111 |        1 |     99% |        59 |
| multiversx\_sdk/core/transactions\_factories/relayed\_transactions\_factory.py                                 |       49 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_factories/smart\_contract\_transactions\_factory.py                         |       61 |        1 |     98% |        78 |
| multiversx\_sdk/core/transactions\_factories/token\_management\_transactions\_factory.py                       |      109 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_factories/token\_transfers\_data\_builder.py                                |       26 |        1 |     96% |         9 |
| multiversx\_sdk/core/transactions\_factories/transaction\_builder.py                                           |       31 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_factories/transactions\_factory\_config.py                                  |       41 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_factories/transfer\_transactions\_factory.py                                |       41 |        1 |     98% |        55 |
| multiversx\_sdk/core/transactions\_outcome\_parsers/\_\_init\_\_.py                                            |        5 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_outcome\_parsers/delegation\_transactions\_outcome\_parser.py               |       23 |        4 |     83% | 28-31, 35 |
| multiversx\_sdk/core/transactions\_outcome\_parsers/delegation\_transactions\_outcome\_parser\_types.py        |        4 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_outcome\_parsers/resources.py                                               |       38 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_outcome\_parsers/smart\_contract\_transactions\_outcome\_parser.py          |       20 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_outcome\_parsers/smart\_contract\_transactions\_outcome\_parser\_types.py   |       12 |        0 |    100% |           |
| multiversx\_sdk/core/transactions\_outcome\_parsers/token\_management\_transactions\_outcome\_parser.py        |      115 |        6 |     95% |52, 63, 66, 230, 242, 248 |
| multiversx\_sdk/core/transactions\_outcome\_parsers/token\_management\_transactions\_outcome\_parser\_types.py |       79 |        0 |    100% |           |
| multiversx\_sdk/core/typecheck.py                                                                              |        5 |        0 |    100% |           |
| multiversx\_sdk/network\_providers/\_\_init\_\_.py                                                             |        7 |        0 |    100% |           |
| multiversx\_sdk/network\_providers/accounts.py                                                                 |       55 |       22 |     60% |33, 45-47, 51-61, 64-66, 71-73, 77-83 |
| multiversx\_sdk/network\_providers/api\_network\_provider.py                                                   |      179 |       30 |     83% |50, 57, 60, 78-81, 84-87, 157-158, 173-174, 203-206, 214-220, 228-229, 236-237 |
| multiversx\_sdk/network\_providers/config.py                                                                   |        9 |        2 |     78% |    10, 13 |
| multiversx\_sdk/network\_providers/constants.py                                                                |        5 |        0 |    100% |           |
| multiversx\_sdk/network\_providers/contract\_query\_requests.py                                                |       11 |        1 |     91% |        19 |
| multiversx\_sdk/network\_providers/contract\_query\_response.py                                                |       26 |        1 |     96% |        34 |
| multiversx\_sdk/network\_providers/contract\_results.py                                                        |       66 |        1 |     98% |        44 |
| multiversx\_sdk/network\_providers/errors.py                                                                   |       12 |        1 |     92% |        18 |
| multiversx\_sdk/network\_providers/interface.py                                                                |       25 |       10 |     60% |6, 11, 14, 19, 22, 27, 30, 33, 36, 39 |
| multiversx\_sdk/network\_providers/network\_config.py                                                          |       33 |        1 |     97% |        39 |
| multiversx\_sdk/network\_providers/network\_general\_statistics.py                                             |       23 |        0 |    100% |           |
| multiversx\_sdk/network\_providers/network\_stake.py                                                           |       15 |        0 |    100% |           |
| multiversx\_sdk/network\_providers/network\_status.py                                                          |       25 |        0 |    100% |           |
| multiversx\_sdk/network\_providers/proxy\_network\_provider.py                                                 |      187 |       38 |     80% |65-67, 70-75, 78-83, 158-161, 188-194, 202-208, 215, 221-224 |
| multiversx\_sdk/network\_providers/resources.py                                                                |       58 |       35 |     40% |20, 25-28, 31-37, 40-45, 48-49, 52-60, 65, 70-74, 77-84 |
| multiversx\_sdk/network\_providers/token\_definitions.py                                                       |      118 |        0 |    100% |           |
| multiversx\_sdk/network\_providers/tokens.py                                                                   |       75 |        0 |    100% |           |
| multiversx\_sdk/network\_providers/transaction\_awaiter.py                                                     |       56 |       10 |     82% |13, 37, 42, 49, 55, 95-96, 102, 105-106 |
| multiversx\_sdk/network\_providers/transaction\_decoder.py                                                     |      164 |       24 |     85% |29, 39-54, 97, 100, 113-114, 131, 134, 137, 165, 169, 172, 175, 220, 222, 229-230 |
| multiversx\_sdk/network\_providers/transaction\_events.py                                                      |       45 |        4 |     91% |41, 56, 59, 67 |
| multiversx\_sdk/network\_providers/transaction\_logs.py                                                        |       29 |        9 |     69% |28-31, 34-39, 42 |
| multiversx\_sdk/network\_providers/transaction\_receipt.py                                                     |       19 |        0 |    100% |           |
| multiversx\_sdk/network\_providers/transaction\_status.py                                                      |       20 |        1 |     95% |        27 |
| multiversx\_sdk/network\_providers/transactions.py                                                             |      123 |       24 |     80% |134, 160-167, 171-190, 193 |
| multiversx\_sdk/network\_providers/utils.py                                                                    |        8 |        4 |     50% |      7-10 |
| multiversx\_sdk/testutils/mock\_network\_provider.py                                                           |      114 |       28 |     75% |53-56, 75-87, 90-92, 116-121, 125-126, 132, 135-136, 143, 154-155 |
| multiversx\_sdk/testutils/utils.py                                                                             |        8 |        0 |    100% |           |
| multiversx\_sdk/testutils/wallets.py                                                                           |       21 |        0 |    100% |           |
| multiversx\_sdk/wallet/\_\_init\_\_.py                                                                         |       11 |        0 |    100% |           |
| multiversx\_sdk/wallet/constants.py                                                                            |        6 |        0 |    100% |           |
| multiversx\_sdk/wallet/core.py                                                                                 |       33 |        0 |    100% |           |
| multiversx\_sdk/wallet/crypto/\_\_init\_\_.py                                                                  |        4 |        0 |    100% |           |
| multiversx\_sdk/wallet/crypto/constants.py                                                                     |        5 |        0 |    100% |           |
| multiversx\_sdk/wallet/crypto/decryptor.py                                                                     |       30 |        3 |     90% |21, 24, 49 |
| multiversx\_sdk/wallet/crypto/encrypted\_data.py                                                               |       21 |        0 |    100% |           |
| multiversx\_sdk/wallet/crypto/encryptor.py                                                                     |       22 |        0 |    100% |           |
| multiversx\_sdk/wallet/crypto/randomness.py                                                                    |        9 |        0 |    100% |           |
| multiversx\_sdk/wallet/errors.py                                                                               |       28 |        8 |     71% |6, 11, 16, 21, 31, 36, 41, 46 |
| multiversx\_sdk/wallet/interfaces.py                                                                           |       11 |        2 |     82% |    15, 18 |
| multiversx\_sdk/wallet/libraries/\_\_init\_\_.py                                                               |        0 |        0 |    100% |           |
| multiversx\_sdk/wallet/libraries/bls\_facade.py                                                                |       68 |        6 |     91% |69, 94, 96-99, 103 |
| multiversx\_sdk/wallet/mnemonic.py                                                                             |       33 |        3 |     91% |36, 42, 45 |
| multiversx\_sdk/wallet/pem\_entry.py                                                                           |       40 |        0 |    100% |           |
| multiversx\_sdk/wallet/user\_keys.py                                                                           |       53 |        9 |     83% |14, 20-22, 43, 46, 52, 72, 75 |
| multiversx\_sdk/wallet/user\_pem.py                                                                            |       36 |        2 |     94% |     26-27 |
| multiversx\_sdk/wallet/user\_signer.py                                                                         |       27 |        4 |     85% |25-26, 31-32 |
| multiversx\_sdk/wallet/user\_verifer.py                                                                        |       13 |        0 |    100% |           |
| multiversx\_sdk/wallet/user\_wallet.py                                                                         |       89 |        4 |     96% |71, 100, 116, 123 |
| multiversx\_sdk/wallet/validator\_keys.py                                                                      |       47 |        9 |     81% |11, 17-18, 34, 37, 40, 46, 63, 66 |
| multiversx\_sdk/wallet/validator\_pem.py                                                                       |       34 |        2 |     94% |     24-25 |
| multiversx\_sdk/wallet/validator\_signer.py                                                                    |       22 |        3 |     86% | 26-27, 34 |
| multiversx\_sdk/wallet/validator\_verifier.py                                                                  |       11 |        0 |    100% |           |
|                                                                                                      **TOTAL** | **4666** |  **498** | **89%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/multiversx/mx-sdk-py/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/multiversx/mx-sdk-py/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/multiversx/mx-sdk-py/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/multiversx/mx-sdk-py/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fmultiversx%2Fmx-sdk-py%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/multiversx/mx-sdk-py/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.