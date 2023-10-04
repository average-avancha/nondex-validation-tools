import os
import pandas as pd
import subprocess
from typing import List

from flakytest import FlakyTest

MODE = 0o777

def ensure_java_17(log_path = "", log_name: str = "java_version.log") -> None:
    if log_path == "":
        log_path = os.getcwd()
    
    if not os.path.isdir(log_path):
        os.mkdir(log_path, mode=MODE)
    os.chdir(log_path)

    if not os.path.isfile(log_name):
        subprocess.call(f"echo ''> {log_path}/{log_name}")

    subprocess.call(f"java --version | tee {log_path}/{log_name}", shell=True)
    # subprocess.call(f"sudo apt-get update && sudo apt-get install openjdk-17-jdk >> {log_name}", shell=True)
    # subprocess.call(f"sudo update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java >> {log_name}", shell=True)
    # subprocess.call(f"sudo update-alternatives --set javac /usr/lib/jvm/java-17-openjdk-amd64/bin/javac >> {log_name}", shell=True)
    # subprocess.call(f"java -version >> {log_name}", shell=True)

def ensure_maven_version(maven_download_url: str = "", log_path = "", log_name: str = "maven_version.log") -> None:
    if log_path == "":
        log_path = os.getcwd()
    
    if not os.path.isdir(log_path):
        os.mkdir(log_path, mode=MODE)
    os.chdir(log_path)

    subprocess.call(f"mvn --version > {log_path}/{log_name}", shell=True)

    # if maven_download_url == "":
    #     maven_download_url = "https://archive.apache.org/dist/maven/maven-3/3.9.2/binaries/apache-maven-3.9.2-bin.tar.gz"
    # filename = maven_download_url.split("/")[-1]
    # maven_version = "-".join(filename.split("-")[:-1])

    # subprocess.run(f"wget {maven_download_url} -O /tmp/{filename} >> {log_name}", shell=True)
    # subprocess.run(f"sudo tar -xvf /tmp/{filename} -C /opt >> {log_name}", shell=True)
    # subprocess.run(f"sudo ln -s /opt/{maven_version} /opt/maven >> {log_name}", shell=True)
    # subprocess.run(f"rm /tmp/{filename} >> {log_name}", shell=True)



def setup_nondex_testing_filestructure(proj_root: str) -> None:
    # Create a directory for nondex_upgrade
    os.chdir(proj_root)
    os.chmod(proj_root, mode=MODE)
    nondex_testing_path = f"{proj_root}/nondex_upgrade_testing"
    if not os.path.isdir(nondex_testing_path):
        os.mkdir(nondex_testing_path, mode=MODE)
    os.chmod(nondex_testing_path, mode=MODE)

def load_flaky_tests(proj_root: str, current_project_url: str = "") -> List[FlakyTest]:
    # Read tests csv
    cwd = f"{proj_root}/nondex_upgrade_testing"
    os.chdir(cwd)

    dataset_name = "modified-pr-data.csv"
    if not os.path.isfile(f"{proj_root}/{dataset_name}"): 
        get_dataset = "wget https://gist.githubusercontent.com/zzjas/2aa06ef5e7f0087496ea7ab17938b115/raw/6e2c8837607dbb44a3c4264af197d4a0230468ca/modified-pr-data.csv"
        subprocess.call(get_dataset, shell=True)
    
    column_names = ["Project URL", 
                    "SHA Detected", 
                    "Module Path", 
                    "Fully-Qualified Test Name (packageName.ClassName.methodName)",
                    "Category",
                    "Status",
                    "PR Link",
                    "Notes"]
    
    dataset = pd.read_csv(f"{cwd}/{dataset_name}", names=column_names)
    # Filter tests to only include current project
    project_tests = dataset.to_numpy()
    if current_project_url != "":
        project_tests = dataset[dataset["Project URL"] == current_project_url].to_numpy()
    
    flaky_tests = []
    for test in project_tests:
        flaky_tests.append(FlakyTest(project_url = test[0], sha_detected = test[1], module_path = test[2], test_name = test[3], category = test[4], status = test[5], pr_link = test[6], notes = test[7]) ) # type: ignore
    
    return flaky_tests