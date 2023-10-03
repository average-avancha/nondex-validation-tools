import os
import subprocess
import pandas

from helper import load_flaky_tests, setup_nondex_testing_filestructure
import flakytest

def main():
    PROJ_ROOT = "/home/neo/cs527"
    nondex_testing_path = f"{PROJ_ROOT}/nondex_upgrade_testing"
    repo_name = "nifi"
    # repo_https_link = "https://github.com/zzjas/nifi.git"
    project_url = "https://github.com/zzjas/nifi"

    setup_nondex_testing_filestructure(PROJ_ROOT)
    project_flaky_tests = load_flaky_tests(PROJ_ROOT, project_url)
    
    # for test in project_flaky_tests:  
    test = project_flaky_tests[0]
    log_path = f"{nondex_testing_path}/flaky_testing_logs/{test.module_path}"
    test.set_nondex_maven_plugin("nondex-maven-plugin:2.1.7-SNAPSHOT")
    test.run_flaky_test(nondex_testing_path, log_path)
        
    # Check current Java version is 17.0.6 at least
    # ensure_java_17()

    # Check Maven version is 3.9.2 at least
    # ensure_maven_3_9_2()
    
    # Clone compatible repo
    # repo_https_link = f"{test.project_url}.git"
    # clone_project_repo(repo_https_link, repo_name, nondex_testing_path)

    # Build repo successfully
    
    
    return


if __name__ == "__main__":
    main()