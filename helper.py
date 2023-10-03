import os
import pandas as pd
import subprocess
from typing import List

from flakytest import FlakyTest

def ensure_java_17() -> None:
    java_version_log_name = "java_version.log"
    
    subprocess.call("java -version >> java_version.log")
    subprocess.call("sudo apt-get update && sudo apt-get install openjdk-17-jdk >> java_version.log")
    subprocess.call("sudo update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java >> java_version.log")
    subprocess.call("sudo update-alternatives --set javac /usr/lib/jvm/java-17-openjdk-amd64/bin/javac >> java_version.log")
    subprocess.call("java -version >> java_version.log")

def ensure_maven_version(maven_download_url: str) -> None:
#   maven_download_url = "https://dlcdn.apache.org/maven/maven-3/3.9.2/binaries/apache-maven-3.9.2-bin.tar.gz"
  filename = maven_download_url.split("/")[-1]
  maven_version = filename.split("-")[:-1]

  subprocess.run(f"wget {maven_download_url} -O /tmp/{filename}")
  subprocess.run(f"tar -xvf /tmp/{filename} -C /opt")
  subprocess.run(f"ln -s /opt/{maven_version} /opt/maven")
  subprocess.run(f"rm /tmp/{filename}")

def setup_nondex_testing_filestructure(proj_root: str) -> None:
    # Create a directory for nondex_upgrade
    if not os.path.isdir(proj_root):
        os.makedirs(proj_root)
    os.chdir(proj_root)
    nondex_testing_path = f"{proj_root}/nondex_upgrade_testing"
    if not os.path.isdir(nondex_testing_path):
        os.mkdir(nondex_testing_path, 777)

def load_flaky_tests(proj_root: str, current_project_url: str) -> List[FlakyTest]:
    # Read tests csv
    os.chdir(f"{proj_root}/nondex_upgrade_testing")
    dataset_name = "modified-pr-data.csv"
    if not os.path.isfile(f"{proj_root}/{dataset_name}"): 
        get_dataset = "wget https://gist.githubusercontent.com/zzjas/2aa06ef5e7f0087496ea7ab17938b115/raw/6e2c8837607dbb44a3c4264af197d4a0230468ca/modified-pr-data.csv"
        subprocess.call(get_dataset)
    
    column_names = ["Project URL", 
                    "SHA Detected", 
                    "Module Path", 
                    "Fully-Qualified Test Name (packageName.ClassName.methodName)",
                    "Category",
                    "Status",
                    "PR Link",
                    "Notes"]
    
    dataset = pd.read_csv(f"{proj_root}/{dataset_name}", names=column_names)
    # Filter tests to only include current project
    project_tests = dataset[dataset["Project URL"] == current_project_url].to_numpy()
    
    flaky_tests = []
    for test in project_tests:
        flaky_tests.append(FlakyTest(project_url = test[0], sha_detected = test[1], module_path = test[2], test_name = test[3], category = test[4], status = test[5], pr_link = test[6], notes = test[7]) ) # type: ignore
    
    return flaky_tests
