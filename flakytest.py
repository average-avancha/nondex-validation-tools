import os
from os import makedirs, chdir
from os.path import isdir
from subprocess import call, run

class FlakyTest:
    def __init__(self, 
                 project_url: str, 
                 sha_detected: str, 
                 module_path: str,
                 test_name: str,
                 category: str,
                 status: str,
                 pr_link: str,
                 notes: str,
                 nondex_maven_plugin: str = "",
                 mode: int = 0o777) -> None:
        
        self.project_url = project_url # Project URL,
        self.sha_detected = sha_detected # SHA Detected,
        self.module_path = module_path # Module Path,
        self.test_name = test_name # Fully-Qualified Test Name (packageName.ClassName.methodName),
        self.category = category # Category,
        self.status = status # Status,
        self.pr_link = pr_link # PR Link,
        self.notes = notes # Notes
        self.project_name = self.project_url.split("/")[-1]
        self.nondex_maven_plugin = self.set_nondex_maven_plugin(nondex_maven_plugin)
        self.mode = mode

    def run_flaky_test(self, testing_root: str, log_path: str = "") -> None:
        if not os.access(os.path.dirname(testing_root), os.W_OK):
            return
        
        if not isdir(testing_root):
            makedirs(testing_root, mode=self.mode)
        chdir(testing_root)

        if not isdir(log_path):
            makedirs(log_path, mode=self.mode)

        # clone and checkout issue branch of the project
        repo_https_link = f"{self.project_url}.git"
        self.clone_project_repo(repo_link=repo_https_link, repo_name=self.project_name, directory=testing_root, log_path=log_path)
        
        project_dir = f"{testing_root}/{self.project_name}"
        if not isdir(project_dir):
            makedirs(project_dir, mode=self.mode)
        log_directory = log_path
        
        self.run_command(command = f"git checkout {self.sha_detected}", directory = project_dir, log_directory = log_directory)
        chdir(project_dir)
        
        # build module
        self.run_command(command = f"mvn install -pl {self.module_path} -am -DskipTests", directory = project_dir, log_directory = log_directory)

        # run test
        run_test = f"mvn -pl {self.module_path} test -Dtest={self.get_test_name_for_mvn(self.test_name)}"
        self.run_command(command=run_test, directory = project_dir, log_directory = log_directory)

        # run test with NonDex 
        # nondex_maven_plugin = "nondex-maven-plugin:2.1.7-SNAPSHOT"
        nondex_test = f"mvn -pl {self.module_path} edu.illinois:{self.nondex_maven_plugin}:nondex -Dtest={self.get_test_name_for_mvn(self.test_name)} -DnondexRuns=50"
        self.run_command(command=nondex_test, directory = project_dir, log_directory = log_directory)

        self.run_command(f"git reset --hard HEAD^", directory = project_dir, log_directory = log_directory)


    def run_command(self, command: str, directory: str, log_output: bool = True, log_directory: str = "") -> None:
        if log_directory == "":
            log_directory = directory

        if not isdir(directory):
            makedirs(directory, mode=self.mode)
        
        chdir(directory)
        
        output = run(command, shell=True, capture_output=True, text=True)
        if log_output:
            data = output.stdout + "\n" + output.stderr
            self.log_output(output=data, directory=log_directory)

    def set_nondex_maven_plugin(self, nondex_maven_plugin = "nondex-maven-plugin:2.1.1"):
        if nondex_maven_plugin == "":
            nondex_maven_plugin = "nondex-maven-plugin:2.1.1"
        self.nondex_maven_plugin = nondex_maven_plugin


    def set_mode(self, mode: int) -> None:
        self.mode = mode
    
    def get_test_name_for_mvn(self, test_name: str) -> str:
        split_path = test_name.split(".")
        return f'"{split_path[:-1]}#{split_path[-1]}"'


    def log_output(self, output: str, directory: str, logname="") -> None:
        if logname == "":
            split_name = self.test_name.split(".")
            reformatted_name = ""
            for n in split_name:
                reformatted_name += n + "-"
            logname = f"{reformatted_name}.log"
        
        if not isdir(directory):
            makedirs(directory, mode=self.mode)
        chdir(directory)

        with open(f"{directory}/{logname}", "a") as f:
            f.write(output)


    def clone_project_repo(self, repo_link: str, repo_name: str, directory: str, log_path: str = "") -> None:
        chdir(directory)
        clone_path = f"{directory}/{repo_name}"
        
        if isdir(clone_path):
            self.run_command(f"rm -rf {clone_path}", directory=directory, log_directory=log_path)
        self.run_command(f"git clone {repo_link} {clone_path}", directory, log_directory=log_path)


    def __str__(self) -> str:
        return (
            "{\n"
            f"\tproject_url: {self.project_url}\n" 
            f"\tsha_detected: {self.sha_detected}\n" 
            f"\tmodule_path: {self.module_path}\n" 
            f"\ttest_name: {self.test_name}\n" 
            f"\tcategory: {self.category}\n"
            f"\tstatus: {self.status}\n" 
            f"\tpr_link: {self.pr_link}\n" 
            f"\tnotes: {self.notes}\n" 
            "}"
        )