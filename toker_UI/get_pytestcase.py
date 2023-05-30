import pytest

def pytest_generate_tests(metafunc):
    if "test_name" in metafunc.fixturenames:
        test_names = get_test_names_from_directory("tests")
        metafunc.parametrize("test_name", test_names)

def get_test_names_from_directory(directory):
    test_names = []
    test_files = pytest.Pytester(directory).parseconfig().getnode(directory).collect()
    
    for item in test_files:
        if isinstance(item, pytest.Item):
            test_names.append(item.name)
        else:
            test_names.extend(get_test_names_from_item(item))
            
    return test_names

def get_test_names_from_item(item):
    test_names = []

    for sub_item in item.collect():
        if isinstance(sub_item, pytest.Item):
            test_names.append(sub_item.name)
        else:
            test_names.extend(get_test_names_from_item(sub_item))

    return test_names

# 示例：获取"tests"目录下所有测试项的名称
if __name__ == "__main__":
    directory_path = "tests"
    test_names = get_test_names_from_directory(directory_path)
    for name in test_names:
        print(name)
