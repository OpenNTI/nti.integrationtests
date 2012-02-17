def runner(x):
    assert True

def test_generator():
    yield runner, 2

def main(args = None):
    import nose
    import sys
    nose.run()
    
if __name__ == '__main__':
    main()