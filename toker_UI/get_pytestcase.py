import os
import pytest

class TestCaseCollector:
    def __init__(self):
        self.test_cases = []

    def pytest_collection_modifyitems(self, items):
        for item in items:
            if isinstance(item, pytest.Function):
                self.test_cases.append(item.name)


def get_testcase_names(test_directory):
    collector = TestCaseCollector()
    pytest.main(["--collect-only", "-q", test_directory], plugins=[collector])
    return collector.test_cases

def get_dir_structure(base_path):
    dir_structure = {}

    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        
        if os.path.isdir(folder_path):
            dir_structure[folder] = {}

            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)

                if os.path.isfile(file_path):
                    dir_structure[folder][file] = get_testcase_names(file_path)

    return dir_structure


if __name__ == "__main__":
    base_path = "./devcase"
    dir_structure = get_dir_structure(base_path)



