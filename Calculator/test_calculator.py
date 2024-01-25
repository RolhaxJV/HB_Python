""" Test Calculator Tkinter """
import pytest
import calculator


def test_number_1_num1():
    """Check if num1 is a float
    """
    assert(isinstance(calculator.entry1.get(),float))


def test_number_2_num2():
    """Check if num1 is a float
    """
    assert(isinstance(calculator.entry2.get(),float))

@pytest.mark.parametrize("number_1, number_2", [(2, 2), (3, 5), (6, 10)])
def test_number_2_my_list_length(number_1, number_2):
    """Check if the operation is egal of the attemp result

    Args:
        number_1 (int): _description_
        number_2 (int): _description_
    """
    computed_result = eval(f"{number_1}+{number_2}")
    expected_result = number_1+number_2
    
    
    assert(computed_result==expected_result)

