""" Test Calculator Tkinter """
import pytest

@pytest.mark.parametrize("number_1, operator, number_2", [('15', '+', '5'),
                                                        ('15','-', '5'),
                                                        ('15', '*', '5'),
                                                        ('15', '**', '5'),
                                                        ('15','/', '5'),
                                                        ('15', '//', '5'),
                                                        ('15', '%', '5')])
def test_perf_ope(number_1, operator, number_2):
    """Check if the operation is egal of the attemp result
    Args:
        number_1 (str): input user
        operator (str): operator selected by user
        number_2 (str): input user
    """
    float(number_1, number_2)
    match operator:
        case "+":
            computed_result = number_1 + number_2

        case "-":
            computed_result = number_1 - number_2

        case "*":
            computed_result = number_1 * number_2

        case "**":
            computed_result = number_1 ** number_2

        case "/":
            computed_result = number_1 / number_2

        case "//":
            computed_result = number_1 // number_2

        case "%":
            computed_result = number_1 % number_2

    expected_result = eval(f"{number_1} {operator} {number_2}")
    assert computed_result == expected_result
