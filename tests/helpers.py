from warnings import catch_warnings, simplefilter


def ignore_warnings(test):
    def do_test(self, *args, **kwargs):
        with catch_warnings():
            simplefilter("ignore")
            test(self, *args, **kwargs)
    return do_test
