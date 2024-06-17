from multiversx_sdk.abi.type_formula_parser import TypeFormulaParser


def test_parse_expression():
    parser = TypeFormulaParser()

    test_vectors = [
        ("i64", "i64"),
        ("  i64  ", "i64"),
        ("utf-8 string", "utf-8 string"),
        ("MultiResultVec<MultiResult2<Address, u64>>", "MultiResultVec<MultiResult2<Address, u64>>"),
        ("tuple3<i32, bytes, Option<i64>>", "tuple3<i32, bytes, Option<i64>>"),
        ("tuple2<i32, i32>", "tuple2<i32, i32>"),
        ("tuple2<i32,i32>  ", "tuple2<i32, i32>"),
        ("tuple<List<u64>, List<u64>>", "tuple<List<u64>, List<u64>>")
    ]

    for input_expression, expected_expression in test_vectors:
        type_formula = parser.parse_expression(input_expression)
        output_expression = str(type_formula)

        assert output_expression == expected_expression
