from helper import load_flaky_tests, setup_nondex_testing_filestructure, ensure_java_17, ensure_maven_version

def main():
    PROJ_ROOT = "/home/neo/cs527"
    nondex_testing_path = f"{PROJ_ROOT}/nondex_upgrade_testing"
    # repo_name = "nifi"
    # repo_https_link = "https://github.com/zzjas/nifi.git"
    # project_url = "https://github.com/zzjas/nifi"
    project_url = ""
    
    setup_nondex_testing_filestructure(PROJ_ROOT)
    project_flaky_tests = load_flaky_tests(PROJ_ROOT, project_url)
    
    # Check current Java version is 17.0.6 at least
    log_path = f"{nondex_testing_path}/flaky_testing_logs"
    ensure_java_17(log_path=log_path)
    # Check Maven version is 3.9.2 at least
    ensure_maven_version(log_path=log_path)

    for test in project_flaky_tests:  
    # test = project_flaky_tests[0]
        log_path = f"{nondex_testing_path}/flaky_testing_logs/{test.project_name}"
        test.set_nondex_maven_plugin("nondex-maven-plugin:2.1.1")
        # test.set_nondex_maven_plugin("nondex-maven-plugin:2.1.7-SNAPSHOT")
        test.run_flaky_test(nondex_testing_path, log_path)
    
    # Clone compatible repo
    # repo_https_link = f"{test.project_url}.git"
    # clone_project_repo(repo_https_link, repo_name, nondex_testing_path)

    # Build repo successfully
    
    
    return


if __name__ == "__main__":
    main()