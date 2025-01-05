import pytest

from pokie.sample import Sample, MyException


class TestSample:

    def test_sample(self):
        s = Sample()
        with pytest.raises(MyException) as exp:
            s.do_work()
        print(exp.value)
